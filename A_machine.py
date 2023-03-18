import numpy as np

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
        # self.receive_type_list = receive_type_list

    def receive(self, product_id):
        # 判断是否能接受该产品
        # 转成二进制，然后移位，判断最后一位是不是1
        if (bin(self.raw_status>>product_id)[-1] == 1):
            return False
        else:
            return True
    
    def update(self, data_line):
        self.x = data_line[0] # 横坐标
        self.y = data_line[1] # 纵坐标
        self.remain_frame = data_line[2]    # 剩余生产时间
        self.raw_status = data_line[3]         # 原材料格状态
        self.product_status = data_line[4] # 产品格状态
