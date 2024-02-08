import cv2
import json
import sys
import time
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtTest import *
import numpy as np
from PIL import ImageFont, ImageDraw, Image

import webbrowser
import queue
import asyncio

from modelEL import *
from cont import *
from common import *
from ui_config import *
from io_ui2 import *

class VideoCap(QThread):
    """_summary_: 카메라를 읽어온다.

    Args:
        QThread (vi_url, vi_size, tag): _description_ 비디오 초기화
        
        interface
            slot : 
    """
    signal_retrieve = pyqtSignal(bool, np.ndarray, int)
    
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.cap = None
        self._run_flag = False
        self._get_flag = False
        

    ### 외부에서 호출 인터페이스 start       
            
    @pyqtSlot()
    def cam_run(self):
        self._run_flag = True
        self.start()
        
    @pyqtSlot()
    def cam_stop(self):
        self._run_flag = False
        
    @pyqtSlot()
    def cam_get_img(self):
        # print(f"cam_get_img...")
        self._get_flag = True
        
    @pyqtSlot()
    def cam_open(self):
        if not self.cap is None:
            self.cap.release()
            
        self.cap = cv2.VideoCapture(self.parent.vi_url)
        if self.cap.isOpened():
            # print("Camera open OK!") 
            
            return True
        else:
            print("Camera open failed!") 
            return False
        
    
    ### 외부에서 호출 인터페이스 end  

    # read frames as soon as they are available, keeping only most recent one
    def run(self):
        print(f"{self.parent.vi_tag}  VideoCap run {self.parent.vi_url}")
        while self._run_flag:
            # self.mutex.lock()
            ret = self.cap.grab()
            if not ret:
                self.signal_retrieve.emit(ret, Img_default, self.parent.vi_tag)
                print(f'{self.parent.vi_tag} cam read error...reconnecting...')
                self.cap.release()
                self.cap = cv2.VideoCapture(self.parent.vi_url)
                # QTest.qWait(100)
                continue
                # break
            
            if self._get_flag:   
                # print(f'videocap  self._get_flag : {self.parent.vi_tag}')
                r,frame = self.cap.retrieve()  ### 오류가 발생하면 frame가 None 이다
                if r :
                    # print(f'self._get_flag {r}')
                    frame = cv2.resize(frame, self.parent.vi_size, interpolation=cv2.INTER_AREA)
                    self.signal_retrieve.emit(r, frame, self.parent.vi_tag)
                else:
                    # print(f'self._get_flag {r}')
                    self.signal_retrieve.emit(r, Img_default, self.parent.vi_tag)
                self._get_flag = False
                
            
        ### thread 종료    
        self.cap.release()
        print(f'VideoCap {self.parent.vi_tag} thread quit')
        
        self.quit()


class ImgLabel(QLabel):
    # ResizeSignal = pyqtSignal(int)
    signal_rect = pyqtSignal(int,bool, QRect)
    log_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()

        self._flag_show_rect = False
        self._flag_show_text = False
        self._flag_draw_rect = False

        ## 여러개의 문자열 표출
        self.list_text = [ ]  ## (10,10,"test"), (100,100,"test") // x, y, "text"
        self.tag = None ## signal_rect 를 어느 이미지에서 보냈는지 확인하기 위한 tag

        self.begin = QPoint()
        self.end = QPoint()

        # self.begin_rect = QPoint()
        # self.end_rect = QPoint()

        # self.disconnect_img = self.load_disconnect_img()

        self.setStyleSheet("color: white; border-style: solid; border-width: 2px; border-color: #54A0FF; background-color: rgb(0,0,0)")
        # self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        # self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # width, height = 300,300
        # self.setGeometry(0, 0, width, height)
        # self.setFrameShape(QFrame.Box)
        # self.setLineWidth(3)
        self.pix = QPixmap()
        self.installEventFilter(self)

        # self.load_default_img()

        self.init_contextmenu()
        
    def set_tag(self, tag):
        self.tag = tag
        
    ### interface start
    @pyqtSlot(np.ndarray)
    def changePixmap(self, cv_img):
        # print(f'changePixmap')
        self.pix = self.convert_cv_qt(cv_img)
        self.repaint()

    @pyqtSlot(QRect)
    def receive_rect(self, rect):
        self.begin = rect.topLeft()
        self.end = rect.bottomRight()
        # self.begin = rect.x(), rect.y()
        # self.end = rect.right(), rect.bottom()
        # print(f'receive begin: {rect.x()}, {rect.y()}  end: {rect.right()}, {rect.bottom()}')
        # self.send_log(f'receive begin: {rect.topLeft()}  end: {rect.bottomRight()}')
        # self.update()

    @pyqtSlot(bool)
    def show_ract(self, state):
        self._flag_show_rect = state

    @pyqtSlot(bool)
    def draw_ract(self, state):
        self._flag_draw_rect = state 
        
    ### interface end

    ## popup 메뉴 
    def init_contextmenu(self):
        self.setContextMenuPolicy(Qt.ActionsContextMenu)

        act_draw = QAction("poi 설정" , self)
        act_save = QAction("poi 저장" , self)
        act_no_use = QAction("poi 사용안함" , self)

        # action1.setData(self.list_img[i])
        # action2.setData(self.list_img[i])

        act_draw.triggered.connect(self.click_act_draw)
        act_save.triggered.connect(self.click_act_save)
        act_no_use.triggered.connect(self.click_act_no_use)

        self.addAction(act_draw)
        self.addAction(act_save)
        self.addAction(act_no_use)
        
    def click_act_draw(self):
        self.show_ract(True)
        self.draw_ract(True)

    def click_act_save(self):
        # print(f'rect   begin: {self.begin.x()}, {self.begin.y()}  end: {self.end.x()}, {self.end.y()}')
        self.show_ract(False)
        self.draw_ract(False)
        self.signal_rect.emit(self.tag, bool(True), QRect(self.begin, self.end))


    def click_act_no_use(self):
        self.show_ract(False)
        self.draw_ract(False)

        self.begin = QPoint(0, 0)
        self.end = QPoint(400-1, 300-1)
        self.signal_rect.emit(self.tag, bool(False), QRect(self.begin, self.end))

    # ## popup 메뉴 end



    # def send_log(self, msg):
    #     self.log_signal.emit(msg)

    # def load_default_img(self):
    #     self.pix = self.convert_cv_qt(Default_img)

    #     self.update()
        
    def paintEvent(self, event):
        if not self.pix.isNull():
            
            # size = self.size()  ## 화면 크기에 맞게
            size = QSize(400,300)  ## 지정된 크기로 
            # print(f"size: {size}")

            painter = QPainter(self)

            point = QPoint(0, 0)
            scaledPix = self.pix.scaled(size, Qt.KeepAspectRatio, transformMode = Qt.FastTransformation) # 비율 고정
            # scaledPix = self.pix.scaled(size, Qt.IgnoreAspectRatio, transformMode=Qt.FastTransformation) # 창 크기에 따라
            painter.drawPixmap(point, scaledPix)

            if self._flag_show_rect:
                br = QBrush(QColor(100, 10, 10, 40))
                painter.setBrush(br)
                painter.drawRect(QRect(self.begin, self.end))
                # print(f'begin: {self.begin.x()}, {self.begin.y()}  end: {self.end.x()}, {self.end.y()}')
                
            # if self._flag_show_text:
            #     painter.setFont(QFont('Times New Roman', 11))
            #     # painter.drawText(10, 290, self.text_str)

            #     ## 여러개의 문자 표시
            #     # print(f'{self.list_text}')
            #     for i, j in enumerate(self.list_text):
            #         painter.drawText(j[0], j[1], j[2])

        else:
            print("pix null")

    ## 마우스 이벤트
    def mousePressEvent(self, event):
        # pass
        if event.button() == Qt.LeftButton:
            # pass
            if self._flag_draw_rect:
                self.begin = event.pos()
                self.end = event.pos()
                self.update()
                # print(f'press {self.begin}, {self.end}')
        
    def mouseMoveEvent(self, event):
        if self._flag_draw_rect:
            self.applye_event(event)
            self.update()
            # print(f'move {event.x()}, {event.y()}')

    def mouseReleaseEvent(self,event):
        if event.button() == Qt.LeftButton:
            if self._flag_draw_rect:
                self.applye_event(event)
                # print(f'Release {event.x()}, {event.y()}')

    def applye_event(self, event):
        self.end = event.pos()

      

    def convert_cv_qt(self, cv_img):
        """Convert from an opencv image to QPixmap"""
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        # p = convert_to_Qt_format.scaled(self.disply_width, self.display_height, Qt.KeepAspectRatio)
        return QPixmap.fromImage(convert_to_Qt_format)

    def draw_text(self, frame, text, x1, y1):
        cv2.putText(frame, text, (x1, y1), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0,255,0), 2)



class Loding_win(QDialog):
    """ 체크 윈도우
    """    
    
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("프로그램 점검")
        
        self.parent = parent
        self.init_ui()
        
        self.count = 10
        self.timer = QTimer()
        self.timer.setInterval(1000)
        # self.timer_get.timeout.connect(self.cam_get_img)
        self.timer.timeout.connect(self.timer_work)
        
        
    def init_ui(self):
        lbl_data = QLabel("환경설정파일 불러오기 ")
        lbl_model = QLabel("영상분석모델 불러오기 ")
        lbl_io = QLabel("IO제어기 연결 확인 ")
        lbl_up_cam_1 = QLabel("상부 카메라 1 ")
        lbl_up_cam_2 = QLabel("상부 카메라 2 ")
        lbl_dn_cam_1 = QLabel("하부 카메라 1 ")
        lbl_dn_cam_2 = QLabel("하부 카메라 2 ")
        
        lbl_data.setFixedWidth(300)
        lbl_model.setFixedWidth(300)
        lbl_io.setFixedWidth(300)
        
        self.lbl_ok_data = QLabel("--------")
        self.lbl_ok_model = QLabel("--------")
        self.lbl_ok_io = QLabel("--------")
        self.lbl_ok_up_cam_1 = QLabel("--------")
        self.lbl_ok_up_cam_2 = QLabel("--------")
        self.lbl_ok_dn_cam_1 = QLabel("--------")
        self.lbl_ok_dn_cam_2 = QLabel("--------")
        self.list_lbl_cam_ok = [self.lbl_ok_up_cam_1, self.lbl_ok_up_cam_2, self.lbl_ok_dn_cam_1, self.lbl_ok_dn_cam_2]
        
        self.lbl_ok_data.setStyleSheet("color:blue")
        self.lbl_ok_model.setStyleSheet("color:blue")
        self.lbl_ok_io.setStyleSheet("color:blue")
        self.lbl_ok_up_cam_1.setStyleSheet("color:blue")
        self.lbl_ok_up_cam_2.setStyleSheet("color:blue")
        self.lbl_ok_dn_cam_1.setStyleSheet("color:blue")
        self.lbl_ok_dn_cam_2.setStyleSheet("color:blue")
        
        
        self.lbl_info = QLabel("")
        self.lbl_info.setAlignment(Qt.AlignCenter)
        self.lbl_info.setStyleSheet("color:green")
        
        self.btn_close = QPushButton("닫기")
        self.btn_close.clicked.connect(self.clicked_close)
        self.btn_close.setDisabled(True)
        self.btn_run = QPushButton("프로그램 시작")
        self.btn_run.clicked.connect(self.clicked_run)
        self.btn_run.setDisabled(True)
        
        lay_data = QHBoxLayout()
        lay_data.addWidget(lbl_data)
        lay_data.addStretch(1)
        lay_data.addWidget(self.lbl_ok_data)
        
        lay_model = QHBoxLayout()
        lay_model.addWidget(lbl_model)
        lay_model.addStretch(1)
        lay_model.addWidget(self.lbl_ok_model)
        
        lay_io = QHBoxLayout()
        lay_io.addWidget(lbl_io)
        lay_io.addStretch(1)
        lay_io.addWidget(self.lbl_ok_io)
        
        lay_up_1 = QHBoxLayout()
        lay_up_1.addWidget(lbl_up_cam_1)
        lay_up_1.addStretch(1)
        lay_up_1.addWidget(self.lbl_ok_up_cam_1)
        
        lay_up_2 = QHBoxLayout()
        lay_up_2.addWidget(lbl_up_cam_2)
        lay_up_2.addStretch(1)
        lay_up_2.addWidget(self.lbl_ok_up_cam_2)
        
        lay_dn_1 = QHBoxLayout()
        lay_dn_1.addWidget(lbl_dn_cam_1)
        lay_dn_1.addStretch(1)
        lay_dn_1.addWidget(self.lbl_ok_dn_cam_1)
        
        lay_dn_2 = QHBoxLayout()
        lay_dn_2.addWidget(lbl_dn_cam_2)
        lay_dn_2.addStretch(1)
        lay_dn_2.addWidget(self.lbl_ok_dn_cam_2)
        
        
        lay_btn = QHBoxLayout()
        lay_btn.addWidget(self.btn_close)
        lay_btn.addWidget(self.btn_run)
        
        lay_main = QVBoxLayout()
        lay_main.addLayout(lay_data)
        lay_main.addLayout(lay_model)
        lay_main.addLayout(lay_io)
        lay_main.addLayout(lay_up_1)
        lay_main.addLayout(lay_up_2)
        lay_main.addLayout(lay_dn_1)
        lay_main.addLayout(lay_dn_2)
        lay_main.addStretch(1)
        lay_main.addWidget(self.lbl_info)
        lay_main.addLayout(lay_btn)
        
        self.setLayout(lay_main)
        
    def timer_work(self):
        self.lbl_info.setText(f'{self.count} 초 후 자동실행됩니다.')
        
        self.count = self.count -1
        if self.count == 0:
            self.clicked_run()
        
    
            
    @pyqtSlot()
    def receive_timer_on(self):
        self.btn_close.setEnabled(True)
        self.btn_run.setEnabled(True)
        """_summary_ 00초후 프로그램이 자동실행 됩니다. 표출 타이머 실행
        """
        self.timer.start()
            
        
    def clicked_close(self):
        self.timer.stop()
        self.reject()
        
        
    def clicked_run(self):
        self.timer.stop()
        self.accept()
        
        
class Main_win4(QMainWindow):
    
    signal_cv_img_0 = pyqtSignal(np.ndarray)
    signal_cv_img_1 = pyqtSignal(np.ndarray)
    signal_cv_img_2 = pyqtSignal(np.ndarray)
    signal_cv_img_3 = pyqtSignal(np.ndarray)
    
    signal_detect_0 = pyqtSignal(str, dict)
    signal_detect_1 = pyqtSignal(str, dict)
    signal_detect_2 = pyqtSignal(str, dict)
    signal_detect_3 = pyqtSignal(str, dict)
    
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("교통약자 인식 엘리베이터 자동호출 시스템")
        
        ###초기화
        self.list_cam = [None, None, None, None]
        self.list_img = [None, None, None, None]
        # self.stat_cam_list = [QLabel(" 상 cam1 "), QLabel(" 상 cam1 "), QLabel(" 상 cam1 "), QLabel(" 상 cam1 ")]  ## 카메라 연결 상태를 표시하려고 하였으나, 여의치 않음
        self.list_cont = [None, None]
        self.list_img_signal = [self.signal_cv_img_0, self.signal_cv_img_1, self.signal_cv_img_2, self.signal_cv_img_3]
        self.list_detect_signal = [self.signal_detect_0, self.signal_detect_1, self.signal_detect_2, self.signal_detect_3]
        
        self.list_url = [None, None, None, None]
        self.list_cam_use = [None, None, None, None]
        self.list_name = ["cam1", "cam2", "cam1", "cam2"]
        self.list_detect = [None, None, None, None]
        self.list_cont = [None, None]
        self.list_poi = [None, None, None, None]
        self.list_io = [None, None]
        
        self.io_thread = None
        
        ### 상태 체크하여 결과값
        self.ok_data = False
        self.ok_model = False
        self.ok_io = False
        self.ok_cam = [False, False, False, False]
            
        self.vi_size = 400,300
        self.img_size_x = 400
        self.img_size_y = 300
        self.repeat_time = 50
        self.repeat_tag = 0
        
        # for id in range(4):
        #     cam = VideoCap()
        #     self.list_cam[id] = cam
            
        # for id in range(4):
        #     lbl = ImgLabel()
        #     lbl.setFixedSize(self.img_size_x, self.img_size_y)
        #     lbl.changePixmap(np.full(shape=(self.img_size_y, self.img_size_x, 3), fill_value=10, dtype=np.uint8))
        #     self.list_img[id] = lbl
            
        # ##cont 초기화
        # for ii in range(2):
        #     cont = Cont()
        #     cont.setFixedSize(300, 300)
        #     self.list_cont[ii] = cont
        
        self.init_timer()
        self.init_ui()
        
        self.show()
        # self.init_signal()
        
        
        QTimer.singleShot(10, self.clicked_play)
        
        
        
    
        
        
    def show_loding_win(self):
        self.loding_dlg = Loding_win(self)
        if self.loding_dlg.exec_():
            print("show_loding_win   acept...")
            self.io_thread._run_flag = True
            self.io_thread.start()
            self.timer_get.start()
            self.action_play.setEnabled(False)
            self.action_stop.setEnabled(True)
            self.action_set.setEnabled(False)
        else:
            print("show_loding_win   cancel...")
            self.clicked_stop()
            
    def show_config_win(self):
        # self.clicked_stop()
        
        ## 창 띄우기
        dlg = UI_config()
        if dlg.exec_():
            print("acept...")
            # QTimer.singleShot(10, self.show_loding_win)
            # QTimer.singleShot(200, self.check_all)
        else:
            print("cancel...")
         
        
    def set_data(self):
        self.data = read_config(Config_path)
        if self.data is None:
            # print(f"환결설정 파일이 없음.")
            return False
            pass
        else:
            print(self.data)
            # self.stat_conf.setText(Config_path)
        
            self.list_url = [self.data['up']['cam1']['cam']['url'], self.data['up']['cam2']['cam']['url'], self.data['dn']['cam1']['cam']['url'], self.data['dn']['cam2']['cam']['url']]
            self.list_cam_use = [self.data['up']['cam1']['cam']['use'], self.data['up']['cam2']['cam']['use'], self.data['dn']['cam1']['cam']['use'], self.data['dn']['cam2']['cam']['use']]
            
            self.list_name = ["cam1", "cam2", "cam1", "cam2"]
            self.list_detect = [self.data['up']['cam1'].get('detect'), self.data['up']['cam2'].get('detect'), self.data['dn']['cam1'].get('detect'), self.data['dn']['cam2'].get('detect')]
            # self.list_cont = [self.ui_autoel.up_floor.edit_cont, self.ui_autoel.up_floor.edit_cont, self.ui_autoel.dn_floor.edit_cont, self.ui_autoel.dn_floor.edit_cont]
            self.list_poi = [self.data['up']['cam1'].get('poi'), self.data['up']['cam2'].get('poi'), self.data['dn']['cam1'].get('poi'), self.data['dn']['cam2'].get('poi')]
            self.list_io = [self.data['up'].get('io'), self.data['up'].get('io'), self.data['dn'].get('io'), self.data['dn'].get('io')]
            # return True
        
            for id in range(4):
                self.list_cam[id].set_data(self.list_url[id], self.vi_size, id )
                
            self.list_cont[0].init_io(self.data['up'].get('io'))
            self.list_cont[1].init_io(self.data['dn'].get('io'))
            return True
        
    def check_all(self):
        
        if not self.check_data():
            self.loding_dlg.lbl_ok_model.setText('Failed')
            self.loding_dlg.lbl_ok_io.setText('Failed')
            self.loding_dlg.list_lbl_cam_ok[0].setText("Failed")
            self.loding_dlg.list_lbl_cam_ok[1].setText("Failed")
            self.loding_dlg.list_lbl_cam_ok[2].setText("Failed")
            self.loding_dlg.list_lbl_cam_ok[3].setText("Failed")
            # self.check_io()
            # # self.connect_signal()
            # self.check_cam()
            # QTimer.singleShot(10, self.loding_dlg.receive_timer_on)
            self.loding_dlg.btn_close.setEnabled(True)
        else:
            self.check_model()
            self.check_io()
            self.check_cam()
            QTimer.singleShot(10, self.loding_dlg.receive_timer_on)
            
        
    def check_data(self):
        ### config.json 파일 존재여부 확인
        if not self.set_data():
            print(f'check_data : 환결설정 파일이 없음')
            self.loding_dlg.lbl_ok_data.setStyleSheet("color:red")
            self.loding_dlg.lbl_ok_data.setText("./data/config.json 파일 없음")
            QTest.qWait(50)
            return False
        else:
            self.loding_dlg.lbl_ok_data.setStyleSheet("color:blue")
            self.loding_dlg.lbl_ok_data.setText("Succeed")
            QTest.qWait(50)
            print(f'check_data : 환결설정 파일이 정상')
            return True
            
    def check_model(self):
        ### model 체크
        if not self.init_model():
            print(f'check_data : model loding failed')
            self.loding_dlg.lbl_ok_model.setStyleSheet("color:red")
            self.loding_dlg.lbl_ok_model.setText('Failed')
            QTest.qWait(50)
            self.ok_model = False
            return False
        else:
            self.loding_dlg.lbl_ok_model.setStyleSheet("color:blue")
            self.loding_dlg.lbl_ok_model.setText('Succeed')
            QTest.qWait(50)
            print(f'check_data : model loding OK')
            self.ok_model = True
            return True
            
    def check_io(self):
        ### IO 체크
        c = ModbusClient(host=self.data['up']['io']['value_io_ip'], port=502, auto_open=True)
        if not c.open():
            self.loding_dlg.lbl_ok_io.setStyleSheet("color:red")
            self.loding_dlg.lbl_ok_io.setText('Failed')
            QTest.qWait(50)
            print(f'check_data : IO 통신체크 failed')
            return False
        else:
            self.loding_dlg.lbl_ok_io.setStyleSheet("color:blue")
            self.loding_dlg.lbl_ok_io.setText('Succeed')
            ### io_thread start
            self.io_thread.set_data(self.data['up']['io']['value_io_ip'], 502)
            QTest.qWait(50)
            print(f'check_data : IO 통신체크 OK')
            return True
            
            
    def check_cam(self):
        ### 카메라 체크
        for id in range(4):
            if not self.list_cam_use[id]:
                img = img_draw_msg_center(Img_default, "사용 안함 ")
                self.list_img_signal[id].emit(img)
                self.loding_dlg.list_lbl_cam_ok[id].setStyleSheet("color:black")
                self.loding_dlg.list_lbl_cam_ok[id].setText("사용안함")
            else:
                re = self.list_cam[id].cam_open()
                if re :
                    self.ok_cam[id] = True
                    self.loding_dlg.list_lbl_cam_ok[id].setStyleSheet("color:blue")
                    self.loding_dlg.list_lbl_cam_ok[id].setText("Succeed")
                    img = img_draw_msg_center(Img_default, "카메라 연결 성공 ")
                    self.list_img_signal[id].emit(img)
                    self.list_cam[id].cam.cam_run()
                    
                    
                else:
                    self.ok_cam[id] = False
                    self.loding_dlg.list_lbl_cam_ok[id].setStyleSheet("color:red")
                    img = img_draw_msg_center(Img_default, "카메라 연결 실패 " )
                    self.list_img_signal[id].emit(img)
                    self.loding_dlg.list_lbl_cam_ok[id].setText("Failed")
                    
            QTest.qWait(50)
                    
        
                    
    # def check_data(self):
    #     if not self.set_data():
    #         print(f'check_data : 환결설정 파일이 없음')
    #         # QMessageBox.critical(self,'오류','환결설정 파일(./data/config.json)이 없음')
    #         self.ok_data = False
    #         self.loding_dlg.receive_ok_data(self.ok_data)
    #         QTest.qWait(50)
            
    #     else:
    #         self.ok_data = True
    #         self.loding_dlg.receive_ok_data(self.ok_data)
    #         QTest.qWait(50)
    #         print(f'check_data : 환결설정 파일이 정상')
            
    #         ### 파일이 존재하면 model 체크
    #         if not self.init_model():
    #             print(f'check_data : model loding failed')
    #             self.ok_model = False
    #             self.loding_dlg.receive_ok_model(self.ok_model)
    #             QTest.qWait(50)
    #         else:
    #             self.ok_model = True
    #             self.loding_dlg.receive_ok_model(self.ok_model)
    #             QTest.qWait(50)
    #             print(f'check_data : model loding OK')
    #             ### IO 체크
    #             c = ModbusClient(host=self.data['up']['io']['value_io_ip'], port=502, auto_open=True)
    #             if not c.open():
    #                 self.ok_io = False
    #                 self.loding_dlg.receive_ok_io(self.ok_io)
    #                 QTest.qWait(50)
    #                 print(f'check_data : IO 통신체크 failed')
    #             else:
    #                 self.ok_io = True
    #                 self.loding_dlg.receive_ok_io(self.ok_io)
    #                 ### io_thread start
    #                 self.init_io_thread()
    #                 QTest.qWait(50)
    #                 print(f'check_data : IO 통신체크 OK')
    #                 ### 카메라는 카메라 고장으로 동작하지 않는 경우도 있으므로, 체크하지 않는다.
                    
    #     QTimer.singleShot(10, self.loding_dlg.receive_timer_on)
                            
            
        
    def ui_panel_cam(self):
        for id in range(4):
            cam = Cam_win()
            self.list_cam[id] = cam
            
        for ii in range(2):
            cont = Cont()
            # cont.setFixedSize(300, 300)
            self.list_cont[ii] = cont
            
        lbl_1 = QLabel("상부")
        lbl_1.setAlignment(Qt.AlignCenter)
        lbl_1.setStyleSheet("color: black;"
                      "border-style: solid;"
                      "border-width: 2px;"
                      "border-radius: 3px")
        lbl_1.setMinimumWidth(70)
        lbl_2 = QLabel("하부")
        lbl_2.setAlignment(Qt.AlignCenter)
        lbl_2.setStyleSheet("color: black;"
                      "border-style: solid;"
                      "border-width: 2px;"
                      "border-radius: 3px")
        lbl_2.setMinimumWidth(70)
            
        self.panel_up = QFrame()
        self.panel_up.setFrameShape(QFrame.Panel | QFrame.Sunken)
        lay_up = QHBoxLayout(self.panel_up)
        lay_up.addWidget(lbl_1)
        lay_up.addWidget(self.list_cam[0])
        lay_up.addWidget(self.list_cam[1])
        lay_up.addWidget(self.list_cont[0])
        self.panel_up.setLayout(lay_up)
        
        
        self.panel_dn = QFrame()
        self.panel_dn.setFrameShape(QFrame.Panel | QFrame.Sunken)
        lay_dn = QHBoxLayout(self.panel_dn)
        lay_dn.addWidget(lbl_2)
        lay_dn.addWidget(self.list_cam[2])
        lay_dn.addWidget(self.list_cam[3])
        lay_dn.addWidget(self.list_cont[1])
        self.panel_dn.setLayout(lay_dn)
        
        self.panel_io = QFrame()
        self.panel_io.setFrameShape(QFrame.Panel | QFrame.Sunken)
        io_ip = QLabel("IP : ")
        io_port = QLabel("Port : ")
        io_up_relay = QLabel("상부 콜 Relay : ")
        io_dn_relay = QLabel("하부 콜 Relay : ")
        self.text_io_ip = QLineEdit("000.000.000.000")
        self.text_io_port = QLineEdit("502")
        self.text_io_up_relay = QLineEdit("0")
        self.text_io_dn_relay = QLineEdit("5")
        lay_io = QHBoxLayout(self.panel_io)
        lay_io.addWidget(io_ip)
        lay_io.addWidget(self.text_io_ip)
        lay_io.addWidget(io_port)
        lay_io.addWidget(self.text_io_port)
        lay_io.addWidget(io_up_relay)
        lay_io.addWidget(self.text_io_up_relay)
        lay_io.addWidget(io_dn_relay)
        lay_io.addWidget(self.text_io_dn_relay)
        self.panel_io.setLayout(lay_io)
        
    def ui_panel_btn(self):
        self.panel_btn = QWidget()
        lay_btn = QHBoxLayout(self.panel_btn)
        self.btn_open = QPushButton("open")
        self.btn_run = QPushButton("run")
        self.btn_get = QPushButton("get")
        self.btn_stop = QPushButton("connect")
        self.btn_test = QPushButton("dis")
        
        # self.btn_open.clicked.connect(self.cam_open)
        # self.btn_run.clicked.connect(self.cam_run)
        self.btn_get.clicked.connect(self.repeat_get_img)
        self.btn_stop.clicked.connect(self.clicked_t2)
        self.btn_test.clicked.connect(self.clicked_test)
        
        
        # lay_btn.addWidget(self.btn_run)
        lay_btn.addWidget(self.btn_stop)
        lay_btn.addWidget(self.btn_get)
        lay_btn.addWidget(self.btn_open)
        lay_btn.addWidget(self.btn_test)
        
    
            
    def init_ui(self):
        self.init_toolbar()
        
        ### IO ui 생성
        self.ui_io = Ui_io()
        self.io_thread = IO_thread()
        self.io_thread.signal_di_relay.connect(self.ui_io.disp_di_relay)
        
        
        self.ui_panel_cam()
        self.ui_panel_btn()
        
        self.connect_signal()
        
        widget_main = QWidget()
        lay_main = QVBoxLayout(widget_main)
        lay_main.addWidget(self.panel_up)
        lay_main.addWidget(self.panel_dn)
        # lay_main.addWidget(self.panel_io)
        # lay_main.addWidget(self.panel_btn)
        lay_main.addWidget(self.ui_io)
        # lay_main.addLayout(lay_btn)
        
        self.setCentralWidget(widget_main)
        
    def init_toolbar(self):
        self.action_exit = QAction(QIcon('./data/exit.png'), 'Exit', self)
        self.action_exit.setShortcut('Ctrl+Q')
        self.action_exit.setStatusTip('Exit application')
        self.action_exit.triggered.connect(qApp.quit)
        self.action_exit.setDisabled(False)
        
        self.action_play = QAction(QIcon('./data/play.png'), 'Play', self)
        self.action_play.setShortcut('Ctrl+P')
        self.action_play.setStatusTip('Exit application')
        self.action_play.triggered.connect(self.clicked_play)
        self.action_play.setDisabled(True)
        
        self.action_stop = QAction(QIcon('./data/stop.png'), 'Stop', self)
        self.action_stop.setShortcut('Ctrl+S')
        self.action_stop.setStatusTip('Exit application')
        self.action_stop.triggered.connect(self.clicked_stop)
        self.action_stop.setDisabled(True)
        
        self.action_set = QAction(QIcon('./data/setting.png'), 'seTting', self)
        self.action_set.setShortcut('Ctrl+T')
        self.action_set.setStatusTip('Exit application')
        self.action_set.triggered.connect(self.clicked_setting)
        self.action_set.setDisabled(True)
        
        
        self.toolbar = self.addToolBar('Exit')
        self.toolbar.addAction(self.action_exit)
        self.toolbar.addAction(self.action_play)
        self.toolbar.addAction(self.action_stop)
        self.toolbar.addAction(self.action_set)
        
    def clicked_test(self):
        self.disconnect_signal()
    
    def clicked_t2(self):
        self.connect_signal()
        
    def clicked_play(self):
        QTimer.singleShot(10, self.show_loding_win)
        QTimer.singleShot(200, self.check_all)
        
        self.action_play.setEnabled(False)
        self.action_stop.setEnabled(True)
        self.action_set.setEnabled(False)
        pass
    
    def clicked_stop(self):
        self.timer_get.stop()
        QTest.qWait(100)
        self.io_thread._run_flag = False
        self.cam_stop()
        QTest.qWait(100)
        # self.disconnect_signal()
        
        self.action_play.setEnabled(True)
        self.action_stop.setEnabled(False)
        self.action_set.setEnabled(True)
        pass
    
    def clicked_setting(self):
                
        self.show_config_win()
        
        self.action_play.setEnabled(True)
        self.action_stop.setEnabled(True)
        self.action_set.setEnabled(True)
        pass
    
    
    @pyqtSlot(int, bool, QRect)
    def receive_rect(self, tag, use, rect):
        print(f'[{now_time_str()}] rect receive : {tag} {use} {rect} {rect.left()} {rect.top()} {rect.width()} {rect.height()}')
        # print(f'{self.list_poi[tag]}')

        self.list_poi[tag]['use'] = use
        self.list_poi[tag]['x'] = str(rect.left())
        self.list_poi[tag]['y'] = str(rect.top())
        self.list_poi[tag]['e_x'] = str(rect.width())
        self.list_poi[tag]['e_y'] = str(rect.height())

        
        if tag == 0:
            self.data['up']['cam1']['poi'] = self.list_poi[0]
        elif tag == 1:
            self.data['up']['cam2']['poi'] = self.list_poi[1]
        elif tag == 2:
            self.data['dn']['cam1']['poi'] = self.list_poi[2]
        elif tag == 3:
            self.data['dn']['cam2']['poi'] = self.list_poi[3]

        # print(f'{self.list_poi[tag]}')
        print(f'{self.data}')

        write_config(Config_path, self.data)
        
        
    #### 인터페이스 start
    @pyqtSlot(bool, np.ndarray, int)  ##signal_retrieve = pyqtSignal(bool, np.ndarray, int)
    def receive_img(self, ret, cv_img, tag):
        # print(f'receive_img : {ret}, {type(cv_img)}, {tag}')
        
        ### infer
        if ret :
            # self.temp_img = cv_img
            
            # print(f'get ok {id}')
            img = cv_img
            if self.ok_model:
                try:
                    ## poi 영역
                    if self.list_poi[tag]['use']:
                        ## 영역만 detect
                        ## poi 영역 계산
                        x= int(self.list_poi[tag]['x'])
                        y= int(self.list_poi[tag]['y'])
                        end_x= int(self.list_poi[tag]['e_x']) + x
                        end_y= int(self.list_poi[tag]['e_y']) + y
                        
                        ## 관심영역 테두리 표시
                        cv2.rectangle(img, (x, y), (end_x, end_y), (0,0,255), 2)
                        
                        ## 관심영역 카피
                        roi_img = img[y:end_y, x:end_x]

                        ## 관심영역 detect
                        roi_img2, label_dict = self.infer(roi_img, self.list_detect[tag])
                        img[y:end_y, x:end_x] = roi_img2

                                
                    else:   ## 전체 detect
                        ## 전체 영역 테두리 표시(관심영역과 동일한 색으로 표시)
                        cv2.rectangle(img, (0, 0), (400, 300), (0,0,255), 2)
                        img, label_dict = self.infer(img, self.list_detect[tag])
                        
                    # self.signal_cv_img.emit(img, id)
                    self.list_img_signal[tag].emit(img)
                    if label_dict == {}:
                        pass
                    else:
                        self.list_detect_signal[tag].emit(self.list_name[tag], label_dict)
                    # print(f"{label_dict}")
                except Exception as e:
                    print(f"try error :{e}")
                    pass
            else:  ### self.ok_model: False
                self.list_img_signal[tag].emit(img)
        else:
            # self.parent.stat_cam_list[tag].setStyleSheet("background-color: gray")
            print(f"{tag} : receive_img read fail...")
        
        
        # ### 다음 영상 호출  ----중간에 카메라 에러나면 전체가 늦어짐
        # QTest.qWait(self.repeat_time)    
        # next = tag + 1
        # if next > 3:
        #     next =0
        # self.list_cam[next].cam._get_flag = True
        # print(f'{next} 호출')
        
    #### 인터페이스 end
        
    def infer(self, cv_img, detect_list):
        
        # print("infer ...")
        labels, cord = self.model.score_frame(cv_img)
        # print(f'score_frame =>  {labels} : {type(labels)}, {cord} : {type(cord)}')
        label_list = []
        label_dict = {}
        n = len(labels)
        frame = cv_img
        x_shape, y_shape = frame.shape[1], frame.shape[0]
        for i in range(n):
            row = cord[i]
            name = self.model.class_to_label(labels[i])
            # print(name)
            if name in detect_list:
                if row[4] > float(detect_list[name]):
                    # print(f'{name} {row[4]} {type(row[4])} {detect_list[name]}, {type(float(detect_list[name]))}, {float(detect_list[name]) - row[4] }')

                    # print(f'row[4] > float(detect_list[name]) {row[4]} {float(detect_list[name])}')
                    x1, y1, x2, y2 = int(row[0] * x_shape), int(row[1] * y_shape), int(row[2] * x_shape), int(row[3] * y_shape)
                    str = name + ": %0.2f" % row[4]
                    # print(f'plot_boxes str : {str}')
                    label_dict[name] = "%0.2f" % row[4]
                    cv2.rectangle(frame, (x1, y1), (x2, y2), self.model.colors(int(labels[i])), 2)
                    
                    cv2.putText(frame, str, (x1+5, y1+15), cv2.FONT_HERSHEY_SIMPLEX, 0.6, self.model.colors(int(labels[i])), 1)
                    
                    # label_list.append(str)
        # time_str = now_time_str()
        # cv2.putText(frame, time_str, (self.img_size_w - 100, self.img_size_h - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,0), 1)
        return frame, label_dict
    
    
    
        
    ### 모델
    def init_model(self):
        print(f"init_model")
        try:
            self.model = None
            self.model = Model()
            if self.model.load_model_el(Yolov5_path, El_pt_path):
                print(f"type(self.model) : {type(self.model)}")
                return True
            else:
                print(f" self.model.load_model_el(): fail")
                return False
        except Exception as e:
            self.model = None
            print(f" self.model.load_model_el(): Exception {e}")
        
        return False
        
        
    def init_timer(self):
        self.timer_get = QTimer()
        self.timer_get.setInterval(200)
        # self.timer_get.timeout.connect(self.cam_get_img)
        self.timer_get.timeout.connect(self.repeat_get_img)
        
    def init_io_thread(self):
        # self.io_thread = None
        # self.io_thread = IO_thread()
        self.io_thread.signal_di_relay.connect(self.ui_io.disp_di_relay)
        self.io_thread.signal_state.connect(self.ui_io.disp_state)
        
        self.io_thread.set_data(self.data['up']['io']['value_io_ip'], 502)
               
        self.ui_io.signal_set_relay.connect(self.io_thread.set_relay)
        
        self.io_thread._run_flag = True
        self.io_thread.start()
        
    def connect_signal(self):
        for id in range(4):
            self.list_cam[id].cam.signal_retrieve.connect(self.receive_img)
            self.list_img_signal[id].connect(self.list_cam[id].lbl_img.changePixmap)
            self.list_cam[id].lbl_img.signal_rect.connect(self.receive_rect)
            
        self.list_detect_signal[0].connect(self.list_cont[0].receive_data)
        self.list_detect_signal[1].connect(self.list_cont[0].receive_data)
        self.list_detect_signal[2].connect(self.list_cont[1].receive_data)
        self.list_detect_signal[3].connect(self.list_cont[1].receive_data)
            
        self.list_cont[0].signal_push_call.connect(self.io_thread.set_relay_on_off)
        self.list_cont[1].signal_push_call.connect(self.io_thread.set_relay_on_off)
        
        self.io_thread.signal_state.connect(self.ui_io.disp_state)
        self.ui_io.signal_set_relay.connect(self.io_thread.set_relay)
    
       
 
            
    def cam_get_img(self):
        for id in range(4):
            self.list_cam[id].cam._get_flag = True
            
    def repeat_get_img(self):
        ### 사용중 카메라에 대해서 get_flag를... 보내고 하나 증가시킨다.
        while True:  
            if self.list_cam_use[self.repeat_tag]:
                break
            else:
                if self.repeat_tag < 3:
                    self.repeat_tag = self.repeat_tag + 1 
                else:
                    self.repeat_tag = 0    
            
        self.list_cam[self.repeat_tag].cam._get_flag = True
        # print(f"repeat_get_img : {self.repeat_tag} call...")
            
        if self.repeat_tag < 3:
            self.repeat_tag = self.repeat_tag + 1 
        else:
            self.repeat_tag = 0
        
        
    # def cam_run(self):
    #     for id in range(4):
    #         self.list_cam[id].cam.cam_run()
        
    def cam_stop(self):
        
        for id in range(4):
            self.list_cam[id].cam_stop()
            img = img_draw_msg_center(Img_default, "stop camera ")
            self.list_img_signal[id].emit(img)
            
        
        

class Cam_win(QWidget):
    
    signal_cv_img = pyqtSignal(np.ndarray)
    
    def __init__(self):
        super().__init__()
        
        self.vi_url = None
        self.vi_size = None
        self.vi_tag = None
        
        self.cam = VideoCap(self)
        self.lbl_img = ImgLabel()
        self.lbl_img.setFixedSize(400,300)
        self.lbl_title = QLabel("title")
        self.lbl_title.setAlignment(Qt.AlignCenter)
        # self.lbl_img.changePixmap(Img_nouse_img)
        
        # self.vi_url = "rtsp://admin:asdQWE12!%40@101.122.3.11:558/LiveChannel/22/media.smp"
        # self.vi_size = 400, 300
        # self.vi_tag = 1
        # self.cam.cam_set_data(self.vi_url, self.vi_size, self.vi_tag )
        
        self.init_ui()
        # self.init_signal()
        self.show()
        
       
        
    def init_ui(self):
        self.btn_open = QPushButton("open")
        self.btn_run = QPushButton("run")
        self.btn_get = QPushButton("get")
        self.btn_stop = QPushButton("stop")
        # self.btn_auto = QPushButton("auto")
        
        self.btn_open.clicked.connect(self.cam_open)
        self.btn_run.clicked.connect(self.cam_run)
        self.btn_get.clicked.connect(self.cam.cam_get_img)
        self.btn_stop.clicked.connect(self.cam_stop)
        # self.btn_auto.clicked.connect(self.auto_start)
        
        lay_btn = QHBoxLayout()
        # lay_btn.setSpacing(0)
        # lay_btn.setContentsMargins(0,0,0,0)
        
        lay_btn.addWidget(self.btn_run)
        lay_btn.addWidget(self.btn_stop)
        lay_btn.addWidget(self.btn_get)
        lay_btn.addWidget(self.btn_open)
        # lay_btn.addWidget(self.btn_auto)
        
        
        
        lay_main = QVBoxLayout()
        lay_main.setSpacing(0)
        lay_main.setContentsMargins(0,0,0,0)
        # lay_main.addWidget(self.lbl_title)
        lay_main.addWidget(self.lbl_img)
        # lay_main.addLayout(lay_btn)
        
        self.setLayout(lay_main)
        
    #### 인터페이스 start
    @pyqtSlot(bool, np.ndarray, int)  ##signal_retrieve = pyqtSignal(bool, np.ndarray, int)
    def receive_img(self, ret, cv_img, tag):
        # print(f'receive_img : {ret}, {type(cv_img)}, {tag}')
        if ret :
            self.signal_cv_img.emit(cv_img)
        else:
            # print(f'receive_img : {ret}, {type(cv_img)}, {tag}')
            self.signal_cv_img.emit(Img_default)
        
    #### 인터페이스 end
    
    def set_data(self, vi_url, vi_size, vi_tag):
        self.vi_url = vi_url
        self.vi_size = vi_size
        self.vi_tag = vi_tag
        self.lbl_img.set_tag(self.vi_tag)
        
        # self.lbl_title.setText(self.vi_url)
    
 
        
    def cam_open(self):
        
        re = self.cam.cam_open()
        if re :
            img = img_draw_msg_center(Img_default, "connect : "+self.vi_url)
            self.signal_cv_img.emit(img)
            return True
            
        else:
            img = img_draw_msg_center(Img_default, "disconnect : "+self.vi_url)
            self.signal_cv_img.emit(img)
            return False
    
        
    def cam_run(self):
        self.cam.cam_run()
        
    def cam_stop(self):
        self.cam.cam_stop()
        img = img_draw_msg_center(Img_default, "stop camera ")
        self.signal_cv_img.emit(img)
        
        

### common data
      


# def make_nouse_img():
#     img = np.full(shape=(300, 400, 3), fill_value=100, dtype=np.uint8)
#     b,g,r,a = 255,255,255,0
    
#     img_pil = Image.fromarray(img)
#     draw = ImageDraw.Draw(img_pil)
#     draw.text((150, 120),  "사용 안함", font=font, fill=(b,g,r,a))
#     img = np.array(img_pil)
    
#     return img



if __name__=="__main__":
    app = QApplication(sys.argv)
    a = Main_win4()
    # a = Cam_win()
    sys.exit(app.exec())
    
#    ### 모델
#     def init_model(self):
#         print(f"init_model")
#         try:
#             self.model = Model()
#             if self.model.load_model_el(Yolov5_path, El_pt_path):
#                 print(f"type(self.model) : {type(self.model)}")
#                 return True
#             else:
#                 print(f" self.model.load_model_el(): fail")
#                 return False
#         except Exception as e:
#             self.model = None
#             print(f" self.model.load_model_el(): Exception {e}")
        
#         return False
        
        
#     def init_timer(self):
#         self.timer_get = QTimer()
#         self.timer_get.start(1000)
#         self.timer_get.timeout.connect(self.cam.cam_get_img)
        
#     def init_signal(self):
#         self.cam.signal_retrieve.connect(self.receive_img)
#         self.signal_cv_img.connect(self.lbl_img.changePixmap)