from kivy.lang.builder import Builder
Builder.load_file('Mainwidget.kv')
Builder.load_file('Popups.kv')

from kivy.uix.popup import Popup
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivy.clock import Clock
from kivymd.uix.boxlayout import BoxLayout
from main_widget import Main_widget, ScanPopup, ModbusPopUp
from pyModbusTCP.client import ModbusClient


class MainApp(MDApp):
    """MAIN basic application."""
    def build(self):
        """Defines the main app"""
        
        self.theme_cls.primary_palette= "Orange"
        self.theme_cls.primary_hue= "700"
        self.theme_cls.accent_palette="Orange"

        return Main_widget(scan_time=1000,server_ip='127.0.0.1',server_port=502,
                                modbus_addrs={
                                'furnace': 1000,
                                'gas': 1001,
                                'gasoline': 1002,
                                'nafta': 1003,
                                'querosine': 1004,
                                'diesel': 1005,
                                'lub_oil': 1006,
                                'fuel_oil': 1007,                                
                                'residues': 1008})

if __name__ == '__main__':
    MainApp().run()
