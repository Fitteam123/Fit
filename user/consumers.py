import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
import json
import logging
from test import generate_data  # 导入生成器函数

logger = logging.getLogger(__name__)

class OutputConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        try:
            self.generator = generate_data()
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
            while True:
                data = next(self.generator)
                message = json.dumps(data)
                await self.send(text_data=message)
                await asyncio.sleep(1)  # 与生成器的sleep时间一致

        except Exception as e:
            error_message = f"Error in send_output: {str(e)}"
            logger.error(error_message)
            await self.send(text_data=json.dumps({"error": error_message}))
            await self.close(code=1000)  # 使用1000作为关闭代码
