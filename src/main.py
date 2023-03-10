from calc_viewer import CalcViewer as cv
import field_utility as fu
import sg_utility as sgu
import PySimpleGUI as sg
import glob, sys, time, threading, keyboard

sg.theme('DarkGrey8')

class Receive():
    def __init__(self):
        self.window: sg.Window = None
        self.ROOP = False

    def target(self):
        while self.ROOP:
            if keyboard.is_pressed('F3'):
                dsname, finame = fu.get_field()
                fikey = finame.strip('[]')
                if dsname != cv.primary_caption:
                    fikey += ' (' + dsname.strip('[]') + ')'

                if fikey in cv.fields:
                    self.window.write_event_value('-qpop-', 'This field is already open')
                else:
                    if dsname in cv.tabdoc.fcap_field and finame in cv.tabdoc.fcap_field[dsname]:
                        f = cv.tabdoc.fcap_field[dsname][finame]
                        if f.calculation is None:
                            self.window.write_event_value('-qpop-', 'This field is not calculated field')
                        else:
                            calc = cv.tabdoc.replace_calc_field_id_to_caption(f.calculation, cv.tabdoc.dscap_dsid[dsname])
                            self.window.write_event_value('-cpop-', (fikey, calc))

                    elif finame in cv.tabdoc.pcap_pid:
                        self.window.write_event_value('-qpop-', 'This field is Parameter')
                    else:
                        self.window.write_event_value('-qpop-', 'This field was not found in the scanned document')
                time.sleep(1)

            elif keyboard.is_pressed('F4'):
                self.window.write_event_value('-all_cv_close-', None)
                time.sleep(1)

    def start(self):
        self.thread = threading.Thread(target=self.target)
        self.thread.start()

if __name__ == '__main__':
    r = Receive()

    def startEvent(window: sg.Window):
        r.window = window
        r.ROOP = True
        r.start()

    def finishEvent():
        r.ROOP = False
        window.close()
        sys.exit()

    def get_current_paths() -> tuple[str, str]:
        cur_paths = glob.glob('*.twb*')
        cur_value = '' if len(cur_paths) == 0 else cur_paths[0]
        return cur_value, cur_paths

    cur_value, cur_paths = get_current_paths()

    layout = [
        [sg.Column(layout=[
            [sg.Text('Primary Datasource')],
            [sg.Text('TWB or TWBX Path')],
            [sg.Button('Scan', pad=((5, 5), (5, 3)))]
        ], pad=(0, 0)),
        sg.Column(layout=[
            [sg.DropDown([], key='-primaryDS-', size=(50, 1), readonly=True, enable_events=True)],
            [sg.Combo(cur_paths, default_value=cur_value, key='-twbpath-', size=(50, 1))],
            [sg.Button('Reload Current Path', pad=((5, 5), (5, 3))),
             sg.FileBrowse('...', target='-twbpath-', file_types=(('Tableau Workbook', '*.twb*'), ),
             initial_folder='.', pad=((5, 5), (5, 3)))]
        ], pad=(0, 0))]
    ]

    window = sg.Window('Tableau Calc Viewer', layout, finalize=True)
    cv.window = window

    opening = True

    while True:
        window, event, values = sg.read_all_windows()

        if opening:
            opening = False
            startEvent(window)

        if event is None:
            if window == cv.window:
                finishEvent()
            else:
                window.close()
                del cv.fields[window.Title]

        elif event == 'Scan':
            cv.scan(values)

        elif event == '-cpop-':
            cv.initialize(values[event])

        elif event == '-qpop-':
            sgu.popup_quick(values[event])

        elif event == '-primaryDS-':
            cv.primary_caption = values[event]

        elif event == 'Reload Current Path':
            cur_value, cur_paths = get_current_paths()
            window['-twbpath-'].update(value=cur_value, values=cur_paths)

        elif event == '-all_cv_close-':
            for fi in cv.fields.values():
                if fi.window != cv.window:
                    fi.window.close()
            cv.fields.clear()
