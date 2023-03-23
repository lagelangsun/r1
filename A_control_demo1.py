import sys
import numpy as np
from A_pre_calculate import CalculateFunc
from A_machine import Machine
from A_robot_demo1 import Robot
import time


class Control(object):
    def __init__(self):
        self.a = 1

    # 可以把计算类挪到公共计算类
    # order_list: [robot_id, target_machine_id, move, buy, sell 1或者0]
    def control(self, order_list, robot_list, machine_list):
        for index, order in enumerate(order_list):
            if order[2] != 0:
                # 小车order[0] move到 machine[order[1]]
                robot_list[order[0]].move(machine_list[order[1]])
            if order[3] != 0:
                robot_list[order[0]].buy()
            if order[4] != 0:
                robot_list[order[0]].sell()
