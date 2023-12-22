# -*- coding: utf-8 -*-
"""엘리베이터 자동호출 시스템 메인

Returns:
    _type_: _description_
"""

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

from common import *
from cont import *
from modelEL import *
from io_ui2 import *
from ui_config import *
## global 상수 사용 : CAM_STAT = ("RUN_OK", "RUN_FAIL", "READ_OK" , "READ_FAIL")



    

class Vi_thread(QThread):
    change_pixmap_signal = pyqtSignal(np.ndarray, int)
    
    # signal_list_img = [pyqtSignal(np.ndarray), pyqtSignal(np.ndarray), pyqtSignal(np.ndarray), pyqtSignal(np.ndarray)]
        
    change_state_signal = pyqtSignal(int, str) ## global RUN, PLAY, STOP, READ_FAIL

    log_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        print(f'vi_thread 생성...')
        self._run_flag = False
        self._show_flag = False # 직접 바로 보낸다
        self._infer_flag = False
        
        self.cap = None
        
        self.set_size = 400, 300
        
        

    def __del__(self):
        print(f'vi_thread 소멸...')
        pass


    def set_data(self, url, cam_use, name, detect, poi, tag):
        self.url = url
        self.cam_use = cam_use
        self.name = name
        self.detect = detect
        self.poi = poi
        self.tag = tag
        
        # ### 카메라 초기화
        # for ii in range(4):
        #     cap = cv2.VideoCapture(self.list_url[ii])
        #     self.list_cap[ii] = cap
            
        # print(f'{self.list_cap}')
        

    def send_log(self, msg):
        # self.log_signal.emit(f'{self.name}:{msg}')
        print(f'{get_time()}:{msg}')

 
            
  
            
    def test_func(self, num):
        self.send_log(f'test func : {num}')
        QTest.qWait(1000)
        
 
    
        
    @pyqtSlot()
    def play(self):
        self._run_flag = True
        self.start()
        
    @pyqtSlot()
    def stop(self):
        self._run_flag = False
        # self.start()


    
     ## 계속 읽음
    def run(self):
                
        self.send_log(f"thread run...")
        self.cap = cv2.VideoCapture(self.url)
        
        while self._run_flag:
            # self.send_log(f"self.list_cap : {self.cap}")
            
            if not self.cap.isOpened():  ## 재시작
                print(f'self.cap None, re try')
                self.cap = cv2.VideoCapture(self.url)
            else:
                # QTest.qWait(100)
                ret, cv_img = self.cap.read()
                if ret:
                    # print(f' self.list_cap read ok...porcess')
                    last_cv_img = cv2.resize(cv_img, self.set_size, interpolation=cv2.INTER_AREA)
                    self.change_pixmap_signal.emit(last_cv_img, self.tag)
                else:
                    self.send_log(f' read error... re connect')
                    self.change_pixmap_signal.emit(Default_img, self.tag)
                    # print(f'{self.cap}  {self.cap.isOpened()}')
                    self.cap.release()
                    # print(f'cap.release()     {self.cap}  {self.cap.isOpened()}')
                    
            # QTest.qWait(1000)
            # time.sleep(0.2)
        self.change_pixmap_signal.emit(Default_img, self.tag)
        self.cap.release()
                        
        self.send_log(f"thread stop...")
    


 
    


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
        self.tag = 0 ## signal_rect 를 어느 이미지에서 보냈는지 확인하기 위한 tag

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

        self.load_default_img()

        self.init_contextmenu()

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

    ## popup 메뉴 end



    def send_log(self, msg):
        self.log_signal.emit(msg)

    def load_default_img(self):
        self.pix = self.convert_cv_qt(Default_img)

        self.update()
        
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

    @pyqtSlot(np.ndarray)
    def changePixmap(self, cv_img):
        # if cv_img is None:
        #     text = f"img is None.............................."
        #     print(f"{text}")

        #     cv_img = self.disconnect_img
            

        self.pix = self.convert_cv_qt(cv_img)

        # print(f'cv_img : {type(cv_img)} {cv_img.shape}, self.pix : {type(self.pix)}')

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
        

class Main_ael_win(QMainWindow):
    signal_auto_show = pyqtSignal()
    
    signal_img_0 = pyqtSignal(np.ndarray)
    signal_img_1 = pyqtSignal(np.ndarray)
    signal_img_2 = pyqtSignal(np.ndarray)
    signal_img_3 = pyqtSignal(np.ndarray)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("자동호출 시스템    Ver 3.5")
        self.statusBar = self.statusBar()
        self.statusBar.showMessage("ready")


        # self.set_data()
        self.init_ui()
        self.init_menu()
        self.setMouseTracking(False)
        # self.ui_btn_overriding()
        
        self.io_show()
        self.show()
        
        
        
        QTimer.singleShot(1000, self.auto_start)
        
        # self.init_thread()
        
        
        
        
        
    
        
    
    def set_data(self):
        self.data = read_config(Config_path)
        print(self.data)
        
        self.cam_list = [None, None, None, None]
        
        
       
        self.list_url = [self.data['up']['cam1']['cam']['url'], self.data['up']['cam2']['cam']['url'], self.data['dn']['cam1']['cam']['url'], self.data['dn']['cam2']['cam']['url']]
        self.list_cam_use = [self.data['up']['cam1']['cam']['use'], self.data['up']['cam2']['cam']['use'], self.data['dn']['cam1']['cam']['use'], self.data['dn']['cam2']['cam']['use']]
        
        self.list_name = ["cam1", "cam2", "cam1", "cam2"]
        self.list_detect = [self.data['up']['cam1'].get('detect'), self.data['up']['cam2'].get('detect'), self.data['dn']['cam1'].get('detect'), self.data['dn']['cam2'].get('detect')]
        # self.list_cont = [self.ui_autoel.up_floor.edit_cont, self.ui_autoel.up_floor.edit_cont, self.ui_autoel.dn_floor.edit_cont, self.ui_autoel.dn_floor.edit_cont]
        self.list_poi = [self.data['up']['cam1'].get('poi'), self.data['up']['cam2'].get('poi'), self.data['dn']['cam1'].get('poi'), self.data['dn']['cam2'].get('poi')]
        self.list_io = [self.data['up'].get('io'), self.data['up'].get('io'), self.data['dn'].get('io'), self.data['dn'].get('io')]
        
    ### 메뉴
    def init_menu(self):
        menubar = self.menuBar()
        menubar.setNativeMenuBar(True)

        fileMenu = menubar.addMenu('File')
        menubar.addSeparator()
        
        viewMenu = menubar.addMenu("보기")
        menubar.addSeparator()
                
        confMenu = menubar.addMenu("설정")
        menubar.addSeparator()
        
        

        helpMenu = menubar.addMenu("&Help")
          
    ### file 하부 메뉴
        exitAction = QAction(QIcon('exit.png'), 'Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        # exitAction.triggered.connect(qApp.quit)
        exitAction.triggered.connect(self.closeEvent)

        fileMenu.addAction(exitAction)

 
    ## 보기 하부 메뉴
        self.io_showAction = QAction('IO제어기 보이기', self)
        self.io_showAction.triggered.connect(self.io_show)
        
        self.io_hideAction = QAction('IO제어기 숨기기', self)
        self.io_hideAction.triggered.connect(self.io_hide)
        
        viewMenu.addAction(self.io_showAction)
        viewMenu.addAction(self.io_hideAction)
  

    ## 설정 하부 메뉴
        self.confAction = QAction('환경설정', self)
        self.confAction.triggered.connect(self.show_configPanel)
        
        confMenu.addAction(self.confAction)

    ## help 하부 메뉴
        self.helpAction = QAction('도움말', self)
        self.helpAction.triggered.connect(self.show_helpPanel)
        
        helpMenu.addAction(self.helpAction)

    def io_show(self):
        self.ui_io.setVisible(True)
        # self.setMinimumHeight(950)
        self.setFixedHeight(950)
        self.statusBar.showMessage("io_show")
        
    def io_hide(self):
        self.ui_io.setVisible(False)
        self.setFixedHeight(760)
        # self.setMinimumHeight(500)
        self.statusBar.showMessage("io_hide")
        
    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Window Close', '프로그램을 종료 할까요?',
				QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
        	event.accept()
        	# print('Window closed')
        else:
        	event.ignore()

    def show_configPanel(self):
        self.auto_stop()
        
        ## 창 띄우기
        dlg = UI_config()
        if dlg.exec_():
            print("acept...")
        else:
            print("cancel...")

        self.auto_start()
        

    def show_helpPanel(self):
        print(f"help")
        # webbrowser.open_new('./help.html')
        
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

    def init_ui(self):
        self.img_list = [None, None, None, None]
        self.img_signal_list = [self.signal_img_0, self.signal_img_1, self.signal_img_2, self.signal_img_3]
        self.cont_list = [None, None]
        
        
        
        # 초기화
        for ii in range(4):
            label = ImgLabel()
            label.tag = int(ii)
            label.setFixedSize(400, 300)
            label._flag_draw = True
            self.img_list[ii] = label
        
        ##cont 초기화
        for ii in range(2):
            cont = Cont()
            cont.setFixedSize(300, 300)
            self.cont_list[ii] = cont
        
                
        # ### test_btn insert
        # self.ui_test_btn = Ui_test_btn()
        
        ### IO ui 생성
        self.ui_io = Ui_io()
        
        
        ### layout
        
        up_groupbox = QGroupBox("상부 엘리베이터 카메라")
        up_groupbox.setStyleSheet("QGroupBox#ColoredGroupBox { border: 1px solid red;}")
        up_box = QHBoxLayout()
        up_box.addWidget(self.img_list[0])
        up_box.addWidget(self.img_list[1])
        up_box.addWidget(self.cont_list[0])
        up_groupbox.setLayout(up_box)
        
        dn_groupbox = QGroupBox("하부 엘리베이터 카메라")
        dn_groupbox.setStyleSheet("QGroupBox#ColoredGroupBox { border: 1px solid red;}")
        dn_box = QHBoxLayout()
        dn_box.addWidget(self.img_list[2])
        dn_box.addWidget(self.img_list[3])
        dn_box.addWidget(self.cont_list[1])
        dn_groupbox.setLayout(dn_box)
        
        
                
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.addWidget(up_groupbox)
        layout.addWidget(dn_groupbox)
        layout.addWidget(self.ui_io)
        # layout.addWidget(self.ui_test_btn)
        
        # self.setLayout(main_layout)
        # # self.resize(600,400)
        
        self.setCentralWidget(widget)
        
    def init_io_thread(self):
        ### io thread start
        self.io_thread = IO_thread()
                
        self.io_thread.set_data(self.data['up']['io']['value_io_ip'], 502)
                
        self.io_thread._run_flag = True
        self.io_thread.start()
        
    def init_test_thread(self):
    ### test thread start
        self.test = Test_thread(self)
        self.test.start()
            
    def init_img_thread(self):
        self.img_thread = Img_thread()
        self.img_thread.set_data(self.list_poi, self.list_detect)
        
    
    def init_vi_thread(self):
        for ii in range(4):
            cam = Vi_thread()
            cam.set_data(self.list_url[ii], self.list_cam_use[ii], self.list_name[ii], self.list_detect[ii], self.list_poi[ii], ii)
            
            # cam.change_pixmap_signal.connect(self.img_list[ii].changePixmap)
            # cam.change_pixmap_signal.connect(self.receive_img)
            self.cam_list[ii] = cam
        
        
    def vi_thread_start(self):
        self.init_vi_thread()
        # self.vi_thread.check_cap()
        for ii in range(4):
            if self.list_cam_use[ii]:
                self.cam_list[ii].play()
        
 
        
    
    def set_signal(self):
        for ii in range(4):
            if self.list_cam_use[ii]:
                self.cam_list[ii].change_pixmap_signal.connect(self.img_thread.receive_img)
                self.img_list[ii].signal_rect.connect(self.receive_rect)
                # self.list_cam[ii].change_pixmap_signal.connect(self.receive_img)
            
            
        self.img_thread.signal_img_0.connect(self.img_list[0].changePixmap)
        self.img_thread.signal_img_1.connect(self.img_list[1].changePixmap)
        self.img_thread.signal_img_2.connect(self.img_list[2].changePixmap)
        self.img_thread.signal_img_3.connect(self.img_list[3].changePixmap)
        
        self.img_thread.signal_detect_0.connect(self.cont_list[0].receive_data)
        self.img_thread.signal_detect_1.connect(self.cont_list[0].receive_data)
        self.img_thread.signal_detect_2.connect(self.cont_list[1].receive_data)
        self.img_thread.signal_detect_3.connect(self.cont_list[1].receive_data)
        
        self.io_thread.signal_di_relay.connect(self.ui_io.disp_di_relay)
        self.io_thread.signal_state.connect(self.ui_io.disp_state)
        self.ui_io.signal_set_relay.connect(self.io_thread.set_relay)
        
        self.cont_list[0].signal_push_call.connect(self.io_thread.set_relay_on_off)
        self.cont_list[1].signal_push_call.connect(self.io_thread.set_relay_on_off)
        
    
        
    def ui_btn_overriding(self):
        # self.ui_test_btn.btn_list[0].setText('rect_show')
        # self.ui_test_btn.btn_list[0].clicked.connect(self.rect_show)
        
        # self.ui_test_btn.btn_list[1].setText('rect_hide')
        # self.ui_test_btn.btn_list[1].clicked.connect(self.rect_hide)
        
        # self.ui_test_btn.btn_list[2].setText('test start')
        # self.ui_test_btn.btn_list[2].clicked.connect(self.init_test_thread)
        
        # self.ui_test_btn.btn_list[3].setText('vi init vi')
        # self.ui_test_btn.btn_list[3].clicked.connect(self.init_vi_thread)
        
        # self.ui_test_btn.btn_list[4].setText('auto')
        # self.ui_test_btn.btn_list[4].clicked.connect(self.auto_start)
        
        # self.ui_test_btn.btn_list[5].setText('all stop')
        # self.ui_test_btn.btn_list[5].clicked.connect(self.auto_stop)
        pass
        
    def init_thread(self):
        self.io_thread = None
        self.io_thread = IO_thread()
        
        self.cam_list = [None, None, None, None]
        for ii in range(4):
            cam = Vi_thread()
            self.cam_list[ii] = cam
            
        self.img_thread = None
        self.img_thread = Img_thread()
        
        
                
        
    def auto_start(self):
        self.set_data()
        
        self.init_thread()
        
        ### signal 연결
        self.set_signal()
        
        
        
        self.cont_list[0].init_io(self.data['up']['io'])
        self.cont_list[1].init_io(self.data['dn']['io'])
        
        ### io thread start
        self.io_thread.set_data(self.data['up']['io']['value_io_ip'], 502)
        self.io_thread._run_flag = True
        self.io_thread.start()
        
              
        ###vi thread start
            
        for ii in range(4):
            if self.list_cam_use[ii]:
                self.cam_list[ii].set_data(self.list_url[ii], self.list_cam_use[ii], self.list_name[ii], self.list_detect[ii], self.list_poi[ii], ii)
                self.cam_list[ii]._run_flag = True
                self.cam_list[ii].start()
            
        
        
        
        
        
        ### img 처리 thread
        
        self.img_thread.set_data(self.list_cam_use, self.list_poi, self.list_detect, self.list_name)
        self.img_thread._run_flag = True
        self.img_thread.start()
        
    def auto_stop(self):
        self.rect_hide()
        
        self.io_thread._run_flag = False
        
        for ii in range(4):
            if self.list_cam_use[ii]:
                self.cam_list[ii]._run_flag = False
            
        time.sleep(1)
           
        self.img_thread._run_flag = False
        
        # self.cont_up = Cont()
        # self.cont_dn = Cont()
        
    def rect_show(self):
        print(f"click rect_show")
        for ii in range(4):
            self.img_list[ii]._flag_show_rect = True
            
    def rect_hide(self):
        print(f"click rect_hide")
        for ii in range(4):
            self.img_list[ii]._flag_show_rect = False
        
        
        
        
        
        
    def btn4(self):
        # self.init_model()
        self.init_vi_thread()
        
        self.init_io_thread()
                
        for ii in range(4):
            if self.list_cam_use[ii]:
                self.cam_list[ii].play()
                
        self.init_img_thread()
        self.img_thread.set_data(self.list_poi, self.list_detect)   #set_data(self, list_poi, list_detect):
        self.img_thread._run_flag = True
        self.img_thread.start()
        
        self.set_signal()
        
        
        
        
    def btn5(self):
        self.img_thread._run_flag = True
        self.img_thread.start()
        
    @pyqtSlot(np.ndarray, int)
    def receive_img(self, cv_img, tag):
        # self.img_list[tag].changePixmap(cv_img)
        self.img_signal_list[tag].emit(cv_img)
        
        
        
        
class Img_thread(QThread):
    
    _run_flag = False
    signal_cv_img = pyqtSignal(np.ndarray, int)
    
    signal_img_0 = pyqtSignal(np.ndarray)
    signal_img_1 = pyqtSignal(np.ndarray)
    signal_img_2 = pyqtSignal(np.ndarray)
    signal_img_3 = pyqtSignal(np.ndarray)
    
    signal_detect_0 = pyqtSignal(str, dict)
    signal_detect_1 = pyqtSignal(str, dict)
    signal_detect_2 = pyqtSignal(str, dict)
    signal_detect_3 = pyqtSignal(str, dict)
    
    def __init__(self):
        super().__init__()
        print(f'Img_thread init...')
        self.init_model()
        
        self.list_cv_img = [None, None, None, None]
        self.list_signal_img = [self.signal_img_0, self.signal_img_1, self.signal_img_2, self.signal_img_3]
        self.list_signal_detect = [self.signal_detect_0, self.signal_detect_1, self.signal_detect_2, self.signal_detect_3]
        self.list_name = [None, None, None, None]
        
        
        
        
        
    ### 모델
    def init_model(self):
        try:
            self.model = Model()
            # self.model.load_model_el()
            # self.model.load_model_yolov5()
            print(f"type(self.model) : {type(self.model)}")
        except:
            self.model = None
        
    @pyqtSlot(np.ndarray, int)
    def receive_img(self, cv_img, tag):
        self.list_cv_img[tag] = cv_img
        
    def set_data(self, list_cam_use, list_poi, list_detect, list_name):
        self.list_cam_use = list_cam_use
        self.list_poi = list_poi
        self.list_detect = list_detect
        self.list_name = list_name
        
        for ii in range(4):
            if self.list_cam_use[ii]:
                pass
            else:
                self.set_no_use(ii)
                
    
        
    def set_no_use(self, id):
        # img = np.full(shape=(300, 400, 3), fill_value=200, dtype=np.uint8)
        # b,g,r,a = 255,255,255,0
        
        # img_pil = Image.fromarray(img)
        # draw = ImageDraw.Draw(img_pil)
        # draw.text((60, 70),  "사용 안함", font=font, fill=(b,g,r,a))
        # img = np.array(img_pil)
        
        self.list_signal_img[id].emit(Nouse_img)
        
    
        
    ## poi 영역 자르기
    def run(self):
        print(f'Img_thread run...')
        while self._run_flag:
            for id in range(4):
                if self.list_cam_use[id]:
                    if self.list_cv_img[id] is None:
                        self.list_signal_img[id].emit(Default_img)
                        pass
                    else:
                        img = self.list_cv_img[id]
                        self.list_cv_img[id] = None
                        try:
                            ## poi 영역
                            if self.list_poi[id]['use']:
                                ## 영역만 detect
                                ## poi 영역 계산
                                x= int(self.list_poi[id]['x'])
                                y= int(self.list_poi[id]['y'])
                                end_x= int(self.list_poi[id]['e_x']) + x
                                end_y= int(self.list_poi[id]['e_y']) + y
                                
                                ## 관심영역 테두리 표시
                                cv2.rectangle(img, (x, y), (end_x, end_y), (0,0,255), 2)
                                
                                ## 관심영역 카피
                                roi_img = img[y:end_y, x:end_x]

                                ## 관심영역 detect
                                roi_img2, label_dict = self.infer(roi_img, self.list_detect[id])
                                img[y:end_y, x:end_x] = roi_img2

                                        
                            else:   ## 전체 detect
                                ## 전체 영역 테두리 표시(관심영역과 동일한 색으로 표시)
                                cv2.rectangle(img, (0, 0), (400, 300), (0,0,255), 2)
                                img, label_dict = self.infer(img, self.list_detect[id])
                                
                            # self.signal_cv_img.emit(img, id)
                            self.list_signal_img[id].emit(img)
                            if label_dict == {}:
                                pass
                            else:
                                self.list_signal_detect[id].emit(self.list_name[id], label_dict)
                            # print(f"{label_dict}")
                        except Exception as e:
                            # print(f"try error :{e}")
                            pass
            QTest.qWait(200)
            # time.sleep(0.2)
        for id in range(4):
            if self.list_cam_use[id]:
                self.list_signal_img[id].emit(Default_img)


    ### 영상분석
    ### input : cv_img, detect_list
    ### return : img, label_list을 
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
    
 

 




if __name__=="__main__":
    app = QApplication(sys.argv)
    
       
    
    # app = QApplication(sys.argv)
    a = Main_ael_win()
    # a.show()
    sys.exit(app.exec())


