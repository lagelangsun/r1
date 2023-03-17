import numpy as np

class Machine(object):
    # 工作台类
    def __init__(self, type, x, y, remain_frame, raw_status, product_status):
        self.id = id
        self.type = type
        self.x = x # 横坐标
        self.y = y # 纵坐标
        self.remain_frame = remain_frame # 剩余生产时间
        self.raw_status = raw_status # 原材料格状态
        self.product_status = product_status # 产品格状态

    def receive(self, product_id):
        # 判断是否能接受该产品
        # 转成二进制，然后移位，判断最后一位是不是1
        if (bin(self.raw_status>>product_id)[-1] == 1):
            return False
        else:
            return True
