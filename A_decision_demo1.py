import sys
import numpy as np
from A_property import Property
from A_pre_calculate import CalculateFunc
from A_machine import Machine
from A_robot import Robot
from A_control_demo1 import Control
import time

class Decision(object): #decision demo1:只针对没有9的情况(只有78)
    def __init__(self, machine_num_of_type):

        self.frame_id = 0
        self.factor1 = 1
        self.factor2 = 2
        self.factor3 = 3
        self.factor4 = 4
        # 型号7所需的型号4,5,6总num


        # self.robot_target_machine_dict = {0:None,1:None,2:None,3:None}
        self.all_robot_order_dict = {0:[0, 0, 0, 0, 0], 1:[1, 0, 0, 0, 0], 2:[2, 0, 0, 0, 0], 3:[3, 0, 0, 0, 0],}
        self.last_all_robot_order_dict = {0:[0, 0, 0, 0, 0], 1:[1, 0, 0, 0, 0], 2:[2, 0, 0, 0, 0], 3:[3, 0, 0, 0, 0],}
        self.robot_order = [0, 0, 0, 0, 0]

        # 1,2,3的数量，其实传进来所有type的数量，以备不时之需
        self.machine_num_of_type = machine_num_of_type

        # 型号7所需的型号4,5,6总num
        self.type7_need_num = {4:machine_num_of_type[7],5:machine_num_of_type[7],6:machine_num_of_type[7]}

        self.control = Control()


    # 现在还需要的是:7工作台的数量；1,2,3工作台的数量；7当前帧所需type4,5,6__num；
    def decesion(self, robot_state_list
                 , machine_state_dict  # 按照工作台类型分类，是个dict
                 , machine_sort_by_receive # 按照可以接受的物料类型分类，是个dict
                 , machine_index_to_type_list # 按照工作台id顺序 ，是个list
                 ): # 是个dict
        
        # self.buySellMove()
        # self.choosen_machine = self.chooseMinDMachine123(machine_state_dict)

        # 逻辑应该是：
        # 1. 初始的时候小车move最近的1,2,3 (move) 没必要，因为初始的时候need_factor 和 empty_factor都是一样的
        # 2. 到了最近的1,2,3之后，触发买指令 (buy)
        # 3. 拿到1,2,3之后，根据公式(D = d * type7_need_type4_num * type_receive_is_empty)计算到可接受这个obj的所有工位的加权距离，小车move到加权距离最短 (move)
        # 4. 到了加权距离最短的工作台后，卖掉 (sell)
        # 5_1. 根据type1,2,3工作台的数量，调度小车去买1,2,3  (buy)
        # 5_2. 若有类型为4,5,6的工作台生产完毕，距离其最近的手上没货的小车去买，然后卖给7 (if move buy4,5,6 move sell7)
        # 6. 将型号i卖给7成功后, 7对应型号nedd_typei_num -1  (self.type7_need_typei_num - 1)
        # 7. 若7生产完毕，且7原料格没满，则不管，直到下次有小车来送原料4,5,6到7，直接买走送到8 (if buy7 move sell8)
        # 8. 若7原料格已满且生产完毕，调度最近手上无货的小车去买7送8

        # buy 1,2,3
        
        # ************************* 决策部分 *********************************
        # machine_state_list =  [machine_state_dict.values()]
        machine_state_list =  [value for key,value in machine_sort_by_receive.items()]
        for i in range(4):                              # 四个小车遍历
            sys.stderr.write("in robot\n")
            robot_at_machine_id = robot_state_list[i].atmachine_id  # 将小车在哪个工作台附近赋给变量robot_at_machine_id
            robot_i = robot_state_list[i]               # 将小车类赋给robot_i
            
            if False:               # 如果有4,5,6生产出来，就调度最近的手上没货的小车去买(这是一个可优化的地方)
                if True:           # 如果7可以接受生产出来的4,5,6,就触发中断
                    self.buyInterupt()

            if robot_at_machine_id == -1 :              # 如果小车现在不在工作台附近，执行运动指令
                sys.stderr.write("in move\n")
                if robot_i.target:                      # 如果已经有目标,即target不为空,target:[目标id, 买，卖]
                        robot_i.move(machine_index_to_type_list[robot_i.target[0]]) # move
                        
                else:                                   # 如果没有目标，就选目标,所以在买卖后需要将target置空，买卖后的下一帧会执行到这里
                    sys.stderr.write("in pick\n")
                    if not robot_i.take_obj:            # 如果机器人手上没货，就要去买，找卖家选择要去哪个target_id买
                        sys.stderr.write("in buy\n")
                        # self.all_robot_order_dict[i][1] = self.pickSellerMachine(machine_state_list, robot_i) # 选择target_machine_id
                        # self.all_robot_order_dict[i][2] = 1  # move
                        target_id = self.pickSellerMachine(machine_state_list, robot_i)
                        robot_i.target = [target_id, 1, 0]# 设置目标位,买位置1
                        robot_i.move(machine_index_to_type_list[target_id]) # move
                        
                    else:                               # 否则就要去卖，找买家，选择要去哪个target_id卖
                        # self.all_robot_order_dict[i][1] = self.pickBuyerMachine(machine_state_list, robot_i) # 选择target_machine_id
                        # self.all_robot_order_dict[i][2] = 1  # move
                        sys.stderr.write("in sell\n")
                        target_id = self.pickBuyerMachine(machine_state_list, robot_i)
                        robot_i.target = [target_id, 0, 1]# 设置目标位，卖位置1
                        robot_i.move(machine_index_to_type_list[target_id]) # move
 
            else:                                              # 如果小车在工作台附近，判断是在哪个工作台附近
                if robot_i.target[0] == robot_at_machine_id:   # 如果是在目标工作台附近,说明有动作，有买或者卖
                    
                    # 判断是要对目标工作台做什么行动，同时应重置目标
                    if robot_i.target[1]:  # 如果是目标是买target_id
                        robot_i.buy()

                    else: # 如果是目标是卖给target_id
                        robot_i.sell()
                    robot_i.target = []             # 清空target,下一帧的时候会重新select目标  ,也不能随意清空，得判断你是不是真的买到了或者卖了再清空，否则就会出错，现在先不考虑这个bug**************************************************
    
                else:   # 否则继续运动
                    robot_i.move(machine_index_to_type_list[robot_i.target[0]])
                    

        # **************** 控制部分 *************************  等着再优化优化，可以把robot里面的控制提出来
        # self.control(self.robot_target_machine_order
        #                          , self.robot_state_list
        #                          , self.machine_index_to_type_list
        #                          , self.all_robot_order_dict  # 这个变量，传起来有点复杂，但是如果能将控制从Robot类中拆出来就会好很多。
        #                          )
            
    def pickSellerMachine(self, machine_state_list, robot_i): #去找1,2,3买

        sys.stderr.write('pick seller \n')
        min_D_machine_id = 0
        D_min = 1000 
        for index_1,machine_type_classlist in enumerate(machine_state_list[0:3]): # machine_dict:[[class1_1..],[class2_1,..],[class3_1]]
            for index_2, machine in enumerate(machine_type_classlist):   # machine_type_classlist:[class1_1,class1_2,..]
                if not (machine.lock_list): # 如果目标没被别人选了
                    
                    D_mid = ((machine.x-robot_i.x)**2 + (machine.y-robot_i.y)**2) #* 1/self.machine_num_of_type[machine.type]  #有需要改的地方，最后一个factor
                    
                    if( (D_mid < D_min)): 
                        min_D_machine_id = machine.id
                        D_min = D_mid
        return min_D_machine_id

    def pickBuyerMachine(self, machine_dict, robot_i):
        
        if robot_i.take_obj in (1,2,3):  # 如果拿的是1.2.3:
            min_D_machine_id = 0
            D_min = 1000 
            for index_1,machine_type_classlist in enumerate(machine_dict[3:6]): # machine_dict:[[class4_1..],[class5_1,..],[class6_1]]
                for index_2, machine in enumerate(machine_type_classlist):   # machine_type_classlist:[class4_1,class4_2,..]
                    if not (machine.lock_list): # 如果目标没被别人选了
                        if machine.receive(robot_i.take_obj): # 目标这个原料格没满
                            
                            D_mid = ((machine.x-robot_i.x)**2 + (machine.y-robot_i.y)**2) * (1/self.type7_need_num[machine.type] * self.factor2)  # 按照公式去找4,5,6 D = d * type7_need_type4_num * type_receive_is_empty

                        
                        if( (D_mid < D_min)): 
                            min_D_machine_id = machine.id
                            D_min = D_mid
                            
            return min_D_machine_id
        
        elif robot_i.take_obj in (4,5,6):    # 去找7，4,5,6只能去找7
            
            min_D_machine_id = 0
            D_min = 1000 
            
            for index_1,machine_type_classlist in enumerate(machine_dict[6]): # machine_dict:[[class1_1..],[class2_1,..],[class3_1]]
                if not (machine.lock_list): # 如果目标没被别人选了
                    if machine.receive(robot_i.take_obj): # 目标这个原料格没满
                        
                        D_mid = ((machine.x-robot_i.x)**2 + (machine.y-robot_i.y)**2) 
                    
                    if( (D_mid < D_min)): 
                        min_D_machine_id = machine.id
                        D_min = D_mid
                        
            return min_D_machine_id
        
        else: # 否则就是拿着7，得去找8
            
            min_D_machine_id = 0
            D_min = 1000 
            
            for index_1,machine_type_classlist in enumerate(machine_dict[7]): # machine_dict:[[class1_1..],[class2_1,..],[class3_1]]
                if not (machine.lock_list): # 如果目标没被别人选了 
                    
                    D_mid = ((machine.x-robot_i.x)**2 + (machine.y-robot_i.y)**2) 
                    
                    if( (D_mid < D_min)): 
                        min_D_machine_id = machine.id
                        D_min = D_mid
                        
            return min_D_machine_id
        
    def buyInterupt(self,):
        
        aa = 1



