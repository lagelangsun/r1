import numpy as np
import sys


#计算模块

class CalculateFunc(object):

    def __init__(self):
        self.receivetype_for_machinetype = {4: [1, 2], 5: [1, 3], 6: [2, 3]
                                            , 7: [4, 5, 6], 8: [7], 9: [1, 2, 3, 4, 5, 6, 7]}
           
    def move(self, machine): # 传入一个robot和一个machine最好
        distance = self.calDistance(machine)
        # sys.stderr.write('move distance'+str(distance)+'\n')
        angle_diff = self.calRotateAngle(machine)
        rotate_angle = 0
        speed = 0
        # sys.stderr.write('robot orientation is: '+str(np.degrees(self.orientation)) + '\n')
        # sys.stderr.write('angle_diff'+str(angle_diff)+'\n')
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
            if (distance > 0.4):
                speed = 6
            else:
                speed = 2
            self.forward(speed)

        self.rotate(rotate_angle)
        # sys.stderr.write('move rotate_angle'+str(rotate_angle)+'\n')
            # sys.stderr.write('move rotate  angle command '+str(rotate_angle)+'\n')
            # sys.stderr.write('ininin'+'\n')


    def buy(self):
        sys.stdout.write('buy %d\n' % self.id)

    def sell(self):
        sys.stdout.write('sell %d\n' % self.id)

    def destroy(self):
        sys.stdout.write('destroy %d\n' % self.id)
    # def judgeReceiveType(self, machine_type):
    #     return self.receivetype_for_machinetype[machine_type]

    def forward(self, linear_speed):
        # 机器人前进指令
        sys.stdout.write('forward %d %d\n' % (self.id, linear_speed))  

    def rotate(self, angular_v):
        # 机器人旋转指令
        sys.stdout.write('rotate %d %f\n' % (self.id, angular_v))

    def calSpeed(self):
        if int(abs(self.y - 50)) < 2 | int(abs(self.y - 0)) < 2 | int(abs(self.x - 50)) < 2 | int(abs(self.x - 0)) < 2:
            return 1
        else:
            return 6
    
    def calDistance(self, machine):
        # 计算a，b两点的距离
        return np.sqrt((machine.x - self.x)**2 + (machine.y - self.y)**2) #只需要机器人(x,y)和工位(x,y)
    
    def calRotateAngle(self, machine):  #需要一个machine类，self改成一个机器人类好一点
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
        
    def calculateLoc(self, staffLoc):  # 传入一个list,代表横纵坐标
        return [staffLoc[1] * 0.5 + 0.25, staffLoc[0] * 0.5 + 0.25]
    