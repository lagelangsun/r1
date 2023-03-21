import sys
import numpy as np
from A_property import Property
from A_pre_calculate import CalculateFunc
from A_machine import Machine
from A_robot_demo1 import Robot
from A_control_demo1 import Control
from A_decision_demo1 import Decision
import time

RECEIVE_MACHINE_ID_LIST = {1: [4, 5, 9], 2: [4, 6, 9], 3: [5, 6, 9], 4: [7, 9],
                           5: [7, 9], 6: [7, 9], 7: [8, 9]}


class IOProcess(object):
    def __init__(self):
        # self.flag = 1 # 判断是否跳帧
        self.start_flag = False  # 开始标志
        self.server_info = []    # 存储接受信息

        self.robot_state_list = []                                      # 机器人list

        self.machine_state_dict = {1: [], 2: [], 3: [], 4: [],          # {key:工作台类型(int),value:[坐标(x,y),剩余生产时间（帧数）,原材料格状态,产品格状态]}
                                   5: [], 6: [], 7: [], 8: [], 9: []}   # 工作台按型号list
        self.machine_sort_by_receive = {1: [], 2: [], 3: [], 4: [],     # 按接收原料种类
                                        5: [], 6: [], 7: []}
        self.receivetype_for_machinetype = {4: [1, 2], 5: [1, 3], 6: [2, 3]  # switch case
                                            , 7: [4, 5, 6], 8: [7], 9: [1, 2, 3, 4, 5, 6, 7]}
        self.machine_index_to_type_list = []     # 按工作台id排序的list

        self.machine_state_dict_id = {1: [], 2: [], 3: [], 4: [],   # 各类型工作台包含的id
                                      5: [], 6: [], 7: [], 8: [], 9: []}

        self.machine_num_of_type = {}
        self.interupt_4567 = []

        self.frame_id = 1  # 帧数
        self.current_money = 200000  # 钱
        self.k = 0  # 机器数量
        # self.product_status_456_dcit = []

        self.preCalculate = CalculateFunc()     # 计算模块

        # self.control = Controlclass() #

    # ***********************************启动，程序运行主方法********************************
    def getInfoFromServer(self):
        try:
            while True:
                input_str = ' '
                while input_str != 'OK':  # 读到OK跳出循环
                    input_str = input()
                    self.server_info.append(input_str)
                self.server_info.pop(-1)  # 删掉OK
                # sys.stderr.write('serverinfo' + str(self.server_info) + '\n')
                # sys.stderr.write('mapinfo' + str(self.machine_index_to_type_list) + '\n')

                ############################lhf##############################
                # ***************************调用决策控制模块*****************************************
                if (self.start_flag):  # 如果不是开始

                    self.getInfo(self.server_info)  # 更新工位和小车信息
                    sys.stdout.write('%d\n' % (self.frame_id))

                    self.decesion.decesion(self.robot_state_list
                                           , self.machine_state_dict
                                           , self.machine_sort_by_receive
                                           , self.machine_index_to_type_list
                                           , self.interupt_4567
                                           )  # 需要小车信息，需要工位信息 demo1:只考虑没有9的情况

                    self.clear4567Products() # 用完就擦除
                    self.finish()

                else:
                    self.getMap(self.server_info)  # 如果是开始就读地图信息
                    self.finish()

        except EOFError:  # 时间到
            pass

    # ****************************************信息更新*********************************************
    def getInfo(self, server_info):

        # 第一行输入 2 个整数，表示帧序号（从 1 开始递增）、当前金钱数。
        # 第二行输入 1 个整数，表示场上工作台的数量 K（K<=50）。
        # 紧接着 K 行数据，每一行表示一个工作台，分别由如下所示的数据构成，共计 6 个数字：
        # 接下来的 4 行数据，每一行表示一个机器人，分别由如下表格中所示的数据构成，每行 10 个数字。
        # 最后，判题器会输出一行 OK，表示所有数据已经写入完毕。

        data_line_0 = server_info[0].strip("\n").split()
        self.frame_id = int(data_line_0[0])
        self.current_money = int(data_line_0[1])
        self.k = int(server_info[1].strip("\n").split()[0])

        self.infoUpdateMachineDict(server_info[2:2+int(self.k)])

        self.infoUpdateRobotList(
            server_info[2 + int(self.k): 2 + int(self.k) + 4])

        self.server_info = []

    # *****更新工作台参数******
    def infoUpdateMachineDict(self, server_info_machine):  # 更新工作台参数,更新两个字典

        # 工作台信息行,index_row的值就是工作台id
        for index_row, line in enumerate(server_info_machine):

            # str转int 这里面从txt读的穿捡来的data_line全是文本，不知道到时候服务器传进来的是整数还是文本
            data_line = list(map(float, line.strip("\n").split()))

            machine_type = data_line[0]  # 型号

            self.infoUpdateMachineStateDict(machine_type, index_row, data_line)

            if(machine_type >= 4):  # 更新按接收分类的字典，我有个问题，是不是更新一次就行了，因为是取地址，所以这个根本不用更新，一次更新就全体更新了******************
                self.infoUpdateMachineSortByRecive(
                    machine_type, index_row, data_line)
                
            if machine_type in (4, 5, 6, 7):  # 如果是4,5,6,7型号的,判断是否生产完毕
                if data_line[5]: # 更新是否生产完毕list，list里面直接append进这个工作台对象去
                    self.infoUpdate4567Products(machine_type, index_row)

    # 更新machine_state_dict
    def infoUpdateMachineStateDict(self, machine_type, index_row, data_line):

        #找到key型号对应的value list,更改这个list可以直接更改dictkey对应的list，dict是对象传递
        machine_type_list = self.machine_state_dict[machine_type]

        # 遍历key[machine_type]对应的list，找到与行相对应的id ,每个id对应的行号都是固定的
        for machine_type_list_class in machine_type_list:
            if machine_type_list_class.id == index_row:     # 从工作台信息行开始第n行对应的就是第n个实例化的class，这个class.id == n
                machine_type_list_class.update(data_line[1:6])  # 更新
                break

    # 更新machine_sort_by_receive字典
    def infoUpdateMachineSortByRecive(self, machine_type, index_row, data_line):
        # 遍历接收该原料的所有Machine，找到对应的id更新
        # machine型号对应的接收原料种类
        for receive_type in self.receivetype_for_machinetype[machine_type]:
            for receive_sort_class in self.machine_sort_by_receive[receive_type]:
                if(receive_sort_class.id == index_row):
                    receive_sort_class.update(data_line[1:6])

    def infoUpdate4567Products(self, machine_type, index_row):
        self.interupt_4567.append(self.machine_index_to_type_list[index_row]
            )  # 把生产好了的工作台类加到list中.

    def clear4567Products(self):  # 每次更新完后都应该清空这个，
        self.interupt_4567 = []
        #其实更符合逻辑的方法是每一帧改变值而不是清空，但是这样的话在决策的时候还要遍历一遍这些找到值为1的，所以相当于遍历了两边，符合逻辑但是时间复杂度高

    # *****更新机器人参数******

    def infoUpdateRobotList(self, server_info_robot):

        for index_row, line in enumerate(server_info_robot):  # 机器人信息行
            data_line = list(map(float, line.strip("\n").split())
                             )
            self.robot_state_list[index_row].update(
                data_line)  # 直接按行更新，因为是按行初始化的

    # ************************************初始化数据结构*****************************************

    def getMap(self, content):  # 读地图，初始化数据结构step1
        self.start_flag = True

        for index_row, line in enumerate(content):
            data_line = line.strip("\n").split()
            for index_cal, map_char in enumerate(data_line[0]):
                if (map_char != '.'):
                    if (map_char == 'A'):
                        self.robot_state_list.append(
                            Robot(self.preCalculate.calculateLoc(
                                [99-index_row, index_cal]))
                        )  # Robot(x,y)
                    else:
                        self.mapUpdateDict(
                            int(map_char), index_row, index_cal)  # 更新字典

        self.mapFinalUpdateDict()
        self.decesion = Decision(self.machine_num_of_type)  # 创建Decision模块
        self.server_info = []

    # 更新machine的x,y,type 初始化数据结构step2
    def mapUpdateDict(self, machine_type, index_row, index_cal):

        # 找到key[machine_type]对应的list: [class1,class2,....]
        machine_loc = self.machine_state_dict[machine_type]

        machine_loc.append(
            Machine(machine_type, self.preCalculate.calculateLoc([99-index_row, index_cal])
                    # ,self.preCalculate.judgeReceiveType(machine_type)  #传入machine_type对应的receive_type ,一个list
                    )  # Machine(type,x,y)
        )

        self.machine_index_to_type_list.append(
            machine_loc[-1])  # 按machine_id加到index_list里

        # machine_loc[-1]: 刚添加的Machine Class，遍历对应表看接收哪几种原料
        if (machine_type >= 4):
            for receive_type in self.receivetype_for_machinetype[machine_type]:
                self.machine_sort_by_receive[receive_type].append(
                    machine_loc[-1])  # 添加到machine_sort_by_receive
                # sys.stderr.write(str(machine_loc[-1])+'\n')

    def mapFinalUpdateDict(self):  # 去除地图中没出现的型号的Machine，初始化数据结构step3
        for i in range(9):
            if (self.machine_state_dict[i+1] == []):
                self.machine_state_dict.pop(i+1, None)

        for i in range(7):
            if (self.machine_sort_by_receive[i+1] == []):
                self.machine_sort_by_receive.pop(i+1, None)

        for i in self.machine_state_dict:
            self.machine_num_of_type[i] = len(self.machine_state_dict[i])
    # *********************************输出到服务器信息****************************************

    def finish(self):
        sys.stdout.write('OK\n')
        sys.stdout.flush()

    # def outputInfo(self):
    #     print()  # 帧ID
    #     print('forward', '')
