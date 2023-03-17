import sys
import numpy as np
from A_property import Property
from A_pre_calculate import CalculateFunc
from Utils import Utils
from Robot import Robot

class IOProcess(object):
    def __init__(self):

        self.start_flag = False  # 开始标志
        self.server_info = []    # 存储接受信息

        self.preCalculate = CalculateFunc()  #计算模块
        self.robot_state_list = []         # 机器人list
        self.machine_list = [] # 工作台list
        self.machine_state_dict = {1: [], 2: [], 3: [], 4: [],  # {key:工作台类型(int),value:[坐标(x,y),剩余生产时间（帧数）,原材料格状态,产品格状态]}
                                   5: [], 6: [], 7: [], 8: [], 9: []}  # 工作台按型号list
        self.receive_state_dict = {1: [], 2: [], 3: [], 4: [],  # {key:物品类型(int),value:[坐标(x,y),剩余生产时间（帧数）,原材料格状态,产品格状态]}
                                   5: [], 6: [], 7: []}  # 能接受该物品类型的工作台list
        # self.sale_count = []
        # self.buy_count = []
        # self.forward_count = []
        # self.rotate_Count = []

        self.frame_id = 1       #帧数
        self.current_money = 200000  #钱
        self.k = 0  #机器数量
        
        # self.control = Controlclass() #
        
    # # def initialize(self):
    # #     # 初始化

    # def start(self):

    def getInfoFromServer(self):
        try:
            # util = Utils()
            i = 1
            while True:
                input_str = ' '
                while input_str != 'OK':  # 读到OK跳出循环
                    input_str = input()
                    self.server_info.append(input_str)
                self.server_info.pop(-1)  # 删掉OK
                sys.stderr.write(self.server_info+'\n')
                if (self.start_flag):  # 如果不是开始
                    self.getInfo(self.server_info)  # 更新工位和小车信息
                    # sys.stderr.write(str(self.robot_state_list))
                    # sys.stderr.write(str(self.machine_state_dict))
                    for i in range(len(self.robot_state_list)):
                        robot = self.robot_state_list(i)
                        at_machine = self.robot_state_list[i][0]
                        take_obj = self.robot_state_list[i][1]
                        if (take_obj == 0):
                            # 没带东西
                            pass
                        else:
                            for machine in self.receive_state_dict[take_obj]:
                                if machine.receive(take_obj):
                                    robot.move(machine) # 到这个machine这里去


                    # sys.stderr.write(str(self.frame_id))

                    # **************************************************

                    #
                    # 想法1： 这里调用控制模块 self.control 
                    # IO demo_1的数据结构：
                    # self.robot_state_list(type:list):  [[xxx ,xxx ,xxx ,.....],[....]*3] [所处工作台ID 携带物品类型 时间价值系数 碰撞价值系数 角速度 线速度x 线速度y 朝向 坐标x 坐标y]   
                    # self.machine_state_dict(type:dictionary): {key:工作台类型(int),value:[[type1_1] ,[type2_2],...]}  [typex_x]:[坐标(x,y),剩余生产时间（帧数）,原材料格状态(二进制,哪位为1代表哪位原材料格有东西),产品格状态]
                    # 其他参数:   帧数:self.frame_id   当前的钱:self.current_money     工作台数量: self.k 
                    
                    # **************************************************


                    # self.outputInfo(xxx,xxx,......)

                    self.finish()
                else:
                    self.getMap(self.server_info)  # 如果是开始就读地图信息
                    self.finish()

        except EOFError: #时间到
            pass

    def outputInfo(self):
        print()  # 帧ID
        print('forward', '')

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

        self.infoUpdateRobotList(server_info[2 + int(self.k): 2 + int(self.k) + 4])

        self.server_info = []

    def infoUpdateMachineDict(self, server_info_machine):

        for index_row, line in enumerate(server_info_machine):  # 工位信息行
            data_line = list(map(float, line.strip("\n").split()))  # str转int 这里面从txt读的穿捡来的data_line全是文本，不知道到时候服务器传进来的是整数还是文本
            
            

            machine_type = data_line[0]  # 型号
            
            # 找到型号key:machineType对应的list[[x1,y1,0,0,0],[x2,y2,0,0,0],[x3,y3,0,0,0]....]
            machine_type_list = self.machine_state_dict[machine_type]
            
            for i in range(len(machine_type_list)):             # 获取该型号机器人的个数，遍历该型号的list，找到对应的机器人
                if (data_line[1] == machine_type_list[i][0]):   # x坐标一样，所以这里要int()一下
                    if (data_line[2] == machine_type_list[i][1]):  # y坐标一样
                        # 对应的型号machinetype的机器人i更新
                        machine_type_list[i] = [
                            data_line[1], data_line[2], data_line[3], data_line[4], data_line[5]]
                        # 对应的型号machinetype更新
                        self.machine_state_dict[machine_type] = machine_type_list
                        break
                    else:
                        continue
                else:
                    continue


    def infoUpdateRobotList(self, server_info_robot):

        for index_row, line in enumerate(server_info_robot):  # 机器人信息行
            data_line = list(map(float, line.strip("\n").split())  
                             )
            self.robot_state_list[index_row] = data_line

    def getMap(self, content): #初始化数据结构

        self.start_flag = True

        for index_row, line in enumerate(content):
            data_line = line.strip("\n").split()  
            for index_cal, map_char in enumerate(data_line[0]):
                if (map_char != '.'):
                    if (map_char == 'A'):
                        # self.robot_state_list.append(
                        #     self.preCalculate.calculateRobot([100-index_row, index_cal]))
                        self.robot_state_list.append(Robot(data_line[0], data_line[1], data_line[2], data_line[3], data_line[4])
                    else:
                        self.mapUpdateDict(
                            int(map_char), self.machine_state_dict, index_row, index_cal)  # 更新字典
        self.mapFinalUpdateDict()

        self.server_info = []

    def mapUpdateDict(self, machine_type, machine_state_dict, index_row, index_cal): #初始化数据结构step2

        Loc = machine_state_dict[machine_type]
        loc_with_index = self.preCalculate.calculateMap(
            [99-index_row, index_cal])
        Loc.append(loc_with_index)
        machine_state_dict[machine_type] = Loc

    def mapFinalUpdateDict(self):  # 去除地图中没出现的型号的Machine，初始化数据结构step3
        for i in range(9):
            if (self.machine_state_dict[i+1] == []):
                self.machine_state_dict.pop(i+1, None)

    def finish(self):
        sys.stdout.write('OK\n')
        sys.stdout.flush()



    # def finishTest(self):
    #     sys.stdout.write('%d\n' % int(self.frame_id))
    #     line_speed, angle_speed = 3, 1.5
    #     for robot_id in range(4):
    #         sys.stdout.write('forward %d %d\n' % (robot_id, line_speed))
    #         sys.stdout.write('rotate %d %f\n' % (robot_id, angle_speed))
    #     self.finish()
