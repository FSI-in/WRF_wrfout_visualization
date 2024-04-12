import xarray as xr
from pyevtk.hl import gridToVTK
import os
import numpy as np
import vtkmodules.all as vtk
from scipy import stats
import matplotlib.pyplot as plt
import pandas as pd
import openpyxl
from expand import *



class wrf_input:
    def __init__(self, ph_data, phb_data):
        
        # 获取地面高度（地势高度）
        geopotential_height = (ph_data + phb_data) / 9.81

        self.geopotential_height = geopotential_height

        # 计算每个网格层的高度厚度（dz）
        dz_data = geopotential_height[:, :, :, 1:] - geopotential_height[:, :, :, :-1]

        # 获取地面高度
        ground_height = geopotential_height[:, :, :, 0]

        self.ground_height = ground_height

        # 计算每个网格层的物理厚度
        physical_thickness = geopotential_height - ground_height[:, :, :, np.newaxis]

        # 网格高度数据
        self.dz_wind = physical_thickness

    # 输出可视化地形文件
    def vtk_output(self, dx, dy, ph_data, phb_data, zoom_factor):

        # 转换为浮点数
        dx = float(dx)
        dy = float(dy)
        zoom_factor = float(zoom_factor)

        # 获取地面高度（地势高度）
        geopotential_height = (ph_data + phb_data) / 9.81

        self.geopotential_height = geopotential_height

        # 计算每个网格层的高度厚度（dz）
        dz_data = geopotential_height[:, :, :, 1:] - geopotential_height[:, :, :, :-1]

        # 获取地面高度
        ground_height = geopotential_height[:, :, :, 0]

        self.ground_height = ground_height

        # 计算每个网格层的物理厚度
        physical_thickness = geopotential_height - ground_height[:, :, :, np.newaxis]

        # 网格高度数据
        self.dz_wind = physical_thickness

        ground_heightm = np.array(ground_height)

        # 选择一个时间步骤，例如第一个时间步骤
        time_step = 0

        # 获取对应于指定时间步骤的高度数据
        Z = ground_heightm[time_step, :, :] * zoom_factor

        # 获取 x 和 y 的范围
        x_min, x_max = 0, ground_heightm.shape[1] * dx
        y_min, y_max = 0, ground_heightm.shape[2] * dy

        # 获取 x 和 y 的分辨率
        x_resolution = ground_heightm.shape[1]  # 假设 x 和 y 具有相同的分辨率
        y_resolution = ground_heightm.shape[2]  # 假设 x 和 y 具有相同的分辨率

        # 创建 x 和 y 坐标数组
        x = np.linspace(x_min, x_max, x_resolution)
        y = np.linspace(y_min, y_max, y_resolution)

        # 创建 X 和 Y 网格
        Y, X = np.meshgrid(y, x)


        # 现在，Z 包含了与 X 和 Y 对应的高度数据

        # 创建vtkPoints

        # 确保 "地形" 文件夹存在，如果不存在则创建它
        output_folder = "地形"
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        # 创建vtkPoints
        points = vtk.vtkPoints()

        for i in range(x_resolution):
            for j in range(y_resolution):
                points.InsertNextPoint(X[i, j], Y[i, j], Z[i, j])

        # 创建vtkPolyData
        wave_surface = vtk.vtkPolyData()
        wave_surface.SetPoints(points)

        # 创建面
        faces = vtk.vtkCellArray()
        for i in range(x_resolution - 1):
            for j in range(y_resolution - 1):
                v0 = i * y_resolution + j
                v1 = v0 + 1
                v2 = v0 + y_resolution
                v3 = v2 + 1
                quad = vtk.vtkQuad()
                quad.GetPointIds().SetId(0, v0)
                quad.GetPointIds().SetId(1, v1)
                quad.GetPointIds().SetId(2, v3)
                quad.GetPointIds().SetId(3, v2)
                faces.InsertNextCell(quad)

        # 将面添加到vtkPolyData
        wave_surface.SetPolys(faces)

        # 创建vtkPolyDataWriter
        writer = vtk.vtkPolyDataWriter()
        output_file = "topographic.vtk"  # 设置文件名
        output_file_path = os.path.join(output_folder, output_file)  # 设置输出文件路径
        writer.SetFileName(output_file_path)
        writer.SetInputData(wave_surface)

        # 写入VTK文件
        writer.Write()

        return "地形表面已保存"

    # 输出可视化风场vtk文件
    def wrf_vtk(self, u_wind, v_wind, w_wind, dz_wind, dx, dy):
        
        dx = float(dx)
        dy = float(dy)
        # 创建VTK文件夹
        os.makedirs("风场VTK", exist_ok=True)

        # 使用总体时间进度的进度条
        for i in range(u_wind.shape[0]):
            # 选择对应时间步的数据
            u = np.ascontiguousarray(u_wind[i])
            v = np.ascontiguousarray(v_wind[i])
            w = np.ascontiguousarray(w_wind[i])

            # 创建网格坐标
            x = np.linspace(0, dx*u_wind.shape[1], u_wind.shape[1])
            y = np.linspace(0, dy*u_wind.shape[2], u_wind.shape[2])
            dz = dz_wind[0, 0, 0, 1:]
            z = np.cumsum(dz)

            # 保存为VTK文件
            output_file = os.path.join("风场VTK", f'output_{i:04d}.vtk')  # 文件名中包含时间步索引，并保存到VTK文件夹中
            gridToVTK(output_file, x, y, z, pointData={'velocity': (u, v, w)})  

        return "风场可视化输出完成"

    # 计算查找网格位置，输出时序头文件
    def mash_height(self, geopotential_height, ground_height, x_location, y_location, dy, z_cell_number, z_max_bts, y_max_bts):
        # 网格尺寸
        dy = float(dy)
        # 风机放置位置
        x_location = int(x_location)
        y_location = int(y_location)
        # 风力机风场宽度
        z_max_bts = float(z_max_bts)
        y_max_bts = float(y_max_bts)

        cell_half = y_max_bts / 2
        
        # 一半的网格数
        self.cell_half_number = int(cell_half // dy)
        
        # 计算每个网格层的物理厚度
        physical_thickness = geopotential_height - ground_height[:, :, :, np.newaxis]

        z_bts = 0
        for i in range(z_cell_number):
            i_int = int(i)
            z_bts += physical_thickness[0, x_location, y_location, i_int + 1]

            if z_bts >= z_max_bts:
                number = i_int
                self.number = number

                break
        z_bts = 0

        output_directory = '时序文件/'
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)

        # 打开文本文件以写入模式
        with open('时序文件/hand.txt', 'w') as file:
            for i in range(self.number):
                i_int = int(i)
                z_bts += physical_thickness[0, x_location, y_location, i_int + 1]
                for j in range(-self.cell_half_number, self.cell_half_number + 1):
                    # 写入数据到文件中
                    file.write(f"{j * dy}  {z_bts}\n")

        return "时间序列文件头已经保存"



    # 傅里叶滤波扩充数据
    def Fourier_filter(self, u_wind, v_wind, w_wind, x_location, y_location, t_number, same, norm, daluan, cutoff_frequency, time_step_original):

        # 三个方向的风速度
        u_wind = np.array(u_wind)
        v_wind = np.array(v_wind)
        w_wind = np.array(w_wind)

        # 扩充数据
        t_number = int(t_number)

        # 原始时间步长
        time_step_original = float(time_step_original)

        x_location = int(x_location)
        y_location = int(y_location)
        # 创建对象
        expand = expand_data()

        # 接收数据
        t, y, z = len(u_wind[:, x_location, y_location, 1]) * t_number, self.cell_half_number * 2 + 1, self.number

        # 用来检测的
        u_pp_max = 0
        v_pp_max = 0
        w_pp_max = 0

        # 用来检测的
        u_pp_min = 1000
        v_pp_min = 1000
        w_pp_min = 1000
        
        # 创建三维数组并初始化为浮点数
        u_my_3d_array = np.zeros((t, y, z), dtype=float)
        v_my_3d_array = np.zeros((t, y, z), dtype=float)
        w_my_3d_array = np.zeros((t, y, z), dtype=float)

        for i in range(self.number):
            for j in range(-self.cell_half_number, self.cell_half_number + 1):
                u_wind_data_point = u_wind[:, x_location, y_location + j, i + 1]
                v_wind_data_point = v_wind[:, x_location, y_location + j, i + 1]
                w_wind_data_point = w_wind[:, x_location, y_location + j, i + 1]

                # 判断那种方法扩充
                if norm == 1 and same == 0 and daluan == 0:
                    u_expand_out_data, u_pp = expand.Fourier_filter_norm(u_wind_data_point, cutoff_frequency, t_number, time_step_original)
                    v_expand_out_data, v_pp = expand.Fourier_filter_norm(v_wind_data_point, cutoff_frequency, t_number, time_step_original)
                    w_expand_out_data, w_pp = expand.Fourier_filter_norm(w_wind_data_point, cutoff_frequency, t_number, time_step_original)
                elif norm == 0 and same == 0 and daluan == 1:
                    u_expand_out_data, u_pp = expand.Fourier_filter_daluan(u_wind_data_point, cutoff_frequency, t_number, time_step_original)
                    v_expand_out_data, v_pp = expand.Fourier_filter_daluan(v_wind_data_point, cutoff_frequency, t_number, time_step_original)
                    w_expand_out_data, w_pp = expand.Fourier_filter_daluan(w_wind_data_point, cutoff_frequency, t_number, time_step_original)
                else:
                    u_expand_out_data, u_pp = expand.Fourier_filter_same(u_wind_data_point, cutoff_frequency, t_number, time_step_original)
                    v_expand_out_data, v_pp = expand.Fourier_filter_same(v_wind_data_point, cutoff_frequency, t_number, time_step_original)
                    w_expand_out_data, w_pp = expand.Fourier_filter_same(w_wind_data_point, cutoff_frequency, t_number, time_step_original)

                if u_pp > u_pp_max:
                    u_pp_max = u_pp
                if v_pp > v_pp_max:
                    v_pp_max = v_pp
                if w_pp > w_pp_max:
                    w_pp_max = w_pp

                if u_pp < u_pp_min:
                    u_pp_min = u_pp
                if v_pp < v_pp_min:
                    v_pp_min = v_pp
                if w_pp < w_pp_min:
                    w_pp_min = w_pp

                # 转换为numpy数组
                u_expand_out_data = np.array(u_expand_out_data)
                v_expand_out_data = np.array(v_expand_out_data)
                w_expand_out_data = np.array(w_expand_out_data)

                for t_t in range(t):
                    u_my_3d_array[t_t][j + self.cell_half_number][i] = u_expand_out_data[t_t]
                    v_my_3d_array[t_t][j + self.cell_half_number][i] = v_expand_out_data[t_t]
                    w_my_3d_array[t_t][j + self.cell_half_number][i] = w_expand_out_data[t_t]
                    
        output_directory = '时序文件/'
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)


        # 创建输出文件
        output_file = open('时序文件/wind_speed.txt', 'w')

        # 输出测风塔数据
        for t_t_t in range(t):
            output_line = f'{time_step_original / 4 * t_t_t:8.4f} '
            for k in range(self.number):
                for j in range(y):
                    output_line += f'{u_my_3d_array[t_t_t, j, k]:8.4f}   '
                    output_line += f'{v_my_3d_array[t_t_t, j, k]:8.4f}   '
                    output_line += f'{w_my_3d_array[t_t_t, j, k]:8.4f}   '

            output_line += '\n'
            # 替换制表符为空格
            output_line = output_line.replace('\t', ' ')
            output_file.write(output_line)

        # 关闭输出文件
        output_file.close()


        max_data = max(u_pp_max, v_pp_max, w_pp_max)
        min_data = min(u_pp_min, v_pp_min, w_pp_min)

        return max_data, min_data

