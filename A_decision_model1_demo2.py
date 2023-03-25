import sys
import numpy as np
import math
import time
from copy import copy

from A_pre_calculate import CalculateFunc
from A_machine import Machine
from A_robot import Robot
from A_control_demo1 import Control


class DecisionModel_1(object): #decision demo1:只针对没有9的情况(只有78)
    def __init__(self, machine_num_of_type):

        self.frame_id = 0
        self.factor3 = 1

        self.factor_456_raw_num = 0.5
        self.factor_456_num = 0.5
        self.factor_7_need_456num = 0.5
        self.factor_7_raw_num = 1
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
        
        # self.buySellMove()
        # self.choosen_machine = self.chooseMinDMachine123(machine_state_dict)
        sys.stderr.write('\n'+str(frame_id)+'****************************\n')

        # 逻辑应该是：
        # 1. 初始的时候小车move最近的1,2,3 (move) 没必要，因为初始的时候need_factor 和 empty_factor都是一样的
        # 2. 到了最近的1,2,3之后，触发买指令 (buy)
        # 3. 拿到1,2,3之后，根据公式(D = d * type7_need_type4_num * type_receive_is_empty)计算到可接受这个obj的所有工位的加权距离，小车move到加权距离最短的4 or 5 or 6 (move)
        # 4. 到了加权距离最短的工作台后，卖掉 (sell),卖掉后清空target，重新找target
        # 5. 根据所需type1,2,3的数量，调度小车去买1 or 2 or 3  (buy)
        # 6. 将型号i卖给7成功后, 7对应型号nedd_typei_num -1  (self.type7_need_typei_num - 1)
        # 7. 若7生产完毕，且7原料格没满，则不管，直到下次有小车来送原料4,5,6到7，直接买走送到8 (if buy7 move sell8)
        # 8. 若7原料格已满且生产完毕，调度最近手上无货的小车去买7送8
        # 中断: ①若有类型为4,5,6的工作台生产完毕，距离其最近的手上没货的小车(且该小车还没有把4,5,6当买家)去买，就算该小车已经把target定为卖家1,2,3，也重新换目标,然后卖给7 (if move buy4,5,6 move sell7)
        #       ②若有类型为7的工作台生产完毕，逻辑同上。

        # buy 1,2,3
        
        # ************************* 决策部分 *********************************
        # machine_state_list =  [machine_state_dict.values()]
        machine_state_list =  [value for key,value in machine_state_dict.items()] 

        # 如果有生产好的4,5,6,7 会在进入for之前截胡，直接把target给设好 ********************可优化，优化成正在生产的，在生产完毕之前提前去拿
        if interupt_4567: # 如果不为空，interupt_4567是个实例化列表[classx,classy,....]
            # sys.stderr.write(str(interupt_4567)+'\n')

            # 遍历这个列表，列表里是一个个machine类
            for product_finish_class in interupt_4567:  # 列表里是一个个machine类

                    # 如果是7，直接去买,先判断interupt_4567里是不是有7,7的优先级高
                    if (product_finish_class.type == 7) & (not product_finish_class.buyer_lock): # 如果是7,并且没被锁住
                        
                        self.buyInterupt(product_finish_class, robot_state_list, machine_index_to_type_list, frame_id)  # 触发中断，找小车去办这事()

                    # 如果是4,5,6, 判断该帧是否有合适的小车去买，没有也无所谓，下一帧还会发来这个list，知道找到合适的小车
                    else:  
                    # sys.stderr.write('i amm 456 \n ' + str(self.type7_need_num)+'\n')
                    # sys.stderr.write(str(self.type7_need_num)+'\n')
                    # 如果还没被锁定(没有小车把这里设为目标)
                        if not product_finish_class.buyer_lock: # 如果还没被锁定
                            
                            

                            # 如果场上有可接受该型号(4,5,6)物料的工作台(目前只考虑了7，没考虑9)
                            if self.type7_need_num[product_finish_class.type] != 0:  #所有7的该型号的原料格不为空 != 0
                                # sys.stderr.write('i need that: '+ str(self.type7_need_num)+'\n')
                                self.buyInterupt(product_finish_class, robot_state_list, machine_index_to_type_list, frame_id)  # 触发中断，找小车去办这事()+
                                
                                
        # 如果有开始生产型号，就对应的全场所需的1,2,3(4,5,6) or 4,5,6(7)增加
        if interupt_4567_start:
            for type_num in  interupt_4567_start:
                
                            # 如果是去买4,5,6，那就买了就要去送给7，那么场上共需4 or 5 or 6的数量就要相应减一
                if type_num != 7:
                    for i in self.machinetype_match_receive[type_num]: 
                            self.type123_need_num[i] += 1
                else:  # 对于型号4,5,6 
                    # sys.stderr.write('7 start produce \n')
                    self.type7_need_num[4] += 1
                    self.type7_need_num[5] += 1
                    self.type7_need_num[6] += 1

                

        # 如果触发了中断小车还要遍历不，其实可以遍历，因为大部分小车逻辑都简单，都是朝目标前进，所以不会执行太久从而引起跳帧
        for i in range(4):                              # 四个小车遍历
            # sys.stderr.write("in robot\n")
            robot_at_machine_id = robot_state_list[i].atmachine_id  # 将小车在哪个工作台附近赋给变量robot_at_machine_id，要不太长了
            robot_i = robot_state_list[i]               # 将小车类赋给robot_i,要不太长了

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

                        self.pickSellerMachine(machine_state_list, robot_i)     # 更新self.min_D_machine_id,默认为-1

                        #如果在这一帧找到了合适的目标
                        if self.min_D_machine_id != -1:   #如果self.min_D_machine_id不是-1了
                            robot_i.target = [self.min_D_machine_id, 1, 0]          # 设置目标位,买位置1
                        else:   #否则，就在这里等等吧 ************************************这个地方还得优化，没找到合适的目标咋办。有9就好办了
                            robot_i.target = [] # 就上一帧的目标，那就置空，等着下一帧再选
                        robot_i.move(machine_index_to_type_list[self.min_D_machine_id]) # move
                    
                    # 机器人手上有货，就要去卖，找买家，选择要去哪个target_id卖
                    else:                               
                        
                        # 选出来的buyer，只可能是类型为4,5,6,7,8,9的工作台
                        self.pickBuyerMachine(machine_state_list, robot_i, machine_index_to_type_list) # 找买家
                        if self.min_D_machine_id != -1:
                            machine_index_to_type_list[self.min_D_machine_id].lock(robot_i.take_obj) # 锁住，选定的machine的take_obj原料格被锁住了
                            robot_i.target = [self.min_D_machine_id, 0, 1]                           # 设置目标位，卖位置1
                        else: # 没找到合适的target去卖
                            robot_i.target = [] # 置空，等着下几帧再选 ************************************
                        robot_i.move(machine_index_to_type_list[self.min_D_machine_id])          # move
                        
            # 如果小车在工作台附近，判断是在哪个工作台附近
            else:                                              
                # sys.stderr.write("in action 1\n")
                # sys.stderr.write(str(robot_at_machine_id)+"\n") 
                # sys.stderr.write(str(robot_i.target)+"\n")

                # 如果是在目标工作台附近,说明需要有动作，有买或者卖
                if robot_i.target[0] == robot_at_machine_id:   # 如果是在目标工作台附近
                    
                    # 判断是要对目标工作台做什么行动，同时应重置目标
                    if robot_i.target[1]:  # 如果是目标是买target_id
                        robot_i.buy()      # *************************后面如果优化1,2,3的话也都要加上买锁
                        machine_index_to_type_list[int(robot_at_machine_id)].buyerUnlock() # 后面如果优化1,2,3的话也都要加上买锁,现在只解4,5,6锁，因为只有4,5,6上锁

                    # 如果是目标是卖给target_id
                    else: 
                        robot_i.sell()
                        self.action_finish = True

                        # # 如果不是8,9，卖了就解锁，其他小车又可以找这个当买家了，因为是找买家的时候锁定
                        # if not (machine_index_to_type_list[int(robot_at_machine_id)].type in (8,9)):
                        #     machine_index_to_type_list[int(robot_at_machine_id)].unlock(int(robot_i.take_obj)) # 卖了就解锁
                        # # 在这里解锁

                    robot_i.target = []             # 清空target,下一帧的时候会重新select目标  ,也不能随意清空，得判断你是不是真的买到了或者卖了再清空，否则就会出错，现在先不考虑这个bug，这个判断很不好搞**************************************************
    
                else:   # 否则继续运动
                    robot_i.move(machine_index_to_type_list[robot_i.target[0]])
                    

        # **************** 控制部分 *************************  等着再优化优化，可以把robot里面的控制提出来
        # self.control(self.robot_target_machine_order
        #                          , self.robot_state_list
        #                          , self.machine_index_to_type_list
        #                          , self.all_robot_order_dict  # 这个变量，传起来有点复杂，但是如果能将控制从Robot类中拆出来就会好很多。
        #                          )
            
    #去找1,2,3买,# **********************可优化，主要是优化factor
    def pickSellerMachine(self, machine_state_list, robot_i): 

        # sys.stderr.write('pick seller \n')

        # 遍历所有卖家1,2,3


        if robot_i.id in (0,1):
            self.pickSellerD(machine_state_list[0], robot_i, machine_state_list)
        elif robot_i.id == 2:
            self.pickSellerD(machine_state_list[1], robot_i, machine_state_list)
        else:
            self.pickSellerD(machine_state_list[2], robot_i, machine_state_list)


        # sys.stderr.write('pick seller '+str(min_D_machine_id)+'\n')

        # sys.stderr.write('robot '+str(robot_i.id)+' have '+str(robot_i.take_obj) +' to '+ str(min_D_machine_id)+' which is type \n')

    def pickSellerD(self, machine_type_classlist, robot_i, machine_state_list):
        min_D_machine_id = -1
        D_max = 0 
        for index_1, machine in enumerate(machine_type_classlist):   # machine_type_classlist:[class1_1,class1_2,..]

            # 如果目标没被别人选了, 其实1,2,3就算被人锁了也可以去买，生产太快了，但是可能撞,所以先上个锁判断
            # if not (machine.lock_list): 
                
            D_mid = (5000 - (machine.x-robot_i.x)**2 - (machine.y-robot_i.y)**2) * self.type123_need_num[machine.type]/(self.type123_num_count) #* 1/self.machine_num_of_type[machine.type]  # factor要考虑现在场上还需要多少1,2,3；优先去拿需要的多的，先把4,5,6填满再说
            # sys.stderr.write(str(self.type123_need_num)+'\n')
            if( (D_mid > D_max)): 
                min_D_machine_id = machine.id
                D_max = copy(D_mid)

        self.min_D_machine_id =  min_D_machine_id

    # 就是这里(找买家的时候)容易出问题**********************
    def pickBuyerMachine(self, machine_state_list, robot_i, machine_index_to_type_list): 
        # sys.stderr.write('in pick Buyer \n')

         # 如果拿的是1.2.3:
        if robot_i.take_obj in (1,2,3):  
            if robot_i.take_obj == 1:
                self.selectMinDMachineId_456(robot_i, machine_state_list[3:5], machine_index_to_type_list, machine_state_list) # 找买家
                self.type123_need_num[1] -= 1 # 场上共需的物料1的数量-1
            
            elif robot_i.take_obj == 2:
                self.selectMinDMachineId_456(robot_i, [machine_state_list[3],machine_state_list[5]], machine_index_to_type_list,machine_state_list) # 找买家
                self.type123_need_num[2] -= 1 # 场上共需的物料2的数量-1
            else:
                self.selectMinDMachineId_456(robot_i, machine_state_list[4:6], machine_index_to_type_list,machine_state_list) # 找买家
                self.type123_need_num[3] -= 1 # 场上共需的物料13的数量-1

        # 去找7；4,5,6只能去找7
        elif robot_i.take_obj in (4,5,6):    
            
            # sys.stderr.write(str(robot_i.id)+'in 4,5,6 ' + str(min_D_machine_id)+'\n')
            min_D_machine_id = -1
            D_min = 5000 
            D_mid = 5000
            for_break = False
            # 遍历所有7,对7来说，应该优先填满原料格，所以7的缺失原料factor应该稍大
            for index_1,machine in enumerate(machine_state_list[6]): # machine_dict:[[class1_1..],[class2_1,..],[class3_1]]
                # sys.stderr.write(str(machine.type)+'  ')

                # # 如果目标没被别的小车选了，不应该加这个是不是，只要原料格没满就行，被别人选了也无所谓
                # if machine.lock_list == []: 
                #     # sys.stderr.write('in if1  ')

                # 妈的，优先选两个7去跑吧，服了
                if (machine.id == machine_state_list[6][0].id) | (machine.id == machine_state_list[6][-1].id):
                    sys.stderr.write('right here\n')
                    if machine.receive(robot_i.take_obj):
                        self.min_D_machine_id = machine.id
                        sys.stderr.write('select: '+str(self.min_D_machine_id)+' type: '+str(machine.type)+'\n')
                        for_break = True
                        machine_index_to_type_list[min_D_machine_id].raw_num += 1
                        break
                # 目标这个原料格没满
   
                if machine.receive(robot_i.take_obj): 
                    # sys.stderr.write('in if2  ')
                    # sys.stderr.write('machine id: '+str(machine.id)+' raw_num:'+str(machine.raw_num)+'\n')
                    D_mid = ((machine.x-robot_i.x)**2 + (machine.y-robot_i.y)**2)  * 1/(machine.raw_num + self.factor_7_raw_num) # 考虑到当前产品格数量，数量越多加权距离应该越小
                    # sys.stderr.write(str(D_mid)+'\n')

                if (D_mid < D_min): 
                    min_D_machine_id = machine.id
                    D_min = copy(D_mid)
            sys.stderr.write(str(robot_i.id)+' to ' + str(min_D_machine_id)+'\n\n')
            if not for_break:
                machine_index_to_type_list[min_D_machine_id].raw_num += 1   # 这个7被设为目标了,那么就得加1
                self.min_D_machine_id = min_D_machine_id

        # 否则就是拿着7，得去找8
        else: 
            
            min_D_machine_id = 0
            D_min = 2500 
            
            for index_1,machine in enumerate(machine_state_list[7]): # machine_dict:[[class1_1..],[class2_1,..],[class3_1]]
        #    if not (machine.lock_list): # 如果目标没被别人选了，8可以不用，8是秒生产
                    
                D_mid = ((machine.x-robot_i.x)**2 + (machine.y-robot_i.y)**2) 
                
                if( (D_mid < D_min)): 
                    min_D_machine_id = machine.id
                    D_min = copy(D_mid)
                        
            self.min_D_machine_id = min_D_machine_id
    
    # 根据最小D选4,5,6买家
    def selectMinDMachineId_456(self, robot_i, machine_dict, machine_index_to_type_list, machine_state_list):

        min_D_machine_id = -1
        D_min = 5000 
        break_flag = False
        go_type = 1

        for i in (4,5,6):
            if (machine_state_list[6][0].receive(i)) | (machine_state_list[6][-1].receive(i)):
                go_type = i
                break

        sys.stderr.write('go_type: '+str(go_type-1)+'\n')
        #遍历所有买家
        for index_1,machine_type_classlist in enumerate(machine_dict): # machine_dict:[[class4_1..],[class5_1,..],[class6_1]]
            for index_2, machine in enumerate(machine_state_list[go_type-1]):   # machine_type_classlist:[class4_1,class4_2,..]
                # if(robot_i.id == 3):
                sys.stderr.write('two for machine_id: '+str(machine.id)+' '+'machine_type '+str(machine.type)+'\n')
                #     if  machine.receive(robot_i.take_obj): sys.stderr.write('can receive\n')
                #     if not (robot_i.take_obj in machine.lock_list): sys.stderr.write('not target\n')

                # # 目标这个原料格没满，并且这个格子没被别人锁住,判断加权距离是不是更近
                if machine.receive(robot_i.take_obj) & (not (robot_i.take_obj in machine.lock_list)) : # 目标这个原料格没满，并且这个格子没被别人锁住

                #     if (machine_state_list[6][0].receive(machine.type)) | (machine_state_list[6][-1].receive(machine.type)):
                #         machine_index_to_type_list[min_D_machine_id].raw_num += 1   # 这个456被设为目标了,那么就得加1
                #         self.min_D_machine_id = machine.type
                #         break_flag = True
                #         break
                #     # if(robot_i.id ==3): sys.stderr.write('in ? machine_id: '+str(machine.id)+' '+'machine_type '+str(machine.type)+'\n')
                #     else:
                    D_mid = ((machine.x-robot_i.x)**2 + (machine.y-robot_i.y)**2) * (1/(self.type7_need_num[machine.type]+ self.factor_7_need_456num))  *  (1/(machine.raw_num + self.factor_456_raw_num))  # 按照公式去找4,5,6 D = d * type7_need_type4_num * type_receive_is_empty
                    # sys.stderr.write('D_mid: '+str(D_mid)+'\n')
                    if(D_mid < D_min): # 判断加权距离是不是更近
                        
                        min_D_machine_id = machine.id
                        # if(robot_i.id ==3): 
                        #     sys.stderr.write('start update machine_id machine_id: '+str(machine.id)+' '+'machine_type '+str(machine.type)+'\n')
                        #     sys.stderr.write('D_mid: '+str(D_mid)+'\n')
                        #     sys.stderr.write('min_D_machine_id: '+str(min_D_machine_id)+'\n')
                        D_min = copy(D_mid)

            # if (robot_i.id ==3): sys.stderr.write('robot '+str(robot_i.id)+' have '+str(robot_i.take_obj) +' to '+ str(min_D_machine_id)+' which is type \n\n')
        if min_D_machine_id != -1:
            machine_index_to_type_list[min_D_machine_id].raw_num += 1   # 这个456被设为目标了,那么就得加1
            self.min_D_machine_id = min_D_machine_id

    def buyInterupt(self, machine, robot_state_list, machine_index_to_type_list, frame_id): # 找到小车去买4,5,6，并且不管他之前的目标是谁，都重新把目标设为4,5,6，如果没携带物品的话   *********** 但是有问题，如果场上现在不需要4,5,6，不能硬买
        # sys.stderr.write('buyInterupt \n')
        min_D_robot = None
        D_min = 5000 

        # 遍历4个小车，找到有空去买这个产品的小车
        for robot_i in robot_state_list: 

            # 如果不是0，即已经携带了物品，就不选这个小车  *********************这个地方没修改好
            if (robot_i.take_obj != 0) :  # 如果不是0
                continue

            # 但是如果帧数太少的话就不建议去买，具体多少帧我不好说，应该是(小车到7的距离+从7到8的距离)/大概的小车平均速度 < 剩余帧数 ,4,5,6,7买了太贵，如果卖不出去血亏，先只考虑7吧
            
                
            else: 
                # 这里代码写的不好，逻辑没问题但是代码复杂，太多ifelse
                #如果小车有target，上一个if已经把找到买家的小车continue了，这个if找的全是要去买货的小车
                
                # 但是如果帧数太少的话就不要去去买，具体怎么算我不好说，应该是(小车到7的距离+从7到8的距离)/大概的小车平均速度 < 剩余帧数 ,4,5,6,7买了太贵，如果卖不出去血亏，先只考虑7吧  ***************************可优化，可以设置为在过了多长时间后才执行这个判断，这样就不用每次都计算了
                if self.calculateTimeEnough(robot_i, machine, frame_id): #1帧是20ms   *************************目前有问题，目前全都continue了
                    continue
                
                else:
                    if robot_i.target != []:  # 如果小车有target
                        # sys.stderr.write(str(robot_i.id)+' here? ' + str(robot_i.target)+' type: '+str(machine_index_to_type_list[robot_i.target[0]])+'\n')
                        # 如果小车已经找的卖家是4,5,6,7，那也不要用这个小车
                        if machine_index_to_type_list[robot_i.target[0]].type in (4,5,6,7): # 如果target类型是4,5,6,7
                            # sys.stderr.write('robot_id_target: '+str(robot_i.target)+' type: '+ str(machine_index_to_type_list[robot_i.target[0]])+'\n')
                            continue  

                        # # 如果小车的卖家是1,2,3, 这小车可以用
                        # else: 
                            
                        #     D_mid = ((machine.x-robot_i.x)**2 + (machine.y-robot_i.y)**2) * self.factor3  

                        #     if(D_mid < D_min): 
                        #         min_D_robot = robot_i
                        #         D_min = copy(D_mid)

                    # 如果小车没携带物品，也就是说小车在找卖家，就调度一下去买4,5,6 存疑，会有空target的现象出现么，还没想明白，先加上这个else再说***
                    else:
                        D_mid = ((machine.x-robot_i.x)**2 + (machine.y-robot_i.y)**2) * self.factor3  

                        if(D_mid < D_min): 
                            min_D_robot = robot_i
                            D_min = copy(D_mid)

        # 确实有小车可以去办这事，首先是设定target，然后锁一下************************
        if min_D_robot != None:    # 确实有小车可以去办这事，首先是设定target，然后锁一下************************
            # sys.stderr.write(str(min_D_robot.id)+' to buy '+ str(machine.type)+' \n\n')
            min_D_robot.target = [machine.id, 1 ,0] # 设定target,让这小车去买
            machine.buyerLock()  # 上买锁,有小车去买这个产品了(只限4,5,6)
            if machine.type != 7:
                self.type7_need_num[machine.type] -= 1 


    # 计算时间是否足够
    def calculateTimeEnough(self, robot_i, machine, frame_id):
        
        if machine.type != 7: #先暂时不考虑4,5,6了，可能出bug
            if 9000 - frame_id <= 200: #如果剩余时间太短就不去拿了，不知道如何计算剩余时间，就先设个常数吧。
                return True
            else:
                return False
        else:
            # need_frame_estimation =  (math.sqrt(machine.min_distance_78)  + math.sqrt((machine.x-robot_i.x)**2 + (machine.y-robot_i.y)**2) ) / 5 / 50  # 设置平均速度5吧，剩余帧数就是距离/5/50 ，除50是转换成帧
            # if need_frame_estimation >= (9000 - frame_id): # 如果所需帧数比剩余帧数大了, 那就是时间不够用了，就不去买了
            #     sys.stderr.write('need_frame_estimation: ' + str(need_frame_estimation) + 'frame_remain: ' + str(9000 - frame_id)+'\n')
            if 9000 - frame_id <= 300: #如果剩余时间太短就不去拿了，不知道如何计算剩余时间，就先设个常数吧。
                return True
            else:
                return False
            

            # sys.stderr.write(str(min_D_robot.take_obj)+ '  ' +str(min_D_robot.target)+ '\n')
