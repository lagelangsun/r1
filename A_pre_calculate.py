import numpy as np
import sys

class CalculateFunc(object):

    
    def calculateMap(self, staffLoc): #传入一个list,代表横纵坐标
        locRecord = [staffLoc[1] * 0.5 + 0.25, staffLoc[0] * 0.5 + 0.25,0,0,0]
        self.startFlag = False
        return locRecord
    
    def calculateRobot(self, staffLoc):
        #所处工作台 ID 携带物品类型 时间价值系数 碰撞价值系数 角速度 线速度 朝向 坐标x 坐标y
        locRecord = [0, 0, 0, 0, 0, 0, 0, staffLoc[1]
                    * 0.5 + 0.25, staffLoc[0] * 0.5 + 0.25]
        return locRecord
    

    


