#添加时间戳
import serial
from datetime import datetime
from threading import Thread

# 设置串口参数
port = 'COM3'  # 根据实际情况修改串口号
baudRate = 115200  # 波特率
dataBits = 8  # 数据位
parity = 'N'  # 校验位
stopBits = 1  # 停止位
timeout = 3600  # 超时时间（-1表示无限制）

class reader:
    def __init__(self):
        for port in ['COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8']:
            try:
                self.ser = serial.Serial(port, baudRate, bytesize=dataBits, parity=parity, stopbits=stopBits, timeout=timeout)
                if self.ser.isOpen():
                    break
            except:
                continue
        self.ser = serial.Serial(port, baudRate, bytesize=dataBits, parity=parity, stopbits=stopBits, timeout=timeout)

        self.data = []
        self.timestamp = []
        self.raw_data = []
        self.raw_timestamp = []
        self.status = False

    def run(self):
        while True:
            if self.status:
                line = self.ser.readline()
                if line:
                    data_str = line.decode(errors='ignore').strip()
                    raw_data = data_str.split(',')
                    raw_data = [float(i) for i in raw_data]
                    self.raw_data.append(raw_data)
                    self.raw_timestamp.append(datetime.now().timestamp())
                    if len(self.raw_data) > 2000:
                        self.raw_data.pop(0)
                        self.raw_timestamp.pop(0)   
            else:
                break

    def start(self):
        if self.ser.isOpen():
            print("串口已打开")
        self.status = True
    
    def stop(self):
        self.status = False 
