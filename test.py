import time
import random

for _ in range(10):
# while True:
    # 生成6个随机数
    numbers = [random.randint(1, 100) for _ in range(6)]
    print(*numbers)  # 将6个数字打印到一行
    time.sleep(1)  # 暂停1秒

