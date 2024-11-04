import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
from robot import Robot
from pymodbus.client import ModbusTcpClient
import robot
import utils


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

    ret = robotDRV.prepareRobotForMotion()
    if not ret:
        print(f"機器人無法進入準備狀態, error code:{robotDRV.getRobotNotReadyReason()}")
        exit()
        
    robotDRV.startMonitorErrors()  # 開始監測錯誤

    try:
        # 移動到 workPosition4
        workPosition4 = parameters["workPosition4"]  # 從 CSV 讀取 workPosition4
        robotDRV.sendMotionCommand(position=workPosition4, speed=80, acceleration=100, deceleration=100,
                                   robotCommand=robot.eRobotCommand.Robot_Go_MovP)

        while not robotDRV.isRobotReachTargetPosition:
            time.sleep(0.1)

        # 夾取物品
        robotDRV.suctionON()
        time.sleep(2)  # 等待吸盤完全啟動
        robotDRV.suctionOFF()
        time.sleep(2)  # 等待吸盤關閉

        # 移動到 workPosition3
        workPosition3 = parameters["workPosition3"]  # 從 CSV 讀取 workPosition3
        robotDRV.sendMotionCommand(position=workPosition3, speed=80, acceleration=100, deceleration=100,
                                   robotCommand=robot.eRobotCommand.Robot_Go_MovP)

        while not robotDRV.isRobotReachTargetPosition:
            time.sleep(0.1)

        # 在 workPosition3 進行後續操作，如釋放物品
        robotDRV.suctionON()  # 再次啟動吸盤以夾取物品
        time.sleep(2)
        robotDRV.suctionOFF()  # 釋放物品
        time.sleep(2)

        # 控制 IO，根據需要
        robotDRV.setIO(int(0b10010101))  # 設定 IO
        time.sleep(2)
        robotDRV.setIO(10, True)          # 設定特定位
        time.sleep(2)
        robotDRV.setIO(10, False)         # 清除特定位
        time.sleep(2)
        robotDRV.setIO(0)                 # 清除所有位

    except robot.RobotErrorException as e:
        print(e)