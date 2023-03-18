import numpy as np
import sys

MACHINE_RECEIVE_OBJECT_LIST = {4: [1, 2], 5: [1, 3], 6: [2, 3], 7: [4, 5, 6], 8: [7], 9:[1, 2, 3, 4, 5, 6, 7]}

class Machine(object):
    _ID = 0
    # 工作台类
    def __init__(self, type, loc_list #,receive_type_list
                 ):

        #坐标(x,y),剩余生产时间（帧数）,原材料格状态(二进制,哪位为1代表哪位原材料格有东西),产品格状态

        self.id = self._ID
        self.__class__._ID += 1
        self.type = type
        self.x = loc_list[0] # 横坐标
        self.y = loc_list[1] # 纵坐标
        self.remain_frame = 0    # 剩余生产时间
        self.raw_status = 0         # 原材料格状态
        self.product_status = 0 # 产品格状态
        # self.receive_list = MACHINE_RECEIVE_OBJECT_LIST

    def receive(self, product_id):
        # 判断是否能接受该产品
        # 转成二进制，然后移位，判断最后一位是不是1
        if bin(int(self.raw_status)>>int(product_id)) == int(1):
            return False
        else:
            return True
    
    def update(self, data_line):
        self.x = data_line[0] # 横坐标
        self.y = data_line[1] # 纵坐标
        self.remain_frame = data_line[2]    # 剩余生产时间
        self.raw_status = data_line[3]         # 原材料格状态
        self.product_status = data_line[4] # 产品格状态
    #     self.receive_list = self.update_receive_list(self.raw_status)

    # def update_receive_list(self, product_status):

