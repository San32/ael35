# -*- coding:utf-8 -*-

import json
import sys
import time
# from PIL import Image,ImageTk,ImageFont
from PIL import ImageFont, ImageDraw, Image
import numpy as np

# global Config_path

global RUN_OK 
global RUN_FAIL
global READ_OK
global READ_FAIL


### PC config
Base_path = "/home/comm/conda_work/ael35/"
Data_path = Base_path + "data/"
Yolov5_path = "/home/comm/data/yolov5"

Font_path = Data_path + "NanumMyeongjoBold.ttf"

Config_path = Data_path + "config.json"
V5_pt_path = Data_path + "yolov5s.pt"
El_pt_path = Data_path + "best.pt"

Img_size_x = 400
Img_size_y = 300
        
            
def make_nouse_img():
    font = ImageFont.truetype(Font_path, 13)
    
    img = np.full(shape=(300, 400, 3), fill_value=100, dtype=np.uint8)
    b,g,r,a = 255,255,255,0
    
    img_pil = Image.fromarray(img)
    draw = ImageDraw.Draw(img_pil)
    draw.text((150, 120),  "사용 안함", font=font, fill=(b,g,r,a))
    img = np.array(img_pil)
    
    return img            

def img_draw_msg_center(img, msg):
    font = ImageFont.truetype(Font_path, 13)
    b,g,r,a = 255,255,255,0
    img_pil = Image.fromarray(img)
    draw = ImageDraw.Draw(img_pil)
    
    font_width, font_height = font.getsize(msg)
    new_width = (Img_size_x - font_width) / 2
    new_height = (Img_size_y - font_height) / 2
    
    draw.text((new_width, new_height),  msg, font=font, fill=(b,g,r,a))
    img = np.array(img_pil)
    
    return img   
            
Img_default = np.full(shape=(300, 400, 3), fill_value=20, dtype=np.uint8)
Img_nouse_img = make_nouse_img()





def read_config(file_path):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            # print("파일 존재함.")
            # print(type(data))
            return data
    except Exception as e:
        print(f"read_config except :{e}")
        return None

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
