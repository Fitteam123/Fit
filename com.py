import serial
from datetime import datetime
from threading import Thread, Lock
import pandas as pd
import numpy as np
import torch
import matplotlib.pyplot as plt
from sklearn.decomposition import NMF
import mne
from queue import Queue
import time
import json

# 设置串口参数
port = 'COM3'  # 根据实际情况修改串口号
baudRate = 115200  # 波特率
dataBits = 8  # 数据位
parity = 'N'  # 校验位
stopBits = 1  # 停止位
timeout = 3600  # 超时时间（-1表示无限制）

mne.set_log_level("WARNING")

def pad_data(data, expected_length):
    """
    Pad the data with zeros if its length is less than expected_length
    """
    if len(data) < expected_length:
        data += [0.0] * (expected_length - len(data))
    return data

def normalize_data(data):
    normalized_data = np.zeros(data.shape)
    for i in range(data.shape[0]):
        max_val = np.mean(np.sort(data[i])[-3:])
        min_val = np.mean(np.sort(data[i])[:3])
        normalized_data[i] = (data[i] - min_val) / (max_val - min_val)
    return normalized_data

def is_float(string):
    try:
        float(string)
        return True
    except ValueError:
        return False

class EMGReader:
    def __init__(self):
        self.ser = None
        for port in ['COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8']:
            try:
                self.ser = serial.Serial(port, baudRate, bytesize=dataBits, parity=parity, stopbits=stopBits, timeout=timeout)
                if self.ser.isOpen():
                    break
            except:
                continue
        self.data_queue = Queue()
        self.status = False
        self.lock = Lock()

    def read_data(self):
        while self.status:
            if self.status:
                line = self.ser.readline()
                if line:
                    data_str = line.decode(errors='ignore').strip()
                    tmp = data_str.split(',')
                    if is_float(tmp[0]):
                        raw_data = [float(i) if is_float(i) else 0.0 for i in tmp]
                        if raw_data:
                            raw_data = pad_data(raw_data, 6)  # 使用pad_data函数填补数据
                            timestamp = datetime.now().timestamp()
                            self.data_queue.put((raw_data, timestamp))

    def start(self):
        if self.ser.isOpen():
            print("串口已打开")
        self.status = True
        self.read_thread = Thread(target=self.read_data)
        self.read_thread.start()

    def stop(self):
        self.status = False
        if self.read_thread.is_alive():
            self.read_thread.join()

def get_emg_signal(raw_data, sampling_rate, low_freq, high_freq):
    iir_params = dict(order=4, ftype="butter")
    filtered_data = mne.filter.filter_data(
        raw_data,
        sampling_rate,
        low_freq,
        high_freq,
        method="iir",
        iir_params=iir_params,
    )
    normalized_data = normalize_data(filtered_data)
    return torch.from_numpy(normalized_data)

def TDMNF_gen(raw_data, sampling_rate, low_freq, high_freq, segment_len):
    emg_signal = get_emg_signal(raw_data, sampling_rate, low_freq, high_freq)
    if emg_signal.size(1) % segment_len != 0:
        emg_signal = emg_signal[:, : (emg_signal.size(1) // segment_len) * segment_len]
    num_segments = emg_signal.size(1) // segment_len
    s = emg_signal.split(segment_len // 4, dim=1)
    segments = [torch.cat([s[i], s[i + 1], s[i + 2], s[i + 3]], dim=1) for i in range(len(s) - 3)]
    tdmnf_values = [calculate_TDMNF(segment) for segment in segments]
    return torch.stack(tdmnf_values)

def calculate_TDMNF(emg_signal, window_len=848, stride=108):
    num_windows = (emg_signal.size(1) - window_len) // stride + 1
    td_mnf = torch.zeros(emg_signal.size(0))
    for ch_i in range(emg_signal.size(0)):
        for i in range(num_windows):
            start = i * stride
            end = start + window_len
            window = emg_signal[ch_i, start:end]
            psd = torch.abs(torch.fft.fft(window)) ** 2
            freq = torch.linspace(0, 1000 / 2, window_len // 2)
            td_mnf[ch_i] += torch.sum(freq * psd[: window_len // 2]) / torch.sum(psd[: window_len // 2])
    td_mnf /= num_windows
    return td_mnf

class EMGProcessor:
    def __init__(self, reader, sampling_rate, low_freq, high_freq, segment_len):
        self.reader = reader
        self.sampling_rate = sampling_rate
        self.low_freq = low_freq
        self.high_freq = high_freq
        self.segment_len = segment_len
        self.raw_data = []
        self.raw_timestamp = []
        self.processed_data = Queue()
        self.status = False

    def process_data(self):
        while self.status:
            if self.reader.status:
                if not self.reader.data_queue.empty():
                    raw_data, timestamp = self.reader.data_queue.get()
                    if len(raw_data) != 6:
                        continue
                    self.raw_data.append(raw_data)
                    self.raw_timestamp.append(timestamp)
                    if len(self.raw_data) >= self.segment_len:
                        segment = np.array(self.raw_data[-self.segment_len:]).T
                        tdmnf_values = TDMNF_gen(segment, self.sampling_rate, self.low_freq, self.high_freq, self.segment_len)
                        self.processed_data.put(tdmnf_values)
                    if len(self.raw_data) >= self.segment_len * 2:
                        self.raw_data = self.raw_data[-self.segment_len:]

    def start(self):
        self.status = True
        self.process_thread = Thread(target=self.process_data)
        self.process_thread.start()

    def stop(self):
        self.status = False
        if self.process_thread.is_alive():
            self.process_thread.join()

SAMPALING_RATE = 425
LOW_FREQ = 10
HIGH_FREQ = 200
SEG_LEN = 848

def generate_data():
    emg_reader = EMGReader()
    emg_processor = EMGProcessor(emg_reader, SAMPALING_RATE, LOW_FREQ, HIGH_FREQ, SEG_LEN)
    emg_reader.start()
    emg_processor.start()

    try:
        while True:
            if not emg_processor.processed_data.empty():
                tdmnf_values = emg_processor.processed_data.get()
                if tdmnf_values.size(1) == 6:  # 假设tdmnf_values是1行6列的tensor
                    tdmnf_list = tdmnf_values.squeeze().tolist()  # 将tensor转换为列表
                    data = {
                        "channel1": tdmnf_list[0],
                        "channel2": tdmnf_list[1],
                        "channel3": tdmnf_list[2],
                        "channel4": tdmnf_list[3],
                        "channel5": tdmnf_list[4],
                        "channel6": tdmnf_list[5]
                    }
                    yield data
            time.sleep(1)  # 模拟数据生成间隔

    except KeyboardInterrupt:
        emg_reader.stop()
        emg_processor.stop()

if __name__ == "__main__":
    emg_data_generator = generate_emg_data()
    while True:
        next(emg_data_generator)
