import sys
import numpy as np
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QFileDialog
from PyQt5.QtCore import QThread, pyqtSignal
from datetime import datetime
from wrf import *
from bts_change import *

# 子线程3
class replacement_bts_data(QThread):
    result_signal = pyqtSignal(str)
    result_signal_2 = pyqtSignal(str)

    def __init__(self, big_bts_name, small_bts_name):
        super().__init__()

        # 读取数据
        self.big_bts_name = big_bts_name
        self.small_bts_name = small_bts_name


    def run(self):

        self.result_signal_2.emit("开始替换，请等待...")


        i = bts_big_in_small(self.big_bts_name[0], self.small_bts_name[0])
        self.result_signal_2.emit(i)
        
        self.result_signal_2.emit("执行结束！")
        self.result_signal_2.emit("_____________________________________")



# 子线程2
class run_data(QThread):
    result_signal = pyqtSignal(str)
    result_signal_2 = pyqtSignal(str)

    def __init__(self, dx_data, dy_data, dt_data, scale_factor_data, x_put_data, y_put_data, 
                    best_bts_z_data, best_bts_y_data, vtk_is_yes, vtk_is_no, same_is_checked, 
                    norm_is_checked, daluan_is_checked, multiple_number, filtering_number):
        super().__init__()

        # 读取数据
        self.dx_data = dx_data
        self.dy_data = dy_data
        self.dt_data = dt_data
        self.scale_factor_data = scale_factor_data
        self.x_put_data = x_put_data
        self.y_put_data = y_put_data
        self.best_bts_z_data = best_bts_z_data
        self.best_bts_y_data = best_bts_y_data
        self.vtk_is_yes = vtk_is_yes
        self.vtk_is_no = vtk_is_no

        self.same_is_checked = same_is_checked
        self.norm_is_checked = norm_is_checked
        self.daluan_is_checked = daluan_is_checked

        self.multiple_number = multiple_number
        self.filtering_number = filtering_number


    def run(self):

        self.result_signal_2.emit("开始执行，请等待...")

        # 创建一个对象
        case = wrf_input(ex.ph_data, ex.phb_data)

        # 输出可视化文件
        if self.vtk_is_yes == 1 and self.vtk_is_no == 0:
            self.result_signal_2.emit("正在输出地形文件，请等待...")
            i = case.vtk_output(self.dx_data, self.dy_data, ex.ph_data, ex.phb_data, self.scale_factor_data)
            self.result_signal_2.emit(i)

            self.result_signal_2.emit("正在输出风场可视化文件，请等待...")
            i = case.wrf_vtk(ex.u_wind, ex.v_wind, ex.w_wind, case.dz_wind, self.dx_data, self.dy_data)
            self.result_signal_2.emit(i)


        self.result_signal_2.emit("正在输出时间序列头文件，请等待...")
        i = case.mash_height(case.geopotential_height, case.ground_height, self.x_put_data, self.y_put_data, self.dy_data, ex.u_wind.shape[3], self.best_bts_z_data, self.best_bts_y_data)
        self.result_signal_2.emit(i)

        self.result_signal_2.emit("正在输出时间序列文件体，请等待...")
        i, j = case.Fourier_filter(ex.u_wind, ex.v_wind, ex.w_wind, self.x_put_data, self.y_put_data, self.multiple_number, self.same_is_checked, self.norm_is_checked, self.daluan_is_checked, self.filtering_number, self.dt_data)
        self.result_signal_2.emit("文件体输出完成") 

        self.result_signal_2.emit("滤波测试 0.5 - 0.2") 
        self.result_signal_2.emit("#_______________________#") 
        self.result_signal_2.emit(str(i))
        self.result_signal_2.emit(str(j))
        self.result_signal_2.emit("#_______________________#") 

        self.result_signal_2.emit("执行结束！")
        self.result_signal_2.emit("_____________________________________")


# 子线程1（读取文件）
class open_data(QThread):
    result_signal = pyqtSignal(str)
    result_signal_2 = pyqtSignal(str)

    def __init__(self, file_name):
        super().__init__()
        self.file_name = file_name

    def run(self):
        self.result_signal_2.emit("正在读取，请稍等...")


        number = 0
        
        # 现在sorted_file_paths中的文件路径按照数字大小从小到大排列
        for file_path in self.file_name:

            number += 1
            data = xr.open_dataset(file_path, engine="netcdf4")  # 尝试使用netcdf4引擎打开文件

            u_wind_1 = data['U']  # 东西向风分量
            v_wind_1 = data['V']  # 南北向风分量
            w_wind_1 = data['W']  # 垂直向上的风分量
            ph_wind_1 = data['PH']
            phb_wind_1 = data['PHB']


            u_data_1 = u_wind_1.values  # 获取u风速的数据
            v_data_1 = v_wind_1.values  # 获取v风速的数据
            w_data_1 = w_wind_1.values  # 获取w风速的数据
            ph_data_1 = ph_wind_1.values  
            phb_data_1 = phb_wind_1.values 


            u_data_2 = np.array(u_data_1)  # 转换u风速的数据
            v_data_2 = np.array(v_data_1)  # 转换v风速的数据
            w_data_2 = np.array(w_data_1)  # 转换w风速的数据
            ph_data_2 = np.array(ph_data_1)
            phb_data_2 = np.array(phb_data_1)  
          

            #修整数组形状，使其长度相等。
            u_data_2 = u_data_2[:, :, :, :-1]
            v_data_2 = v_data_2[:, :, :-1, :]
            w_data_2 = w_data_2[:, :-1, :, :]
            ph_data_2 = ph_data_2[:, :-1, :, :]
            phb_data_2 = phb_data_2[:, :-1, :, :]

            #判断是否拼接
            if number == 1:

                u_data = u_data_2  # 获取u风速的数据
                v_data = v_data_2  # 获取v风速的数据
                w_data = w_data_2  # 获取w风速的数据
                ph_data = ph_data_2  # 获取w风速的数据
                phb_data = phb_data_2  # 获取w风速的数据


            else:

                if u_data.shape[1] == u_data_2.shape[1] and \
                   u_data.shape[2] == u_data_2.shape[2] and \
                   u_data.shape[3] == u_data_2.shape[3]:


                    self.result_signal_2.emit("维度长度相等")
                else:
                    self.result_signal_2.emit("错误：维度不相同！")
                    self.result_signal_2.emit("请重新选择数据")

                #拼接数据
                u_data = np.concatenate((u_data, u_data_2), axis=0)
                v_data = np.concatenate((v_data, v_data_2), axis=0)
                w_data = np.concatenate((w_data, w_data_2), axis=0)
                ph_data = np.concatenate((ph_data, ph_data_2), axis=0)
                phb_data = np.concatenate((phb_data, phb_data_2), axis=0)


        #数据重组使其维度为t，x，y，z
        ex.u_wind = np.transpose(u_data, (0, 3, 2, 1))
        ex.v_wind = np.transpose(v_data, (0, 3, 2, 1))
        ex.w_wind = np.transpose(w_data, (0, 3, 2, 1))
        ex.ph_data = np.transpose(ph_data, (0, 3, 2, 1))
        ex.phb_data = np.transpose(phb_data, (0, 3, 2, 1))

        self.result_signal.emit("________________________")
        self.result_signal.emit("此风场维度：")
        self.result_signal.emit(" \n    时间步" + str(ex.u_wind.shape[0]))
        self.result_signal.emit("    X方向网数" + str(ex.u_wind.shape[1]))
        self.result_signal.emit("    Y方向网数" + str(ex.u_wind.shape[2]))
        self.result_signal.emit("    Z方向网数" + str(ex.u_wind.shape[3]))
        self.result_signal.emit("________________________")
        self.result_signal.emit("\n")
        self.result_signal_2.emit("读取完成")


# 主线程
class FileOpener(QMainWindow):
    def __init__(self):
        super().__init__()

        self.initUI()
        # 其他初始化代码

    def initUI(self):
        # 读取ui文件
        self.ui = uic.loadUi("./WRF_bts.ui")

        # 提取控件
        self.open_data = self.ui.pushButton         # 打开文件按钮
        self.textBrowser = self.ui.textBrowser      # 文本显示区域1
        self.textBrowser_2 = self.ui.textBrowser_2  # 文本显示区域2
        self.dx = self.ui.lineEdit                  # 网格dx
        self.dy = self.ui.lineEdit_2                # 网格dy
        self.dt = self.ui.lineEdit_3                # 时间步长
        self.scale_factor = self.ui.lineEdit_4      # 网格高度缩放系数
        self.x_put = self.ui.lineEdit_5             # 放置位置x
        self.y_put = self.ui.lineEdit_6             # 放置位置y
        self.best_vertical_bts = self.ui.lineEdit_7 # 处理高度
        self.best_level_bts = self.ui.lineEdit_8    # 处理宽度
        self.run_ing = self.ui.pushButton_2         # 开始运行

        self.same = self.ui.radioButton             # 同分布按钮
        self.norm = self.ui.radioButton_2           # 正态分布按钮
        self.daluan = self.ui.radioButton_3         # 打乱分布按钮

        self.vtk_yes = self.ui.radioButton_4        # 可视化输出按钮
        self.vtk_no = self.ui.radioButton_5         # 可视化不输出按钮

        self.multiple = self.ui.lineEdit_9          # 扩充倍数
        self.filtering = self.ui.lineEdit_10        # 滤波

        self.open_big_bts = self.ui.pushButton_3    # 打开大bts文件按钮
        self.open_small_bts = self.ui.pushButton_4    # 打开小bts文件按钮

        self.replacement_bts = self.ui.pushButton_5    # 打开小bts文件按钮

        # 设置初始文本
        # 获取当前时间
        current_time = datetime.now()

        self.textBrowser_2.append("++++++++++++++++++++++++++++++++++++")
        self.textBrowser_2.append("WRF_bts")
        self.textBrowser_2.append("版本：1.0")
        self.textBrowser_2.append("当前时间: {}".format(current_time))
        self.textBrowser_2.append("++++++++++++++++++++++++++++++++++++")
        self.textBrowser_2.append("")
        self.textBrowser_2.append("")



        # 连接按钮的点击事件到openFile函数
        # 打开文件按钮绑定
        self.open_data.clicked.connect(self.openFile)

        # 运行按钮绑定
        self.run_ing.clicked.connect(self.data_run_ing)

        # 打开最大bts按钮绑定
        self.open_big_bts.clicked.connect(self.open_big_Bts)

        # 打开最大bts按钮绑定
        self.open_small_bts.clicked.connect(self.open_small_Bts)

        # 替换bts按钮绑定
        self.replacement_bts.clicked.connect(self.replacement_Bts)
        
        # 判断是否可以替换bts文件
        self.open_1 = 0
        self.open_2 = 0



    def open_big_Bts(self):
        
        # 打开大bts文件
        options = QFileDialog.Options()

        file_name, _ = QFileDialog.getOpenFileNames(self, "打开文件", "", "All Files (*);;Text Files (*.txt)", options=options)       

        self.big_bts_name = file_name
        if self.big_bts_name:
            self.textBrowser_2.append("大bts文件读取成功")
            self.open_1 = 1

    def open_small_Bts(self):
        
        # 打开小bts文件
        options = QFileDialog.Options()

        file_name, _ = QFileDialog.getOpenFileNames(self, "打开文件", "", "All Files (*);;Text Files (*.txt)", options=options)       

        self.small_bts_name = file_name
        if self.small_bts_name:
            self.textBrowser_2.append("小bts文件读取成功")
            self.open_2 = 1

    def replacement_Bts(self):

        if self.open_1 == 1 and self.open_2 == 1:

            # 创建一个线程(子线程3)
            self.replacement_bts_data = replacement_bts_data(self.big_bts_name, self.small_bts_name)

            # 建立信号与槽
            self.replacement_bts_data.result_signal.connect(self.display_result)
            self.replacement_bts_data.result_signal_2.connect(self.display_result_2)
            self.replacement_bts_data.start()
        else:
            self.textBrowser_2.append("错误！")
            self.textBrowser_2.append("bts文件未读取")
        


    #打开文件夹读取文件函数
    def openFile(self):

        # 打开文件
        options = QFileDialog.Options()

        file_name, _ = QFileDialog.getOpenFileNames(self, "打开文件", "", "All Files (*);;Text Files (*.txt)", options=options)

        if file_name:
            # 创建一个线程(子线程1)
            self.open_data = open_data(file_name)

            # 建立信号与槽
            self.open_data.result_signal.connect(self.display_result)
            self.open_data.result_signal_2.connect(self.display_result_2)
            self.open_data.start()

    def data_run_ing(self):

        # 提取ui上的输入值
        self.dx_data = self.dx.text()
        self.dy_data = self.dy.text()
        self.dt_data = self.dt.text()
        self.scale_factor_data = self.scale_factor.text()
        self.x_put_data = self.x_put.text()
        self.y_put_data = self.y_put.text()
        self.best_bts_z_data = self.best_vertical_bts.text()
        self.best_bts_y_data = self.best_level_bts.text()

        self.multiple_number = self.multiple.text()
        self.filtering_number = self.filtering.text()



        # 判断vtk是否输出
        vtk_yes_checked = self.vtk_yes.isChecked()
        vtk_no_checked = self.vtk_no.isChecked()

        if vtk_yes_checked:
            self.vtk_is_yes = 1
            self.vtk_is_no = 0
        elif vtk_no_checked:
            self.vtk_is_yes = 0
            self.vtk_is_no = 1
        else:
            self.vtk_is_yes = 0
            self.vtk_is_no = 0

        # 判断扩充方式
        same_checked = self.same.isChecked()
        norm_checked = self.norm.isChecked()
        daluan_checked = self.daluan.isChecked()

        if same_checked:
            self.same_is_checked = 1
            self.norm_is_checked = 0
            self.daluan_is_checked = 0
        elif norm_checked:
            self.same_is_checked = 0
            self.norm_is_checked = 1
            self.daluan_is_checked = 0
        elif daluan_checked:
            self.same_is_checked = 0
            self.norm_is_checked = 0
            self.daluan_is_checked = 1
        else:
            self.same_is_checked = 0
            self.norm_is_checked = 0
            self.daluan_is_checked = 0

        

        # 判断有没有设置，如果没有设置就输出：设置错误！
        if (not self.dx_data or
            not self.dy_data or
            not self.dt_data or
            not self.scale_factor_data or
            not self.x_put_data or
            not self.y_put_data or
            not self.best_bts_z_data or
            not self.best_bts_y_data or
            not self.multiple_number or
            not self.filtering_number):
            self.textBrowser_2.append("设置错误！")
        else:
            # 创建一个线程(子线程2)
            self.run_data = run_data(self.dx_data, self.dy_data, self.dt_data, 
                                        self.scale_factor_data, self.x_put_data, 
                                        self.y_put_data, self.best_bts_z_data, 
                                        self.best_bts_y_data, self.vtk_is_yes, 
                                        self.vtk_is_no, self.same_is_checked,
                                        self.norm_is_checked, self.daluan_is_checked,
                                        self.multiple_number, self.filtering_number)

            # 建立信号与槽
            self.run_data.result_signal.connect(self.display_result)
            self.run_data.result_signal_2.connect(self.display_result_2)
            self.run_data.start()


    def display_result(self, result):
        # 更新结果标签
        self.textBrowser.append(result)

        #self.result_label.setText(result)
    def display_result_2(self, result):
        # 更新结果标签
        self.textBrowser_2.append(result)

# 运行部分
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = FileOpener()
    ex.ui.show()
    sys.exit(app.exec_())
