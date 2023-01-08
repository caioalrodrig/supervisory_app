# import sys
# from cx_Freeze import setup, Executable
# from kivy.lang.builder import Builder
# Builder.load_file('Mainwidget.kv')
# Builder.load_file('Popups.kv')
# from kivy.uix.popup import Popup
# from kivymd.app import MDApp
# from kivymd.uix.screen import MDScreen
# from kivy.clock import Clock
# from kivymd.uix.boxlayout import BoxLayout
# from main_widget import Main_widget, ScanPopup, ModbusPopUp
# from pyModbusTCP.client import ModbusClient
# from kivy.core.window import Window
# from threading import Thread
# from time import sleep
# from datetime import datetime
# from kivy.uix.label import Label
# import random
# from kivymd.uix.snackbar import Snackbar
# from kivy_garden.graph import LinePlot
# from TimesSeriesGraph import TimeSeriesGraph
# from bdhandle import BDHandle


# base = None
# if sys.platform == "win32":
#     base = "Win32GUI"

# executables = [
#         Executable("main.py", base=base)
# ]

# buildOptions = dict(
#         packages = [],
#         includes = ["kivy","kivymd","bdhandle","threading","main_widget","time","datetime","random","TimesSeriesGraph"],
#         include_files = [],
#         excludes = []
# )




# setup(
#     name = "Refinery",
#     version = "1.0",
#     description = "Jogo da cobrinha",
#     options = dict(build_exe = buildOptions),
#     executables = executables
#  )
