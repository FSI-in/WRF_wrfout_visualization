import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

class expand_data:
    def __init__(self):
        pass

    # 傅里叶滤波扩充数据
    def Fourier_filter_norm(self, original_data, cutoff_frequency, number_expand, time_step_original):
        
        original_data = np.array(original_data)
        # 原始数据时间步常


        time_step_original = float(time_step_original)

        number_expand = int(number_expand)

        original_data_len = int(len(original_data)/2)
        # 要滤掉的以上的频率
        cutoff_frequency = int(cutoff_frequency)
        cutoff_frequency = int(original_data_len * cutoff_frequency / 100)


        # 生成随机数
        np.random.seed(0)  # 设置随机数种子以确保可重复性
        num_points = len(original_data)

        total_time_original = num_points * time_step_original - 0.000001    #  这里有一个精度误差，要减去
        t_original = np.arange(0, total_time_original, time_step_original)

        # 执行傅立叶变换
        fft_result = np.fft.fft(original_data)

        # 设置需要滤波的高频分量为零（示例中保留前10个频率分量，其他设为零）
        fft_result[cutoff_frequency+1:-cutoff_frequency] = 0

        # 执行傅立叶逆变换，将数据从频域转换回时域
        filtered_data = np.fft.ifft(fft_result)

        # 计算新的时间步长和总时间（加密后的）
        time_step_new = time_step_original / number_expand
        total_time_new = total_time_original
        t_new = np.arange(0, total_time_new, time_step_new)

        # 插值以获得更高时间分辨率的数据
        combined_data_interpolated = np.interp(t_new, t_original, filtered_data)

        # 原始数据减去滤波数据
        change_data = original_data - filtered_data.real

        # 检验
        # 取绝对值
        absolute_values = np.abs(change_data)

        # 计算绝对值后的数组的平均值
        average_of_absolute_values = np.mean(absolute_values)

        # 指定要生成的数组的数据量
        sample_size = len(change_data)

        # 指定均值和标准差
        mean = np.mean(change_data)
        std_dev = np.std(change_data)

        # 创建一个传递的空数组
        two_dimensional_array = []

        for i in range(number_expand - 1):
            new_data = np.random.normal(mean, std_dev, sample_size)
            two_dimensional_array.append(new_data)

        # 创建一个空列表
        change_data_over = []

        for i in range(sample_size):
            change_data_over.append(change_data[i])
            for j in range(number_expand - 1):
                change_data_over.append(two_dimensional_array[j][i])

        # 将列表转换为 NumPy 数组
        change_data_over = np.array(change_data_over)

        new_data_out = combined_data_interpolated.real + change_data_over

        return new_data_out, average_of_absolute_values

    # 打乱扩充数据
    def Fourier_filter_daluan(self, original_data, cutoff_frequency, number_expand, time_step_original):
        original_data = np.array(original_data)

        # 原始数据时间步常
        time_step_original = float(time_step_original)

        number_expand = int(number_expand)

        original_data_len = int(len(original_data)/2)
        # 要滤掉的以上的频率
        cutoff_frequency = int(cutoff_frequency)
        cutoff_frequency = int(original_data_len * cutoff_frequency / 100)


        # 生成随机数
        np.random.seed(0)  # 设置随机数种子以确保可重复性
        num_points = len(original_data)

        total_time_original = num_points * time_step_original - 0.000001    #  这里有一个精度误差，要减去
        t_original = np.arange(0, total_time_original, time_step_original)

        # 执行傅立叶变换
        fft_result = np.fft.fft(original_data)

        # 设置需要滤波的高频分量为零（示例中保留前10个频率分量，其他设为零）
        fft_result[cutoff_frequency+1:-cutoff_frequency] = 0

        # 执行傅立叶逆变换，将数据从频域转换回时域
        filtered_data = np.fft.ifft(fft_result)

        # 计算新的时间步长和总时间（加密后的）
        time_step_new = time_step_original / number_expand
        total_time_new = total_time_original
        t_new = np.arange(0, total_time_new, time_step_new)

        # 插值以获得更高时间分辨率的数据
        combined_data_interpolated = np.interp(t_new, t_original, filtered_data)

        # 原始数据减去滤波数据
        change_data = original_data - filtered_data.real

        # 检验
        # 取绝对值
        absolute_values = np.abs(change_data)

        # 计算绝对值后的数组的平均值
        average_of_absolute_values = np.mean(absolute_values)

        # 指定要生成的数组的数据量
        sample_size = len(change_data)

        # 指定均值和标准差
        mean = np.mean(change_data)
        std_dev = np.std(change_data)

        # 创建一个传递的空数组
        two_dimensional_array = []

        # 保存原有数据
        data_daluan = change_data

        # 随机打乱数组的顺序
        for i in range(number_expand - 1):
            np.random.shuffle(data_daluan)
            two_dimensional_array.append(data_daluan)
            data_daluan = change_data

        # 创建一个空列表
        change_data_over = []

        for i in range(sample_size):
            change_data_over.append(change_data[i])
            for j in range(number_expand - 1):
                change_data_over.append(two_dimensional_array[j][i])

        # 将列表转换为 NumPy 数组
        change_data_over = np.array(change_data_over)

        new_data_out = combined_data_interpolated.real + change_data_over

        return new_data_out, average_of_absolute_values

    # 同分布扩充数据
    def Fourier_filter_same(self, original_data, cutoff_frequency, number_expand, time_step_original):

        original_data = np.array(original_data)
        # 原始数据时间步常
        time_step_original = float(time_step_original)

        number_expand = int(number_expand)

        original_data_len = int(len(original_data)/2)
        # 要滤掉的以上的频率
        cutoff_frequency = int(cutoff_frequency)
        cutoff_frequency = int(original_data_len * cutoff_frequency / 100 )

        # 生成随机数
        np.random.seed(0)  # 设置随机数种子以确保可重复性
        num_points = len(original_data)

        total_time_original = num_points * time_step_original - 0.000001    # 这里有一个精度误差，要减去
        t_original = np.arange(0, total_time_original, time_step_original)


        # 执行傅立叶变换
        fft_result = np.fft.fft(original_data)

        # 设置需要滤波的高频分量为零（示例中保留前10个频率分量，其他设为零）
        fft_result[cutoff_frequency+1:-cutoff_frequency] = 0

        # 执行傅立叶逆变换，将数据从频域转换回时域
        filtered_data = np.fft.ifft(fft_result)

        # 计算新的时间步长和总时间（加密后的）
        time_step_new = time_step_original / number_expand
        total_time_new = total_time_original
        t_new = np.arange(0, total_time_new, time_step_new)


        # 插值以获得更高时间分辨率的数据
        combined_data_interpolated = np.interp(t_new, t_original, filtered_data)
        

        # 原始数据减去滤波数据
        change_data = original_data - filtered_data.real

        # 检验
        # 取绝对值
        absolute_values = np.abs(change_data)

        # 计算绝对值后的数组的平均值
        average_of_absolute_values = np.mean(absolute_values)


        # 指定要生成的数组的数据量
        sample_size = len(change_data)

        # 指定均值和标准差
        mean = np.mean(change_data)
        std_dev = np.std(change_data)

        # 创建一个传递的空数组
        two_dimensional_array = []

        for i in range(number_expand - 1):
            new_data = np.random.normal(mean, std_dev, sample_size)
            two_dimensional_array.append(new_data)

        # 创建一个空列表
        change_data_over = []

        for i in range(sample_size):
            change_data_over.append(change_data[i])
            for j in range(number_expand - 1):
                change_data_over.append(two_dimensional_array[j][i])

        # 将列表转换为 NumPy 数组
        change_data_over = np.array(change_data_over)

        new_data_out = combined_data_interpolated.real + change_data_over

        return new_data_out, average_of_absolute_values


