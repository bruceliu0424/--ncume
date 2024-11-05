import cv2
import mediapipe as mp
import math
import time

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands

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
    if f1<50 and f2>=50 and f3>=50 and f4>=50 and f5>=50:
        return 'good'
    elif f1>=50 and f2>=50 and f3<50 and f4>=50 and f5>=50:
        return 'no!!!'
    elif f1>=50 and f2>=50 and f3<50 and f4<50 and f5<50:
        return 'ok'
    elif f1>=50 and f2>=50 and f3>=50 and f4>=50 and f5>=50:
        return '0'
    elif f1>=50 and f2<50 and f3>=50 and f4>=50 and f5>=50:
        return '1'
    elif f1>=50 and f2<50 and f3<50 and f4>=50 and f5>=50:
        return '2'
    elif f1>=50 and f2<50 and f3<50 and f4<50 and f5>50:
        return '3'
    elif f1>=50 and f2<50 and f3<50 and f4<50 and f5<50:
        return '4'
    elif f1<50 and f2<50 and f3<50 and f4<50 and f5<50:
        return '5'
    elif f1<50 and f2>=50 and f3>=50 and f4>=50 and f5<50:
        return '6'
    elif f1<50 and f2<50 and f3>=50 and f4>=50 and f5>=50:
        return '7'
    elif f1<50 and f2<50 and f3<50 and f4>=50 and f5>=50:
        return '8'
    elif f1<50 and f2<50 and f3<50 and f4<50 and f5>=50:
        return '9'
    else:
        return ''
    

prev_time = time.time()
dx_sum=0
dy_sum = 0

# 跟踪前一帧的手部關節座標
prev_hand_landmarks = None

cap = cv2.VideoCapture(0)            # 讀取攝影機
fontFace = cv2.FONT_HERSHEY_SIMPLEX  # 印出文字的字型
lineType = cv2.LINE_AA               # 印出文字的邊框

# mediapipe 啟用偵測手掌
with mp_hands.Hands(
    model_complexity=0,
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
            for hand_landmarks in results.multi_hand_landmarks:
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
                    text = hand_pos(finger_angle)            # 取得手勢所回傳的內容
                    #cv2.putText(img, text, (360,100), fontFace,  2, (0,0,0), 5, lineType) # 印出文字
                                        
                                        
                                        
                                        
                # 畫出手部關節連線
                mp_drawing.draw_landmarks(
                    img, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                # 如果有前一帧的手部關節座標，計算移動向量
                if prev_hand_landmarks:
                    for prev_point, curr_point in zip(prev_hand_landmarks.landmark, hand_landmarks.landmark):
                        # 計算移動向量
                        dx = curr_point.x - prev_point.x
                        dy = curr_point.y - prev_point.y
                        
                        dx_sum += dx
                        dy_sum += dy

                        # 在圖像中畫出移動向量
                        cv2.arrowedLine(img, 
                            (int(prev_point.x * img.shape[1]), int(prev_point.y * img.shape[0])),
                            (int(curr_point.x * img.shape[1]), int(curr_point.y * img.shape[0])),
                            (0, 255, 0), 2)
       
                # 更新前一帧的手部關節座標
                prev_hand_landmarks = hand_landmarks

        
        curr_time = time.time()
        if curr_time - prev_time > 0.01 :

            if dx_sum > 0.5:
                cv2.putText(img, "Left", (180,100), fontFace, 2, (0,0,0), 5, lineType)
            
            if dx_sum < -0.5:
                cv2.putText(img, "Right", (180,100), fontFace, 2, (0,0,0), 5, lineType)

            if dy_sum > 0.5:
                cv2.putText(img, "Down", (180,100), fontFace, 2, (0,0,0), 5, lineType)
            
            if dy_sum < -0.5:
                cv2.putText(img, "Up", (180,100), fontFace, 2, (0,0,0), 5, lineType)

            prev_time = curr_time
            dx_sum = 0 
            dy_sum = 0                                        
                                        
                                        
        cv2.imshow('oxxostudio', img)
        if cv2.waitKey(5) == ord('q'):
            break
cap.release()
cv2.destroyAllWindows() 