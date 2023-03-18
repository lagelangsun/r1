import numpy as np
import sys


#计算模块

class CalculateFunc(object):

    def __init__(self):
        self.receivetype_for_machinetype = {4: [1, 2], 5: [1, 3], 6: [2, 3]
                                            , 7: [4, 5, 6], 8: [7], 9: [1, 2, 3, 4, 5, 6, 7]}

    def calculateLoc(self, staffLoc):  # 传入一个list,代表横纵坐标
        return [staffLoc[1] * 0.5 + 0.25, staffLoc[0] * 0.5 + 0.25]

    # def judgeReceiveType(self, machine_type):
    #     return self.receivetype_for_machinetype[machine_type]
