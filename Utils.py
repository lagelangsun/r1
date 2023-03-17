
import sys
import numpy as np

class Utils(object):
    # 工具类    
    def forward(self, robot_id, line_speed):
        sys.stdout.write('forward %d %d\n' % (robot_id, line_speed))

    def rotate(robot_id, angle_speed):
        sys.stdout.write('rotate %d %d\n' % (robot_id, angle_speed)) 

    def buy(robot_id):
        sys.stdout.write('buy %d\n' % robot_id) 

    def sell(robot_id):
        sys.stdout.write('sell %d\n' % robot_id)

    def calDistance(a, b):
        # 计算a，b两点的距离
        return np.sqrt((a.x - b.x)**2 + (a.y - b.y)**2)

    def calOrientation(robot, machine, robot_orientation):
        # 计算机器人和工作台之间的角度差
        rotate_orientation = np.degrees(np.arctan2((machine.y - robot.y), (machine.x - robot.x)))
        return rotate_orientation - np.degrees(robot_orientation) # 返回度数