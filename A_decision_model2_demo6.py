import sys
import numpy as np
import math
import time
from copy import copy

from A_pre_calculate import CalculateFunc
from A_machine import Machine
from A_robot import Robot
from A_control_demo1 import Control



class DecisionModel_2(object): #decision demo1:只针对没有9的情况(只有78)
    def __init__(self, machine_num_of_type):

        self.frame_id = 0
        self.factor3 = 3


        self.factor_pick_456 = 0.5
        self.factor_456_num = 0  
        self.factor_7_need_456num = 0.5
        self.factor_7_raw_num = 0.5

        self.min_D_machine_id = -1
        self.action_finish = True
        # 型号7所需的型号4,5,6总num


        # self.robot_target_machine_dict = {0:None,1:None,2:None,3:None}
        self.all_robot_order_dict = {0:[0, 0, 0, 0, 0], 1:[1, 0, 0, 0, 0], 2:[2, 0, 0, 0, 0], 3:[3, 0, 0, 0, 0],}
        self.last_all_robot_order_dict = {0:[0, 0, 0, 0, 0], 1:[1, 0, 0, 0, 0], 2:[2, 0, 0, 0, 0], 3:[3, 0, 0, 0, 0],}
        self.robot_order = [0, 0, 0, 0, 0]

        # 1,2,3的数量，其实传进来所有type的数量，以备不时之需
        self.machine_num_of_type = machine_num_of_type # {1:int,2:int,....}

        # 型号7所需的型号4,5,6总num
        self.type7_need_num = {4:machine_num_of_type[7],5:machine_num_of_type[7],6:machine_num_of_type[7]} 
        # sys.stderr.write(str(self.type7_need_num))
        self.type123_need_num ={1:machine_num_of_type[4]+machine_num_of_type[5],2:machine_num_of_type[4]+machine_num_of_type[6],3:machine_num_of_type[5]+machine_num_of_type[6]}
        self.type123_num_count = self.type123_need_num[1] +  self.type123_need_num[2] +self.type123_need_num[3]

        self.machinetype_match_receive = {4:[1,2], 5:[1,3], 6:[2,3]}


        self.control = Control()


    # 现在还需要的是:7工作台的数量；1,2,3工作台的数量；7当前帧所需type4,5,6__num；
    def decision(self, robot_state_list
                 , machine_state_dict  # 按照工作台类型分类，是个dict
                 , machine_sort_by_receive # 按照可以接受的物料类型分类，是个dict
                 , machine_index_to_type_list # 按照工作台id顺序 ，是个list
                 , interupt_4567
                 , interupt_4567_start
                 , frame_id
                 ): # 是个dict
        
        sys.stderr.write('\n'+str(frame_id)+'****************************\n')
        
        # ************************* 决策部分 *********************************
        machine_state_list =  [value for key,value in machine_state_dict.items()] 

        # 如果有生产好的4,5,6,7 会在进入for之前截胡，直接把target给设好 ********************可优化，优化成正在生产的，在生产完毕之前提前去拿
        if interupt_4567: # 如果不为空，interupt_4567是个实例化列表[classx,classy,....]

            sys.stderr.write('in interupt'+'\n')
            sys.stderr.write(str(interupt_4567[0].id)+' '+str(interupt_4567[0].type)+'\n')

            # 遍历这个列表，列表里是一个个machine类
            for product_finish_class in interupt_4567:  # 列表里是一个个machine类

                    # 如果是7，直接去买,先判断interupt_4567里是不是有7,7的优先级高
                    if (product_finish_class.type == 7) : # 如果是7
                        
                        self.buyInterupt(product_finish_class, robot_state_list, machine_index_to_type_list, frame_id)  # 触发中断，找小车去办这事()

                    # 如果是4,5,6, 判断该帧是否有合适的小车去买，没有也无所谓，下一帧还会发来这个list，知道找到合适的小车
                    else:  
                    # sys.stderr.write('i amm 456 \n ' + str(self.type7_need_num)+'\n')
                    # sys.stderr.write(str(self.type7_need_num)+'\n')
                    # 如果还没被锁定(没有小车把这里设为目标
                            
                        # 如果场上有可接受该型号(4,5,6)物料的工作台(目前只考虑了7，没考虑9)
                        sys.stderr.write('self.type7_need_num: '+str(self.type7_need_num)+'\n')
                        if self.type7_need_num[product_finish_class.type] != 0:  #所有7的该型号的原料格不为空 != 0
                            # sys.stderr.write('i need that: '+ str(self.type7_need_num)+'\n')
                            self.buyInterupt(product_finish_class, robot_state_list, machine_index_to_type_list, frame_id)  # 触发中断，找小车去办这事()+
                                
               
        # 如果有开始生产型号，就对应的全场所需的1,2,3(4,5,6) or 4,5,6(7)增加
        if interupt_4567_start:
            for type_num in  interupt_4567_start:
                
                # 如果是4,5,6开始生产,那么对应的所需type123_need_num就要加1
                if type_num != 7:
                    for i in self.machinetype_match_receive[type_num]: 
                            self.type123_need_num[i] += 1
                else:  # 对于型号4,5,6 
                    sys.stderr.write('7 start produce \n')
                    self.type7_need_num[4] += 1
                    self.type7_need_num[5] += 1
                    self.type7_need_num[6] += 1

                

        # 如果触发了中断小车还要遍历不，其实可以遍历，因为大部分小车逻辑都简单，都是朝目标前进，所以不会执行太久从而引起跳帧
        for robot_i in robot_state_list:                              # 四个小车遍历

            if (robot_i.id == 1) | (robot_i.id == 0) | (robot_i.id == 2):
                sys.stderr.write('aaaaa robot & target:'+str(robot_i.id)+' '+str(robot_i.target)+'\n')
            # sys.stderr.write("in robot\n")
            robot_at_machine_id = robot_i.atmachine_id  # 将小车在哪个工作台附近赋给变量robot_at_machine_id，要不太长了

            # 如果小车现在不在工作台附近，或者没有目标，则执行运动指令，因为可能出现刚买卖完还没设定目标下一帧还在工作台附近的情况
            if (robot_at_machine_id == -1) | (not (robot_i.target)):              
                # sys.stderr.write("in move\n")

                # 如果已经有目标,说明不是刚买卖完的情况。target:[目标id, 买，卖]
                if robot_i.target:  # target不为空,target:[目标id, 买，卖]              
                        robot_i.move(machine_index_to_type_list[robot_i.target[0]]) # move 
                
                # 如果没有目标(刚买卖完)，就到这里选目标,所以在买卖后需要将target置空，买卖后的下一帧会执行到这里
                else:                                  

                    # 如果机器人手上没货，就要去买，找卖家选择要去哪个target_id买
                    if not robot_i.take_obj:            # 如果机器人手上没货

                        self.pickSellerMachine(machine_state_list, machine_index_to_type_list, robot_i)     # 更新self.min_D_machine_id,默认为-1

                        #如果在这一帧找到了合适的目标
                        if self.min_D_machine_id != -1:   #如果self.min_D_machine_id不是-1了
                            robot_i.target = [self.min_D_machine_id, 1, 0]          # 设置目标位,买位置1
                        else:   #否则，就在这里等等吧 ************************************这个地方还得优化，没找到合适的目标咋办。有9就好办了
                            robot_i.target = [] # 就上一帧的目标，那就置空，等着下一帧再选
                        robot_i.move(machine_index_to_type_list[self.min_D_machine_id]) # move
                    
                    # 机器人手上有货，就要去卖，找买家，选择要去哪个target_id卖
                    else:                               

                        self.pickBuyerMachine(machine_state_list, robot_i, machine_index_to_type_list) # 找买家
                        if self.min_D_machine_id != -1:
                            machine_index_to_type_list[self.min_D_machine_id].lock(robot_i.take_obj) # 锁住，选定的machine的take_obj原料格被锁住了
                            # if  machine_index_to_type_list[self.min_D_machine_id].type ==7: 
                            #     sys.stderr.write("in lock 1\n")    
                            #     sys.stderr.write('robot id: '+ str(robot_i.id)+'   robot take obj: '+ str(robot_i.take_obj)+'\n')
                            #     sys.stderr.write('machine id: ' +str(machine_index_to_type_list[self.min_D_machine_id].id)+ '   lock: ' +str(machine_index_to_type_list[self.min_D_machine_id].lock_list)+'\n\n')
                            robot_i.target = [self.min_D_machine_id, 0, 1]                           # 设置目标位，卖位置1
                        else: # 没找到合适的target去卖
                            robot_i.target = [] # 置空，等着下几帧再选 ************************************
                        robot_i.move(machine_index_to_type_list[self.min_D_machine_id])          # move
                        
            # 如果小车在工作台附近，判断是在哪个工作台附近
            else:                                              
                # sys.stderr.write("in action 1\n")
                # 如果是在目标工作台附近,说明需要有动作，有买或者卖
                if robot_i.target[0] == robot_at_machine_id:   # 如果是在目标工作台附近
                    
                    # 判断是要对目标工作台做什么行动，同时应重置目标
                    if robot_i.target[1]:  # 如果是目标是买target_id
                        robot_i.buy()      # *************************后面如果优化1,2,3的话也都要加上买锁
                        sys.stderr.write('robot & target:'+str(robot_i.id)+' '+str(robot_i.target)+'\n')
                        machine_index_to_type_list[int(robot_at_machine_id)].buyerUnlock() # 后面如果优化1,2,3的话也都要加上买锁,现在只解4,5,6锁，因为只有4,5,6上锁

                    # 如果是目标是卖给target_id
                    else: 
                        robot_i.sell()
                        # if machine_index_to_type_list[int(robot_i.target[0])].type == 8:
                            # sys.stderr.write('sell 8\n')
                        self.action_finish = True

                        # 如果不是8,9，卖了就解锁，其他小车又可以找这个当买家了，因为是找买家的时候锁定
                        # if not (machine_index_to_type_list[int(robot_at_machine_id)].type in (8,9)):
                        #     machine_index_to_type_list[int(robot_at_machine_id)].unlock(int(robot_i.take_obj)) # 卖了就解锁
                        # 在这里解锁

                    robot_i.target = []             # 清空target,下一帧的时候会重新select目标  ,也不能随意清空，得判断你是不是真的买到了或者卖了再清空，否则就会出错，现在先不考虑这个bug，这个判断很不好搞**************************************************
    
                else:   # 否则继续运动
                    robot_i.move(machine_index_to_type_list[robot_i.target[0]])
                    

            
    #去找1,2,3买,# **********************可优化，主要是优化factor
    def pickSellerMachine(self, machine_state_list, machine_index_to_type_list, robot_i): 
        
        min_D_machine_id = -1
        D_max = 0 
        # type123_most_need = max(self.type123_need_num, key=self.type123_need_num.get) 
        # sys.stderr.write('most_need: '+str(type123_most_need)+'\n')
        # 遍历所有卖家
        for index_1,machine in enumerate(machine_state_list[0:3]): # machine_dict:[[class1_1..],[class2_1,..],[class3_1]]
                if (machine.x<25) & (machine.y<25):
                    D_mid = (5000 - (machine.x-robot_i.x)**2 - (machine.y-robot_i.y)**2) #* self.type123_need_num[machine.type]/(self.type123_num_count) #* 1/self.machine_num_of_type[machine.type]  # factor要考虑现在场上还需要多少1,2,3；优先去拿需要的多的，先把4,5,6填满再说
                    if( (D_mid > D_max)): 
                        min_D_machine_id = machine.id
                        D_max = copy(D_mid)

        # sys.stderr.write('pick seller '+str(min_D_machine_id)+'\n')
        # sys.stderr.write('robot id: '+str(robot_i.id)+'    pick seller id:'+str(min_D_machine_id)+' seller type: '+str(machine_index_to_type_list[min_D_machine_id].type) +'\n\n')
        self.min_D_machine_id = min_D_machine_id

       

    # 就是这里(找买家的时候)容易出问题**********************
    def pickBuyerMachine(self, machine_dict, robot_i, machine_index_to_type_list): 
      
         # 如果拿的是1.2.3:
        if robot_i.take_obj in (1,2,3):  
            if robot_i.take_obj == 1:
                self.selectMinDMachineId_456(robot_i, machine_dict, machine_index_to_type_list) # 找买家
                if self.min_D_machine_id != -1:
                    self.type123_need_num[1] -= 1 # 场上共需的物料1的数量-1
            
            elif robot_i.take_obj == 2:
                self.selectMinDMachineId_456(robot_i, machine_dict, machine_index_to_type_list) # 找买家
                if self.min_D_machine_id != -1:
                    self.type123_need_num[2] -= 1 # 场上共需的物料2的数量-1
            else:
                self.selectMinDMachineId_456(robot_i, machine_dict, machine_index_to_type_list) # 找买家
                if self.min_D_machine_id != -1:
                    self.type123_need_num[3] -= 1 # 场上共需的物料1的数量-1

        # 去找7；4,5,6只能去找7
        elif robot_i.take_obj in (4,5,6):    
            
            if (robot_i.id == 1) | (robot_i.id == 0) | (robot_i.id == 2): 
                sys.stderr.write(str(robot_i.id)+' in 4,5,6 find buyer wity type ' + str(robot_i.take_obj)+'\n')
            min_D_machine_id = -1
            D_min = 5000 
            D_mid = 5000

            # 遍历所有7,对7来说，应该优先填满原料格，所以7的缺失原料factor应该稍大
            for index_1,machine in enumerate(machine_dict[6]): # machine_dict:[[class1_1..],[class2_1,..],[class3_1]]
                # sys.stderr.write(str(machine.type)+'  ')

                if (robot_i.id == 1) | (robot_i.id == 0) | (robot_i.id == 2):     
                    sys.stderr.write('machine id: ' +str(machine.id)+ '   lock: ' +str(machine.lock_list)+'\n')
                    sys.stderr.write('robot id: '+ str(robot_i.id)+'   robot take obj: '+ str(robot_i.take_obj)+'\n')

                # 目标这个原料格没满
                if robot_i.take_obj not in machine.lock_list: 
                    # if robot_i.id == 1: 
                    #     sys.stderr.write('in if2  \n')
                    #     sys.stderr.write(str(machine.lock_list)+'\n')
                    #     sys.stderr.write('machine id: '+str(machine.id)+' raw_num:'+str(machine.raw_num)+'\n')
                    D_mid = ((machine.x-robot_i.x)**2 + (machine.y-robot_i.y)**2)  * 1/(machine.raw_num + self.factor_7_raw_num) # 考虑到当前产品格数量，数量越多加权距离应该越小
                    # sys.stderr.write(str(D_mid)+'\n')

                
                    if (D_mid < D_min): 
                        min_D_machine_id = machine.id
                        D_min = copy(D_mid)
            if (robot_i.id == 1) | (robot_i.id == 0) | (robot_i.id == 2): sys.stderr.write(str(robot_i.id)+'in 4,5,6 last to ' + str(min_D_machine_id)+'\n')
            if min_D_machine_id != -1:
                machine_index_to_type_list[min_D_machine_id].raw_num += 1   # 这个7被设为目标了,那么就得加1
            self.min_D_machine_id = min_D_machine_id

        # 否则就是拿着7，得去找8
        else: 
            
            min_D_machine_id = 0
            D_min = 2500 
            
            for index_1,machine in enumerate(machine_dict[7]): # machine_dict:[[class1_1..],[class2_1,..],[class3_1]]
        #    if not (machine.lock_list): # 如果目标没被别人选了，8可以不用，8是秒生产
                    
                D_mid = ((machine.x-robot_i.x)**2 + (machine.y-robot_i.y)**2) 
                
                if( (D_mid < D_min)): 
                    min_D_machine_id = machine.id
                    D_min = copy(D_mid)
                        
            self.min_D_machine_id = min_D_machine_id

    # 根据最小D选4,5,6买家
    def selectMinDMachineId_456(self, robot_i, machine_state_dict, machine_index_to_type_list):

        min_D_machine_id = -1
        D_max = 0 

        type456_num = []
        type456_most_need = max(self.type7_need_num, key=self.type7_need_num.get) 
        if robot_i.take_obj not in self.machinetype_match_receive[type456_most_need]:
            if type456_most_need == 4:
                if self.type7_need_num[5] >= self.type7_need_num[6]:
                    type456_most_need = 5
                else:
                    type456_most_need = 6
            elif(type456_most_need == 5):
                if self.type7_need_num[4] >= self.type7_need_num[6]:
                    type456_most_need = 4
                else:
                    type456_most_need = 6
            else:
                if self.type7_need_num[4] >= self.type7_need_num[5]:
                    type456_most_need = 4
                else:
                    type456_most_need = 5

        sys.stderr.write('most_need: '+str(type456_most_need)+'\n')
        for index_1,machine in enumerate(machine_state_dict[type456_most_need-1]): # machine_dict:[[class1_1..],[class2_1,..],[class3_1]]
            sys.stderr.write('machine id: '+str(machine.id)+'\n')
            if machine.receive(robot_i.take_obj) & (not (robot_i.take_obj in machine.lock_list)) :
                sys.stderr.write('machine: '+str(machine.id)+' can take it\n')
                D_mid = (5000 - (machine.x-robot_i.x)**2 - (machine.y-robot_i.y)**2) #* self.type123_need_num[machine.type]/(self.type123_num_count) #* 1/self.machine_num_of_type[machine.type]  # factor要考虑现在场上还需要多少1,2,3；优先去拿需要的多的，先把4,5,6填满再说
                if( (D_mid > D_max)): 
                    min_D_machine_id = machine.id
                    D_max = copy(D_mid)

        sys.stderr.write('pick buyer '+str(min_D_machine_id)+'\n')
        sys.stderr.write('robot id: '+str(robot_i.id)+'    pick seller id:'+str(min_D_machine_id)+' seller type: '+str(machine_index_to_type_list[min_D_machine_id].type) +'\n\n')
        self.min_D_machine_id = min_D_machine_id
        

    def buyInterupt(self, machine, robot_state_list, machine_index_to_type_list, frame_id): # 找到小车去买4,5,6，并且不管他之前的目标是谁，都重新把目标设为4,5,6，如果没携带物品的话   *********** 但是有问题，如果场上现在不需要4,5,6，不能硬买
        sys.stderr.write('in buyInterupt '+' for '+ str(machine.id)+ ' type is '+str(machine.type)+'\n')
        min_D_robot = None
        fast_to_get = False
        ready_to_go = False

        if machine.remain_frame > 0: # 如果剩余生产时间>0，说明传进来了一个正在生产的工作台要判断小车赶到后是否能拿上东西
            fast_to_get = True
        else:
            ready_to_go = True  # 否则，说明是个已经生产完毕的工作台
            
        robot_can_get_list = [] #把可以去买这个小车的列在一块
        
        # 遍历4个小车，找到有空去买这个产品的小车
        for robot_i in robot_state_list: 

            if robot_i.target != []: # 如果已经有小车以这个为目标去卖了，就别让别的再把它设为目标了吧
                if (robot_i.id == 2): sys.stderr.write(' robot '+str(robot_i.id)+' can getin? target: '+str(robot_i.target)+'\n')
                if (robot_i.target == [machine.id,0,1]) :
                    if (robot_i.id == 2): sys.stderr.write(' robot '+str(robot_i.id)+' already to sell, target: '+str(robot_i.target)+'\n')
                    robot_can_get_list = [] # 这一帧就先不安排小车去办这事了，因为有车要去卖
                    break

            if fast_to_get: # 如果它是False的话，ready_to_go就不可能是True
                ready_to_go = self.calBuyTimeEnough(robot_i, machine) # 判断剩余生产时间是否小于小车过去的时间

            if robot_i.id == 2: sys.stderr.write('bbbbbbbbb robot: '+str(robot_i.id)+'  target:'+str(robot_i.target)+'\n')
            if ready_to_go:
                # 如果不是0，即已经携带了物品，就不选这个小车  *********************这个地方没修改好
                if (robot_i.take_obj != 0) :  # 如果不是0,还要判断,这小车的目标是不是这个machine，如果目标是这个machine的话，也要参与竞争 
                    if robot_i.target != []: 
                        if robot_i.target[0] == machine.id: # 如果目标是去这个工作台卖的的话，也要去参与竞争，因为大概率卖完就能买 *****************下次优化试试直接让这个工位锁定这个工作台
                            robot_can_get_list.append(robot_i)
                        else:
                            continue
                    else: # 如果它携带货物，而且根本没有目标的话，那这种情况好像不存在啊，有货物怎么可能没目标呢
                        continue

                # 但是如果帧数太少的话就不建议去买，具体多少帧我不好说，应该是(小车到7的距离+从7到8的距离)/大概的小车平均速度 < 剩余帧数 ,4,5,6,7买了太贵，如果卖不出去血亏，先只考虑7吧
                
                    
                else: 
                    # 这里代码写的不好，逻辑没问题但是代码复杂，太多ifelse
                    # 如果小车有target，上一个if已经把找到买家的小车continue了，这个if找的全是要去买货的小车
                    
                    # 但是如果帧数太少的话就不要去去买，具体怎么算我不好说，应该是(小车到7的距离+从7到8的距离)/大概的小车平均速度 < 剩余帧数 ,4,5,6,7买了太贵，如果卖不出去血亏，先只考虑7吧  ***************************可优化，可以设置为在过了多长时间后才执行这个判断，这样就不用每次都计算了
                    if self.calculateLaseTimeEnough(robot_i, machine, frame_id): #1帧是20ms   *************************目前有问题，目前全都continue了
                        continue
                    
                    else:
                        if robot_i == 1: sys.stderr.write('in here1\n')
                        if robot_i.target != []:  # 如果小车有target
                            # sys.stderr.write(str(robot_i.id)+' here? ' + str(robot_i.target)+' type: '+str(machine_index_to_type_list[robot_i.target[0]])+'\n')
                            # 如果小车已经找的卖家是4,5,6,7，那也不要用这个小车
                            if (machine_index_to_type_list[robot_i.target[0]].type in (4,5,6,7)) & (robot_i.target[0] != machine.id): # 如果target类型是4,5,6,7,并且小车的目标不是当前这个machine
                                # sys.stderr.write('robot_id_target: '+str(robot_i.target)+' type: '+ str(machine_index_to_type_list[robot_i.target[0]])+'\n')
                                continue  

                            # 如果小车的卖家是1,2,3, 这小车可以用
                            else: 
                                robot_can_get_list.append(robot_i)

                        # 如果小车没携带物品，也就是说小车在找卖家，就调度一下去买4,5,6 存疑，会有空target的现象出现么，还没想明白，先加上这个else再说***
                        else:
                            robot_can_get_list.append(robot_i)

        min_D_robot  = self.selectRobotToGet(machine, robot_can_get_list) 
        sys.stderr.write(' robot can get list: '+str(robot_can_get_list)+'\n')
        # 确实有小车可以去办这事，首先是设定target，然后锁一下************************
        if min_D_robot != None:    # 确实有小车可以去办这事，首先是设定target，然后锁一下************************
            # sys.stderr.write('which robot can do it to buy\n')
            self.robotToBuy4567(machine, min_D_robot, robot_state_list)


    def robotToBuy4567(self, machine, min_D_robot, robot_state_list):

        sys.stderr.write('car '+str(min_D_robot.id)+' do it , to buy '+ str(machine.type)+' \n\n')

        # 如果选出来的小车是本来就去这里卖的，那么这一帧就不要管他，不要cleartarget,也不用专门设置小车去买了
        # 因为这个小车卖了货之后按说会在下一帧直接被选为最近的去买才对
        if min_D_robot.target != []: # 选出来的小车是个有目标的小车，首先排除是去卖货的小车，携带物品的都被排除了(除了来这个工作台卖货的)
            if min_D_robot.target[2] == 0 : # 如果选出来的这个小车是去买的，而不是本来就朝着7走去卖的，就设置去买，否则这一帧不管
                self.clearLastTarget(min_D_robot, robot_state_list, machine)
                min_D_robot.target = [machine.id, 1 ,0] # 设定target,让这小车去买

                # 但是得是被去买的小车锁定的时候再上锁，被去卖的小车锁定了(也就是这一帧先不管)先不上锁
                if (not machine.buyer_lock) & (machine.type != 7)  :  # 如果没被上买锁,没问题啊，第一次选好小车的时候就相当于锁定了，肯定会有人去买，只不过后面去买的小车会随时变更
                    machine.buyerLock()  # 上买锁,啥时候解锁呢，我寻思寻思
                    self.type7_need_num[machine.type] -= 1 
            else:
                pass # 否则这一帧不管，加上个pass提醒一下

        else: # 如果选出来的小车目前没目标，那就是准备去买东西的
            self.clearLastTarget(min_D_robot, robot_state_list, machine)
            min_D_robot.target = [machine.id, 1 ,0] # 设定target,让这小车去买
            
            if (not machine.buyer_lock) & (machine.type != 7)  :  # 如果没被上买锁,没问题啊，第一次选好小车的时候就相当于锁定了，肯定会有人去买，只不过后面去买的小车会随时变更
                machine.buyerLock()  # 上买锁,啥时候解锁呢，我寻思寻思
                self.type7_need_num[machine.type] -= 1 

        sys.stderr.write('now robot & target:'+str(min_D_robot.id)+' '+str(min_D_robot.target)+'\n')
        

    def selectRobotToGet(self, machine, robot_can_get_list):
        if robot_can_get_list == []:
            return None
        
        else:
            D_min = 20000 
            for robot_can_get in robot_can_get_list:
                D_mid = ((machine.x-robot_can_get.x)**2 + (machine.y-robot_can_get.y)**2) * self.factor3  
                if(D_mid < D_min): 
                    min_D_robot = robot_can_get
                    D_min = copy(D_mid)

            return min_D_robot

   # 把上一个以它为目标的小车的target置为[]
    def clearLastTarget(self, min_D_robot_now, robot_state_list, machine):
        for robot_i in robot_state_list:
            if robot_i.target != []: 
                if (robot_i.target[0] == machine.id) & (robot_i.target[2] == 0): # 说明我只是去卖的，你不要把我target置空
                    if robot_i.id ==0:
                        sys.stderr.write('last robot & target:'+str(robot_i.id)+' '+str(robot_i.target)+'\n')
                        # sys.stderr.write('last robot & target:'+str(robot_i.id)+' '+str(robot_i.target)+'\n')

                    robot_i.target = []
    
    def calBuyTimeEnough(self, robot_i, machine):
        distance = math.sqrt((machine.x-robot_i.x)**2 + (machine.y-robot_i.y)**2)
        need_time = distance / 6 * 50 # 距离 / 6: 需要多少秒; 再 / 50,需要多少帧 
        # sys.stderr.write('robot_i :' + str(robot_i.id)+' calculate dis with:' +str(machine.id)+' type: ' +str(machine.type)+ '  dis: '+str(distance)+ ' time:'+str(need_time)+'\n')
        if machine.remain_frame < need_time:  # 过去的时间大于生产剩余时间
            return True
        else:
            return False

    # 计算时间是否足够
    def calculateLaseTimeEnough(self, robot_i, machine, frame_id):
        
        if machine.type != 7: #先暂时不考虑4,5,6了，可能出bug
            if 9000 - frame_id <= 500: #如果剩余时间太短就不去拿了，不知道如何计算剩余时间，就先设个常数吧。
                return True
            else:
                return False
        else:
            # need_frame_estimation =  (math.sqrt(machine.min_distance_78)  + math.sqrt((machine.x-robot_i.x)**2 + (machine.y-robot_i.y)**2) ) / 5 / 50  # 设置平均速度5吧，剩余帧数就是距离/5/50 ，除50是转换成帧
            # if need_frame_estimation >= (9000 - frame_id): # 如果所需帧数比剩余帧数大了, 那就是时间不够用了，就不去买了
            #     sys.stderr.write('need_frame_estimation: ' + str(need_frame_estimation) + 'frame_remain: ' + str(9000 - frame_id)+'\n')
            if 9000 - frame_id <= 600: #如果剩余时间太短就不去拿了，不知道如何计算剩余时间，就先设个常数吧。
                return True
            else:
                return False
            

            # sys.stderr.write(str(min_D_robot.take_obj)+ '  ' +str(min_D_robot.target)+ '\n')