import numpy as np
import sys

class Robot(object):
    # 机器人类\
    def __init__(self, id, x, y, orientation, take_obj):
        self.id = id
        self.x = x # 横坐标
        self.y = y # 纵坐标
        self.orientation = orientation # 朝向
        self.take_obj = take_obj # 携带物品类型

    def move(self, machine):
        # 到这个machine这里去
        rotate_angle = self.calRotateAngle(machine)
        distance = self.calDistance(machine)
        if (abs(rotate_angle) > 3.6):
            sys.stdout.write('rotate %d %d\n' % (0, np.pi*(rotate_angle/abs(rotate_angle))))
        else:
            sys.stdout.write('rotate %d %d\n' % (0, 0))
        if (distance > 0.4):
            sys.stdout.write('forward %d %d\n' % (0, 6))
        else:
            sys.stdout.write('forward %d %d\n' % (0, 1))

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

    def Rotate(self, rotate_angle):
        # 机器人旋转指令
        if (abs(rotate_angle) > 3.6):
            sys.stdout.write('rotate %d %d\n' % (self.id, np.pi*(rotate_angle/abs(rotate_angle))))

    def buy(self):
        sys.stdout.write('buy %d\n' % self.id)

    def sell(self):
        sys.stdout.write('sell %d\n' % self.id)