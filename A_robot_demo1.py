import numpy as np
import sys

class Robot(object):
    # 机器人类\
    _ID = 0
    def __init__(self, loc_list):

        #[所处工作台ID 携带物品类型 时间价值系数 碰撞价值系数 角速度 线速度x 线速度y 朝向 坐标x 坐标y]

        self.id = self._ID
        self.__class__._ID += 1

        self.atmachine_id = 0 #所处工作台ID 
        self.take_obj = 0 # 携带物品类型
        self.time_value = 0 #时间价值系数
        self.crash_value = 0 #碰撞价值系数
        self.angular_v = 0 #角速度
        self.linear_v_x = 0 #线速度x
        self.linear_v_y = 0 #线速度y
        self.orientation = 0 # 朝向
        self.x = loc_list[0] # 横坐标
        self.y = loc_list[1] # 纵坐标
        self.target = [] # 正在移动
        self.target1 = None # 正在移动 TODO
        self.target_type = -1
        self.behavior = '' # 行为：买/卖+目标工作台id+物品类型


    def calDistance(self, machine):
        # 计算a，b两点的距离
        return np.sqrt((machine.x - self.x)**2 + (machine.y - self.y)**2)

    def calRotateAngle(self, machine):
        # 计算机器人和工作台之间的角度差
        # 2个向量模的乘积
        v1 = [machine.x - self.x, machine.y - self.y]
        v2 = [1, 0]
        TheNorm = np.linalg.norm(v1)*np.linalg.norm(v2)
        # 叉乘
        rho =  np.rad2deg(np.arcsin(np.cross(v1, v2)/TheNorm))
        # 点乘
        theta = np.rad2deg(np.arccos(np.dot(v1,v2)/TheNorm))
        if rho < 0:
            return theta - np.rad2deg(self.orientation)
        else:
            return - theta - np.rad2deg(self.orientation)

    
    def forward(self, linear_speed):
        # 机器人前进指令
        sys.stdout.write('forward %d %d\n' % (self.id, linear_speed))
           
    def move(self, machine):

        distance = self.calDistance(machine)
        angle_diff = self.calRotateAngle(machine)

        rotate_angle = 0
        speed = 0

        if (abs(angle_diff) > 3.6):
            if angle_diff > 0:
                if angle_diff > 180:
                    rotate_angle = - np.pi
                else:
                    rotate_angle = np.pi
            else:
                if angle_diff < - 180:
                    rotate_angle = np.pi
                else:
                    rotate_angle = - np.pi
            speed = 3
            self.forward(speed)
        else:
            if (distance > 1):
                speed = 6
            else:
                speed = 1
            self.forward(speed)

        self.rotate(rotate_angle)


    def rotate(self, angular_v):
        # 机器人旋转指令
        sys.stdout.write('rotate %d %f\n' % (self.id, angular_v))

    def calSpeed(self):
        if int(abs(self.y - 50)) < 2 | int(abs(self.y - 0)) < 2 | int(abs(self.x - 50)) < 2 | int(abs(self.x - 0)) < 2:
            return 1
        else:
            return 6
    
    def buy(self):
        sys.stdout.write('buy %d\n' % self.id)

    def sell(self):
        sys.stdout.write('sell %d\n' % self.id)

    def destroy(self):
        sys.stdout.write('destroy %d\n' % self.id)

    def update(self, data_line):

        self.atmachine_id = data_line[0]
        self.take_obj = data_line[1] # 携带物品类型
        self.time_value = data_line[2] #时间价值系数
        self.crash_value = data_line[3] #碰撞价值系数
        self.angular_v = data_line[4] #角速度
        self.linear_v_x = data_line[5] #线速度x
        self.linear_v_y = data_line[6] #线速度y
        self.orientation = data_line[7] # 朝向
        self.x = data_line[8] # 横坐标
        self.y = data_line[9] # 纵坐标


    def find_most_valuable_machine(self, machine_state_dict):
        # 没有携带物品时，寻找价值最大的工作台
        # nearest_machine = None
        # sys.stderr.write('jin lai le ma ')
        # wait_flag = True # 如果原材料格都满了，等待
        # sys.stderr.write('machine_raw_status is\n')
        # if 7 in machine_state_dict.keys():
        #     for machine in machine_state_dict[7]:
        #         sys.stderr.write('machine_raw_status is'+ str(machine.raw_status)+'\n')
        #         if not machine.raw_full():
        #             # 没有装满，继续
                    
        #             wait_flag = False
        #             break
        # if wait_flag == True:
        #     for obj_id in range(4, 7):
        #         for machine in machine_state_dict[obj_id]:
        #             if not machine.raw_full():
        #                 # 没有装满，继续
        #                 wait_flag = False
        #                 break
                    
        # if wait_flag == False:
        machine_list = []
        if 7 in machine_state_dict.keys():
            for machine in machine_state_dict[7]:
                sys.stderr.write('machine_raw_status is'+ str(machine.raw_status)+'\n')
                sys.stderr.write(str(machine.raw_full())+'\n')
                if (int(machine.product_status) == 1) & ( not machine.product_lock):
                    machine_list.append(machine)
            # sys.stderr.write('jin lai le ma 11111')
            if self.find_nearest_machine(machine_list) != None:
                return self.find_nearest_machine(machine_list)
            
        machine_list = []       
        for obj_id in range(4, 7):
            for machine in machine_state_dict[obj_id]:
                # sys.stderr.write('machine_product_status is'+ str(machine.product_status)+'\n')
                # sys.stderr.write('machine_product_lock is'+ str(machine.product_lock)+'\n')
                # sys.stderr.write('machine_raw_status is'+ str(machine.raw_status)+'\n')
                # sys.stderr.write(str(machine.raw_full())+'\n')
                if (int(machine.product_status) == 1) & ( not machine.product_lock):
                    # sys.stderr.write('***************************************************************\n')
                    machine_list.append(machine)
        if machine_list != []:
            # sys.stderr.write('jin lai le ma 222222222222222222222222222222222222222222')
            # for machine in machine_list:
            #     sys.stderr.write('machine xxxxxxx' + str(machine.type))
            # sys.stderr.write('machine_list'+ str(machine_list)+'\n')
            if self.find_nearest_machine(machine_list) != None:
                return self.find_nearest_machine(machine_list)
            
        machine_list = []
        for obj_id in range(1, 4):
            for machine in machine_state_dict[obj_id]:
                # sys.stderr.write('machine_raw_status is'+ str(machine.raw_status)+'\n')
                # sys.stderr.write(str(machine.raw_full())+'\n')
                if int(machine.product_status) == 1:
                    machine_list.append(machine)
        if machine_list != []:
            # sys.stderr.write('jin lai le ma 33333333333333333333333333333333333333333')
            # for machine in machine_list:
            #     sys.stderr.write('machine xxxxxxx' + str(machine.type))
            
            if self.find_nearest_machine(machine_list) != None:
                return self.find_nearest_machine(machine_list)
        return None
    
    def find_nearest_machine(self, machine_list):
        # 在machine_list中寻找最近的machine
        nearest_distance = 10000
        nearest_machine = None
        # sys.stderr.write('machine_list'+str(machine_list) + '\n')
        # for machine in machine_list:
        #     sys.stderr.write('machine_type '+ str(machine.type) + '\n')
        if machine_list != []:
            for machine in machine_list:
                # sys.stderr.write('status_type'+str(machine.product_status) + '\n')
                # if int(machine.product_status) == 1:
                distance = self.calDistance(machine)
                # sys.stderr.write('distance'+str(distance) + '\n')
                # sys.stderr.write('nearest_machine'+str(nearest_distance) + '\n')
                if distance < nearest_distance:
                    nearest_machine = machine
                    nearest_distance = distance
                    # sys.stderr.write('nearest_machine'+str(nearest_machine) + '\n')
        # if nearest_machine != None:                    
        #     nearest_machine.product_status = 0
        # sys.stderr.write('nearest_machine'+str(nearest_machine) + '\n')            
        return nearest_machine
    
    def find_buyer(self, machine_sort_by_receive):
        buyer_list = [] # 有空间购买该物品的工作台list
        buyer = None
        for machine in machine_sort_by_receive[self.take_obj]:
            if machine.receive(self.take_obj) & (self.take_obj not in machine.lock_list):
                # 如果该工作台可以购买该物品，加入进list
                if (self.take_obj in [1, 2, 3]) & (int(machine.type) == 9):
                    continue
                buyer_list.append(machine)

            # 寻找上面的list中最近的工作台
        buyer = self.find_nearest_machine(buyer_list)
        return buyer