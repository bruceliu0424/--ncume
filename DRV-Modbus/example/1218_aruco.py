import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import cv2
import numpy as np
import cv2.aruco as aruco
import realsense
# 重新排序四個角點座標 (左上、右上、左下、右下)

def sort_corners(c_center_list):
    c_center_list = np.array(c_center_list)
    sorted_sum = c_center_list[np.argsort(c_center_list.sum(axis=1))]
    sorted_diff = c_center_list[np.argsort(np.diff(c_center_list, axis=1).flatten())]
    return np.array([sorted_sum[0], sorted_diff[-1], sorted_diff[0], sorted_sum[-1]])

def Warp(frame, c_center_list, width, height):
    p1 = np.float32(sort_corners(c_center_list))
    p2 = np.float32([[0, 0], [width, 0], [0, height], [width, height]])
    m = cv2.getPerspectiveTransform(p1, p2)
    output = cv2.warpPerspective(frame, m, (width, height))
    return output, m

def detect_aruco_and_correct(frame, real_width, real_height):
    if frame is None:
        raise ValueError("frame為空")
        
    aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_5X5_250)
    parameters = cv2.aruco.DetectorParameters()
    detector = cv2.aruco.ArucoDetector(aruco_dict, parameters)
    corners, ids, _ = detector.detectMarkers(frame)

    if ids is not None and len(ids) >= 4:  # 偵測到至少 4 個 ArUco 標記
        c_center_list = []
        for i, corner in enumerate(corners):
            center_x = int(np.mean(corner[0][:, 0]))
            center_y = int(np.mean(corner[0][:, 1]))
            c_center_list.append([center_x, center_y])
            cv2.circle(frame, (center_x, center_y), 5, (0, 0, 255), -1)
            cv2.putText(frame, f"ID: {ids[i][0]}", (center_x - 20, center_y - 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

        if len(c_center_list) == 4:  # 當有四個標記時，執行影像校正
            output, m = Warp(frame, c_center_list, int(real_width), int(real_height))
            return output, frame
    return None, frame

while __name__ == "__main__":
    # 加載影像

    while True:
        frame = realsense.Get_RGB_Frame()

        _, frame = detect_aruco_and_correct(frame,350,300)
        cv2.imshow("Detected Markers", frame)
        cv2.imshow("_", _)
        cv2.waitKey(10)