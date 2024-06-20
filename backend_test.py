import time
import random

def generate_data():
    while True:
        data = {
            "channel1": random.uniform(0.5, 0.7),
            "channel2": random.uniform(0.5, 0.7),
            "channel3": random.uniform(0.5, 0.7),
            "channel4": random.uniform(0.5, 0.7),
            "channel5": random.uniform(0.5, 0.7),
            "channel6": random.uniform(0.5, 0.7)
        }
        yield data
        time.sleep(1)  # 模拟数据生成间隔