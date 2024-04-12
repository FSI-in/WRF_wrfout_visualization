from pyFAST.input_output import TurbSimFile
import os
import numpy as np
from pyevtk.hl import gridToVTK

big_bts = '/home/in/cold/wrf_new/da.bts'
small_bts = '/home/in/cold/wrf_new/xiao.bts'




ts_big = TurbSimFile(big_bts)
ts_small = TurbSimFile(small_bts)


# 计算去边
i_stand = (ts_big['u'][1].shape[1] - ts_small['u'][1].shape[1])/2


# 化整
i_stand = int(i_stand)


# 替换数据
for t in range(ts_big['u'][1].shape[0]):
	for i in range(ts_small['u'][1].shape[1]):
		for j in range(ts_small['u'][1].shape[2]):

			ts_small['u'][0, t, i, j] = ts_big['u'][0, t, i + i_stand, j]
			ts_small['u'][1, t, i, j] = ts_big['u'][1, t, i + i_stand, j]
			ts_small['u'][2, t, i, j] = ts_big['u'][2, t, i + i_stand, j]

output_directory = 'bts输出文件/'
if not os.path.exists(output_directory):
	os.makedirs(output_directory)

ts_small.write('bts输出文件/New_small.bts')
