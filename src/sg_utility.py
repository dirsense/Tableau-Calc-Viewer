import PySimpleGUI as sg

def popup_quick(message: str):
    duration = 1 if len(message) <= 35 else 2
    sg.popup_quick_message(message, keep_on_top=True, auto_close_duration=duration, background_color='#4A6886')