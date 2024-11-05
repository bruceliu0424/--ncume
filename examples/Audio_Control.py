import sys
import os
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

# 搜尋關鍵字並執行相應動作
def search_and_run_action(robotDRV, text, keywords):
    for keyword in keywords:
        if keyword in text:
            print(f"找到關鍵字: {keyword}")
            if keyword == "抓取物品":
                # 執行抓取物品動作
                robotDRV.suctionON()
                time.sleep(2)
                robotDRV.suctionOFF()
                print("完成抓取動作")
            elif keyword == "移動到下一點位":
                # 執行移動到下一個點位
                workPosition3 = parameters["workPosition3"]
                robotDRV.sendMotionCommand(position=workPosition3, speed=80, acceleration=100, deceleration=100,
                                           robotCommand=robot.eRobotCommand.Robot_Go_MovP)
                print("移動到下一點位")
            return
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
        # 1. 移動到第一個位置（例如 workPosition1）
        workPosition1 = parameters["workPosition1"]
        robotDRV.sendMotionCommand(position=workPosition1, speed=80, acceleration=100, deceleration=100,
                                   robotCommand=robot.eRobotCommand.Robot_Go_MovP)
        
        while not robotDRV.isRobotReachTargetPosition:
            time.sleep(0.1)

        # 2. 語音指令偵測並執行
        keywords = ["抓取物品", "移動到下一點位"]  # 可根據需求調整的關鍵字列表
        print("已到達點位，準備偵測語音指令...")
        text = recognize_speech()
        
        # 3. 如果有識別到語音，則根據指令執行對應動作
        if text:
            search_and_run_action(robotDRV, text, keywords)
        
    except robot.RobotErrorException as e:
        print(e)
