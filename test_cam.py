# -*- coding:utf-8 -*-

import cv2

vi = 'rtsp://admin:asdQWE12!%40@101.122.3.201:554/profile2/media.smp'
capture = cv2.VideoCapture(vi)

while capture.isOpened():
    run, frame = capture.read()
    if not run:
        print("[프레임 수신 불가] - 종료합니다")
        break
    img = cv2.cvtColor(frame, cv2.IMREAD_COLOR)
    cv2.imshow('video', frame)
    if cv2.waitKey(30) & 0xFF == ord('q'):
        break

capture.release()
cv2.destroyAllWindows()