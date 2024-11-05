from pyModbusTCP.client import ModbusClient
import cv2
import numpy as np
import mediapipe as mp
import math
import time
from collections import Counter

# 根據兩點的座標，計算角度
def vector_2d_angle(v1, v2):
    v1_x = v1[0]
    v1_y = v1[1]
    v2_x = v2[0]
    v2_y = v2[1]
    try:
        angle_= math.degrees(math.acos((v1_x*v2_x+v1_y*v2_y)/(((v1_x**2+v1_y**2)**0.5)*((v2_x**2+v2_y**2)**0.5))))
    except:
        angle_ = 180
    return angle_

# 根據傳入的 21 個節點座標，得到該手指的角度
def hand_angle(hand_):
    angle_list = []
    # thumb 大拇指角度
    angle_ = vector_2d_angle(
        ((int(hand_[0][0])- int(hand_[2][0])),(int(hand_[0][1])-int(hand_[2][1]))),
        ((int(hand_[3][0])- int(hand_[4][0])),(int(hand_[3][1])- int(hand_[4][1])))
        )
    angle_list.append(angle_)
    # index 食指角度
    angle_ = vector_2d_angle(
        ((int(hand_[0][0])-int(hand_[6][0])),(int(hand_[0][1])- int(hand_[6][1]))),
        ((int(hand_[7][0])- int(hand_[8][0])),(int(hand_[7][1])- int(hand_[8][1])))
        )
    angle_list.append(angle_)
    # middle 中指角度
    angle_ = vector_2d_angle(
        ((int(hand_[0][0])- int(hand_[10][0])),(int(hand_[0][1])- int(hand_[10][1]))),
        ((int(hand_[11][0])- int(hand_[12][0])),(int(hand_[11][1])- int(hand_[12][1])))
        )
    angle_list.append(angle_)
    # ring 無名指角度
    angle_ = vector_2d_angle(
        ((int(hand_[0][0])- int(hand_[14][0])),(int(hand_[0][1])- int(hand_[14][1]))),
        ((int(hand_[15][0])- int(hand_[16][0])),(int(hand_[15][1])- int(hand_[16][1])))
        )
    angle_list.append(angle_)
    # pink 小拇指角度
    angle_ = vector_2d_angle(
        ((int(hand_[0][0])- int(hand_[18][0])),(int(hand_[0][1])- int(hand_[18][1]))),
        ((int(hand_[19][0])- int(hand_[20][0])),(int(hand_[19][1])- int(hand_[20][1])))
        )
    angle_list.append(angle_)
    return angle_list
    # 根據手指角度的串列內容，返回對應的手勢名稱

def hand_pos(finger_angle):
    f1 = finger_angle[0]   # 大拇指角度
    f2 = finger_angle[1]   # 食指角度
    f3 = finger_angle[2]   # 中指角度
    f4 = finger_angle[3]   # 無名指角度
    f5 = finger_angle[4]   # 小拇指角度
    # 小於 50 表示手指伸直，大於等於 50 表示手指捲縮
    if f1>=50 and f2>=50 and f3<50 and f4<50 and f5<50:
        return 100
    elif f1>=50 and f2>=50 and f3>=50 and f4>=50 and f5>=50:
        return 99
    elif f1>=50 and f2<50 and f3>=50 and f4>=50 and f5>=50:
        return 1
    elif f1>=50 and f2<50 and f3<50 and f4>=50 and f5>=50:
        return 2
    elif f1>=50 and f2<50 and f3<50 and f4<50 and f5>50:
        return 3
    elif f1>=50 and f2<50 and f3<50 and f4<50 and f5<50:
        return 4
    elif f1<50 and f2<50 and f3<50 and f4<50 and f5<50:
        return 5
    elif f1<50 and f2>=50 and f3>=50 and f4>=50 and f5<50:
        return 6
    elif f1<50 and f2<50 and f3>=50 and f4>=50 and f5>=50:
        return 7
    elif f1<50 and f2<50 and f3<50 and f4>=50 and f5>=50:
        return 8
    elif f1<50 and f2<50 and f3<50 and f4<50 and f5>=50:
        return 9

def hand_move(dx_sum,dy_sum):
    displacement = 0.1
    if dx_sum > displacement:
            return 4
    elif dx_sum < -displacement:
            return 3
    elif dy_sum > displacement:
            return 2
    elif dy_sum < -displacement:
            return 1

def most_common_elements(lst):
    elements_to_remove = {'', None}
    lst = list(filter(lambda x: x not in elements_to_remove, lst))
    count = Counter(lst)
    if not count:
        return []
    max_count = max(count.values())
    most_common = [elem for elem, cnt in count.items() if cnt == max_count]
    return most_common[0]


command = []
operate_times = 3

for z in range(operate_times):
    mp_drawing = mp.solutions.drawing_utils
    mp_drawing_styles = mp.solutions.drawing_styles
    mp_hands = mp.solutions.hands
    
    
    prev_time = time.time()
    dx_sum = 0
    dy_sum = 0

    # 跟踪前一帧的手部關節座標
    prev_hand_landmarks = None

    cap = cv2.VideoCapture(0)            # 讀取攝影機
    fontFace = cv2.FONT_HERSHEY_SIMPLEX  # 印出文字的字型
    lineType = cv2.LINE_AA               # 印出文字的邊框

    dominant_hand = 'Right'

    video = cv2.VideoCapture(0)
    A = []
    B = []

    with mp_hands.Hands(
        model_complexity=0,
        static_image_mode=False, 
        max_num_hands=2,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5) as hands:

        if not cap.isOpened():
            print("Cannot open camera")
            exit()
        w, h = 540, 310                                  # 影像尺寸
        while True:
            ret, img = cap.read()
            img = cv2.resize(img, (w,h))                 # 縮小尺寸，加快處理效率
            if not ret:
                print("Cannot receive frame")
                break
            # 轉換顏色空間，從BGR到RGB
            frame_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

            # 檢測手部姿勢
            results = hands.process(frame_rgb) 

            # 偵測手勢
            if results.multi_hand_landmarks:
                curr_time = time.time()
                for idx,hand_landmarks in enumerate(results.multi_hand_landmarks):

                    hand_label = results.multi_handedness[idx].classification[0].label

                    if hand_label == 'Left':
                        hand_color = (255, 0, 0)  # 左手藍色
                    else:
                        hand_color = (0, 0, 255)  # 右手紅色


                    finger_points = []                   # 記錄手指節點座標的串列
                    for i in hand_landmarks.landmark:
                        # 將 21 個節點換算成座標，記錄到 finger_points
                        x = int(i.x*w)
                        y = int(i.y*h)
                        finger_points.append((x,y))
                        # 繪製手指節點
                        cv2.circle(img, (x, y), 5, (0, 255, 0), -1)
                    if finger_points:
                        finger_angle = hand_angle(finger_points) # 計算手指角度，回傳長度為 5 的串列
                        #print(finger_angle)                     # 印出角度 ( 有需要就開啟註解 )
                        text = hand_pos(finger_angle)  if hand_label != dominant_hand else ''          # 取得手勢所回傳的內容

                        A.append(text)

                        #cv2.putText(img, text, (360,100), fontFace,  2, (0,0,0), 5, lineType) # 印出文字

                    # 畫出手部關節連線
                    mp_drawing.draw_landmarks(
                    img, hand_landmarks, mp_hands.HAND_CONNECTIONS,
                    mp_drawing.DrawingSpec(color=hand_color, thickness=2, circle_radius=4),
                    mp_drawing.DrawingSpec(color=hand_color, thickness=2))

                    # 如果有前一帧的手部關節座標，計算移動向量
                    if prev_hand_landmarks:

                        for prev_point, curr_point in zip(prev_hand_landmarks.landmark, hand_landmarks.landmark):
                            # 計算移動向量
                            dx_sum += curr_point.x - prev_point.x
                            dy_sum += curr_point.y - prev_point.y

                    # 更新前一帧的手部關節座標
                    prev_hand_landmarks = hand_landmarks


                    if curr_time - prev_time > 0.01 :
                    
                        movement = hand_move(dx_sum, dy_sum) if hand_label == dominant_hand else ''

                        B.append(movement)

                        #cv2.putText(img, movement , (180,100), fontFace, 2, (0,0,0), 5, lineType)

                        prev_time = curr_time
                        dx_sum = 0 
                        dy_sum = 0  


            cv2.imshow('oxxostudio', img)
            if cv2.waitKey(5) == ord(' '):
                break

    cap.release()
    cv2.destroyAllWindows()

    order = []
    order.append(most_common_elements(B))
    order.append(most_common_elements(A))

    if order[1] == 99 or order[1] == 100:
        order[0] = 5

    for i in range(len(order)):
        command.append(order[i])

    print(order)
    
    
unit = [[x, x] for x in command]
print(unit)

c = ModbusClient(host="192.168.1.1", port=502, unit_id=2, auto_open=True)


for i in range(len(unit)):
    if c.write_multiple_registers(5201 + i, unit[i]):
        print("write ok")