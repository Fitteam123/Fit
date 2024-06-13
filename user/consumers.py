import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer


class OutputConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

        # 启动后台任务
        await self.send_output()

    async def disconnect(self, close_code):
        pass

    async def send_output(self):
        process = await asyncio.create_subprocess_exec(
            'python', 'com_test.py',
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        while True:
            line = await process.stdout.readline()
            if not line:
                break
            await self.send(text_data=line.decode('utf-8'))
