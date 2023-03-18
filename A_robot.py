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


    def calDistance(self, machine):
        # 计算a，b两点的距离
        return np.sqrt((machine.x - self.x)**2 + (machine.y - self.y)**2)

    def calRotateAngle(self, machine):
        # 计算机器人和工作台之间的角度差
        rotate_angle_to_0 = np.degrees(np.arctan2((machine.y - self.y), (machine.x - self.x)))
        return rotate_angle_to_0 - np.degrees(self.orientation) # 返回机器人需要旋转的度数

    def forward(self, linear_speed):
        # 机器人前进指令
        sys.stdout.write('forward %d %d\n' % (self.id, linear_speed))


    def find_most_valuable_machine(self, machine_state_dict):
        # 没有携带物品时，寻找价值最大的工作台
        nearest_machine = None
        
        for index in range(1, 10):
            obj_id = 10 - index
            nearest_machine = self.find_nearest_machine(machine_state_dict[obj_id])
           
            if nearest_machine != None:
                return nearest_machine
        
        return nearest_machine
    
    def find_nearest_machine(self, machine_list):
        # 在machine_list中寻找最近的machine
        nearest_distance = 10000
        nearest_machine = None
        
        if machine_list != []:
            for machine in machine_list:
                # sys.stderr.write(str(machine.product_status) + '\n')
                if machine.product_status == 1:
                    distance = self.calDistance(machine)
                    
                    if distance < nearest_distance:
                        nearest_machine = machine
                        nearest_distance
        if nearest_machine != None:                    
            nearest_machine.product_status = 0
        return nearest_machine
    
    def find_nearest_machine1(self, machine_list):
        # 在machine_list中寻找最近的machine
        nearest_distance = 10000
        nearest_machine = None
        
        if machine_list != []:
            for machine in machine_list:
                distance = self.calDistance(machine)
                if distance < nearest_distance:
                    nearest_machine = machine
                    nearest_distance
        # if nearest_machine != None:                    
        #     nearest_machine.product_status = 0
        return nearest_machine
    
    def move(self, machine):
        distance = self.calDistance(machine)
        rotate_angle = self.calRotateAngle(machine)
        if (abs(rotate_angle) > 3.6):
            self.rotate(np.pi*(rotate_angle/abs(rotate_angle)))
        else:
            self.rotate(0)

        if (distance > 0.4):
            self.forward(6)
        else:
            self.forward(1)

    def rotate(self, angular_v):
        # 机器人旋转指令
        sys.stdout.write('rotate %d %f\n' % (self.id, angular_v))

    def buy(self):
        sys.stdout.write('buy %d\n' % self.id)

    def sell(self):
        sys.stdout.write('sell %d\n' % self.id)

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
