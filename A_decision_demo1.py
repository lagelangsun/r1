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
        self.min_D_machine_id = -1
        self.action_finish = True
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
                 , interupt_4567
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
        machine_state_list =  [value for key,value in machine_state_dict.items()] 

        if interupt_4567: # 如果不为空，interupt_4567是个实例化列表[classx,classy,....],经过决策部分就会给小车设了target了
                          # 会在进入for之前截胡，直接把target给设好
            # sys.stderr.write(str(interupt_4567)+'\n')
            for product_finish_class in interupt_4567:  # 遍历这个列表
                if product_finish_class.type in (4,5,6): # 如果是4,5,6
                    if self.type7_need_num[product_finish_class.type]:  # 如果可接受该型号，即所有7的该型号的原料格不为空 != 0
                        self.buyInterupt(product_finish_class, robot_state_list)  # 触发中断，找小车去办这事()
                else:
                    self.buyInterupt(product_finish_class, robot_state_list)  # 触发中断，找小车去办这事()

                

        # 如果触发了中断小车还要遍历不，其实可以遍历，因为大部分小车逻辑都简单，都是朝目标前进，所以不会执行太久从而引起跳帧
        for i in range(4):                              # 四个小车遍历
            # sys.stderr.write("in robot\n")
            robot_at_machine_id = robot_state_list[i].atmachine_id  # 将小车在哪个工作台附近赋给变量robot_at_machine_id
            robot_i = robot_state_list[i]               # 将小车类赋给robot_i

            if (robot_at_machine_id == -1) | (not (robot_i.target)):              # 如果小车现在不在工作台附近，或者没有目标执行运动指令，因为可能出现刚买卖完下一帧还在工作台附近的情况
                # sys.stderr.write("in move\n")
                if robot_i.target:                      # 如果已经有目标,即target不为空,说明不是刚买卖完的情况。target:[目标id, 买，卖]
                        robot_i.move(machine_index_to_type_list[robot_i.target[0]]) # move 
                        
                else:                                   # 如果没有目标(刚买卖完)，就选目标,所以在买卖后需要将target置空，买卖后的下一帧会执行到这里

                    if not robot_i.take_obj:            # 如果机器人手上没货，就要去买，找卖家选择要去哪个target_id买

                        self.pickSellerMachine(machine_state_list, robot_i)     # 更新self.min_D_machine_id
                        if self.min_D_machine_id != -1:   #如果在这一帧找到了合适的目标
                            robot_i.target = [self.min_D_machine_id, 1, 0]          # 设置目标位,买位置1
                        else:   #否则，就在这里等等吧 ************************************
                            robot_i.target = [] # 就上一帧的目标，那就置空，等着下一帧再选
                        robot_i.move(machine_index_to_type_list[self.min_D_machine_id]) # move
                        
                    else:                               # 否则就要去卖，找买家，选择要去哪个target_id卖

                        self.pickBuyerMachine(machine_state_list, robot_i)
                        if self.min_D_machine_id != -1:
                            machine_index_to_type_list[self.min_D_machine_id].lock(robot_i.take_obj) # 锁住，选定的machine的take_obj原料格被锁住了
                            robot_i.target = [self.min_D_machine_id, 0, 1]                           # 设置目标位，卖位置1
                        else: # 没找到合适的target去卖
                            robot_i.target = [] # 置空，等着下几帧再选 ************************************
                        robot_i.move(machine_index_to_type_list[self.min_D_machine_id])          # move
                        
 
            else:                                              # 如果小车在工作台附近，判断是在哪个工作台附近
                # sys.stderr.write("in action 1\n")
                # sys.stderr.write(str(robot_at_machine_id)+"\n") 
                # sys.stderr.write(str(robot_i.target)+"\n")
                if robot_i.target[0] == robot_at_machine_id:   # 如果是在目标工作台附近,说明有动作，有买或者卖
                    
                    # 判断是要对目标工作台做什么行动，同时应重置目标
                    if robot_i.target[1]:  # 如果是目标是买target_id
                        robot_i.buy()

                    else: # 如果是目标是卖给target_id
                        robot_i.sell()
                        self.action_finish = True
                        machine_index_to_type_list[int(robot_at_machine_id)].unlock(int(robot_i.take_obj)) # 卖了就解锁，其他小车又可以找这个当买家了，因为是找买家的时候锁定的
                        # 在这里解锁

                    robot_i.target = []             # 清空target,下一帧的时候会重新select目标  ,也不能随意清空，得判断你是不是真的买到了或者卖了再清空，否则就会出错，现在先不考虑这个bug**************************************************
    
                else:   # 否则继续运动
                    robot_i.move(machine_index_to_type_list[robot_i.target[0]])
                    

        # **************** 控制部分 *************************  等着再优化优化，可以把robot里面的控制提出来
        # self.control(self.robot_target_machine_order
        #                          , self.robot_state_list
        #                          , self.machine_index_to_type_list
        #                          , self.all_robot_order_dict  # 这个变量，传起来有点复杂，但是如果能将控制从Robot类中拆出来就会好很多。
        #                          )
            
    def pickSellerMachine(self, machine_state_list, robot_i): #去找1,2,3买,# **********************可优化

        # sys.stderr.write('pick seller \n')
        min_D_machine_id = -1
        D_min = 2500 
        for index_1,machine_type_classlist in enumerate(machine_state_list[0:3]): # machine_dict:[[class1_1..],[class2_1,..],[class3_1]]
            for index_2, machine in enumerate(machine_type_classlist):   # machine_type_classlist:[class1_1,class1_2,..]
                if not (machine.lock_list): # 如果目标没被别人选了, 其实1,2,3就算被人锁了也可以去买，生产太快了，但是可能撞
                    
                    D_mid = ((machine.x-robot_i.x)**2 + (machine.y-robot_i.y)**2) #* 1/self.machine_num_of_type[machine.type]  #有需要改的地方，最后一个factor
                    
                    if( (D_mid < D_min)): 
                        min_D_machine_id = machine.id
                        D_min = D_mid
        # sys.stderr.write('pick seller '+str(min_D_machine_id)+'\n')

        self.min_D_machine_id = min_D_machine_id

    def pickBuyerMachine(self, machine_dict, robot_i): # 就是这里容易出问题**********************
        # sys.stderr.write('in pick Buyer \n')
        if robot_i.take_obj in (1,2,3):  # 如果拿的是1.2.3:
            if robot_i.take_obj == 1:
                self.selectMinDMachineId_456(robot_i, machine_dict[3:5])
            
            elif robot_i.take_obj == 2:
                self.selectMinDMachineId_456(robot_i, [machine_dict[3],machine_dict[5]])
        
            else:
                self.selectMinDMachineId_456(robot_i, machine_dict[4:6])

        elif robot_i.take_obj in (4,5,6):    # 去找7；4,5,6只能去找7
            
            # sys.stderr.write(str(robot_i.id)+'in 4,5,6 ' + str(min_D_machine_id)+'\n')
            min_D_machine_id = -1
            D_min = 2500 
            D_mid = 2500
            for index_1,machine in enumerate(machine_dict[6]): # machine_dict:[[class1_1..],[class2_1,..],[class3_1]]
                sys.stderr.write(str(machine.type)+'  ')
                if machine.lock_list == []: # 如果目标没被别人选了
                    # sys.stderr.write('in if1  ')
                    if machine.receive(robot_i.take_obj): # 目标这个原料格没满
                        # sys.stderr.write('in if2  ')
                        D_mid = ((machine.x-robot_i.x)**2 + (machine.y-robot_i.y)**2) 
                        # sys.stderr.write(str(D_mid)+'\n')

                    if (D_mid < D_min): 
                        min_D_machine_id = machine.id
                        D_min = D_mid
            # sys.stderr.write(str(robot_i.id)+' in 4,5,6 ' + str(min_D_machine_id)+'\n')

            self.min_D_machine_id = min_D_machine_id
        
        else: # 否则就是拿着7，得去找8
            
            min_D_machine_id = 0
            D_min = 2500 
            
            for index_1,machine in enumerate(machine_dict[7]): # machine_dict:[[class1_1..],[class2_1,..],[class3_1]]
                if not (machine.lock_list): # 如果目标没被别人选了 
                    
                    D_mid = ((machine.x-robot_i.x)**2 + (machine.y-robot_i.y)**2) 
                    
                    if( (D_mid < D_min)): 
                        min_D_machine_id = machine.id
                        D_min = D_mid
                        
            self.min_D_machine_id = min_D_machine_id
    
    def selectMinDMachineId_456(self, robot_i, machine_dict): # 根据最小D选456买家

        min_D_machine_id = -1
        D_min = 2500 
        for index_1,machine_type_classlist in enumerate(machine_dict): # machine_dict:[[class4_1..],[class5_1,..],[class6_1]]
            for index_2, machine in enumerate(machine_type_classlist):   # machine_type_classlist:[class4_1,class4_2,..]

                if machine.receive(robot_i.take_obj) & (not (robot_i.take_obj in machine.lock_list)) : # 目标这个原料格没满，并且这个格子没被别人锁住
    
                    D_mid = ((machine.x-robot_i.x)**2 + (machine.y-robot_i.y)**2) * (1/(self.type7_need_num[machine.type]+0.1) * self.factor2)  # 按照公式去找4,5,6 D = d * type7_need_type4_num * type_receive_is_empty

                    if(D_mid < D_min): 
                        min_D_machine_id = machine.id
                        D_min = D_mid
                    
        self.min_D_machine_id = min_D_machine_id

    def buyInterupt(self, machine, robot_state_list):
        # sys.stderr.write('buyInterupt \n')
        min_D_robot = None
        D_min = 2500 
        for robot_i in robot_state_list: # 遍历4个小车，找到有空去买这个产品的小车
            if robot_i.take_obj != 0:  # 如果不是0，即已经携带了物品，就不选这个小车
                continue
            else:
                D_mid = ((machine.x-robot_i.x)**2 + (machine.y-robot_i.y)**2) * self.factor3  

                if(D_mid < D_min): 
                    min_D_robot = robot_i
                    D_min = D_mid

        if min_D_robot != None:    # 确实有小车可以去办这事，首先是设定target，然后锁一下************************
            # sys.stderr.write(str(min_D_robot)+'\n')
            min_D_robot.target = [machine.id, 1 ,0] # 让这小车去买
            if machine.type != 7:
                self.type7_need_num[machine.type] -= 1
            else:
                self.type7_need_num[4] += 1
                self.type7_need_num[5] += 1
                self.type7_need_num[6] += 1

            # sys.stderr.write(str(min_D_robot.take_obj)+ '  ' +str(min_D_robot.target)+ '\n')

            
                    
                

        



