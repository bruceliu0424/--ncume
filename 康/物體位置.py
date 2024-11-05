import cv2
import numpy as np
from pyModbusTCP.client import ModbusClient

video = cv2.VideoCapture(0)
A = []
B = []
while(1):
    ret,frame = video.read()
    if ret == False:
        continue
    imgray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    ret,thresh = cv2.threshold(imgray,150,255,0)
    contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    for i in contours:
        if np.shape(i)[0]>100:
            area = cv2.contourArea(i)

            frame = cv2.drawContours(frame, i, -1, (0, 255, 0), 3)
            M = cv2.moments(i)
            cx = int(M['m10'] / M['m00'])
            cy = int(M['m01'] / M['m00'])
            cv2.circle(frame,(cx,cy),7,(255,0,0),-1)
            cx=178.821-cx*276/640
            cy=508.153-cy*191/480
            print (cx)
            print (cy)
            A.append(cx)
            A.append(cy)

        #frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask1 = cv2.inRange(frame, (0, 0, 100), (100, 100, 255))
        c = ModbusClient(host="192.168.1.1", port=502, unit_id=2, auto_open=True)
        cv2.imshow('output', mask1)
        cv2.waitKey(1)
        break
print(A)
num=len(A)


if c.write_multiple_registers(5000,[(int(num/2))]):
    print("write ok")
for i in range(num):
    if c.write_multiple_registers(5200+i, [int(A[i])]):
        print("write ok")