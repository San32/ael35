# -*- coding:utf-8 -*-

import cv2
import json
import sys
import time
import os
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtTest import *
import numpy as np


# cam_dict = {
#     "url": "",
#     "cam_use": "true",
#     "value_open" : 0,
#     "value_close" : "",
#     "value_wheelchair" : "",
#     "value_stroller" : "",
#     "value_silvercar" : "",
#     "value_scuter" : "",
#     "poi_use" : "",
#     "value_x" : "",
#     "value_y" : "",
#     "value_w" : "",
#     "value_h" : "",
# }

# io_dict =  {
#     "value_io_ip": "",
#     "value_io_relay_port": "",
#     "value_io_delay_time": "",
#     }

url_width = 500

from common import *


## 인식률 lineEdit
class ValueBox(QLineEdit):
    def __init__(self, val):
        super().__init__(val)
        self.setMaximumWidth(45)
        self.setAlignment(Qt.AlignRight)

class KSpinBox(QSpinBox):
    def __init__(self):
        super().__init__()
        self.setMaximum(640)
        self.setMinimum(0)

## QLabel 우측정렬 // 타이틀 표시용으로 사용
class KLabel(QLabel):
    def __init__(self, title):
        super().__init__()
        self.setText(title)
        # self.setAlignment(Qt.AlignRight)
        # self.setAlignment(Qt.AlignLeft)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("color: blue;"
                      "border-style: solid;"
                      "border-width: 2px;"
                      "border-color: green;"
                      "border-radius: 3px")
        self.setMinimumWidth(150)

# ## 공통사항 설정 UI
# class Common_conf_ui(QWidget):

#     def __init__(self, title):
#         super().__init__()
#         self.title = title
#         self.init_ui()
#         # self.show()

#     def init_ui(self):
#         self.conf_path = QLineEdit()    
#         self.conf_path.setFixedWidth(400)
#         self.conf_change = QPushButton("파일 변경")
        
#         lay_1 = QHBoxLayout()
#         lay_1.addWidget(KLabel(self.title))
#         lay_1.addWidget(QLabel("파일 경로"))
#         lay_1.addWidget(self.conf_path)
#         # lay_1.addWidget(QLabel("        카메라 영상분석 반복 시간"))
#         lay_1.addWidget(self.conf_change)
#         lay_1.addStretch(1)

#         self.setLayout(lay_1)

#     def set_data(self, data):
#         try:
#             self.auto_start.setChecked(bool(data['auto_start']))
#             self.read_cam_time.setText(data['read_cam_time'])
#         except:
#             # print("err")
#             return "E"

#     def get_data(self):
#         try:
#             data = {
#                     "auto_start": self.auto_start.isChecked(),
#                     "read_cam_time" : self.read_cam_time.text(),
#                 }
#             return data

#         except:
#             # print("err")
#             return "E"

## 공통사항 설정 UI
class Common_conf_ui(QWidget):

    def __init__(self, title):
        super().__init__()
        self.title = title
        self.init_ui()
        # self.show()

    def init_ui(self):
        self.conf_path = QLineEdit()    
        self.conf_path.setFixedWidth(400)
        self.conf_change = QPushButton("파일 변경")
        
        lay_1 = QHBoxLayout()
        lay_1.addWidget(KLabel(self.title))
        lay_1.addWidget(QLabel("파일 경로"))
        lay_1.addWidget(self.conf_path)
        # lay_1.addWidget(QLabel("        카메라 영상분석 반복 시간"))
        lay_1.addWidget(self.conf_change)
        lay_1.addStretch(1)

        self.setLayout(lay_1)

    def set_data(self, data):
        try:
            self.auto_start.setChecked(bool(data['auto_start']))
            self.read_cam_time.setText(data['read_cam_time'])
        except:
            # print("err")
            return "E"

    def get_data(self):
        try:
            data = {
                    "auto_start": self.auto_start.isChecked(),
                    "read_cam_time" : self.read_cam_time.text(),
                }
            return data

        except:
            # print("err")
            return "E"


## IO제어기 설정 UI
class IO_conf_ui(QWidget):

    def __init__(self, title):
        super().__init__()
        self.title = title
        self.init_ui()
        # self.show()

    def init_ui(self):
        self.io_ip = QLineEdit("192.168.0.0")
        self.io_relay_port = QLineEdit("0")
        self.io_delay_time = QLineEdit("10")

        lay_1 = QHBoxLayout()
        lay_1.addWidget(KLabel(self.title))
        lay_1.addWidget(QLabel("   IP"))
        lay_1.addWidget(self.io_ip)
        lay_1.addWidget(QLabel("   릴레이 포트"))
        lay_1.addWidget(self.io_relay_port)
        lay_1.addWidget(QLabel("   지연시간"))
        lay_1.addWidget(self.io_delay_time)
        lay_1.addStretch(1)

        self.setLayout(lay_1)

    def set_data(self, data):
        try:
            self.io_ip.setText(data['value_io_ip'])
            self.io_relay_port.setText(data['value_io_relay_port'])
            self.io_delay_time.setText(data['value_io_delay_time'])
        except:
            # print("err")
            return "E"

    def get_data(self):
        try:
            data = {
                    "value_io_ip": self.io_ip.text(),
                    "value_io_relay_port" : self.io_relay_port.text(),
                    "value_io_delay_time" : self.io_delay_time.text(),
                }
            return data

        except:
            # print("err")
            return "E"

## 카메라 설정 UI
class ELCam_conf_ui(QWidget):

    signal_clicked_btn_cam_set = pyqtSignal()

    def __init__(self, title):
        super().__init__()
        self.title = title
        self.init_ui()
        # self.show()

    def set_data(self, data):
        try:
            self.cam_url.setText(data['cam']['url'])
            self.cam_cam_use.setChecked(bool(data['cam']['use']))
            self.cam_value_open.setText(data['detect']['door_open'])
            self.cam_value_close.setText(data['detect']['door_close'])
            self.cam_value_wheelchair.setText(data['detect']['wheelchair'])
            self.cam_value_stroller.setText(data['detect']['stroller'])
            self.cam_value_silvercar.setText(data['detect']['silvercar'])
            self.cam_value_scuter.setText(data['detect']['scuter'])
            self.cam_poi_use.setChecked(bool(data['poi']['use']))
            self.cam_poi_x.setText(data['poi']['x'])
            self.cam_poi_y.setText(data['poi']['y'])
            self.cam_poi_w.setText(data['poi']['e_x'])
            self.cam_poi_h.setText(data['poi']['e_y'])
        except Exception as e:
            print(f'err {e}')
            return "E"

    def get_data(self):
        try:
            cam_data = {
                "url": self.cam_url.text(),
                "use": self.cam_cam_use.isChecked(),
            }

            detect_data = {
                "door_open" : self.cam_value_open.text(),
                "door_close" : self.cam_value_close.text(),
                "wheelchair" : self.cam_value_wheelchair.text(),
                "stroller" : self.cam_value_stroller.text(),
                "silvercar" : self.cam_value_silvercar.text(),
                "scuter" : self.cam_value_scuter.text(),
            }

            poi_data = {
                "use" : self.cam_poi_use.isChecked(),
                "x" : self.cam_poi_x.text(),
                "y" : self.cam_poi_y.text(),
                "e_x" : self.cam_poi_w.text(),
                "e_y" : self.cam_poi_h.text(),
            }
            data = {
                    "cam": cam_data,
                    "detect": detect_data,
                    "poi" : poi_data
            }
            return data

        except:
            # print("err")
            return "E"

    def change_cam_use(self, state):
        if state == Qt.Checked:
            self.cam_url.setEnabled(True)
        else:
            self.cam_url.setEnabled(False)

    def clicked_btn_cam_set(self):
        self.signal_clicked_btn_cam_set.emit()
        # pass

    def change_poi_use(self, state):
        if state == Qt.Checked:
            ## 
            self.cam_poi_x.setEnabled(True)
            self.cam_poi_y.setEnabled(True)
            self.cam_poi_w.setEnabled(True)
            self.cam_poi_h.setEnabled(True)
        else:
            self.cam_poi_x.setEnabled(False)
            self.cam_poi_y.setEnabled(False)
            self.cam_poi_w.setEnabled(False)
            self.cam_poi_h.setEnabled(False)

    def init_ui(self):
        ## 생성
        self.cam_url = QLineEdit()
        self.cam_cam_use = QCheckBox()
        self.cam_value_open = ValueBox("0.8")
        self.cam_value_close = ValueBox("0.8")
        self.cam_value_wheelchair = ValueBox("0.8")
        self.cam_value_stroller = ValueBox("0.8")
        self.cam_value_silvercar = ValueBox("0.8")
        self.cam_value_scuter = ValueBox("0.8")
        self.cam_poi_use = QCheckBox()
        self.cam_poi_x = ValueBox("0")
        self.cam_poi_y = ValueBox("0")
        self.cam_poi_w = ValueBox("400")
        self.cam_poi_h = ValueBox("300")

        self.btn_cam_set = QPushButton("설정")

        ## 설정
        self.cam_url.setMinimumWidth(600)
        
        self.cam_cam_use.stateChanged.connect(self.change_cam_use)
        self.cam_poi_use.stateChanged.connect(self.change_poi_use)
        self.btn_cam_set.clicked.connect(self.clicked_btn_cam_set)

        self.cam_url.setEnabled(False)
        self.cam_poi_x.setEnabled(False)
        self.cam_poi_y.setEnabled(False)
        self.cam_poi_w.setEnabled(False)
        self.cam_poi_h.setEnabled(False)
        

        ##
        lay_1 = QHBoxLayout()
        # lay_1.addWidget(KLabel("카메라 설정"))
        lay_1.addWidget(QLabel("사용"))
        lay_1.addWidget(self.cam_cam_use)
        lay_1.addWidget(QLabel("   URL"))
        lay_1.addWidget(self.cam_url)
        lay_1.addStretch(1)
        

        lay_2 = QHBoxLayout()
        # lay_2.addWidget(KLabel("민감도 설정"))
        lay_2.addWidget(QLabel("문 열림"))
        lay_2.addWidget(self.cam_value_open)
        lay_2.addWidget(QLabel("문 닫힘"))
        lay_2.addWidget(self.cam_value_close)
        lay_2.addWidget(QLabel("휠체어"))
        lay_2.addWidget(self.cam_value_wheelchair)
        lay_2.addWidget(QLabel("유모차"))
        lay_2.addWidget(self.cam_value_stroller)
        lay_2.addWidget(QLabel("실버카"))
        lay_2.addWidget(self.cam_value_silvercar)
        lay_2.addWidget(QLabel("스쿠터"))
        lay_2.addWidget(self.cam_value_scuter)
        lay_2.addStretch(1)

        lay_3 = QHBoxLayout()
        # lay_3.addWidget(KLabel("관심영역"))
        lay_3.addWidget(QLabel("사용"))
        lay_3.addWidget(self.cam_poi_use)
        # lay_3.addWidget(QLabel("   "), 1)
        lay_3.addWidget(QLabel("   시작점 x:"))
        lay_3.addWidget(self.cam_poi_x)
        lay_3.addWidget(QLabel("y:"))
        lay_3.addWidget(self.cam_poi_y)
        lay_3.addWidget(QLabel("   끝점 x"))
        lay_3.addWidget(self.cam_poi_w)
        lay_3.addWidget(QLabel("y:"))
        lay_3.addWidget(self.cam_poi_h)
        lay_3.addStretch(1)
        # lay_3.addWidget(self.btn_cam_set)   ## 카메라 설정버튼 비활성화

        vbox = QVBoxLayout()
        vbox.addLayout(lay_1)
        vbox.addLayout(lay_2)
        vbox.addLayout(lay_3)   ##poi 설정 비활성화

        ##
        lay = QHBoxLayout()
        lay.addWidget(KLabel(self.title))
        lay.addLayout(vbox)
        
        self.setLayout(lay)


class ELCam_conf_ui2(QWidget):

    signal_clicked_btn_cam_set = pyqtSignal()

    def __init__(self, title):
        super().__init__()
        self.title = title
        self.init_ui()
        # self.show()

    def set_data(self, data):
        try:
            self.cam_url.setText(data['cam']['url'])
            self.cam_cam_use.setChecked(bool(data['cam']['use']))
            self.cam_value_open.setText(data['detect']['door_open'])
            self.cam_value_close.setText(data['detect']['door_close'])
            self.cam_value_wheelchair.setText(data['detect']['wheelchair'])
            self.cam_value_stroller.setText(data['detect']['stroller'])
            self.cam_value_silvercar.setText(data['detect']['silvercar'])
            self.cam_value_scuter.setText(data['detect']['scuter'])
            self.cam_poi_use.setChecked(bool(data['poi']['use']))
            self.cam_poi_x.setText(data['poi']['x'])
            self.cam_poi_y.setText(data['poi']['y'])
            self.cam_poi_w.setText(data['poi']['e_x'])
            self.cam_poi_h.setText(data['poi']['e_y'])
        except Exception as e:
            print(f'err {e}')
            return "E"

    def get_data(self):
        try:
            cam_data = {
                "url": self.cam_url.text(),
                "use": self.cam_cam_use.isChecked(),
            }

            detect_data = {
                "door_open" : self.cam_value_open.text(),
                "door_close" : self.cam_value_close.text(),
                "wheelchair" : self.cam_value_wheelchair.text(),
                "stroller" : self.cam_value_stroller.text(),
                "silvercar" : self.cam_value_silvercar.text(),
                "scuter" : self.cam_value_scuter.text(),
            }

            poi_data = {
                "use" : self.cam_poi_use.isChecked(),
                "x" : self.cam_poi_x.text(),
                "y" : self.cam_poi_y.text(),
                "e_x" : self.cam_poi_w.text(),
                "e_y" : self.cam_poi_h.text(),
            }
            data = {
                    "cam": cam_data,
                    "detect": detect_data,
                    "poi" : poi_data
            }
            return data

        except:
            # print("err")
            return "E"

    def change_cam_use(self, state):
        if state == Qt.Checked:
            self.cam_url.setEnabled(True)
        else:
            self.cam_url.setEnabled(False)

    def clicked_btn_cam_set(self):
        self.signal_clicked_btn_cam_set.emit()
        # pass

    def change_poi_use(self, state):
        if state == Qt.Checked:
            ## 
            self.cam_poi_x.setEnabled(True)
            self.cam_poi_y.setEnabled(True)
            self.cam_poi_w.setEnabled(True)
            self.cam_poi_h.setEnabled(True)
        else:
            self.cam_poi_x.setEnabled(False)
            self.cam_poi_y.setEnabled(False)
            self.cam_poi_w.setEnabled(False)
            self.cam_poi_h.setEnabled(False)

    def init_ui(self):
        ## 생성
        self.cam_url = QLineEdit()
        self.cam_cam_use = QCheckBox()
        self.cam_value_open = ValueBox("0.5")
        self.cam_value_close = ValueBox("0.5")
        self.cam_value_wheelchair = ValueBox("0.5")
        self.cam_value_stroller = ValueBox("0.5")
        self.cam_value_silvercar = ValueBox("0.5")
        self.cam_value_scuter = ValueBox("0.5")
        self.cam_poi_use = QCheckBox()
        self.cam_poi_x = ValueBox("0")
        self.cam_poi_y = ValueBox("0")
        self.cam_poi_w = ValueBox("640")
        self.cam_poi_h = ValueBox("480")

        self.btn_cam_set = QPushButton("설정")

        ## 설정
        self.cam_url.setMinimumWidth(600)
        
        self.cam_cam_use.stateChanged.connect(self.change_cam_use)
        self.cam_poi_use.stateChanged.connect(self.change_poi_use)
        self.btn_cam_set.clicked.connect(self.clicked_btn_cam_set)

        self.cam_url.setEnabled(False)
        self.cam_poi_x.setEnabled(False)
        self.cam_poi_y.setEnabled(False)
        self.cam_poi_w.setEnabled(False)
        self.cam_poi_h.setEnabled(False)
        

        ##
        lay_1 = QHBoxLayout()
        # lay_1.addWidget(KLabel("카메라 설정"))
        lay_1.addWidget(QLabel("사용"))
        lay_1.addWidget(self.cam_cam_use)
        lay_1.addWidget(QLabel("   URL"))
        lay_1.addWidget(self.cam_url)
        lay_1.addStretch(1)
        

        lay_2 = QHBoxLayout()
        # lay_2.addWidget(KLabel("민감도 설정"))
        lay_2.addWidget(QLabel("문 열림"))
        lay_2.addWidget(self.cam_value_open)
        lay_2.addWidget(QLabel("문 닫힘"))
        lay_2.addWidget(self.cam_value_close)
        lay_2.addWidget(QLabel("휠체어"))
        lay_2.addWidget(self.cam_value_wheelchair)
        lay_2.addWidget(QLabel("유모차"))
        lay_2.addWidget(self.cam_value_stroller)
        lay_2.addWidget(QLabel("실버카"))
        lay_2.addWidget(self.cam_value_silvercar)
        lay_2.addWidget(QLabel("스쿠터"))
        lay_2.addWidget(self.cam_value_scuter)
        lay_2.addStretch(1)

        lay_3 = QHBoxLayout()
        # lay_3.addWidget(KLabel("관심영역"))
        lay_3.addWidget(QLabel("사용"))
        lay_3.addWidget(self.cam_poi_use)
        # lay_3.addWidget(QLabel("   "), 1)
        lay_3.addWidget(QLabel("   시작점 x:"))
        lay_3.addWidget(self.cam_poi_x)
        lay_3.addWidget(QLabel("y:"))
        lay_3.addWidget(self.cam_poi_y)
        lay_3.addWidget(QLabel("   끝점 x"))
        lay_3.addWidget(self.cam_poi_w)
        lay_3.addWidget(QLabel("y:"))
        lay_3.addWidget(self.cam_poi_h)
        lay_3.addStretch(1)
        lay_3.addWidget(self.btn_cam_set)  ##카메라 관심영역 설정버튼 비활성화

        vbox = QVBoxLayout()
        vbox.addLayout(lay_1)
        vbox.addLayout(lay_2)
        vbox.addLayout(lay_3)

        ##
        lay = QHBoxLayout()
        # lay.addWidget(KLabel(self.title))
        lay.addLayout(vbox)
        
        self.setLayout(lay)


class UI_config(QDialog):

    def __init__(self, config_path):
        super().__init__()
        
        self.config_path = config_path
        
        self.init_ui()
        self.init_signal()
        self.clicked_read()
        
        # self.show()
        # self.auto_process()

    # def auto_process(self):
        
        # if os.path.exists(Config_path):
        #     print(f'path_config : {Config_path}')
            # self.clicked_read()
        

    def init_ui(self):
        # self.comm_conf = Common_conf_ui("설정 파일")

        self.up_cam1 = ELCam_conf_ui("cam1")
        self.up_cam2 = ELCam_conf_ui("cam2")
        self.up_io = IO_conf_ui("IO 제어기")

        self.dn_cam1 = ELCam_conf_ui("cam1")
        self.dn_cam2 = ELCam_conf_ui("cam2")
        self.dn_io = IO_conf_ui("IO 제어기")

        ##버튼
        # self.btn_read = QPushButton("파일 불러오기")
        self.btn_save = QPushButton("저장")
        self.btn_cancel = QPushButton("취소")

        btn_widget = QWidget()
        btn_lay = QHBoxLayout()
        # btn_lay.addWidget(self.btn_read)
        btn_lay.addWidget(self.btn_save)
        btn_lay.addWidget(self.btn_cancel)
        btn_widget.setLayout(btn_lay)

        ## 공통사항 그룹박스
        # comm_grb = QGroupBox("공통사항")
        # comm_lay = QVBoxLayout()
        # comm_lay.addWidget(self.comm_conf)
        # comm_grb.setLayout(comm_lay)

        ##
        up_grb = QGroupBox("상부 카메라")
        up_lay = QVBoxLayout()
        up_lay.addWidget(self.up_cam1)
        up_lay.addWidget(self.up_cam2)
        up_lay.addWidget(self.up_io)
        up_grb.setLayout(up_lay)

        dn_grb = QGroupBox("하부 카메라")
        dn_lay = QVBoxLayout()
        dn_lay.addWidget(self.dn_cam1)
        dn_lay.addWidget(self.dn_cam2)
        dn_lay.addWidget(self.dn_io)
        dn_grb.setLayout(dn_lay)
        
        
        ### 종료 판넬
        self.lbl_info = QLabel(f"10초 후 자동으로 실행됨...")
        self.lbl_info.setStyleSheet(" background-color: blue; color : white")
        self.lbl_info.setAlignment(Qt.AlignCenter)

        ##
        vbox = QVBoxLayout()
        # vbox.addWidget(comm_grb)
        vbox.addWidget(up_grb)
        vbox.addWidget(dn_grb)
        # vbox.addWidget(self.lbl_info)
        vbox.addWidget(btn_widget)
        
        # self.up_cam1.setDisabled(True)
        # self.up_cam2.setDisabled(True)
        # self.up_io.setDisabled(True)
        # self.dn_cam1.setDisabled(True)
        # self.dn_cam2.setDisabled(True)
        # self.dn_io.setDisabled(True)

        self.setLayout(vbox)
        self.resize(1000,500)


    def init_signal(self):

        # self.btn_read.clicked.connect(self.clicked_read)
        self.btn_save.clicked.connect(self.clicked_save)
        self.btn_cancel.clicked.connect(self.clicked_cancel)

        # self.up_cam1.signal_clicked_btn_cam_set.connect(self.clicked_btn_view_up_cam_1)
        # self.up_cam2.signal_clicked_btn_cam_set.connect(self.clicked_btn_view_up_cam_2)
        # self.dn_cam1.signal_clicked_btn_cam_set.connect(self.clicked_btn_view_dn_cam_1)
        # self.dn_cam2.signal_clicked_btn_cam_set.connect(self.clicked_btn_view_dn_cam_2)

        # ## io
        # self.up_io.btn_io_test.clicked.connect(self.clicked_up_io_btn_test)
        # self.dn_io.btn_io_test.clicked.connect(self.clicked_dn_io_btn_test)

    def clicked_up_io_btn_test(self):
            data = self.up_io.get_data()
            # print(data)
            io = View_io_test(data['value_io_ip'], 502)
            io.showModal()
            

    def clicked_dn_io_btn_test(self):
            data = self.dn_io.get_data()
            io = View_io_test(data['value_io_ip'], 502)
            io.showModal()
            

    def showModal(self):
        return super().exec_()
 


    ## 입력 시험
    def clicked_read(self):
        data = read_config(self.config_path)
        # print(data)
        self.disp_data(data)
        pass

    def clicked_save(self):
        data = self.read_ui_make_data()
        print(data)
        write_config(self.config_path, data)
        pass
        self.accept()

    def clicked_cancel(self):
        self.reject()

    ## 현재 UI에 설정된 값을 읽어온다
    def read_ui_make_data(self):
        pass
        # comm_data = {}
        up_data = {}
        dn_data = {}
        data ={}

        # ## comm 데이터 가져오기
        # comm_data = self.comm_conf.get_data()

        cam1 = self.up_cam1.get_data()
        cam2 = self.up_cam2.get_data()
        io = self.up_io.get_data()

        up_data['cam1'] = cam1
        up_data['cam2'] = cam2
        up_data['io'] = io

        ##
        cam1 = self.dn_cam1.get_data()
        cam2 = self.dn_cam2.get_data()
        io = self.dn_io.get_data()

        dn_data['cam1'] = cam1
        dn_data['cam2'] = cam2
        dn_data['io'] = io

        ##
        # data['comm'] = comm_data
        data['up'] = up_data
        data['dn'] = dn_data

        return data

    def disp_data(self, data): 
        # try:
        #     self.comm_conf.set_data(data['comm'])
        # except :
        #     pass

        try:
            self.up_cam1.set_data(data['up']['cam1'])
            self.up_cam2.set_data(data['up']['cam2'])
            self.up_io.set_data(data['up']['io'])

            self.dn_cam1.set_data(data['dn']['cam1'])
            self.dn_cam2.set_data(data['dn']['cam2'])
            self.dn_io.set_data(data['dn']['io'])
        except :
            pass

    def cam_get_test(self):
        print(f'clicked read')

        data = self.up_cam1.get_data()
        print(f'type : {type(data)}')
        print(data)

        data = self.up_io.get_data()
        print(f'type : {type(data)}')
        print(data)

    def cam_set_test(self):
        print(f'clicked save')
        cam_dict = {
				"url": "rtsp:............111",
				"cam_use": "true",
				"value_open" : "",
				"value_close" : "",
				"value_wheelchair" : "",
				"value_stroller" : "",
				"value_silvercar" : "",
				"value_scuter" : "",
				"poi_use" : "false",
				"value_x" : "",
				"value_y" : "",
				"value_w" : "",
				"value_h" : "",
			}
        self.up_cam1.set_data(cam_dict)

        io_dict =  {
            "value_io_ip": "000.000.000.000",
            "value_io_relay_port": "1",
            "value_io_delay_time": "10",
            }
        self.up_io.set_data(io_dict)


class UI_conf_cam_panel(QWidget):

    def __init__(self):
        super().__init__()
        self.init_ui()
        # self.init_signal()


    def init_ui(self):
        self.up_cam1 = ELCam_conf_ui("cam1")
        self.up_cam2 = ELCam_conf_ui("cam2")
        self.up_io = IO_conf_ui("IO 제어기")

        self.dn_cam1 = ELCam_conf_ui("cam1")
        self.dn_cam2 = ELCam_conf_ui("cam2")
        self.dn_io = IO_conf_ui("IO 제어기")

        ##버튼
        self.btn_read = QPushButton("read")
        self.btn_save = QPushButton("save")

        btn_widget = QWidget()
        btn_lay = QHBoxLayout()
        btn_lay.addWidget(self.btn_read)
        btn_lay.addWidget(self.btn_save)
        btn_widget.setLayout(btn_lay)

        ##
        up_grb = QGroupBox("상부 카메라")
        up_lay = QVBoxLayout()
        up_lay.addWidget(self.up_cam1)
        up_lay.addWidget(self.up_cam2)
        up_lay.addWidget(self.up_io)
        up_grb.setLayout(up_lay)

        dn_grb = QGroupBox("하부 카메라")
        dn_lay = QVBoxLayout()
        dn_lay.addWidget(self.dn_cam1)
        dn_lay.addWidget(self.dn_cam2)
        dn_lay.addWidget(self.dn_io)
        dn_grb.setLayout(dn_lay)

        ##
        vbox = QVBoxLayout()
        vbox.addWidget(up_grb)
        vbox.addWidget(dn_grb)
        vbox.addWidget(btn_widget)

        self.setLayout(vbox)
        self.resize(1000,500)


    def init_signal(self):

        self.btn_read.clicked.connect(self.clicked_read)
        self.btn_save.clicked.connect(self.clicked_save)

        # self.up_cam1.signal_clicked_btn_cam_set.connect(self.clicked_btn_view_up_cam_1)
        # self.up_cam2.signal_clicked_btn_cam_set.connect(self.clicked_btn_view_up_cam_2)
        # self.dn_cam1.signal_clicked_btn_cam_set.connect(self.clicked_btn_view_dn_cam_1)
        # self.dn_cam2.signal_clicked_btn_cam_set.connect(self.clicked_btn_view_dn_cam_2)

        # ## io
        # self.up_io.btn_io_test.clicked.connect(self.clicked_up_io_btn_test)
        # self.dn_io.btn_io_test.clicked.connect(self.clicked_dn_io_btn_test)

    def clicked_up_io_btn_test(self):
            data = self.up_io.get_data()
            # print(data)
            io = View_io_test(data['value_io_ip'], 502)
            io.showModal()
            

    def clicked_dn_io_btn_test(self):
            data = self.dn_io.get_data()
            io = View_io_test(data['value_io_ip'], 502)
            io.showModal()
            

 


    ## 입력 시험
    def clicked_read(self):
        data = read_config(path_config)
        self.disp_data(data)
        pass

    def clicked_save(self):
        data = self.read_ui_make_data()
        print(data)
        write_config(path_config, data)
        pass

    def read_ui_make_data(self):
        pass
        up_data = {}
        dn_data = {}
        data ={}

        cam1 = self.up_cam1.get_data()
        cam2 = self.up_cam2.get_data()
        io = self.up_io.get_data()

        up_data['cam1'] = cam1
        up_data['cam2'] = cam2
        up_data['io'] = io

        ##
        cam1 = self.dn_cam1.get_data()
        cam2 = self.dn_cam2.get_data()
        io = self.dn_io.get_data()

        dn_data['cam1'] = cam1
        dn_data['cam2'] = cam2
        dn_data['io'] = io

        ##
        data['up'] = up_data
        data['dn'] = dn_data

        return data

    def disp_data(self, data):  
        self.up_cam1.set_data(data['up']['cam1'])
        self.up_cam2.set_data(data['up']['cam2'])
        self.up_io.set_data(data['up']['io'])

        self.dn_cam1.set_data(data['dn']['cam1'])
        self.dn_cam2.set_data(data['dn']['cam2'])
        self.dn_io.set_data(data['dn']['io'])

    def cam_get_test(self):
        print(f'clicked read')

        data = self.up_cam1.get_data()
        print(f'type : {type(data)}')
        print(data)

        data = self.up_io.get_data()
        print(f'type : {type(data)}')
        print(data)

    def cam_set_test(self):
        print(f'clicked save')
        cam_dict = {
				"url": "rtsp:............111",
				"cam_use": "true",
				"value_open" : "",
				"value_close" : "",
				"value_wheelchair" : "",
				"value_stroller" : "",
				"value_silvercar" : "",
				"value_scuter" : "",
				"poi_use" : "false",
				"value_x" : "",
				"value_y" : "",
				"value_w" : "",
				"value_h" : "",
			}
        self.up_cam1.set_data(cam_dict)

        io_dict =  {
            "value_io_ip": "000.000.000.000",
            "value_io_relay_port": "1",
            "value_io_delay_time": "10",
            }
        self.up_io.set_data(io_dict)
    


if __name__=="__main__":
    app = QApplication(sys.argv)
    ex = UI_config()
    ex.show()
    sys.exit(app.exec_())
    