# -*- coding:utf-8 -*-

import json
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtTest import *
import time
# from e1214_modbus import *
from pyModbusTCP.client import ModbusClient

from common import *

"""
"io": {
			"value_io_ip": "10.128.17.49",
			"value_io_relay_port": "0",
			"value_io_delay_time": "10"
		}
"""

class Cont(QPlainTextEdit):
    signal_push_call = pyqtSignal(int)
    
    def __init__(self):
        super().__init__()
        
        self.setMaximumBlockCount(50)

        self.io = None

        self.door_open = False
        self.called = False

        self.init_cont_contextmenu()

        self.last_open_time = time.time()
        self.last_close_time = time.time()
        self.last_detect_time = time.time()
        self.last_call_time = time.time()

    ## popup 메뉴 
    def init_cont_contextmenu(self):
        

        self.setContextMenuPolicy(Qt.ActionsContextMenu)

        act_open = QAction("출입문 열림" , self)
        act_close = QAction("출입문 닫힘" ,self)
        act_whe = QAction("휠체어" ,self)
        act_scu = QAction("스쿠터" ,self)
        act_sto = QAction("유모차" ,self)
        act_sil = QAction("실버카" ,self)
        act_push = QAction("E/L 호출" ,self)


        act_open.triggered.connect(self.detect_open)  #self.detect_wheelchair
        act_close.triggered.connect(self.detect_close)
        act_whe.triggered.connect(self.detect_wheelchair)
        act_scu.triggered.connect(self.detect_scuter)
        act_sto.triggered.connect(self.detect_stroller)
        act_sil.triggered.connect(self.detect_silvercar)
        act_push.triggered.connect(self.detect_call)

        self.addAction(act_open)
        self.addAction(act_close)
        self.addAction(act_whe)
        self.addAction(act_scu)
        self.addAction(act_sto)
        self.addAction(act_sil)
        self.addAction(act_push)


    def init_io(self, data):
        self.io_ip = data['value_io_ip']
        self.io_port = 502
        self.io_relay_port = int(data['value_io_relay_port'])
        self.io_delay_time = int(data['value_io_delay_time'])
        self.io_relay_push_time = 300

        ## 값 확인
        print(f"self.io_ip:{self.io_ip} self.io_port:{self.io_port} self.io_relay_port:{self.io_relay_port} self.io_delay_time:{self.io_delay_time} ")

        # arr_relay = [0, 0, 0, 0, 0, 0]
        # self.io.e1214.write_multiple_coils(0, arr_relay)

    def append_log(self, str):
        self.appendPlainText(f'[{self.now_time_str()}] {str}')

    @pyqtSlot(str)
    def receive_log(self, msg):
        self.append(f'r: {msg}')

    @pyqtSlot(str, dict)
    def receive_data(self, name, dict_value):
        
        if "door_open" in dict_value:
            self.receive_open()
        elif "door_close" in dict_value:
            self.receive_close()
        elif "wheelchair" in dict_value:
            self.check_process(name, dict_value)
        elif "stroller" in dict_value:
            self.check_process(name, dict_value)
        elif "silvercar" in dict_value:
            self.check_process(name, dict_value)
        elif "scuter" in dict_value:
            self.check_process(name, dict_value)
        else:
            print(f"no match dict key")

    @pyqtSlot()
    def receive_open(self):
        # print(f'receive_open...{self.door_open}')
        if self.door_open == False:
            self.append_log(f'open')
            self.last_open_time = time.time()
            self.door_open = True
            self.called = False

    @pyqtSlot()
    def receive_close(self):
        # print(f'receive_close...{self.door_open}')

        if self.door_open == True:
            self.append_log(f'close')
            self.last_close_time = time.time()

            self.door_open = False

    def push_call(self):
        self.append_log(f'E/L call [IO Relay:{self.io_relay_port}]')

        self.signal_push_call.emit(self.io_relay_port)
        

 

    def now_time_str(self):
        now = time.localtime()
        return time.strftime('%H:%M:%S', now)

    """
    detect시 문이 단혀있으면 호출했었는지 확인하여 처리
    한번 호출후 3초후 재 호출, EL 출발시간 기다린다
    """

    # @pyqtSlot()
    def check_process(self, name, dict):  # 사물이 인식 되었으면
        self.append_log(f'[{name}] {dict}')
        # print(f'check_process...{name}, {dict}')
        if self.door_open == True:  # 문이 열려있으면 넘어감
            # print("detect : door_open == True  $$$$$$$   pass")
            pass

        elif self.called == True:  # 문이 닫혀있고, 호출을 하였으면 넘어감
            # print("detect : called == True     $$$$$$$   pass")
            pass

        else:  # 단혀있고, 호출한적이 없으면 호출한다.
            gap = time.time() - self.last_close_time
            if gap > self.io_delay_time:  # 한번 호출후 딜레이 시간 후 재 호출, EL 출발시간 기다린다
                
                # self.append(f"대기시간 :{'%0d' %gap}")
                self.push_call()
                self.called = True

            else: 
                self.append_log(f"문 닫힘 후 {self.io_delay_time}초 미만")

    ##  외부에서 콜을 던질때 사용
    @pyqtSlot()
    def detect_wheelchair(self):
        dict = {"wheelchair": 0.9}
        self.receive_data("Test", dict)

    @pyqtSlot()
    def detect_stroller(self):
        dict = {"stroller": 0.9}
        self.receive_data("Test",dict)

    @pyqtSlot()
    def detect_silvercar(self):
        dict = {"silvercar": 0.9}
        self.receive_data("Test",dict)

    @pyqtSlot()
    def detect_scuter(self):
        dict = {"scuter": 0.9}
        self.receive_data("Test",dict)

    @pyqtSlot()
    def detect_open(self):
        dict = {"door_open":0.9}
        self.receive_data("Test",dict)

    @pyqtSlot()
    def detect_close(self):
        dict = {"door_close":0.9}
        self.receive_data("Test",dict)

    @pyqtSlot()
    def detect_call(self):
        self.push_call()





class Gui(QWidget):

    def __init__(self):
        super().__init__()

        self.init_ui()
        self.init_param()
        

    def init_ui(self):
        main_layout = QHBoxLayout()
        
        self.read_config()

        self.cont = Cont()
        self.init_param()

        

        # self.panel_btn = Panel_cont_btn(self.cont)

        main_layout.addWidget(self.cont)
        # main_layout.addWidget(self.panel_btn)

        self.setLayout(main_layout)

    def init_param(self):
        self.cont.init_io(self.data['up']['io'])

    def read_config(self):
        self.data = read_config(path_config)
   



if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = Gui()
    gui.show()
    sys.exit(app.exec_())
