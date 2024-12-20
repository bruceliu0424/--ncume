from realsense import realsense
import cv2
from ultralytics import YOLO
import numpy as np
import os
from drv_modbus import send
from drv_modbus import request
from realsense import realsense
from pymodbus.client import ModbusTcpClient
import numpy as np
import cv2
import time
from ultralytics import YOLO
import pyrealsense2 as rs
import random
import torch
#from distance_detection import main1
# 相機內部參數
fx = 911.4920654296875  # 焦距 x，單位為像素
fy = 911.7120971679688  # 焦距 y，單位為像素
ppx = 638.875           # 影像中心 x，單位為像素
ppy = 364.4305725097656  # 影像中心 y，單位為像素

Nozzle = [335.816, 3.093, 661.793, 179.986, -0.209, -21.319]
home = [289.612, 3.093, 520.061, 179.986, -
        0.209, -103.270]  # 初始拍攝位置，要看到4個aruco
drop0 = [157.252, 343.368, 274.394, 179.986, -0.209, 88.962]  # 藍色茶包放置點
drop1 = [279.601, 343.368, 274.394, 179.986, -0.209, 88.962]  # 橘色茶包放置點
drop2 = [400.490, 343.368, 274.394, 179.986, -0.209, 88.962]  # 紫色茶包放置點
drop3 = [517.395, 343.368, 274.394, 179.986, -0.209, 88.962]  # 黃色茶包放置點
# 模型路徑
model = YOLO("C:/Users/User/OneDrive/桌面/Applications-of-Machine-Vision-and-Intelligent-Robot-main/train12/weights/best.pt")
c = ModbusTcpClient(host="192.168.1.1", port=502, unit_id=2)
c.connect()
# 創建照片儲存的資料夾
save_dir = 'captured_images'
os.makedirs(save_dir, exist_ok=True)
proceed = True
send.Go_Position(c, home[0], home[1], home[2], home[3], home[4], home[5], 100)

distance = 43.3
z_camera = distance/10  # 實際距離，單位為 cm
print("目前偵測距離為:", distance)
grab = home[2] - distance + 43
print(grab)
if grab < 125 or grab > 130:
    grab = 125
    distance = 440
print("預估要抵達的z軸深度為:", grab, "cm")
def Suction_Behave(color, x_camera, y_camera):

    send.Go_Position(c, Nozzle[0]+y_camera*10, Nozzle[1]+x_camera*10 + 12*(grab-127) /
                     200 +25, grab, Nozzle[3], Nozzle[4], Nozzle[5], 100)  # 顯示結果 架高平台要大於325會比較好 目前固定328
    send.Suction_ON(c)  # 吸目標"顏色"茶包
    # print("類別：", color,",信心值:",confident) #(0：藍色；1：橘色；2：紫色；3：黃色)
    send.Go_Position(c, Nozzle[0]+y_camera*10, Nozzle[1]+x_camera*10 + 12*(grab-127)/200+20,
                     drop0[2], Nozzle[3], Nozzle[4], Nozzle[5], 100)  # 顯示結果 架高平台要大於325會比較好 目前固定328
    
    if color == 'blue_Tea_bag':
       # send.Go_Position(c, x_center, y_center, drop0[2], home[3], home[4], home[5], 100) #拉高，回目標"藍色"茶包上方（避免撞到）
        send.Go_Position(c, drop0[0], drop0[1], drop0[2],
                         drop0[3], drop0[4], drop0[5], 100)  # 到要丟的位置
        send.Suction_OFF(c)  # 關吸嘴

    elif color == 'orange_Tea_bag':
        # send.Go_Position(c, x_center, y_center, drop1[2], home[3], home[4], home[5], 100) #拉高，回目標"橘色"茶包上方（避免撞到）
        send.Go_Position(c, drop1[0], drop1[1], drop1[2],
                         drop1[3], drop1[4], drop1[5], 100)  # 到要丟的位置
        send.Suction_OFF(c)  # 關吸嘴

    elif color == 'purple_Tea_bag':
        # send.Go_Position(c, x_center, y_center, drop2[2], home[3], home[4], home[5], 100) #拉高，回目標"紫色"茶包上方（避免撞到）
        send.Go_Position(c, drop2[0], drop2[1], drop2[2],
                         drop2[3], drop2[4], drop2[5], 100)  # 到要丟的位置
        send.Suction_OFF(c)  # 關吸嘴

    elif color == 'yellow_Tea_bag':
        # send.Go_Position(c, x_center, y_center, drop3[2], home[3], home[4], home[5], 100) #拉高，回目標"黃色"茶包上方（避免撞到）
        send.Go_Position(c, drop3[0], drop3[1], drop3[2],
                         drop3[3], drop3[4], drop3[5], 100)  # 到要丟的位置
        send.Suction_OFF(c)  # 關吸嘴
    send.Go_Position(c, home[0], home[1], home[2],
                     home[3], home[4], home[5], 100)  # 完成動作後回原位


while proceed:
    send.Go_Position(c, home[0], home[1], home[2],
                     home[3], home[4], home[5], 100)

    # 回傳的距離d要減掉35~37 要注意平台的最低位置不要低於123
    # 拍攝一張照片

    frame = realsense.Get_RGB_Frame()

    # 獲取影像的高度和寬度
    height, width, _ = frame.shape

    # 將影像從 RGB 轉為 BGR，因為 OpenCV 使用 BGR 格式
    frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

    # 使用 YOLO 模型進行物體檢測
    results = model.predict(source=frame_bgr, save=True, conf=0.1)

    # 獲取檢測結果
    detections = results[0].boxes  # 轉換為 NumPy 格式 (xyxy 表示物體框的左上角和右下角的座標)
    detections = [det for det in detections if det.conf[0].item() >= 0.30]

    # 按信心值排序
    detections = sorted(detections, key=lambda x: x.conf[0], reverse=True)

    # 類別
    class_names = results[0].names
    teabag = len(results[0].boxes[0:])
    # 儲存拍攝的照片
    timestamp = int(cv2.getTickCount())
    filename = os.path.join(save_dir, f'image_{timestamp}.jpg')
    cv2.imwrite(filename, frame_bgr)
    print("目前還剩下多少茶包: ", teabag)
    print("類別 ", class_names)

    print(f'Photo saved as {filename}')
    if teabag == 0:
        print("job done")
        break
    # 依照信心值順序處理每個檢測結果
    for det in detections:
        # 取出檢測框的坐標和信心值
        x1, y1, x2, y2 = det.xyxy[0].tolist()
        conf = det.conf[0].item()
        cls = int(det.cls[0].item())
        label = f'{class_names[cls]} {conf:.2f}'
        color, confident = label.split()

        # 計算中心座標
        center_x_pixel = (x1 + x2) / 2
        center_y_pixel = (y1 + y2) / 2

        # 計算實際座標
        x_camera = (center_x_pixel - ppx) * z_camera / fx
        y_camera = (center_y_pixel - ppy) * z_camera / fy
        z_camera = z_camera  # 目標到相機的距離

        # 在照片上繪製邊界框和中心座標
        cv2.rectangle(frame_bgr, (int(x1), int(y1)),
                      (int(x2), int(y2)), (0, 255, 0), 2)
        cv2.putText(frame_bgr, label, (int(x1), int(y1) - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        cv2.putText(frame_bgr, f'Center: ({x_camera:.2f} cm, {y_camera:.2f} cm, {z_camera:.2f} cm)', (int(
            x1), int(y1) - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

        # 在螢幕上印出中心座標
        print(
            f'Detected object: {label}, Center: ({x_camera:.2f} cm, {y_camera:.2f} cm, {z_camera:.2f} cm)')
        cv2.imshow("Detection Result", frame_bgr)
        key = cv2.waitKey(3000)
        cv2.destroyAllWindows()
        if key == ord('q'):
            print("重新拍攝照片...")
            break  # 跳出內部迴圈，重新拍照
        else:
            Suction_Behave(color, x_camera, y_camera)
            break  # 處理完這個物件後退出內部迴圈
        break
    # cv2.imshow("Detection Result", frame_bgr)

    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
