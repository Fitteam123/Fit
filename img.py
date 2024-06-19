from flask import Flask, render_template
from flask_socketio import SocketIO
import numpy as np
import cv2
from io import BytesIO
import mediapipe as mp
import numpy as np
import matplotlib.pyplot as plt

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_pose = mp.solutions.pose

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('message')
def handle_message(data):
    print('Received image data')
    # 读取图像数据并处理
    image = np.frombuffer(data, np.uint8)
    img = cv2.imdecode(image, cv2.IMREAD_COLOR)
    if img is not None:
        # 这里可以进行图像处理
        processed_img = process_image(img)
        # 如果需要发送处理后的图像，可以进行编码并发送
        _, buffer = cv2.imencode('.jpg', processed_img)
        socketio.send(buffer.tobytes())

def print_all(landmarks_list):
    for landmarks in landmarks_list:
        fig = plt.figure()
        ax = fig.add_subplot(111)
        for i in range(33):
            ax.scatter(landmarks[i].x,1 - landmarks[i].y)
            ax.text(landmarks[i].x,1 - landmarks[i].y,str(i))
        plt.show()

def get_degree1(landmarks):
    p12 = np.array([landmarks[12].x,landmarks[12].y,landmarks[12].z])
    p14 = np.array([landmarks[14].x,landmarks[14].y,landmarks[14].z])
    p16 = np.array([landmarks[16].x,landmarks[16].y,landmarks[16].z])

    v1 = p12 - p14
    v2 = p16 - p14

    cos = np.dot(v1,v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
    return np.arccos(cos) * 180 / np.pi

def get_degree2(landmarks):
    p11 = np.array([landmarks[11].x,landmarks[11].y,landmarks[11].z])
    p12 = np.array([landmarks[12].x,landmarks[12].y,landmarks[12].z])
    p24 = np.array([landmarks[24].x,landmarks[24].y,landmarks[24].z])
    p14 = np.array([landmarks[14].x,landmarks[14].y,landmarks[14].z])

    # Calculate normal vector to the plane defined by points 11, 12 and 24
    v1 = p12 - p11
    v2 = p24 - p11
    normal = np.cross(v1, v2)

    # Calculate vector between points 12 and 14
    v3 = p14 - p12

    # Calculate the angle between the normal and the vector
    cos = np.dot(normal, v3) / (np.linalg.norm(normal) * np.linalg.norm(v3))
    return 90 - np.arccos(cos) * 180 / np.pi

def get_degree3(landmarks):
    p11 = np.array([landmarks[11].x,landmarks[11].y,landmarks[11].z])
    p12 = np.array([landmarks[12].x,landmarks[12].y,landmarks[12].z])
    p14 = np.array([landmarks[14].x,landmarks[14].y,landmarks[14].z])
    p16 = np.array([landmarks[16].x,landmarks[16].y,landmarks[16].z])

    # Calculate normal vector to the plane defined by points 12, 14 and 16
    v1 = p14 - p12
    v2 = p16 - p12
    normal = np.cross(v1, v2)

    # Calculate vector between points 12 and 11
    v3 = p11 - p12

    # Calculate the angle between the normal and the vector
    cos = np.dot(normal, v3) / (np.linalg.norm(normal) * np.linalg.norm(v3))
    return np.abs(90 - np.arccos(cos) * 180 / np.pi)

# Your main code will now look like this:
# print_all(landmarks_list=landmarks_list)
def get_ang(x):

    str1 = '小臂与大臂角度:{}'.format(get_degree1(x))
    str2 = '大臂与躯干平面角度:{}'.format(get_degree2(x))
    str3 = '手臂平面与肩部水平线角度:{}'.format(get_degree3(x))
    return str1 + str2 + str3


def process_image(img):
    # 在这里进行图像处理，例如转换为灰度图像
    image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    image_height, image_width, _ = image.shape
    # Convert the BGR image to RGB before processing.
    results = pose.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

    if not results.pose_landmarks:
        return None

    return get_ang(results.pose_landmarks.landmark)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=8000)