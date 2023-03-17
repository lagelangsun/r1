import sys
import numpy as np
from A_property import Property
from A_pre_calculate import CalculateFunc


class IOProcess(object):
    def __init__(self):

        self.start_flag = False         #开始标志
        self.server_info = []
        
        self.preCalculate = CalculateFunc()
        self.robot_state_list= []         # 机器人list
        self.machine_state_dict = {1: [], 2: [], 3: [], 4: [],  #key:工作台类型,value:[坐标(x,y),剩余生产时间（帧数）,原材料格状态,产品格状态]
                               5: [], 6: [], 7: [], 8: [], 9: []}  # 工作台按型号list 
        
        self.sale_count = []
        self.buy_count = []
        self.forward_count = []
        self.rotate_Count = []
        
        self.frame_id = 1
        self.current_money = 1
        self.machine_count = 0
        

    def getInfoFromServer(self):
        try:
            while True:
                input_str = ' '
                while input_str != 'OK':                #读到OK跳出循环
                    input_str = input()                    
                    self.server_info.append(input_str)
                self.server_info.pop(-1)                #删掉OK
                if(self.start_flag):                    #如果不是开始
                    self.getInfo(self.server_info) #就是交互信息
                    sys.stderr.write(str(self.frame_id))
                    self.finishTest()
                else:
                    self.getMap(self.server_info)    #如果是开始就读地图信息
                    self.finish()
                
        except EOFError:
            pass
        

    def outputInfo(self):
        print()#帧ID
        print('forward','')


    def getInfo(self, server_info):
        # 第一行输入 2 个整数，表示帧序号（从 1 开始递增）、当前金钱数。
        # 第二行输入 1 个整数，表示场上工作台的数量 K（K<=50）。
        # 紧接着 K 行数据，每一行表示一个工作台，分别由如下所示的数据构成，共计 6 个数字：
        # 接下来的 4 行数据，每一行表示一个机器人，分别由如下表格中所示的数据构成，每行 10 个数字。
        # 最后，判题器会输出一行 OK，表示所有数据已经写入完毕。
        data_line_0 = server_info[0].strip("\n").split()
        self.frame_id = int(data_line_0[0])
        # sys.stderr.write(data_line_0[0]+'\n')
        # sys.stderr.write('here \n')
        self.current_money = int(data_line_0[1])
        k = int(server_info[1].strip("\n").split()[0])

        self.infoUpdateMachineDict(server_info[2:2+int(k)])

        self.infoUpdateRobotList(server_info[2 + int(k): 2 + int(k) + 4])

        self.server_info = []


    def infoUpdateMachineDict(self,server_info_machine): 

        for index_row, line in enumerate(server_info_machine):  # 接下来的行
            data_line = list(map(float, line.strip("\n").split()))  #str转int

            #到了工位 行 的时候
            #这里面从txt读的穿捡来的data_line全是文本，不知道到时候服务器传进来的是整数还是文本
            machine_type = data_line[0] #型号
            machine_type_list = self.machine_state_dict[machine_type]  #找到型号key:machineType对应的list[[x1,y1,0,0,0],[x2,y2,0,0,0],[x3,y3,0,0,0]....]
            for i in range(len(machine_type_list)): #获取该型号机器人的个数，遍历该型号的list，找到对应的机器人
                if(data_line[1] == machine_type_list[i][0]): #x坐标一样，所以这里要int()一下
                    if(data_line[2] == machine_type_list[i][1]): #y坐标一样
                        machine_type_list[i] = [data_line[1],data_line[2],data_line[3],data_line[4],data_line[5]]  #对应的型号machinetype的机器人i更新
                        self.machine_state_dict[machine_type] = machine_type_list                                         #对应的型号machinetype更新
                        break
                    else:
                        continue
                else:
                    continue

    def infoUpdateRobotList(self,server_info_robot):

        for index_row, line in enumerate(server_info_robot):  # 接下来的行
            data_line = list(map(float, line.strip("\n").split())  #str转int
                            )  
            self.robot_state_list[index_row] = data_line


    def getMap(self, content):

        self.start_flag = True

        for index_row, line in enumerate(content):
            data_line = line.strip("\n").split()  # 去除首尾换行符，并按空格划分
            for index_cal, map_char in enumerate(data_line[0]):
                if(map_char != '.'):
                    if(map_char == 'A'):
                        self.robot_state_list.append(
                            self.preCalculate.calculateRobot([100-index_row, index_cal]))
                    else:
                        self.mapUpdateDict(
                            int(map_char), self.machine_state_dict, index_row, index_cal) #更新字典
        self.mapFinalUpdateDict()

        self.server_info = []

        
    def mapUpdateDict(self, machine_type, machine_state_dict, index_row, index_cal):

        Loc = machine_state_dict[machine_type]
        loc_with_index = self.preCalculate.calculateMap([99-index_row, index_cal])
        Loc.append(loc_with_index)
        machine_state_dict[machine_type] = Loc


    def mapFinalUpdateDict(self):  # 去除地图中没出现的型号的Machine
        for i in range(9):
            if(self.machine_state_dict[i+1] == []):
                self.machine_state_dict.pop(i+1, None)
            # else:
            #     machine_state_dict[i+1] = {'loc':machine_state_dict[i+1]}
        

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
                
        