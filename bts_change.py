from pyFAST.input_output import TurbSimFile
import os
import numpy as np

# 读取bts文件

def bts_big_in_small(big_bts, small_bts):
	
	
	print(big_bts)
	print(small_bts)
	input("_______")
	ts_big = TurbSimFile(big_bts)
	ts_small = TurbSimFile(small_bts)

	inter_data= np.zeros((3, ts_small['u'][1].shape[0], ts_small['u'][1].shape[1], ts_small['u'][1].shape[2]))  # 创建一个3x4的零矩阵



	# 计算去边
	i_stand = (ts_big['u'][1].shape[1] - ts_small['u'][1].shape[1])/2

	# 化整
	i_stand = int(i_stand)

	# 替换数据
	for t in range(ts_big['u'][1].shape[0]):
		for i in range(ts_small['u'][1].shape[1]):
			for j in range(ts_small['u'][1].shape[2]):

				inter_data[0, t, i, j] = ts_big['u'][0, t, i + i_stand, j]
				inter_data[1, t, i, j] = ts_big['u'][1, t, i + i_stand, j]
				inter_data[2, t, i, j] = ts_big['u'][2, t, i + i_stand, j]

	for t in range(ts_big['u'][1].shape[0]):
		for i in range(ts_small['u'][1].shape[1]):
			for j in range(ts_small['u'][1].shape[2]):

				ts_small['u'][0, t, i, j] = inter_data[0, t, i, j]
				ts_small['u'][1, t, i, j] = inter_data[1, t, i, j]
				ts_small['u'][2, t, i, j] = inter_data[2, t, i, j]


	ts_small.write('success_output.bts')


	return "替换完成"

if __name__ == "__main__":
    # a = bts_change()
    bts_big_in_small("/home/in/cold/wrf_new/da.bts", "/home/in/cold/wrf_new/xiao.bts")

