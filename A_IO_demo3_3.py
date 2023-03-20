import sys
import numpy as np
from A_property import Property
from A_pre_calculate import CalculateFunc
from A_machine import Machine
from A_robot import Robot
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

        self.preCalculate = CalculateFunc()                             # 计算模块
        self.robot_state_list = []                                      # 机器人list
        self.machine_state_dict = {1: [], 2: [], 3: [], 4: [],          # {key:工作台类型(int),value:[坐标(x,y),剩余生产时间（帧数）,原材料格状态,产品格状态]}
                                   5: [], 6: [], 7: [], 8: [], 9: []}   # 工作台按型号list
        self.machine_sort_by_receive = {1: [], 2: [], 3: [], 4: [],     # 按接收原料种类
                                        5: [], 6: [], 7: []}

        self.receivetype_for_machinetype = {4: [1, 2], 5: [1, 3], 6: [2, 3]  # switch case
                                            , 7: [4, 5, 6], 8: [7], 9: [1, 2, 3, 4, 5, 6, 7]}
        self.machine_index_to_type_list = []     # 按工作台id排序的list
        self.robot_behavior = ['', '', '', '']
        # self.sale_count = []
        # self.buy_count = []
        # self.forward_count = []
        # self.rotate_Count = []

        self.frame_id = 1  # 帧数
        self.current_money = 1  # 钱
        self.k = 0  # 机器数量

        self.decesion = Decision()
        self.control = Control()

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
                # ***************************调用控制模块*****************************************
                if (self.start_flag):  # 如果不是开始
                    
                    self.getInfo(self.server_info)  # 更新工位和小车信息
                    sys.stdout.write('%d\n' % (self.frame_id))
                    
                    # sys.stderr.write('flag %d\n' % (self.flag))
                    # sys.stderr.write('***************************** frame_id is ' + str(self.frame_id)+'*******************************\n')
                    # for i in range(len(self.robot_state_list)):
                    # sys.stderr.write(str(self.machine_state_dict.keys()))
                    # sys.stderr.write('machine id is : '+str(self.machine_state_dict))
                    # for machine in self.machine_state_dict[6]:
                    #     sys.stderr.write('machine id is : '+str(machine.id)+'\n')
                    #     sys.stderr.write('machine type is : '+str(machine.type)+'\n')
                    for i in range(4):
                        # 获取机器人对象
                        robot = self.robot_state_list[i]
                        # nearest_machine = None
                        # sys.stderr.write('---------------I am robot ' + str(robot.id) + '-------------\n')
                        # 机器人携带的物品
                        # sys.stderr.write('my x is ' + str(robot.x)+'\n')
                        # sys.stderr.write('my y is ' + str(robot.y)+'\n')
                        take_obj = int(self.robot_state_list[i].take_obj) 
                        # sys.stderr.write('take_obj is '+ str(take_obj)+'\n')
                        # if robot.target == None:
                        #     sys.stderr.write('my init target is none\n')
                        # else:
                        #     sys.stderr.write('my init target is '+ str(robot.target.type)+'\n')
                        #     sys.stderr.write('my init target id is '+ str(robot.target.id)+'\n')
                        if int(robot.atmachine_id) == int(-1):
                            at_machine_type = -1
                        else:
                            at_machine = self.machine_index_to_type_list[int(robot.atmachine_id)]
                            at_machine_type = at_machine.type 
                        # sys.stderr.write('at_machine_type is '+ str(at_machine_type)+'\n')
                        
                        if self.frame_id <= 50:
                            # 前50帧所有物品都没有生产好，找最近的123号工作台并移动过去
                            if at_machine_type in [1, 2, 3]:
                                robot.move(at_machine)
                                robot.target = at_machine
                            else:
                                machine_list = []
                                for i in range(1, 4):
                                    for machine in self.machine_state_dict[i]:
                                        machine_list.append(machine)
                                                        
                                nearest_machine = robot.find_nearest_machine(machine_list)
                                if (int(nearest_machine.type) not in [1, 2, 3]) & (not nearest_machine.product_lock):
                                    nearest_machine.product_lock = True
                                    # sys.stderr.write('lock '+ str(nearest_machine.type) + 'product its id is'+ str(nearest_machine.id) + '\n')

                                if robot.target == None:
                                    robot.move(nearest_machine)
                                    robot.target = nearest_machine
                                else:
                                    robot.move(robot.target)
                                # if robot.target != None:
                                #     sys.stderr.write('target is changed to'+ str(robot.target.type) + '\n')
                                #     sys.stderr.write('target_id is changed to: '+str(robot.target.id) + '\n')
                            
                        else:

                            if take_obj == 0:
                                # 如果机器人没有携带物品，寻找最大价值的工作台
                                if robot.target == None:
                                    # 如果机器人没有移动的目标，寻找最大价值的工作台
                                    nearest_machine = robot.find_most_valuable_machine(self.machine_state_dict)
                                    sys.stderr.write(str(nearest_machine == None)+'\n')
                                    if nearest_machine != None:
                                        # 如果找到了，预定这个工作台的产品并移动过去
                                        if (int(nearest_machine.type) not in [1, 2, 3]) & (not nearest_machine.product_lock):
                                            nearest_machine.product_lock = True
                                        # sys.stderr.write('nearest_machine'+str(nearest_machine.type) + '\n')
                                        robot.move(nearest_machine) # 移动至目标工作台
                                        robot.target = nearest_machine
                                        # sys.stderr.write('target is changed to'+ str(robot.target.type) + '\n')
                                        # sys.stderr.write('target_id is changed to: '+str(robot.target.id) + '\n')
                                else:
                                    # 如果机器人有移动的目标，判断机器人所处位置
                                    if at_machine_type != -1:
                                        # 如果机器人处在某个工作台
                                        # sys.stderr.write('at_machine.product_status is xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx' + str(at_machine.product_status)+'\n')
                                        if robot.target == at_machine:
                                            # 如果机器人所处工作台就是目标工作台，尝试购买
                                            # if int(at_machine.product_status) == 1:
                                            if int(at_machine.product_status) == 1:
                                                robot.buy()
                                                if int(at_machine_type) not in  [1, 2, 3]:
                                                    at_machine.product_lock = False
                                                    # sys.stderr.write('unlock '+ str(at_machine_type) + 'product its id is'+ str(at_machine.id) + '\n')
                                                # robot.unlock(at_machine)
                                                robot.target = None
                                            else:
                                                # 如果不能购买，继续寻找最大价值工作台
                                                nearest_machine = robot.find_most_valuable_machine(self.machine_state_dict)
                                                if nearest_machine != None:
                                                    # 如果找到了，移动过去
                                                    if (int(nearest_machine.type) not in [1, 2, 3]) & (not nearest_machine.product_lock):
                                                        nearest_machine.product_lock = True
                                                        sys.stderr.write('lock '+ str(nearest_machine.type) + 'product its id is'+ str(nearest_machine.id) + '\n')
                                                    # sys.stderr.write('nearest_machine'+str(nearest_machine.type) + '\n')
                                                    robot.move(nearest_machine) # 移动至目标工作台
                                                    robot.target = nearest_machine
                                                    # sys.stderr.write('target is changed to'+ str(robot.target.type) + '\n')
                                                    # sys.stderr.write('target_id is changed to: '+str(robot.target.id) + '\n')
                                                else:
                                                    # 如果没找到，继续在原工作台等待
                                                    robot.move(robot.target)
                                                    # sys.stderr.write('target is changed to'+ str(robot.target.type) + '\n')
                                                    # sys.stderr.write('target_id is changed to: '+str(robot.target.id) + '\n')
                                            
                                        else:

                                            robot.move(robot.target)
                                            # sys.stderr.write('target is changed to'+ str(robot.target.type) + '\n')
                                            # sys.stderr.write('target_id is changed to: '+str(robot.target.id) + '\n')
                                       
                                    else:

                                        robot.move(robot.target) # 移动至目标工作台
                                        # sys.stderr.write('target is changed to'+ str(robot.target.type) + '\n')
                                        # sys.stderr.write('target_id is changed to: '+str(robot.target.id) + '\n')
                                            # robot.target = nearest_machine
                                            # sys.stderr.write('target is '+ str(target.type) + '\n')
                            else:
                                # 如果机器人携带物品，寻找能购买该物品的工作台
                                # 如果机器人所处工作台能够购买该物品，直接卖
                                # receive_machine_list = RECEIVE_MACHINE_ID_LIST[take_obj]
                                # if at_machine_type in receive_machine_list:
                                # 如果机器人位于能够卖出的工作台附近，判断能否工作台能否购买
                                if at_machine_type != -1:
                                    if at_machine.receive(take_obj):
                                        # 如果工作台可以购买，立即卖出
                                        # sys.stderr.write('hhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhh\n')
                                        robot.sell()
                                        if take_obj in at_machine.lock_list:
                                            at_machine.unlock(take_obj)
                                        robot.target = None
                                    else:
                                        # 如果机器人所处工作台不能够购买该物品
                                        # if robot.target != None:
                                        #     robot.move(robot.target)
                                        # else:
                                        # 如果机器人没有目标，寻找一个最近的
                                        # sys.stderr.write('hhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhh\n')
                                        buyer = robot.find_buyer(self.machine_sort_by_receive)
                                        if buyer != None:
                                            robot.move(buyer)
                                            robot.target = buyer
                                            if take_obj in [4, 5, 6, 7]:
                                                buyer.lock(take_obj)
                                            # sys.stderr.write('buyer is to'+ str(robot.target.type) + '\n')
                                            # sys.stderr.write('buyer_id is to: '+str(robot.target.id) + '\n')
                                        # else:
                                        #     if take_obj in [1, 2, 3]:
                                        #         robot.destroy()
                                            # robot.unlock()
                                else:
                                    # 如果机器人不在任何工作台，寻找最近的
                                    if robot.target != None:
                                        robot.move(robot.target)
                                    else:
                                        # 如果机器人没有目标，寻找一个最近的
                                        # sys.stderr.write('hhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhh\n')
                                        buyer = robot.find_buyer(self.machine_sort_by_receive)
                                        
                                        if buyer != None:
                                            # behavior = 'sell' + str(buyer.id) + str(take_obj)
                                            # if behavior 
                                            robot.move(buyer)
                                            robot.target = buyer
                                            if take_obj in [4, 5, 6, 7]:
                                                buyer.lock(take_obj)
                                            # buyer.buy_status = buyer.buy_status + pow(2, int(take_obj))
                                            # sys.stderr.write('buyer is to'+ str(robot.target.type) + '\n')
                                            # sys.stderr.write('buyer_id is to: '+str(robot.target.id) + '\n')
                                        # else:
                                        #     if take_obj in [1, 2, 3]:
                                        #         robot.destroy()
                                            # robot.unlock()
                                        
                               

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

    def infoUpdateMachineDict(self, server_info_machine):  # 更新工作台参数,更新两个字典

        for index_row, line in enumerate(server_info_machine):  # 工作台信息行

            # str转int 这里面从txt读的穿捡来的data_line全是文本，不知道到时候服务器传进来的是整数还是文本
            data_line = list(map(float, line.strip("\n").split()))

            machine_type = data_line[0]  # 型号

            self.infoUpdateMachineStateDict(machine_type, index_row, data_line)

            if(machine_type >= 4):  # *************demo3_2*********
                self.infoUpdateMachineSortByRecive(
                    machine_type, index_row, data_line)

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

    def infoUpdateRobotList(self, server_info_robot):  # 更新机器人参数

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

    # *********************************输出到服务器信息****************************************

    def finish(self):
        sys.stdout.write('OK\n')
        sys.stdout.flush()

    def finishTest(self):
        sys.stdout.write('%d\n' % int(self.frame_id))
        line_speed, angle_speed = 3, 1.5
        for robot_id in range(4):
            sys.stdout.write('forward %d %d\n' % (robot_id, line_speed))
            sys.stdout.write('rotate %d %f\n' % (robot_id, angle_speed))
        self.finish()

    # def outputInfo(self):
    #     print()  # 帧ID
    #     print('forward', '')