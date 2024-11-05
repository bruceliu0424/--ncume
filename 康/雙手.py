import cv2
import mediapipe as mp

# 初始化 Mediapipe Hands 模型
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

# 開啟攝影機
cap = cv2.VideoCapture(0)

with mp_hands.Hands(static_image_mode=False, max_num_hands=2, min_detection_confidence=0.7) as hands:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # 將影像轉換為 RGB 格式
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # 使用 Mediapipe 進行手部姿勢辨識
        results = hands.process(image_rgb)

        # 繪製手部關鍵點及連線
        if results.multi_hand_landmarks:
            for idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
                # 判斷手的位置，左手 or 右手
                hand_label = results.multi_handedness[idx].classification[0].label
                if hand_label == 'Left':
                    hand_color = (255, 0, 0)  # 左手藍色
                else:
                    hand_color = (0, 0, 255)  # 右手紅色

                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS, 
                                          mp_drawing.DrawingSpec(color=hand_color, thickness=2, circle_radius=4),
                                          mp_drawing.DrawingSpec(color=hand_color, thickness=2))

        # 顯示結果
        cv2.imshow('Hand Pose Detection', frame)

        # 若按下 q 鍵則離開迴圈
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

# 釋放資源
cap.release()
cv2.destroyAllWindows()
