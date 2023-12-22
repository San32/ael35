# -*- coding:utf-8 -*-

import json
import sys
import time
# from PIL import Image,ImageTk,ImageFont
from PIL import ImageFont, ImageDraw, Image
import numpy as np

global path_config

global RUN_OK 
global RUN_FAIL
global READ_OK
global READ_FAIL



### PC config

# font_path = "/home/nvidia/work/auto_el/data/NanumMyeongjoBold.ttf"
# font = ImageFont.truetype(font_path, 20)
# pwd = "/home/comm/conda_work/git_test/ael/"
# path_config = pwd + "config.json"
### PC config ---end


### xavier config

# font_path = "/home/nvidia/work/ael_data/NanumMyeongjoBold.ttf"
# font = ImageFont.truetype(font_path, 20)

# pwd = "/home/nvidia/work/ael35/"
# path_config = pwd + "config.json"

# yolov5_path = '/home/nvidia/work/yolov5'
# el_pt_path = "/home/nvidia/work/ael_data/best.pt"

Base_path = "/home/nvidia/ael35/"
Data_path = "/home/nvidia/ael35/data/"
Yolov5_path = "/home/nvidia/work/yolov5"

Font_path = Data_path + "NanumMyeongjoBold.ttf"

Config_path = Data_path + "config.json"
V5_pt_path = Data_path + "yolov5s.pt"
El_pt_path = Data_path + "best.pt"


### PC config ---end

# Base_path = "/home/comm/conda_work/ael35/"
# Data_path = "/home/comm/conda_work/ael_data/"
# Yolov5_path = "/home/comm/data/yolov5"

# Font_path = Data_path + "NanumMyeongjoBold.ttf"

# Config_path = Data_path + "config.json"
# V5_pt_path = Data_path + "yolov5s.pt"
# El_pt_path = Data_path + "best.pt"
        
###

def make_nouse_img():
    font = ImageFont.truetype(Font_path, 20)
    
    img = np.full(shape=(300, 400, 3), fill_value=100, dtype=np.uint8)
    b,g,r,a = 255,255,255,0
    
    img_pil = Image.fromarray(img)
    draw = ImageDraw.Draw(img_pil)
    draw.text((150, 120),  "사용 안함", font=font, fill=(b,g,r,a))
    img = np.array(img_pil)
    
    return img

# def make_nouse_img():
#     img = np.full(shape=(300, 400, 3), fill_value=100, dtype=np.uint8)
#     b,g,r,a = 255,255,255,0
    
#     img_pil = Image.fromarray(img)
#     draw = ImageDraw.Draw(img_pil)
#     draw.text((150, 120),  "사용 안함", font=font, fill=(b,g,r,a))
#     img = np.array(img_pil)
    
#     return img

Nouse_img = make_nouse_img()
Default_img = np.full(shape=(300, 400, 3), fill_value=200, dtype=np.uint8)

def read_config(file_path):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            # print("파일 존재함.")
            # print(type(data))
            return data
    except Exception as e:
        print(f"read_config except :{e}")
        return e

##저장
def write_config(file_path, data):
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent="\t")
            return True
    except(e):
        print(f'write_config except {e}')
        return False

def now_time_str():
    now = time.localtime()
    return time.strftime('%H:%M:%S', now)

# class Common():
