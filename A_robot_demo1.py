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