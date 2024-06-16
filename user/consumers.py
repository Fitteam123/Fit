import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
import json
import logging
from test import generate_data  # 导入生成器函数

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
