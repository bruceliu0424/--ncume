import cv2
import numpy as np
import cv2.aruco as aruco

# 加载相机校准数据（如果需要的话）
# 参数为相机内参和畸变系数, 你可以加载你自己的相机标定文件
# 例如：camera_matrix, dist_coeffs = cv2. FileStorage("calibration.yaml", cv2.FILE_STORAGE_READ)

# 加载Aruco字典
aruco_dict = aruco.Dictionary(aruco.DICT_5X5_250)  # 5x5 Aruco字典
parameters = aruco.DetectorParameters_create()

# 使用相机（默认为第一个摄像头）
cap = cv2.VideoCapture(0)
while True:
    ret, frame = cap.read()
    if not ret:
        print("无法获取视频帧")
        break
    
    # 转换为灰度图像
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # 检测Aruco标记
    corners, ids, rejected_img_points = aruco.detectMarkers(gray, aruco_dict, parameters=parameters)

    if len(corners) > 0:
        # 绘制检测到的标记
        frame_markers = aruco.drawDetectedMarkers(frame.copy(), corners, ids)

        # 获取四个标记的角点
        for i in range(len(corners)):
            if ids[i] is not None:
                # 假设我们只关心找到的标记，找到角点后限制视窗
                pts = np.array(corners[i][0], dtype=np.int32)

                # 计算包围这些角点的矩形
                rect = cv2.boundingRect(pts)  # 返回 (x, y, w, h)
                
                # 在图像上绘制矩形
                cv2.rectangle(frame_markers, (rect[0], rect[1]), (rect[0] + rect[2], rect[1] + rect[3]), (0, 255, 0), 2)
                
                # 裁剪图像，得到视窗
                roi = frame[rect[1]:rect[1] + rect[3], rect[0]:rect[0] + rect[2]]

                # 显示裁剪后的区域
                cv2.imshow("ROI", roi)
    
    # 显示带有标记和矩形框的原始图像
    cv2.imshow("Frame", frame_markers)
    
    # 按下'q'退出
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 释放资源
cap.release()
cv2.destroyAllWindows()
