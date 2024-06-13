import time
import random

def generate_tdmnf():
    """Generate a random tdmnf value."""
    return random.uniform(0, 100)

if __name__ == "__main__":
    for _ in range(100):  # 输出10次
        tdmnf_value = generate_tdmnf()
        print(f"tdmnf: {tdmnf_value}")
        time.sleep(1)  # 每隔1秒输出一次
