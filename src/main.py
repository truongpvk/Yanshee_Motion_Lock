import time
import cv2
import numpy as np
import queue

import angle_processing as angle
import distance_processing as dpr
import offset_processing as offset
import motion_processing as motion

robot_api = '10.220.5.226'
url = f'http://{robot_api}:8000/stream.mjpg'

#Biến thời gian
last_time = time.time()
pause_time = 5

#Góc nguyên bản
origin_z = 0.0
#Kiểm tra xem đã lấy góc chưa
isGetAngle = False

#Kiểm tra có phát hiện vật thể không:
notFoundObject = 0

#Kiểm tra có đang dừng lại không
isStop = False

def measure_offset(frame):
    global isGetAngle
    global origin_z
    global notFoundObject

    # Lấy kích thước khung hình
    height, width, _ = frame.shape
    center_x, center_y = width // 2, height // 2

    # Chuyển đổi khung hình sang không gian màu HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Định nghĩa khoảng màu đỏ trong không gian HSV
    lower_red1 = np.array([0, 100, 100])
    upper_red1 = np.array([10, 255, 255])
    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)

    lower_red2 = np.array([160, 100, 100])
    upper_red2 = np.array([180, 255, 255])
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)

    mask = mask1 + mask2

    # Xử lý mặt nạ để loại bỏ nhiễu
    mask = cv2.GaussianBlur(mask, (5, 5), 0)
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)

    response = {
        'frame': frame,
        'mask': mask,
    }

    # Tìm các đường viền của các vùng màu đỏ
    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    if contours:
        # Sắp xếp các đường viền theo diện tích từ lớn đến nhỏ
        contours = sorted(contours, key=cv2.contourArea, reverse=True)

        for contour in contours:
            # Kiểm tra diện tích của vùng màu đỏ
            area = cv2.contourArea(contour)
            if area > 500:  # Giảm diện tích tối thiểu để phát hiện
                z = angle.getAngle(angle.getSensorResponse(angle.api_instance))

                # Lấy góc nguyên bản hoặc trả về góc hiện tại
                if not isGetAngle:
                    origin_z = z
                    isGetAngle = True
                    notFoundObject = 34

                # Tính toán hình chữ nhật bao quanh vùng màu đỏ
                rect = cv2.minAreaRect(contour)
                box = cv2.boxPoints(rect)
                box = np.int32(box)  # Thay đổi từ np.int0 thành np.int32

                # Tính toán độ lệch so với trung tâm
                object_center_x = int(rect[0][0])
                object_center_y = int(rect[0][1])

                # Vẽ hình chữ nhật bao quanh vùng màu đỏ
                cv2.drawContours(frame, [box], 0, (0, 255, 0), 2)

                # Tính toán khoảng cách dựa trên kích thước thực tế và kích thước trên hình ảnh
                width_on_image = min(rect[1])
                distance = (actual_width * focal_length) / width_on_image

                # Tính toán độ lệch so với trung tâm
                offset_x, offset_y = object_center_x - center_x, object_center_y - center_y

                # Trả về các kết quả vị trí
                response['offset_x'] = offset_x
                response['distance'] = distance

                # Xấp xỉ đa giác để kiểm tra hình vuông
                epsilon = 0.02 * cv2.arcLength(contour, True)
                approx = cv2.approxPolyDP(contour, epsilon, True)

                print(f"khoảng cách = {distance:.2f} cm, độ lệch: ({offset_x}, {offset_y})")

    if not isGetAngle:
        notFoundObject += 1

    # Vẽ chấm đỏ ở giữa khung hình
    return response

if __name__ == '__main__':
    last_send_time = time.time()

    cap = cv2.VideoCapture(url)

    actions = queue.Queue()

    # Kích thước thực tế của vật thể (cm)
    actual_width = 8.0
    #Tiêu cự (mm)
    focal_length = 640

    while True:
        # Đọc khung hình từ camera
        ret, frame = cap.read()

        height, width, _ = frame.shape
        center_x, center_y = width // 2, height // 2

        measure_response = measure_offset(frame)

        current_time = time.time()

        frame = measure_response['frame']
        mask = measure_response['mask']

        #Kiểm tra vị trí và xử lý mỗi một khoảng thời gian
        if current_time - last_time >= pause_time:

            if notFoundObject > 35:
                #Quay xung quanh tìm kiếm
                motion.putMotion('turn around', 'left', 1)

            offset_x = measure_response['offset_x'] if 'offset_x' in measure_response else 0
            distance = measure_response['distance'] if 'distance' in measure_response else dpr.distance_accept
            z = angle.getAngle(angle.getSensorResponse(angle.api_instance))

            angle_response = angle.isAccept(z, origin_z)
            angleAccept = angle_response['isAccept']

            if isGetAngle and (not angleAccept):
                direction = angle_response['direction']
                repeat = angle.getRepeat(z, origin_z)

                total_time = motion.putMotion(action='turn around', direction=direction, repeat=repeat)
                pause_time = total_time / 1000 + 2 if total_time / 1000 >= 1 else 2

                last_time = time.time()

                continue

            distance_response = dpr.checkDistance(distance)
            distanceAccept = distance_response['isAccept']

            if not distanceAccept:
                direction = distance_response['direction']
                repeat = dpr.getRepeat(distance)

                total_time = motion.putMotion(action='walk', direction=direction, repeat=repeat)
                pause_time = total_time / 1000 + 2 if total_time / 1000 >= 1 else 2

                last_time = time.time()

                continue

            offset_response = offset.checkOffset(offset_x)
            offsetAccept = offset_response['isAccept']

            if not offsetAccept:
                direction = offset_response['direction']
                repeat = offset.getRepeat(offset_x)

                total_time = motion.putMotion(action='walk', direction=direction, repeat=repeat)
                pause_time = total_time / 1000 + 2 if total_time / 1000 >= 1 else 2

                last_time = time.time()

                continue

            last_time = time.time()

        # Hiển thị khung hình và mặt nạ
        cv2.imshow('Frame', frame)
        cv2.imshow('Mask', mask)


        # Nhấn 'q' để thoát
        if cv2.waitKey(2) & 0xFF == ord('q'):
            break

    # Giải phóng camera và đóng tất cả cửa sổ
    cap.release()
    cv2.destroyAllWindows()
