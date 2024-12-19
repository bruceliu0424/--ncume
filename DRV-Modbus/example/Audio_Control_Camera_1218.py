import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import time
import cv2
import numpy as np
import pyrealsense2 as rs
from robot import Robot
from pymodbus.client import ModbusTcpClient
import speech_recognition as sr
import utils
from realsense import realsense
from landmark import aruco
from drv_modbus import send
from drv_modbus import request

# 初始化機械手臂參數
home = [379.870, -2.034, 680.0, 179.987, -0.004, -106.121]
drop = [466.225, -2.033, 360.695, 179.987, -0.004, 13.131]
z_height = 346.40000000000003

# 初始化 RealSense 相機
pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
pipeline.start(config)

# 初始化機械手臂
c = ModbusTcpClient(host="192.168.1.1", port=502)
c.connect()

# 語音指令功能
def recognize_speech():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("請說話...")
        audio = recognizer.listen(source)
    try:
        text = recognizer.recognize_google(audio, language="zh-TW")
        print(f"你說的是: {text}")
        return text
    except sr.UnknownValueError:
        print("無法識別語音")
        return None
    except sr.RequestError:
        print("無法連接到語音服務")
        return None

# 讀取照片並進行目標匹配
def detect_object_by_features(target_image_path, gray_image):
    target_image = cv2.imread(target_image_path, cv2.IMREAD_GRAYSCALE)
    if target_image is None:
        print("目標圖像加載失敗")
        return None, None

    # 使用 ORB 檢測和匹配特徵
    orb = cv2.ORB_create()
    kp1, des1 = orb.detectAndCompute(target_image, None)
    kp2, des2 = orb.detectAndCompute(gray_image, None)
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = bf.match(des1, des2)
    matches = sorted(matches, key=lambda x: x.distance)

    # 如果匹配數量足夠多，計算物品中心並返回
    if len(matches) > 10:
        src_pts = np.float32([kp1[m.queryIdx].pt for m in matches]).reshape(-1, 1, 2)
        dst_pts = np.float32([kp2[m.trainIdx].pt for m in matches]).reshape(-1, 1, 2)
        center_x = int(np.mean([p[0][0] for p in dst_pts]))
        center_y = int(np.mean([p[0][1] for p in dst_pts]))

        # 繪製匹配到的特徵點
        matched_image = cv2.drawMatches(target_image, kp1, gray_image, kp2, matches[:20], None, flags=2)
        cv2.imshow("Matches", matched_image)

        return (center_x, center_y), kp2
    else:
        print("匹配失敗或特徵點不足")
        return None, None
    

# 機械手臂移動與吸附
def move_and_pick_target(x, y):
    send.Go_Position(c, x, y, home[2], home[3], home[4], home[5], speed=50)
    send.Go_Position(c, x, y, z_height, home[3], home[4], home[5], speed=50)
    send.Suction_ON(c)
    time.sleep(2)
    send.Go_Position(c, x, y, home[2], home[3], home[4], home[5], speed=50)
    send.Go_Position(c, drop[0], drop[1], drop[2], home[3], home[4], home[5], speed=50)
    send.Suction_OFF(c)
    send.Go_Position(c, home[0], home[1], home[2], home[3], home[4], home[5], speed=50)
    print("吸附完成")

# 在主迴圈中加入框選目標的邏輯
if __name__ == "__main__":
    base_path = r"C:\Users\Bruce\OneDrive\Desktop\DRV-Modbus-main\examples"
    while True:
        try:
            # 語音指令選擇目標
            text = recognize_speech()
            if not text:
                continue

            if "橡皮擦" in text:
                target_name = "橡皮擦"
                target_image_path = os.path.join(base_path, "images", "eraser.jpg")
            elif "硬幣" in text:
                target_name = "硬幣"
                target_image_path = os.path.join(base_path, "images", "coin.jpg")
            else:
                print("未識別的目標物品")
                continue

            # 獲取相機畫面
            frames = pipeline.wait_for_frames()
            color_frame = frames.get_color_frame()
            if not color_frame:
                print("無法獲取相機畫面")
                continue
            color_image = np.asanyarray(color_frame.get_data())

            # 將彩色影像轉換為灰階影像
            gray_image = cv2.cvtColor(color_image, cv2.COLOR_BGR2GRAY)

            # 目標物品匹配與吸附
            position, keypoints = detect_object_by_features(target_image_path, gray_image)
            if position:
                x, y = position
                print(f"{target_name} 位置: {x}, {y}")

                # 在彩色影像上框選目標
                annotated_image = color_image.copy()
                cv2.circle(annotated_image, (x, y), 10, (0, 255, 0), 2)
                cv2.putText(annotated_image, target_name, (x - 50, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                # 顯示彩色影像
                cv2.imshow("Detected Object", annotated_image)
                cv2.waitKey(1)

                # 執行吸附動作
                move_and_pick_target(x, y)
            else:
                print(f"無法找到 {target_name}")
                # 顯示灰階影像以供調試
                cv2.imshow("Camera View - Grayscale", gray_image)
                cv2.waitKey(1)
        except KeyboardInterrupt:
            print("程式結束")
            break
        except Exception as e:
            print(f"發生錯誤: {e}")
