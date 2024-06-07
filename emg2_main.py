import os
import pandas as pd
import mne
import numpy as np
import torch
import matplotlib.pyplot as plt
from sklearn.decomposition import NMF
import torch.nn.functional as F

mne.set_log_level("WARNING")


class sEMGConfig:
    def __init__(self, file_path):
        self.file_path = file_path
        self.sampling_rate = sampling_rate
        self.raw_data = None
        self.resized_data = None

    def loadAndresize_data(self, file_path):
        self.resized_data = pd.read_csv(file_path).to_numpy(dtype=np.float64)
        self.resized_data = self.resized_data[:, 1:].T * 1.0
        print(f"数据加载并转换后类型: {self.resized_data.dtype}")  # 调试输出

    def normalize_data(self, data):
        # data应该是一个形状为(channels, time)的numpy数组
        normalized_data = np.zeros(data.shape)
        for i in range(data.shape[0]):
            # 找出最大的三个值的平均和最小的三个值的平均
            max_val = np.mean(np.sort(data[i])[-3:])
            min_val = np.mean(np.sort(data[i])[:3])
            normalized_data[i] = (data[i] - min_val) / (max_val - min_val)
        return normalized_data

    def preprocess_data(self, low_freq, high_freq):
        if self.resized_data is not None:
            iir_params = dict(order=4, ftype="butter")  # 设置为巴特沃兹滤波器
            filtered_data = mne.filter.filter_data(
                self.resized_data,
                self.sampling_rate,
                low_freq,
                high_freq,
                method="iir",
                iir_params=iir_params,
            )
            normalized_data = self.normalize_data(filtered_data)
            return normalized_data
        else:
            print("Please load and resize the data first.")
            return None

    def pipeline(self, low_freq, high_freq):
        self.loadAndresize_data(self.file_path)
        preprocessed_data = self.preprocess_data(low_freq, high_freq)
        emg_signal = torch.from_numpy(preprocessed_data)
        return emg_signal


def calculate_TDMNF(emg_signal, window_len=848, stride=108):  # 计算TD-MNF特征  768 96是固定超参
    num_windows = (emg_signal.size(1) - window_len) // stride + 1  # 计算窗口数量
    td_mnf = torch.zeros(emg_signal.size(0))  # 存储每个通道的TD-MNF值
    for ch_i in range(emg_signal.size(0)):
        for i in range(num_windows):
            start = i * stride
            end = start + window_len
            window = emg_signal[ch_i, start:end]

            # 计算功率谱
            psd = torch.abs(torch.fft.fft(window)) ** 2
            freq = torch.linspace(0, 1000 / 2, window_len // 2)
            td_mnf[ch_i] += torch.sum(freq * psd[: window_len // 2]) / torch.sum(
                psd[: window_len // 2]
            )

    td_mnf /= num_windows  # 计算每个通道的TD-MNF的平均值
    # td_mnf = F.softmax(td_mnf, dim=0)*100

    return td_mnf


def calculate_TDMNF_for_segments(file_path):
    # 读取文件数据
    eeg_config = sEMGConfig(file_path)
    emg_signal = eeg_config.pipeline(low_freq, high_freq)
    # 检查数据长度是否是 segment_len 的整数倍
    if emg_signal.size(1) % segment_len != 0:
        emg_signal = emg_signal[:, : (emg_signal.size(1) // segment_len) * segment_len]

    # 将数据切分为长度为segment_len的段
    num_segments = emg_signal.size(1) // segment_len
    s = emg_signal.split(segment_len // 4, dim=1)
    segments = [
        torch.cat([s[i], s[i + 1], s[i + 2], s[i + 3]], dim=1)
        for i in range(len(s) - 3)
    ]
    # 对每个段调用 calculate_TDMNF 函数
    tdmnf_values = [calculate_TDMNF(segment) for segment in segments]

    return torch.stack(tdmnf_values)


def TDMNFs(file_paths):
    all_tdmnf_values = []
    for file_path in file_paths:
        # 计算当前文件的tdmnf_values
        tdmnf_values = calculate_TDMNF_for_segments(file_path)
        all_tdmnf_values.append(tdmnf_values)

    # 将所有文件的tdmnf_values堆叠成一个多维张量
    # all_tdmnf_values = torch.stack(all_tdmnf_values)
    return all_tdmnf_values


def plot_TDMNFs(all_tdmnf_values):
    # 获取通道数量
    num_channels = all_tdmnf_values[0][0].size(0)

    # 为每个通道创建一个子图
    fig, axs = plt.subplots(num_channels)

    # 在每个子图中绘制对应通道的结果
    for ch_i in range(num_channels):
        for tdmnf_values in all_tdmnf_values:
            axs[ch_i].plot([tdmnf[ch_i] for tdmnf in tdmnf_values])
        axs[ch_i].set_ylabel("TDMNF")

    plt.tight_layout()
    plt.show()


def calculate_NNMF_from_TDMNF(all_tdmnf_values, n_components):
    all_W = []
    all_H = []
    for tdmnf_values in all_tdmnf_values:
        #转置
        tdmnf_values = tdmnf_values.T
        # 转换为numpy数组
        tdmnf_values = tdmnf_values.numpy()
        # 创建一个NMF模型，增加最大迭代次数
        model = NMF(
            n_components=n_components, init="nndsvd", random_state=0, max_iter=1000
        )
        # 拟合并转换数据
        W = model.fit_transform(tdmnf_values)
        # 查看组件
        H = model.components_
        all_W.append(W)
        all_H.append(H)

    return all_W, all_H


def calculate_rankings(data):
    # data应该是一个形状为(time,channel)的numpy数组
    rankings = np.zeros(data.shape)
    for i in range(data.shape[0]):
        rankings[i] = data[i].argsort().argsort()
    return rankings


def calculate_VAF(original_matrix, reconstructed_matrix):
    # 计算两个矩阵之间的差异
    difference = original_matrix - reconstructed_matrix

    # 计算差异值平方的累加和
    squared_difference_sum = torch.sum(torch.square(difference))

    # 计算原矩阵的平方的累计和
    squared_original_sum = torch.sum(torch.square(original_matrix))

    # 计算并返回VAF
    VAF = 1 - (squared_difference_sum / squared_original_sum)
    return VAF


sampling_rate = 425
low_freq = 10
high_freq = 200  # 应小于sampling_rate/2
segment_len = 848  # 切片长度（425为一秒）   与window_len相同
file_paths = [
    f"D:/AA_HZJ/com_test/data/{file_name}"
    for file_name in os.listdir("D:/AA_HZJ/com_test/data")
    if file_name.startswith("re")
]


if __name__ == "__main__":
    all_tdmnf_values = TDMNFs(file_paths)
    all_W = []
    all_H = []
    all_rankings = []
    all_vaf = []

    for i, tdmnf_values in enumerate(all_tdmnf_values):
        print(f"第{i+1}个文件的TDMNF值为：")
        print(tdmnf_values)
        rankings = calculate_rankings(tdmnf_values)
        print(rankings)
        all_rankings.append(rankings)
        W, H = calculate_NNMF_from_TDMNF([tdmnf_values], n_components=4)  # n_components是运动类别数
        all_W.append(W)
        all_H.append(H)
        vaf = calculate_VAF(tdmnf_values.T, np.dot(W[0], H[0]))
        all_vaf.append(vaf)
        print(vaf)   #大于0.95则说明拟合效果较好


        
        
        #W，H有待归一化...
        print(f"第{i+1}个文件的肌肉协同结构矩阵：")   #w1，w2等等表示各肌肉协同结构,表示各肌肉在该协同募集模式中的贡献程度
        print(W)
        
        print(f"第{i+1}个文件的肌肉协同激活系数矩阵：")     #h1，h2等等表示各肌肉协同激活系数，表示按时间调制的下行神经信号的强弱程度
        print(H)

        #对于H，定义当幅值大于峰值的0.5倍时，认为该肌肉协同为明显激活！！！


        Cw = np.mean(W[0], axis=0)
        print("该肌肉协同的肌肉贡献度：")   #理解为肌肉的重要程度？ 又被称为募集模式？
        print(Cw)
        Ch = np.mean(H[0], axis=1)
        print("该肌肉协同的激活程度：")
        print(Ch)
        
        
    plot_TDMNFs(all_tdmnf_values)
    