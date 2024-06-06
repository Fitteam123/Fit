#正常获取字节串形式数据
# import serial
#
# # 设置串口参数
# port = 'COM3'  # 根据实际情况修改串口号
# baudRate = 115200  # 波特率
# dataBits = 8  # 数据位
# parity = 'N'  # 校验位
# stopBits = 1  # 停止位
# timeout = 3600  # 超时时间（-1表示无限制）
#
# # 打开串口连接
# ser = serial.Serial(port, baudRate, bytesize=dataBits, parity=parity, stopbits=stopBits, timeout=timeout)
#
# if (ser.isOpen()):
#     print("open success")
# # 向端口些数据 字符串必须译码
# while (True):
#     line = ser.readline()
#     if(line):
#         print(line)
#     line=0
# else:
#     print("open failed")
#     ser.close()#关闭端口



#正常获取数据并且保存到文件当中
# import serial

# # 设置串口参数
# port = 'COM3'  # 根据实际情况修改串口号
# baudRate = 115200  # 波特率
# dataBits = 8  # 数据位
# parity = 'N'  # 校验位
# stopBits = 1  # 停止位
# timeout = 3600  # 超时时间（-1表示无限制）
#
# # 打开串口连接
# ser = serial.Serial(port, baudRate, bytesize=dataBits, parity=parity, stopbits=stopBits, timeout=timeout)
#
# if (ser.isOpen()):
#     print("串口已打开")
# else:
#     print("串口打开失败")
#     exit()
#
# # 创建文件用于保存数据
# file_path = "received_data.txt"
#
# # 读取并保存数据到文件中
# with open(file_path, "w") as file:
#     while True:
#         line = ser.readline()  # 读取字节串数据
#         if line:  # 如果接收到数据
#             data_str = line.decode().strip()  # 使用默认编码解码为字符串并去除空白字符
#             file.write(data_str + "\n")  # 将数据写入文件
#             print("已写入数据：", data_str)
#         else:
#             print("未接收到数据")
#
# # 关闭串口连接
# ser.close()

#添加时间戳
import serial
from datetime import datetime

# 设置串口参数
port = 'COM3'  # 根据实际情况修改串口号
baudRate = 115200  # 波特率
dataBits = 8  # 数据位
parity = 'N'  # 校验位
stopBits = 1  # 停止位
timeout = 3600  # 超时时间（-1表示无限制）

# 打开串口连接
ser = serial.Serial(port, baudRate, bytesize=dataBits, parity=parity, stopbits=stopBits, timeout=timeout)

if ser.isOpen():
    print("串口已打开")
else:
    print("串口打开失败")
    exit()

# 创建文件用于保存数据
file_path = "received_data"

# 读取并保存数据到文件中
with open(file_path, "w") as file:
    file.write("timestamp,Channel 1,Channel 2,Channel 3,Channel 4,Channel 5,Channel 6\n")
    first_line = ser.readline()
    while True:
        line = ser.readline()  # 读取字节串数据
        if line:  # 如果接收到数据
            # timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # 获取当前时间戳
            timestamp = int(datetime.now().timestamp())  # 获取 Unix 时间戳
            data_str = line.decode(errors='ignore').strip()  # 使用默认编码解码为字符串并去除空白字符
            file.write(f"{timestamp},{data_str}\n")  # 将带时间戳的数据写入文件
            print("已写入数据：", timestamp,',', data_str)
        else:
            print("未接收到数据")

# 关闭串口连接
ser.close()



