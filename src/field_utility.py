from calc_analyzer import CalcAnalyzer as ca
from win32gui import GetWindowText, GetForegroundWindow, GetClassName
import pyautogui as ag
import re, time
import win32clipboard

def get_field() -> tuple[str, str]:
    dsname = ''
    finame = ''
    win_title, win_class = get_active_window_info()

    if win_class[:2] == 'Qt':
        dsname, finame = get_field_in_qtform(win_title)

    elif win_class[:2] == 'Tk' and win_title in ca.fields:
        dsname, finame = get_field_in_tkform(win_title)

    return dsname, finame

def get_field_in_qtform(win_title: str) -> tuple[str, str]:
    if win_title[:7] == 'Tableau':
        ag.press('f2', interval=0.01)
    else:
        ag.doubleClick(duration=0.01)

    ag.hotkey('ctrl', 'c')
    OpenClipboardWithEvilRetries()
    clip_field = win32clipboard.GetClipboardData()
    win32clipboard.CloseClipboard()

    dsname = ca.primary_caption
    ptn = re.findall('\[.+?\]', clip_field)
    finame = ''

    if len(ptn) == 1:
        finame = str(ptn[0])

    elif len(ptn) == 2:
        dsname = str(ptn[0])
        finame = str(ptn[1])

    elif len(ptn) == 0:
        ag.hotkey('ctrl', 'a', interval=0.01)
        ag.hotkey('ctrl', 'c', interval=0.01)
        OpenClipboardWithEvilRetries()
        clip_field2 = win32clipboard.GetClipboardData()
        win32clipboard.CloseClipboard()

        finame = '[' + clip_field2 + ']'

    return dsname, finame

def get_field_in_tkform(win_title: str) -> tuple[str, str]:
    cf = ca.fields[win_title]
    calc = cf.calc
    tk_cursor_pos = str(cf.window['-mline-'].Widget.index('insert')).split('.')

    row = int(tk_cursor_pos[0])
    cursor_pos = int(tk_cursor_pos[1])
    calc = cf.calc.splitlines()[row-1]

    if cursor_pos <= 0 or cursor_pos >= len(calc) - 1:
        return '', ''
    
    blend_name = ''
    ds_name = ''
    field_name = ''
    left_part = ''
    right_part = ''

    for i in range(cursor_pos-1, -1, -1):
        if calc[i] == ']':
            break
        elif calc[i] == '[':
            left_part = calc[i:cursor_pos]
            if i >= 4 and calc[i-2:i] == '].':
                for b in range(i-3, -1, -1):
                    if calc[b] == '[':
                        blend_name = calc[b:i-1]
            break

    for i in range(cursor_pos, len(calc)):
        if calc[i] == '[':
            break
        elif calc[i] == ']':
            right_part = calc[cursor_pos:i+1]
            break

    if left_part != '' and right_part != '':
        field_name = left_part + right_part

    if blend_name == '':
        ds_name = ca.primary_caption
    else:
        ds_name = blend_name
    
    return ds_name, field_name

def get_active_window_info() -> tuple[str, str]:
    hwnd = GetForegroundWindow()
    return GetWindowText(hwnd), GetClassName(hwnd)

def OpenClipboardWithEvilRetries(retries=10, delay=0.1):
    while True:
        try:
            return win32clipboard.OpenClipboard()
        except:
            if retries == 0:
                raise
            retries -= 1
            time.sleep(delay)

