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

# 初始化 RealSense 相機
pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
pipeline.start(config)

# 初始化機械手臂參數
parameters = utils.readListFromCsv("examples/datas/parameters.csv")
robotDRV = Robot(
    ModbusTcpClient(host=parameters["host"], port=parameters["port"]),
    defaultSpeed=int(parameters["defaultSpeed"]),
    defaultAcceleration=int(parameters["defaultAcceleration"]),
    defaultDeceleration=int(parameters["defaultDeceleration"]),
)

# 定義語音識別功能
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

# 定義物品識別功能
def detect_object(target_name):
    frame = pipeline.wait_for_frames()
    color_frame = frame.get_color_frame()
    if not color_frame:
        return None
    color_image = np.asanyarray(color_frame.get_data())
    # 使用 OpenCV 進行物品識別
    hsv = cv2.cvtColor(color_image, cv2.COLOR_BGR2HSV)
    if target_name == "橡皮擦":
        lower_bound = np.array([0, 50, 50])  # 假設橡皮擦顏色範圍
        upper_bound = np.array([10, 255, 255])
    elif target_name == "硬幣":
        lower_bound = np.array([20, 100, 100])  # 假設硬幣顏色範圍
        upper_bound = np.array([30, 255, 255])
    else:
        return None

    mask = cv2.inRange(hsv, lower_bound, upper_bound)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        largest_contour = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(largest_contour)
        cv2.rectangle(color_image, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.imshow("Detected Object", color_image)
        cv2.waitKey(1)
        return (x + w // 2, y + h // 2)  # 返回物品中心點位置
    return None

# 主程式
if __name__ == "__main__":
    try:
        # 初始化機械手臂
        if not robotDRV.prepareRobotForMotion():
            print(f"機械手臂無法準備: {robotDRV.getRobotNotReadyReason()}")
            exit()
        robotDRV.startMonitorErrors()

        while True:
            # 語音指令接收
            text = recognize_speech()
            if text:
                if "橡皮擦" in text:
                    target_name = "橡皮擦"
                elif "硬幣" in text:
                    target_name = "硬幣"
                else:
                    print("未識別的目標物品")
                    continue

                # 物品定位
                position = detect_object(target_name)
                if position:
                    x, y = position
                    print(f"{target_name} 位置: {x}, {y}")
                    
                    # 控制機械手臂抓取
                    robotDRV.moveToPosition(x, y)  # 假設有方法將位置轉換為機械手臂指令
                    robotDRV.suctionON()  # 啟動吸盤
                    time.sleep(2)
                    robotDRV.suctionOFF()
                    print(f"{target_name} 已抓取完成")
                else:
                    print(f"無法找到 {target_name}")
            time.sleep(1)
    except Exception as e:
        print(f"發生錯誤: {e}")
    finally:
        pipeline.stop()
        cv2.destroyAllWindows()
