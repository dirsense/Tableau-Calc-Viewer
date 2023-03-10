from __future__ import annotations
from tab_document import TabDocument
import sg_utility as sgu
import PySimpleGUI as sg
import os

class CalcViewer():
    window: sg.Window = None
    primary_caption = ''
    fields: dict[str, CalcViewer] = {}
    tabdoc: TabDocument = None

    def __init__(self, ft: tuple[str, str]):
        self.caption = ft[0]
        self.calc = ft[1]
        layout = [
            [sg.Multiline(self.calc, key='-mline-', expand_x=True, expand_y=True, enable_events=True)],
        ]
        self.window = sg.Window(self.caption, layout, size=(700, 300), finalize=True, keep_on_top=True, resizable=True)

    @classmethod
    def initialize(cls, ft: tuple[str, str]):
        cls.fields[ft[0]] = CalcViewer(ft)

    @classmethod
    def scan(cls, values):
        twbpath = values['-twbpath-']
        if not os.path.isfile(twbpath):
            sg.popup('Specified file does not exist')
            return
        cls.tabdoc = TabDocument(twbpath)

        primaries = list(cls.tabdoc.dscap_dsid.keys())
        cls.primary_caption = primaries[0]
        cls.window['-primaryDS-'].update(value=primaries[0], values=primaries)

        sgu.popup_quick('Scan complete')