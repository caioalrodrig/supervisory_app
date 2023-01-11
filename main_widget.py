from kivymd.uix.boxlayout import BoxLayout
from kivymd.uix.screen import MDScreen
from kivy.clock import Clock
from kivy.uix.popup import Popup
from pyModbusTCP.client import ModbusClient
from kivy.core.window import Window
from threading import Thread
from time import sleep
from datetime import datetime
from kivy.uix.label import Label
import random
from kivymd.uix.snackbar import Snackbar
from kivy_garden.graph import LinePlot
from TimesSeriesGraph import TimeSeriesGraph
from bdhandle import BDHandle


class ModbusPopUp(Popup):
    """Auxiliar class for popup MODBUS connection"""

    def __init__(self,**kwargs):
        """Constructor"""
        self._clientMOD= ModbusClient()
        super().__init__(**kwargs)
        self._msg= None

        
    def setInfo(self,message):
        if self._msg is not None:
            self.ids.config.remove_widget(self.info_label)
            self.info_label=Label(text="")
            self.ids.config.add_widget(self.info_label)
            self._msg=True

        else:
            self.info_label=Label(text=message)
            self.ids.config.add_widget(self.info_label)
            self._msg=True

        

    def clearInfo(self):
        if self._msg is not None:
            self.ids.config.remove_widget(self.info_label)
            self._msg=None

        else:
            self.info_label=Label(text="")
            self.ids.config.add_widget(self.info_label)
            self.ids.config.remove_widget(self.info_label)
            self._msg=None

            


class ScanPopup(Popup):
    """Auxiliar class for popup time settings just need a stance for updating scan time """
    def __init__(self,time,**kwargs):
        super().__init__(**kwargs)
        self.ids.scan.text=str(time)



class Main_widget(MDScreen):
    """  App home-screen MDScreen """
    _updateThread= None
    _updateWidget = None
    _tags={}
    def __init__(self,db_path,scan_time,server_ip,server_port,modbus_addrs,**kwargs):
        super().__init__(**kwargs)
        self._scantime = scan_time
        self._ip = server_ip
        self._port = server_port
        self._addrs= modbus_addrs
        self._mbuspopup = ModbusPopUp()
        self._scanpopup= ScanPopup(self._scantime)
        self._mbusclient = ModbusClient(host=self._ip,port=self._port)
        self._meas= {}
        self._meas['timestamp']=None
        self._meas['values']={}
        self._max_points=20
        for key,value in self._addrs.items():
            if key == 'furnace':
                plot_color = (1,0,0,1)
            else:
                plot_color = (random.random(),random.random(),random.random(),1)
            self._tags[key]= {'addr': value,'color': plot_color}
        self._graph= self.checkBoxDataGraph()
        self._histGraph=self.histGraphScreen(self._tags)
        self._db=BDHandle(db_path,self._tags)

    def updater(self):
        """Method for updating server and GUI """
        try:
            while self._updateThread:
                self.read_data()
                self.updateGUI()
                self._db.insertData(self._meas)
                sleep(self._scantime/1000)
        except Exception as e:
            self._mbusclient.close()
            print("Erro",e.args)

    def updaterStart(self,ip,port):
        "Method for thread instancing."
        try:
            Window.set_system_cursor("wait")
            self._mbusclient.open()
            if(self._mbusclient.is_open):
                self._mbuspopup.clearInfo()
                Snackbar(text="Server connected succesfully.",bg_color=(0,0,1,1)).open()
                self._mbuspopup.setInfo(message="App already connected.")
                Window.set_system_cursor("arrow")
                self._updateThread = Thread(target= self.updater)
                self._updateThread.start()
                self._mbuspopup.dismiss()
            else:
                self._mbuspopup.setInfo(message="Server connection failed.")
                Window.set_system_cursor("arrow")
        except Exception as e:
            print("Erro de conexao com servidor: ", e.args)
            


    def read_data(self):
        """MODBUS Data reading method """
        self._meas['timestamp']= datetime.now()
        try:
            for key,value in self._tags.items():
                self._meas['values'][key]=self._mbusclient.read_holding_registers(value['addr'],1)[0]       #parte loka
        except Exception as e:
            print("Error:", e)
            self._mbusclient.close()

    def updateGUI(self):
        """update GUI with data read"""
        try:
            for key,value in self._tags.items():
                self.ids[key].text= str(self._meas['values'][key]) +'ºC'
            # self.ids.lb_temp.size = (0.9*self.ids.lb_temp.size[0],self._meas['values']['furnace']/450*self.ids.termometer.size[1])

            self.ids.graf.updateGraph((self._meas['timestamp'],self._meas['values']['furnace']),0)
        except Exception as e:
            print("Error during tag reading:",e)


    def stopRefresh(self):
        """Stop GUI updating"""
        pass


    def checkBoxDataGraph(self):
        self.plot = LinePlot(line_width=1.5,color=self._tags['furnace']['color'])
        self.ids.graf.add_plot(self.plot)
        self.ids.graf.xmax=self._max_points

    def histGraphScreen(self,tags):
        for key, value in tags.items():
            cb=LabeledCheckBoxHistGraph()
            cb.ids.label.text=key
            cb.ids.label.color = value['color']
            cb.id=key
            self.ids.sensores.add_widget(cb)

    def stopRefresh(self):
        self._updateWidgets =False

    def getDataDB(self):
        """Method for users data collecting and DB look up  """
        try: 
            init_t = self.parseDTString(self.ids.tx_init_time.text)
            final_t=self.parseDTString(self.ids.tx_final_time.text) 
            cols =[]
            for sensor in self.ids.sensores.children:
                if sensor.ids.checkbox.active:
                    cols.append(sensor.id)
            if init_t is None or final_t is None or len(cols)==0:
                return
            cols.append('timestamp')
            dados= self._db.selectData(cols,init_t,final_t)

            if dados is None or len(dados['timestamp'])==0:
                return

            self.ids.grafdb.clearPlots() #class timeserie

            for key, value in dados.items():
                if key == 'timestamp':
                    continue
                p = LinePlot(line_width=1.5,color=self._tags[key]['color'])
                p.points = [(x,value[x]) for x in range(0,len(value))]
                self.ids.grafdb.add_plot(p)
            self.ids.grafdb.xmax=len(dados[cols[0]])
            self.ids.grafdb.update_x_labels([datetime.strftime(x,"%Y-%m-%d  %H:%M:%S.%f") for x in dados['timestamp']])
        except Exception as e:
            print("Erro na consulta de dados ",e)



    def parseDTString(self,datetime_str):
        try:
            d=datetime.strptime(datetime_str, '%d/%m/%Y %H:%M:%S')
            return d.strftime('%Y-%m-%d %H:%M:%S')
        except Exception as e:
            print("Error :",e)


class LabeledCheckBoxDataGraph(BoxLayout):
    pass

class LabeledCheckBoxHistGraph(BoxLayout):
    pass

def stopRefresh(self):
    self._updateWidgets =False

