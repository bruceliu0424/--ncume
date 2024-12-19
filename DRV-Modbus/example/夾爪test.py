import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
from robot import Robot
from pymodbus.client import ModbusTcpClient
import robot
import utils
import speech_recognition as sr

# 定義語音識別功能
def recognize_speech():
    recognizer = sr.Recognizer()
    mic_index = 1  # 替換為指定麥克風索引
    with sr.Microphone(device_index=mic_index) as source:
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

# 從位置移動並進行物品抓取和放置
def move_and_grab(robotDRV, from_position, to_position, parameters):
    try:
        # 1. 移動到起始位置
        workPosition = parameters[f"workPosition{from_position}"]  # 確保在parameters中定義好workPosition
        robotDRV.sendMotionCommand(position=workPosition, speed=80, acceleration=100, deceleration=100,
                                   robotCommand=robot.eRobotCommand.Robot_Go_MovP)

        # 等待直到機器人到達起始位置
        while not robotDRV.isRobotReachTargetPosition:
            time.sleep(0.1)

        # 2. 啟動夾爪以抓取物品
        robotDRV.setIO(int(0b01000000))  # 合閉夾爪 (抓取)
        print("夾爪合閉，正在抓取物品...")
        time.sleep(2)  # 維持抓取動作的時間

        # 3. 移動到目標位置
        workPosition = parameters[f"workPosition{to_position}"]  # 確保在parameters中定義好workPosition
        robotDRV.sendMotionCommand(position=workPosition, speed=120, acceleration=100, deceleration=100,
                                   robotCommand=robot.eRobotCommand.Robot_Go_MovP)

        # 等待直到機器人到達目標位置
        while not robotDRV.isRobotReachTargetPosition:
            time.sleep(0.1)

        # 4. 釋放物品
        robotDRV.setIO(int(0b10000000))  # 放開夾爪 (釋放)
        print("夾爪放開，物品已釋放...")
        time.sleep(2)  # 維持放開的時間
        robotDRV.setIO(0)  # 設定所有 bit 為 0，釋放夾爪
        print("物品已放下")

    except robot.RobotErrorException as e:
        print(e)

# 搜尋關鍵字並執行相應動作
def search_and_run_action(robotDRV, text, parameters):
    if "從" in text and "到" in text:
        # 擷取起始位置和目標位置的數字
        from_position = text.split("從")[-1].split("到")[0].strip()
        to_position = text.split("到")[-1].strip()

        # 檢查位置是否有效
        if from_position in ["1", "2", "3", "4"] and to_position in ["1", "2", "3", "4"]:
            move_and_grab(robotDRV, from_position, to_position, parameters)
        else:
            print("未識別到有效的起始位置或目標位置")
    elif "停止" in text:
        print("停止指令已接收，結束程序。")
        robotDRV.setIO(int(0b10000000))  # 放開夾爪 (釋放)
        time.sleep(2) 
        robotDRV.setIO(0)
        return True  # 返回 True 表示需要停止循環
    else:
        print("未找到匹配的指令")

# 主程式整合
if __name__ == "__main__":
    parameters = utils.readListFromCsv("examples/datas/parameters.csv")
    
    host = parameters["host"]
    port = parameters["port"]
    modbusTCPClient = ModbusTcpClient(host=host, port=port)
    
    defaultSpeed = int(parameters["defaultSpeed"])
    defaultAcceleration = int(parameters["defaultAcceleration"])
    defaultDeceleration = int(parameters["defaultDeceleration"])
    
    robotDRV = Robot(modbusTCPClient, defaultSpeed=defaultSpeed,
                     defaultAcceleration=defaultAcceleration,
                     defaultDeceleration=defaultDeceleration)

    if not robotDRV.prepareRobotForMotion():
        print(f"機器人無法進入準備狀態, error code:{robotDRV.getRobotNotReadyReason()}")
        exit()

    robotDRV.startMonitorErrors()  # 開始監測錯誤

    try:
        # 進入語音指令循環
        while True:
            print("準備偵測語音指令...")
            text = recognize_speech()
            
            # 如果有識別到語音，則根據指令執行對應動作
            if text:
                if search_and_run_action(robotDRV, text, parameters):
                    break  # 如果返回 True，則退出循環
            
            # 短暫等待，以避免快速重複檢測
            time.sleep(1)
        
    except robot.RobotErrorException as e:
        print(e)