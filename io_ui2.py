#-*-coding:utf-8-*-

"""
어쩌구 저쩌구
"""

import sys

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtTest import *

import numpy as np
import cv2

from queue import Queue

from pyModbusTCP.client import ModbusClient


# TCP auto connect on first modbus request
# e1214 = ModbusClient(host="10.128.17.49", port=502, unit_id=1, auto_open=True)

# TCP auto connect on modbus request, close after it
# c = ModbusClient(host="10.128.17.49", auto_open=True, auto_close=True)





        

        
"""
DI port  0,  1,  2,  3,  4,   5
reg     [1] [2] [4] [8] [16] [32]
"""

def get_time():
    current_time = QTime.currentTime()
    text_time = current_time.toString("hh:mm:ss")
    # time_msg = "현재시간: " + text_time
    return text_time




class R_Button(QPushButton):
    """
    QPushButton 은 QWidget을 상속받고 있으므로 단일 창으로 표출 가능
    """
    def __init__(self, title):
        QPushButton.__init__(self, title)
        self.setFixedSize(100, 20)
        # self.setStyleSheet("background-color: green")

        self.setCheckable(True)
        self.toggled.connect(self.slot_toggle)
        self.slot_toggle(False)

    @pyqtSlot(bool)
    def slot_toggle(self, state):
        """
        toggle 상태에 따라 배경색과 상태 텍스트 변환
        """
        self.setStyleSheet("background-color: %s" % ({True: "red", False: "green"}[state]))
        self.setText({True: "Close", False: "Open"}[state])


class DI_Label(QLabel):
    """
    QPushButton 은 QWidget을 상속받고 있으므로 단일 창으로 표출 가능
    """
    di_input = ["color:blue; background-color:red;", "input"]
    di_none =  ["color:blue; background-color:green;", "none"]

    def __init__(self, title):
        QLabel.__init__(self, title)
        # self.setFixedSize(100, 30)
        self.setAlignment(Qt.AlignCenter)
        self.set_state(False)

    @pyqtSlot(bool)
    def set_state(self, state):
        # print(f'DI  set_state {state}')
        # if state:
        #     self.setStyleSheet(self.di_input[0])
        #     self.setText(self.di_input[1]) 
        # else:
        #     self.setStyleSheet(self.di_none[0])
        #     self.setText(self.di_none[1])     
        """
        toggle 상태에 따라 배경색과 상태 텍스트 변환
        """
        self.setStyleSheet({True: self.di_input[0], False: self.di_none[0]}[state])
        self.setText({True: self.di_input[1], False: self.di_none[1]}[state])

        
class R_Label(QLabel):
    """
    QPushButton 은 QWidget을 상속받고 있으므로 단일 창으로 표출 가능
    """
    r_close = ["color:blue; background-color:red;", "Close"]
    r_open =  ["color:blue; background-color:green;", "Open"]

    def __init__(self, title):
        QLabel.__init__(self, title)
        # self.setFixedSize(100, 30)
        self.setAlignment(Qt.AlignCenter)
        self.set_state(False)

    @pyqtSlot(bool)
    def set_state(self, state):
        # if state:
        #     self.setStyleSheet(self.r_close[0])
        #     self.setText(self.r_close[1]) 
        # else:
        #     self.setStyleSheet(self.r_open[0])
        #     self.setText(self.r_open[1])  
            
        """
        toggle 상태에 따라 배경색과 상태 텍스트 변환
        """
        self.setStyleSheet({True: self.r_close[0], False: self.r_open[0]}[state])
        self.setText({True: self.r_close[1], False: self.r_open[1]}[state])

class Test_thread(QThread):
        
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        print(f"Test_thread 생성")
        
    def __del__(self):
        print(f"Test_thread 소멸")
        
    def set_data(self, ip, port):
        self.io_ip = ip
        self.io_port = port
        
    def run(self):
        print(f"Test_thread run")
        while True:
            print(f"{get_time()}: Test_thread")
            QTest.qWait(500)
        

class IO_thread(QThread):
    signal_di_relay = pyqtSignal(list, list)
    signal_state = pyqtSignal(bool) ## 연결: true 단절: False 2가지로만 나타낸다.
    
        
    def __init__(self):
        super().__init__()
        self.parent = None
        print(f"IO_thread 생성")
        
        self.que_relay_on = Queue() ## 릴레이 셋
        self.que_relay_off = Queue() ## 릴레이 셋
        
        
        self.relay_push_time = 200
        
        self._run_flag = False
        
        self.io_ip = None
        self.io_port = None
        
        self.io_state = None
        
        self.di_rega = None
        self.coil_regs = None
        
        # self.relay_write_value = None
        
    def __del__(self):
        print(f"IO_thread 소멸")
        
    def set_data(self, ip, port):
        self.io_ip = ip
        self.io_port = port
        
    @pyqtSlot(int, bool)
    def set_relay(self, io_num, value):
        c = ModbusClient(host=self.io_ip, port=self.io_port, auto_open=True)
        if c.open():
            c.write_single_coil(io_num, value)
            
    @pyqtSlot(int)
    def set_relay_on_off(self, io_num):
        print(f'set_relay_on_off / io_num:{io_num} ')
        self.que_relay_on.put(io_num)
        self.que_relay_off.put(io_num)
            
    def relay_on_off(self, io_num, delay_time):
        print(f'relay_on_off / io_num:{io_num}, delay_time:{delay_time} ')
        c = ModbusClient(host=self.io_ip, port=self.io_port, auto_open=True)
        if c.open():
            c.write_single_coil(io_num, True)
            QTest.qWait(delay_time)
            c.write_single_coil(io_num, False)
            
            
    def run(self):
        if self._run_flag :
            # print(f"IO_thread run")
            self.io_state = False
            c = ModbusClient(host=self.io_ip, port=self.io_port, auto_open=True)
            while self._run_flag:
                
                if c.open():
                    # print(f"{get_time()} ModbusClient open ? : {c.open()}")
                    
                    ### relay control
                    if self.que_relay_on.qsize() > 0:
                        while self.que_relay_on.qsize() > 0:
                            c.write_single_coil(self.que_relay_on.get(), True)
                    else:
                        if self.que_relay_off.qsize() > 0:
                            while self.que_relay_off.qsize() > 0:
                                c.write_single_coil(self.que_relay_off.get(), False)
                        
                    ### read modbus
                    self.di_regs = c.read_input_registers(0x30, 1)
                    self.r_regs = c.read_coils(0, 6)
                    # print(f"IO_thread : {self.di_regs} {self.r_regs}")
                    self.signal_di_relay.emit(self.di_regs2di_bool(self.di_regs[0]), c.read_coils(0, 6))
                    QTest.qWait(200)

                else: #c.open : False
                    # self.io_state = False
                    self.signal_state.emit(False)
                    print(f"{get_time()} open fail,   QTest.qWait(500), re connect")
                    QTest.qWait(200)
                    c = ModbusClient(host=self.io_ip, port=self.io_port, auto_open=True)
                    # print('unable to read coils...loop break')
                    
                
    def di_regs2di_bool(self, num):
        binary_num = bin(num)[2:]
        flip_binary = binary_num[::-1]
        # print(flip_binary)
        # # return flip_binary

        st_bool = []

        if num == 0:
            st_bool = [False, False, False, False, False, False]
        else:
            for ss in flip_binary:
                if ss == '1':
                    st_bool.append(True)
                else :
                    st_bool.append(False)

        # print(st_bool)
        return st_bool
        

class Ui_test_btn(QWidget):
    # signal_set_relay  = pyqtSignal(int, bool)
    
    def __init__(self):
        super().__init__()
        
        self.init_ui()
        
    def init_ui(self):
        self.btn_name_list = ["0", "1", "2", "3", "4", "5"]
        self.btn_list = []
        
        box_main = QHBoxLayout()
        
        for i in range(len(self.btn_name_list)):
            btn = QPushButton(self.btn_name_list[i])
            btn.setObjectName(str(i))
            btn.clicked.connect(self.clicked_test_btn)
            self.btn_list.append(btn)
            box_main.addWidget(btn)
            
        self.setLayout(box_main)
        
    def clicked_test_btn(self):
        sending_button = self.sender()
        print(f'test_btn_clicked : {int(sending_button.objectName())}')
        

class Ui_io(QGroupBox):
    signal_set_relay  = pyqtSignal(int, bool)
    
    def __init__(self):
        super().__init__()
        
        # print("Ui_io  init...")
        self.init_ui()
        
        
    def init_ui(self):
        self.list_di = []
        self.list_r = []
        self.list_call = []
        self.stat_label = None
        
        self.label_style = "color: white; border-style: solid; border-color: #54A0FF; background-color: rgb(0,0,0)"
        
        port_label = ["PORT 0", "PORT 1", "PORT 2", "PORT 3", "PORT 4", "PORT 5"]
        di_label = ["None", "None", "None", "None", "None", "None"]
        relay_label = ["open", "open", "open", "open", "open", "open"]

        self.setTitle("IO 제어기")
        
        #타이틀
        box_label = QHBoxLayout()
        label = QLabel("구분")
        label.setStyleSheet(self.label_style)
        label.setMinimumSize(100, 20)
        label.setAlignment(Qt.AlignCenter)
        box_label.addWidget(label)
        for i in range(6):
            label = QLabel(port_label[i])
            # label.setStyleSheet(self.unset)
            label.setMinimumSize(100, 20)
            label.setAlignment(Qt.AlignCenter)
            # self.list_di.append(label)
            box_label.addWidget(label)
        
        #DI
        box_di = QHBoxLayout()
        label = QLabel("DI 상태")
        label.setStyleSheet(self.label_style)
        label.setMinimumSize(100, 20)
        label.setAlignment(Qt.AlignCenter)
        box_di.addWidget(label)
        for i in range(6):
            label = DI_Label(di_label[i])
            label.setMinimumSize(100, 20)
            self.list_di.append(label)
            box_di.addWidget(label)

        ##### Relay box
        box_R = QHBoxLayout()
        label = QLabel("Relay 상태")
        label.setStyleSheet(self.label_style)
        label.setMinimumSize(100, 20)
        label.setAlignment(Qt.AlignCenter)
        box_R.addWidget(label)
        for i in range(6):
            btn = R_Label(relay_label[i])
            btn.setObjectName(str(i))
            # btn.clicked.connect(self.clicked_r_btn)
            self.list_r.append(btn)
            box_R.addWidget(btn)

        ##### push Relay 
        box_call = QHBoxLayout()
        label = QLabel("Push Call")
        label.setStyleSheet(self.label_style)
        label.setMinimumSize(100, 20)
        label.setAlignment(Qt.AlignCenter)
        box_call.addWidget(label)
        for i in range(6):
            btn = QPushButton(str(i))
            btn.setObjectName(str(i))
            # btn.clicked.connect(self.clicked_call_btn)
            btn.pressed.connect(self.call_btn_pressed)
            btn.released.connect(self.call_btn_released)
            self.list_call.append(btn)
            box_call.addWidget(btn)
            
        ##### 상태 표시용 라벨
        self.stat_label = QLabel("IO제어기 연결 안됨")

 
        box_main = QVBoxLayout()
        box_main.addLayout(box_label)
        box_main.addLayout(box_di)
        box_main.addLayout(box_R)
        box_main.addLayout(box_call)
        box_main.addWidget(self.stat_label)

        self.setLayout(box_main)

 

    def call_btn_pressed(self):
        sending_button = self.sender()
        print(f'call_btn_pressed : {int(sending_button.objectName())}')
        
        self.signal_set_relay.emit(int(sending_button.objectName()), True)
        
    def call_btn_released(self):
        sending_button = self.sender()
        print(f'call_btn_released : {int(sending_button.objectName())}')
        
        self.signal_set_relay.emit(int(sending_button.objectName()), False)
    
    @pyqtSlot(bool)
    def disp_state(self, stat):
        print(f'recived io state : {stat}')
        if stat:
            self.stat_label.setText(f'IO 제어기 연결됨')
        else:
            self.stat_label.setText(f'IO 제어기 연결 해제')
                
    @pyqtSlot(list)
    def disp_relay(self, st_r):
        # print(f'recived relay : {st_r}')
        for i in range(len(st_r)):
            
            self.list_r[i].set_state(st_r[i])
            
    @pyqtSlot(list)
    def disp_di(self, ans):
        # print(f'recived di: {ans}')        
        for i in range(len(ans)):
            self.list_di[i].set_state(ans[i])
            
    @pyqtSlot(list, list)
    def disp_di_relay(self, di, rel):
        # print(f'recived di relay: {di} {rel}')   
        self.stat_label.setText(f'IO 제어기 데이터 수신 시각 : {get_time()} ')
        for i in range(6):
            self.list_di[i].set_state(di[i])
            self.list_r[i].set_state(rel[i])
        
        
    @pyqtSlot(int)
    def push_call(self, no):
        # global io_ok
        
        self.io.set_relay_on_off(no, self.on_off_delay_time)
            
     

class Test_main(QMainWindow):
    
    def __init__(self):
        super().__init__()
        
        ## 사용변수 초기화
        self.ui_io = None
        self.io_thread = None
        
        self.io_ip = None
        self.io_port = None
        
        self.init_ui()
        self.set_data()
        
        ### 테스트용 버튼 정의
        self.init_test_btn()
        
    def init_ui(self):
        self.setWindowTitle("자동호출 시스템    Ver 3.1")

        self.statusBar = self.statusBar()
        self.statusBar.showMessage("ready")

        # self.setWindowIcon(QIcon('./assets/editor.png'))
        # self.setGeometry(0, 0, 1300, 600)

        self.ui_io = Ui_io()
        self.ui_test_btn = Ui_test_btn()

        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.addWidget(self.ui_io)
        layout.addWidget(self.ui_test_btn)

        self.setCentralWidget(widget)
        # self.layout = QVBoxLayout(self.ui_test_btn)
        
    def set_data(self):
        self.io_ip = "10.128.17.49"
        self.io_port = 502
        
    def init_test_btn(self):
                
        self.ui_test_btn.btn_list[0].setText("start")
        self.ui_test_btn.btn_list[0].clicked.connect(self.init_start)
        
        
    def init_start(self):
        ### test thread start
        # self.test = Test_thread(self)
        # self.test.start()
        
        ### io thread start
        self.io_thread = IO_thread()
        # self.io_thread.signal_relay.connect(self.ui_io.disp_relay)
        # self.io_thread.signal_di.connect(self.ui_io.disp_di)
        self.io_thread.signal_di_relay.connect(self.ui_io.disp_di_relay)
        self.io_thread.signal_state.connect(self.ui_io.disp_state)
        
        self.io_thread.set_data(self.io_ip, self.io_port)
               
        self.ui_io.signal_set_relay.connect(self.io_thread.set_relay)
        
        self.io_thread._run_flag = True
        self.io_thread.start()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    
    
    ##
    # a = Ui_io()
    # a.show()
    
    a = Test_main()
    a.show()
    
    
    sys.exit(app.exec_())
