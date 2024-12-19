import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import threading
import time
import cv2
from pynput import keyboard
from robot.classRobot import Robot
from robot.enumRobotCommand import eRobotCommand
from pymodbus.client import ModbusTcpClient
import utils
from realsense import realsense

# 定義全局變數
isTabbed = False
R_TRIG_tab = utils.R_TRIG()
robotCommand: eRobotCommand = None
stop_event = threading.Event()  # 用於停止線程

# 機械手臂控制的線程
def sendMotionCommand(robotDRV: Robot, stop_event: threading.Event):
    while not stop_event.is_set():
        print(robotDRV.getTCPPose())
        if robotCommand is not None:
            robotDRV.sendMotionCommand(robotCommand=robotCommand)
        time.sleep(0.1)

# 鍵盤按下事件
def on_press(key):
    global isTabbed, robotCommand
    print(f"{key} pressed")
    try:
        if R_TRIG_tab(key == keyboard.Key.tab):
            isTabbed = not isTabbed
            print(f"isTabbed is {isTabbed}")
        if not isTabbed:
            if key == keyboard.Key.up:
                robotCommand = eRobotCommand.Continue_JOG_X_Negative
            elif key == keyboard.Key.down:
                robotCommand = eRobotCommand.Continue_JOG_X_Positive
            elif key == keyboard.Key.left:
                robotCommand = eRobotCommand.Continue_JOG_Y_Negative
            elif key == keyboard.Key.right:
                robotCommand = eRobotCommand.Continue_JOG_Y_Positive
            elif key == keyboard.Key.ctrl_l:
                robotCommand = eRobotCommand.Continue_JOG_Z_Negative
            elif key == keyboard.Key.shift_l:
                robotCommand = eRobotCommand.Continue_JOG_Z_Positive
        else:
            if key == keyboard.Key.up:
                robotCommand = eRobotCommand.Continue_JOG_RX_Negative
            elif key == keyboard.Key.down:
                robotCommand = eRobotCommand.Continue_JOG_RX_Positive
            elif key == keyboard.Key.left:
                robotCommand = eRobotCommand.Continue_JOG_RY_Negative
            elif key == keyboard.Key.right:
                robotCommand = eRobotCommand.Continue_JOG_RY_Positive
            elif key == keyboard.Key.ctrl_l:
                robotCommand = eRobotCommand.Continue_JOG_RZ_Negative
            elif key == keyboard.Key.shift_l:
                robotCommand = eRobotCommand.Continue_JOG_RZ_Positive
    except AttributeError:
        print(f"undefined {key} has been pressed")

# 鍵盤釋放事件
def on_release(key):
    global robotCommand
    print(f"{key} released")
    R_TRIG_tab(key == keyboard.Key.tab)
    robotCommand = eRobotCommand.Motion_Stop
    if key == keyboard.Key.esc:
        stop_event.set()
        return False

# RealSense 畫面顯示的線程
def show_camera():
    print("Starting RealSense camera...")
    while not stop_event.is_set():
        frame = realsense.Get_RGB_Frame()
        if frame is not None:
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            cv2.imshow("RealSense", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            stop_event.set()
            break
    cv2.destroyAllWindows()

if __name__ == "__main__":
    # 初始化機械手臂參數
    parameters = utils.readListFromCsv("examples/datas/parameters.csv")
    host = parameters["host"]
    port = parameters["port"]
    modbusTCPClient = ModbusTcpClient(host=host, port=port)
    defaultSpeed = int(parameters["defaultSpeed"])
    defaultAcceleration = int(parameters["defaultAcceleration"])
    defaultDeceleration = int(parameters["defaultDeceleration"])

    robotDRV = Robot(
        modbusTCPClient,
        defaultSpeed=defaultSpeed,
        defaultAcceleration=defaultAcceleration,
        defaultDeceleration=defaultDeceleration
    )

    if not robotDRV.prepareRobotForMotion():
        print("機械手臂無法進入準備狀態")
        exit()

    # 啟動機械手臂控制線程
    threading.Thread(target=sendMotionCommand, args=(robotDRV, stop_event)).start()

    # 啟動 RealSense 顯示線程
    threading.Thread(target=show_camera).start()

    # 啟動鍵盤監聽器
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()
