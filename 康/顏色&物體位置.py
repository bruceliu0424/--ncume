import cv2
import numpy as np
from pyModbusTCP.client import ModbusClient
lowerR = np.array([130, 210, 40])  # 轉換成 NumPy 陣列，範圍稍微變小 ( 55->30, 70->40, 252->200 )
upperR = np.array([150, 230, 60])  # 轉換成 NumPy 陣列，範圍稍微加大 ( 70->90, 80->100, 252->255 )

lowerB = np.array([130, 210, 40])  # 轉換成 NumPy 陣列，範圍稍微變小 ( 55->30, 70->40, 252->200 )
upperB = np.array([150, 230, 60])  # 轉換成 NumPy 陣列，範圍稍微加大 ( 70->90, 80->100, 252->255 )

video = cv2.VideoCapture(0)
A = []
B = []
while(1):
    ret,frame = video.read()
    if ret == False:
        continue
    imgray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    ret,thresh = cv2.threshold(imgray,150,255,0)
    contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    for i in contours:
        if np.shape(i)[0]>100:
            area = cv2.contourArea(i)
            if area <= 10000:
                frame = cv2.drawContours(frame, i, -1, (0, 255, 0), 3)
                M = cv2.moments(i)
                cx = int(M['m10'] / M['m00'])
                cy = int(M['m01'] / M['m00'])
                cv2.circle(frame,(cx,cy),7,(255,0,0),-1)
                cx=221.3-cx*300/1920
                cy=302.22-cy*210/1080
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


while(0):
    ret,frame = video.read()


    if ret == False:
        continue
    imgray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    ret,thresh = cv2.threshold(imgray,150,255,0)
    contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    for i in contours:
        if np.shape(i)[0]>100:
            area = cv2.contourArea(i)
            if area <= 10000:
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
        mask2 = cv2.inRange(frame, (100, 0, 0), (255, 100, 100))
        c = ModbusClient(host="192.168.1.1", port=502, unit_id=2, auto_open=True)
        cv2.imshow('output', mask2)
        cv2.waitKey(1)
        break

if c.write_multiple_registers(5000,[(int(num/2))]):
    print("write ok")
for i in range(num):
    if c.write_multiple_registers(5200+i, [int(A[i])]):
        print("write ok")
