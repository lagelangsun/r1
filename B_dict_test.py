import sys
import numpy as np
import copy

machine_sort_by_receive = {1: [1,2,3], 2: [4,5], 3: [6,7], 4: [8,9],  # {key:工作台类型(int),value:[坐标(x,y),剩余生产时间（帧数）,原材料格状态,产品格状态]}
                                   5: [10,11], 6: [12,13], 7: [14,15]}  # 工作台按型号list
machine_state_dict = {1: [], 2: [], 3: [], 4: [],  # {key:工作台类型(int),value:[坐标(x,y),剩余生产时间（帧数）,原材料格状态,产品格状态]}
                                   5: [], 6: [], 7: [], 8: [], 9: []}  # 工作台按型号list
MyScore = {1: 10, 2: 20, 3: 20}  # 工作台按型号list


maxScore_name = max(MyScore, key=MyScore.get)
print(maxScore_name)

# print([machine_sort_by_receive[1],machine_sort_by_receive[2],machine_sort_by_receive[3]])
# A = [1,2,3,4,5]
# if not [value for key,value in machine_sort_by_receive.items()]:
#     print(A)
# A = [1,2,3,4,5,6]
# B = [key for key,value in machine_sort_by_receive.items()]
# if 4 in B:
#     print('sss')
# if not(15.0 in B):
#     print('aaa')
# else:
#     print('ccccc')

# b = np.array([np.sqrt(3)/3 ,np.sqrt(3)/3,np.sqrt(3)/3])
# print(b)
# constant = np.matmul(b,b.T)
# print(constant)
# c = np.matmul(b.T,b)/constant
# print(c)
# c = 2
# if(c==2) & (not (1 in A)):
#     print(A)
# else:
#     print(c)
# if B:
#     print("B1")
# C = -1
# if (C==-1) | (not B):
#     print('B2')
# for i in range(9):
#     if i in (1,2,3,4,5,6,7,8,9):
#         if i == 3:
#             continue
#         else:
#             print(i)
#         print(i)
# for i in range(9):
#     if i in machine_sort_by_receive:
#         print(i)
# for key,value in machine_state_dict.items(): #是key
#     if(key == 4):
#         for index, singal_value in enumerate(value):
#             machine_sort_by_receive[1].append(singal_value)
#             machine_sort_by_receive[2].append(singal_value)
#     if(key == 5):
#         for index, singal_value in enumerate(value):
#             machine_sort_by_receive[1].append(singal_value)
#             machine_sort_by_receive[3].append(singal_value)
#     if(key == 6):
#         for index, singal_value in enumerate(value):
#             machine_sort_by_receive[2].append(singal_value)
#             machine_sort_by_receive[3].append(singal_value)
#     if(key == 7):
#         for index, singal_value in enumerate(value):
#             machine_sort_by_receive[4].append(singal_value)
#             machine_sort_by_receive[5].append(singal_value)
#             machine_sort_by_receive[6].append(singal_value)
#     if(key == 8):
#         for index, singal_value in enumerate(value):
#             machine_sort_by_receive[7].append(singal_value)
#     if(key == 9):
#         for index, singal_value in enumerate(value):
#             for i in range(7):
#                 machine_sort_by_receive[i+1].append(singal_value)
