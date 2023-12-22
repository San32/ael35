# -*- coding:utf-8 -*-

"""
모델을 로딩하고, 판명한다
입력 : 그림파일
출력 : 그림, 측정값
"""

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtTest import *
import time
import numpy as np
import cv2
import sys
import json
import queue
# import log
import torch
from PIL import Image, ImageFont, ImageDraw

from common import *

class Colors:
    # Ultralytics color palette https://ultralytics.com/
    def __init__(self):
        # hex = matplotlib.colors.TABLEAU_COLORS.values()
        hexs = ('FF3838', 'FF9D97', 'FF701F', 'FFB21D', 'CFD231', '48F90A', '92CC17', '3DDB86', '1A9334', '00D4BB',
                '2C99A8', '00C2FF', '344593', '6473FF', '0018EC', '8438FF', '520085', 'CB38FF', 'FF95C8', 'FF37C7')
        self.palette = [self.hex2rgb(f'#{c}') for c in hexs]
        self.n = len(self.palette)

    def __call__(self, i, bgr=False):
        c = self.palette[int(i) % self.n]
        return (c[2], c[1], c[0]) if bgr else c

    @staticmethod
    def hex2rgb(h):  # rgb order (PIL)
        return tuple(int(h[1 + i:1 + i + 2], 16) for i in (0, 2, 4))


class Model(QWidget):

    def __init__(self):
        super().__init__()
        self.font = ImageFont.truetype(Font_path, 10)
        
        self.colors = Colors()

        ## 모델 다변화
        self.load_model_el(Yolov5_path, El_pt_path)
        # self.load_model_v5(Yolov5_path, V5_pt_path)


    def infer_img(self, cv_img, detect_list):
        infer_img = None
        label_list = None
        try:
            if self.model != None:
                results = self.score_frame(cv_img)

                infer_img, label_list = self.plot_boxes(results, cv_img, detect_list)
        except Exception as e:
            print(f"infer_img : {e}")
            pass

        return infer_img, label_list
        


    def put_text(self, frame, text, w, h, color):
        try:
            # 한글 표출
            img_pillow = Image.fromarray(frame)
            draw = ImageDraw.Draw(img_pillow)
            draw.text((w, h), text, fill=color, font=self.font, align="right")

            frame = np.array(img_pillow)  # 다시 OpenCV가 처리가능하게 np 배열로 변환
        except Exception as e:
            print(f"put_text : {e}")
        return frame

    def load_model_el(self, yolov5_path, pt_path):

        try:
            # model1 = torch.hub.load('ultralytics/yolov5', 'yolov5s')
            self.model = torch.hub.load(yolov5_path, 'custom', source='local', path=pt_path, force_reload=True)

            self.classes = self.model.names
            self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
            print(f'model type : {type(self.model)}')

        except Exception as e:
            print(f"load_model exception : {e}")

    def load_model_v5(self, yolov5_path, pt_path):

        try:
            self.model = torch.hub.load(yolov5_path, 'yolov5s')
            # self.model = torch.hub.load(yolov5_path, 'custom', source='local', path=pt_path, force_reload=True)

            self.classes = self.model.names
            self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
            print(f'model type : {type(self.model)}')

        except Exception as e:
            print(f"load_model exception : {e}")

    # @pyqtSlot(np.ndarray)
    # def infer(self, cv_frame):
    #     results = self.score_frame(cv_frame)
    #     infer_img, label_list = self.plot_boxes(results, cv_frame)
    #     self.infer_img_signal.emit(infer_img)
    #     self.infer_label_signal.emit(label_list)

    def score_frame(self, frame):
        """
        Takes a single frame as input, and scores the frame using yolo5 model.
        :param frame: input frame in numpy/list/tuple format.
        :return: Labels and Coordinates of objects detected by model in the frame.
        """
        self.model.to(self.device)
        frame = [frame]
        results = self.model(frame)
        labels, cord = results.xyxyn[0][:, -1].cpu().numpy(), results.xyxyn[0][:, :-1].cpu().numpy()

        # print(f'score_frame - labels : {labels}')

        return labels, cord

    def class_to_label(self, x):
        """
        For a given label value, return corresponding string label.
        :param x: numeric label
        :return: corresponding string label
        """
        return self.classes[int(x)]

    def plot_boxes(self, results, frame, detect_list):
        """
        Takes a frame and its results as input, and plots the bounding boxes and label on to the frame.
        :param results: contains labels and coordinates predicted by model on the given frame.
        :param frame: Frame which has been scored.
        :return: Frame with bounding boxes and labels ploted on it.
        """
        labels, cord = results
        # print(f'plot_boxes  {labels}  {type(labels)}, {type(cord)}')
        label_list = []
        label_dict = {}
        n = len(labels)
        x_shape, y_shape = frame.shape[1], frame.shape[0]
        for i in range(n):
            row = cord[i]
            name = self.class_to_label(labels[i])
            # print(name)
            if name in detect_list:
                if row[4] > float(detect_list[name]):
                    # print(f'{name} {row[4]} {type(row[4])} {detect_list[name]}, {type(float(detect_list[name]))}')

                    # print(f'row[4] > float(detect_list[name]) {row[4]} {float(detect_list[name])}')
                    x1, y1, x2, y2 = int(row[0] * x_shape), int(row[1] * y_shape), int(row[2] * x_shape), int(
                        row[3] * y_shape)
                    str = name + ": %0.1f" % row[4]
                    # print(f'plot_boxes str : {str}')
                    label_dict[name] = "%0.1f" % row[4]
                    cv2.rectangle(frame, (x1, y1), (x2, y2), self.colors(int(labels[i])), 2)
                    cv2.putText(frame, str, (x1, y1), cv2.FONT_HERSHEY_SIMPLEX, 0.9, self.colors(int(labels[i])), 2)
                    # label_list.append(str)
        return frame, label_dict

def main():
    model = Model()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    # a = App2()
    # a.show()
    # sys.exit(app.exec_())

    main()