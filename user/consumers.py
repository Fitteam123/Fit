import asyncio
import json
import logging
from backend_test import generate_data  # 导入生成器函数
import os
import cv2
import numpy as np
import matplotlib.pyplot as plt
import mediapipe as mp
from channels.generic.websocket import AsyncWebsocketConsumer

logger = logging.getLogger(__name__)

class OutputConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        self.keep_running = True  # 标志位
        try:
            self.generator = generate_data()
            asyncio.create_task(self.send_output())  # 启动send_output作为独立任务
        except Exception as e:
            error_message = f"Error in connect: {str(e)}"
            logger.error(error_message)
            await self.send(text_data=json.dumps({"error": error_message}))
            await self.close(code=1000)  # 使用1000作为关闭代码

    async def disconnect(self, close_code):
        self.keep_running = False  # 关闭连接时设置标志位为False

    async def receive(self, text_data=None, bytes_data=None):
        pass

    async def send_output(self):
        try:
            while self.keep_running:
                data = next(self.generator)
                message = json.dumps(data)
                await self.send(text_data=message)
                await asyncio.sleep(1)  # 与生成器的sleep时间一致
        except StopIteration:
            pass  # 生成器结束
        except Exception as e:
            if not self.keep_running:
                return  # 连接已经关闭，忽略发送错误
            error_message = f"Error in send_output: {str(e)}"
            logger.error(error_message)
            try:
                await self.send(text_data=json.dumps({"error": error_message}))
            except Exception:
                # 发送错误时再次检查连接状态
                if self.keep_running:
                    await self.close(code=1000)  # 使用1000作为关闭代码

mp_pose = mp.solutions.pose
pose = mp_pose.Pose()

class VideoConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.frame_index = 0  # 初始化帧索引
        os.makedirs('frames', exist_ok=True)  # 确保 frames 目录存在

    async def connect(self):
        await self.accept()
        print("Video WebSocket connected")

    async def disconnect(self, close_code):
        print("Video WebSocket disconnected")

    async def receive(self, text_data=None, bytes_data=None):
        if bytes_data:
            # print("Received video data")
            image = np.frombuffer(bytes_data, np.uint8)
            img = cv2.imdecode(image, cv2.IMREAD_COLOR)
            if img is not None:
                # 进行图像处理
                processed_data = self.process_image(img)
                if processed_data is not None:
                    await self.send(text_data=json.dumps(processed_data))

    def get_degree1(self, landmarks):
        p12 = np.array([landmarks[12].x, landmarks[12].y, landmarks[12].z])
        p14 = np.array([landmarks[14].x, landmarks[14].y, landmarks[14].z])
        p16 = np.array([landmarks[16].x, landmarks[16].y, landmarks[16].z])

        v1 = p12 - p14
        v2 = p16 - p14

        cos = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
        return np.arccos(cos) * 180 / np.pi

    def get_degree2(self, landmarks):
        p11 = np.array([landmarks[11].x, landmarks[11].y, landmarks[11].z])
        p12 = np.array([landmarks[12].x, landmarks[12].y, landmarks[12].z])
        p24 = np.array([landmarks[24].x, landmarks[24].y, landmarks[24].z])
        p14 = np.array([landmarks[14].x, landmarks[14].y, landmarks[14].z])

        # 计算点 11, 12 和 24 定义的平面的法向量
        v1 = p12 - p11
        v2 = p24 - p11
        normal = np.cross(v1, v2)

        # 计算点 12 和 14 之间的向量
        v3 = p14 - p12

        # 计算法向量与该向量之间的角度
        cos = np.dot(normal, v3) / (np.linalg.norm(normal) * np.linalg.norm(v3))
        return 90 - np.arccos(cos) * 180 / np.pi

    def get_degree3(self, landmarks):
        p11 = np.array([landmarks[11].x, landmarks[11].y, landmarks[11].z])
        p12 = np.array([landmarks[12].x, landmarks[12].y, landmarks[12].z])
        p14 = np.array([landmarks[14].x, landmarks[14].y, landmarks[14].z])
        p16 = np.array([landmarks[16].x, landmarks[16].y, landmarks[16].z])

        # 计算点 12, 14 和 16 定义的平面的法向量
        v1 = p14 - p12
        v2 = p16 - p12
        normal = np.cross(v1, v2)

        # 计算点 12 和 11 之间的向量
        v3 = p11 - p12

        # 计算法向量与该向量之间的角度
        cos = np.dot(normal, v3) / (np.linalg.norm(normal) * np.linalg.norm(v3))
        return abs(90 - np.arccos(cos) * 180 / np.pi)

    def process_image(self, img):
        # 转换为 RGB 图像
        image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = pose.process(image)

        if not results.pose_landmarks:
            return None

        landmarks = results.pose_landmarks.landmark

        box1 = self.get_degree1(landmarks)
        box2 = self.get_degree2(landmarks)
        box3 = self.get_degree3(landmarks)

        return {
            "box1": box1,
            "box2": box2,
            "box3": box3
        }

