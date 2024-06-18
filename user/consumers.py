import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer,WebsocketConsumer
import json
import logging
from backend_test import generate_data  # 导入生成器函数
import cv2
import os
import numpy as np
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
            print("Received video data")
            self.frame_index += 1
            # 将二进制数据转换为 numpy 数组
            nparr = np.frombuffer(bytes_data, np.uint8)

            # 解码图像
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            if frame is not None:
                # 保存图像
                filename = f'frames/frame_{self.frame_index:04d}.jpg'
                cv2.imwrite(filename, frame)
                print(f"Frame {self.frame_index} saved as {filename}")
            else:
                print("Failed to decode frame")
        elif text_data:
            print("Received text data in video consumer")
        else:
            print("null")
