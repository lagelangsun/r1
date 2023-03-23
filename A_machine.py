import numpy as np
import sys
import copy

MACHINE_RECEIVE_OBJECT_LIST = {4: [1, 2], 5: [1, 3], 6: [2, 3], 7: [4, 5, 6], 8: [7], 9:[1, 2, 3, 4, 5, 6, 7]}

class Machine(object):
    _ID = 0
    # 工作台类
    def __init__(self, type, loc_list #,receive_type_list
                 ):

        #坐标(x,y),剩余生产时间（帧数）,原材料格状态(二进制,哪位为1代表哪位原材料格有东西),产品格状态

        self.id = self._ID
        self.__class__._ID += 1
        self.type = type # float
        self.x = loc_list[0] # 横坐标
        self.y = loc_list[1] # 纵坐标
        self.remain_frame = 0    # 剩余生产时间
        self.raw_status = 0         # 原材料格状态
        self.product_status = 0 # 产品格状态
        
        self.product_lock = False # 产品格锁
        self.buy_status = 0 # 工作台已经预定购买的产品状态
        
        
        self.lock_list = []
        self.buyer_lock = False
        
        # 有关剩余生产时间的优化
        self.last_remain_frame = -1
        self.manufacture_start = False
        
        # 有关最后一段时间决定是不是还要买的优化,现在还只考虑了7，因为7实在太贵了
        self.min_distance_78 = 5000

        # self.receive_list = MACHINE_RECEIVE_OBJECT_LIST

    def receive(self, product_id):
        # 判断是否能接受该产品
        # 转成二进制，然后移位，判断最后一位是不是1
        # if int(self.type) == 6:
        #     sys.stderr.write('machine_id is'+str(self.id)+'\n')
        #     sys.stderr.write('raw_status is'+str(self.raw_status)+'\n')
        #     sys.stderr.write(str(int(bin(int(self.raw_status)>>int(product_id))[-1])==int(1))+'\n')
        if int(bin(int(self.raw_status)>>int(product_id))[-1]) == int(1):
            return False # 不可接受
        else:
            return True
    
    def lock(self, obj_id):
        if int(self.type) not in [8, 9]:
            self.lock_list.append(obj_id)
        # sys.stderr.write('lock_list'+str(self.lock_list)+'\n')

    def unlock(self, obj_id):
        self.lock_list.remove(obj_id)

    def buyerLock(self):
        self.buyer_lock = True

    def buyerUnlock(self):
        self.buyer_lock = False
        
    def update(self, data_line):
        
        
        self.last_remain_frame = copy.deepcopy(self.remain_frame) # 在更新这一帧的剩余生产时间之前，先把当前剩余时间赋给上一帧标志,这个deepcopy不管用啊
        self.x = data_line[0] # 横坐标
        self.y = data_line[1] # 纵坐标
        self.remain_frame = data_line[2]    # 剩余生产时间
        self.raw_status = data_line[3]         # 原材料格状态
        self.product_status = data_line[4] # 产品格状态
    #     self.receive_list = self.update_receive_list(self.raw_status)

    # def update_receive_list(self, product_status):