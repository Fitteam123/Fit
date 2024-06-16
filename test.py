# test.py
import time
import random

def generate_data():
    while True:
        data = {
            "channel1": random.randint(0, 100),
            "channel2": random.randint(0, 100),
            "channel3": random.randint(0, 100),
            "channel4": random.randint(0, 100),
            "channel5": random.randint(0, 100),
            "channel6": random.randint(0, 100)
        }
        yield data
        time.sleep(1)  # 模拟数据生成间隔
