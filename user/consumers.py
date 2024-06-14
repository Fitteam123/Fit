import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
import subprocess
import json
import logging

logger = logging.getLogger(__name__)

class OutputConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        try:
            await self.send_output()
        except Exception as e:
            error_message = f"Error in connect: {str(e)}"
            logger.error(error_message)
            await self.send(text_data=json.dumps({"error": error_message}))
            await self.close(code=1000)  # 使用1000作为关闭代码

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data=None, bytes_data=None):
        pass

    async def send_output(self):
        try:
            result = subprocess.Popen(
                ['python', 'test.py'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True  # 将 stdout 和 stderr 解码为文本
            )

            while True:
                line = result.stdout.readline()
                if not line:
                    break

                numbers = line.strip().split()  # 将每行数据分割成列表
                data = {
                    "channel1": numbers[0],
                    "channel2": numbers[1],
                    "channel3": numbers[2],
                    "channel4": numbers[3],
                    "channel5": numbers[4],
                    "channel6": numbers[5]
                }
                message = json.dumps(data)
                await self.send(text_data=message)

        except Exception as e:
            error_message = f"Error in send_output: {str(e)}"
            logger.error(error_message)
            await self.send(text_data=json.dumps({"error": error_message}))
            await self.close(code=1000)  # 使用1000作为关闭代码
