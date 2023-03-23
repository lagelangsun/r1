import numpy as np
from copy import copy

RECEIVE_MACHINE_ID_LIST = {1: [4, 5, 9], 2: [4, 6, 9], 3: [5, 6, 9], 4: [7, 9],  
                           5: [7, 9], 6: [7, 9], 7: [8, 9]}

class DecisionModel_2(object): #decision demo1:只针对没有9的情况(只有78)
    def __init__(self):
        self.id = 0


    # 现在还需要的是:7工作台的数量；1,2,3工作台的数量；7当前帧所需type4,5,6__num；
    def decision(self, robot_state_list
                 , machine_state_dict  # 按照工作台类型分类，是个dict
                 , machine_sort_by_receive # 按照可以接受的物料类型分类，是个dict
                 , machine_index_to_type_list # 按照工作台id顺序 ，是个list
                 , interupt_4567
                 , interupt_4567_start
                 , frame_id
                 ): # 是个dict
        
        # self.flag = self.flag + 1
        # # sys.stderr.write('flag %d\n' % (self.flag))
        # # sys.stderr.write('frame_id %d\n' % (self.frame_id))
        # for i in range(len(self.robot_state_list)):
        # for i in range(4):
            # robot = self.robot_state_list[i]
            # wait_flag = True # 如果原材料格都满了，等待
            # # # sys.stderr.write('machine_raw_status is\n')
            # if 7 in self.machine_state_dict.keys():
            #     for machine in self.machine_state_dict[7]:
            #         # # sys.stderr.write('machine_raw_status is'+ str(machine.raw_status)+'\n')
            #         if not machine.raw_full():
            #             # 没有装满，继续
            #             wait_flag = False
            #             break
            # if wait_flag == True:
            #     for obj_id in range(4, 7):
            #         for machine in self.machine_state_dict[obj_id]:
            #             if not machine.raw_full():
            #                 # 没有装满，继续
            #                 wait_flag = False
            #                 break
            # if wait_flag == True:
            #     self.finish()
            # # sys.stderr.write('fsdfhkasghahgjklahgladgjhasljgiklahlgilajlgjaligjlikajgljadlghjkladhgfjilj\n')    
        for i in range(4):
            # 获取机器人对象
            robot = robot_state_list[i]
            # nearest_machine = None
            # sys.stderr.write('---------------I am robot ' + str(robot.id) + '-------------\n')
            # 机器人携带的物品
            # sys.stderr.write('my x is ' + str(robot.x)+'\n')
            # sys.stderr.write('my y is ' + str(robot.y)+'\n')
            take_obj = int(robot_state_list[i].take_obj) 
            # sys.stderr.write('take_obj is '+ str(take_obj)+'\n')
            # if robot.target1 == None:
            #     # sys.stderr.write('my init target1 is none\n')
            # else:
                # sys.stderr.write('my init target1 is '+ str(robot.target1.type)+'\n')
                # sys.stderr.write('my init target1 id is '+ str(robot.target1.id)+'\n')
            if int(robot.atmachine_id) == int(-1):
                at_machine_type = -1
            else:
                at_machine = machine_index_to_type_list[int(robot.atmachine_id)]
                at_machine_type = at_machine.type 
            # sys.stderr.write('at_machine_type is '+ str(at_machine_type)+'\n')
            
            if frame_id <= 50:
                # 前50帧所有物品都没有生产好，找最近的123号工作台并移动过去
                if at_machine_type in [1, 2, 3]:
                    robot.move(at_machine)
                    robot.target1 = at_machine
                else:
                    machine_list = []
                    for i in range(1, 4):
                        for machine in machine_state_dict[i]:
                            machine_list.append(machine)
                                            
                    nearest_machine = robot.find_nearest_machine(machine_list)
                    if (int(nearest_machine.type) not in [1, 2, 3]) & (not nearest_machine.product_lock):
                        nearest_machine.product_lock = True
                        # sys.stderr.write('lock '+ str(nearest_machine.type) + 'product its id is'+ str(nearest_machine.id) + '\n')

                    if robot.target1 == None:
                        robot.move(nearest_machine)
                        robot.target1 = nearest_machine
                    else:
                        robot.move(robot.target1)
                    # if robot.target1 != None:
                    #     # sys.stderr.write('target1 is changed to'+ str(robot.target1.type) + '\n')
                    #     # sys.stderr.write('target1_id is changed to: '+str(robot.target1.id) + '\n')
                
            else:

                if take_obj == 0:
                    # 如果机器人没有携带物品，寻找最大价值的工作台
                    if robot.target1 == None:
                        # 如果机器人没有移动的目标，寻找最大价值的工作台
                        nearest_machine = robot.find_most_valuable_machine(machine_state_dict)
                        # sys.stderr.write(str(nearest_machine == None)+'\n')
                        if nearest_machine != None:
                            # 如果找到了，预定这个工作台的产品并移动过去
                            if (int(nearest_machine.type) not in [1, 2, 3]) & (not nearest_machine.product_lock):
                                nearest_machine.product_lock = True
                            # # sys.stderr.write('nearest_machine'+str(nearest_machine.type) + '\n')
                            robot.move(nearest_machine) # 移动至目标工作台
                            robot.target1 = nearest_machine
                            # # sys.stderr.write('target1 is changed to'+ str(robot.target1.type) + '\n')
                            # # sys.stderr.write('target1_id is changed to: '+str(robot.target1.id) + '\n')
                    else:
                        # 如果机器人有移动的目标，判断机器人所处位置
                        if at_machine_type != -1:
                            # 如果机器人处在某个工作台
                            # # sys.stderr.write('at_machine.product_status is xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx' + str(at_machine.product_status)+'\n')
                            if robot.target1 == at_machine:
                                # 如果机器人所处工作台就是目标工作台，尝试购买
                                # if int(at_machine.product_status) == 1:
                                if int(at_machine.product_status) == 1:
                                    robot.buy()
                                    if int(at_machine_type) not in  [1, 2, 3]:
                                        at_machine.product_lock = False
                                        # sys.stderr.write('unlock '+ str(at_machine_type) + 'product its id is'+ str(at_machine.id) + '\n')
                                    # robot.unlock(at_machine)
                                    robot.target1 = None
                                else:
                                    # 如果不能购买，继续寻找最大价值工作台
                                    nearest_machine = robot.find_most_valuable_machine(machine_state_dict)
                                    if nearest_machine != None:
                                        # 如果找到了，移动过去
                                        if (int(nearest_machine.type) not in [1, 2, 3]) & (not nearest_machine.product_lock):
                                            nearest_machine.product_lock = True
                                            # sys.stderr.write('lock '+ str(nearest_machine.type) + 'product its id is'+ str(nearest_machine.id) + '\n')
                                        # # sys.stderr.write('nearest_machine'+str(nearest_machine.type) + '\n')
                                        robot.move(nearest_machine) # 移动至目标工作台
                                        robot.target1 = nearest_machine
                                        # # sys.stderr.write('target1 is changed to'+ str(robot.target1.type) + '\n')
                                        # # sys.stderr.write('target1_id is changed to: '+str(robot.target1.id) + '\n')
                                    else:
                                        # 如果没找到，继续在原工作台等待
                                        robot.move(robot.target1)
                                        # # sys.stderr.write('target1 is changed to'+ str(robot.target1.type) + '\n')
                                        # # sys.stderr.write('target1_id is changed to: '+str(robot.target1.id) + '\n')
                                
                            else:

                                robot.move(robot.target1)
                                # # sys.stderr.write('target1 is changed to'+ str(robot.target1.type) + '\n')
                                # # sys.stderr.write('target1_id is changed to: '+str(robot.target1.id) + '\n')
                            
                        else:

                            robot.move(robot.target1) # 移动至目标工作台
                            # # sys.stderr.write('target1 is changed to'+ str(robot.target1.type) + '\n')
                            # # sys.stderr.write('target1_id is changed to: '+str(robot.target1.id) + '\n')
                                # robot.target1 = nearest_machine
                                # # sys.stderr.write('target1 is '+ str(target1.type) + '\n')
                else:
                    # 如果机器人携带物品，寻找能购买该物品的工作台
                    # 如果机器人所处工作台能够购买该物品，直接卖
                    # receive_machine_list = RECEIVE_MACHINE_ID_LIST[take_obj]
                    # if at_machine_type in receive_machine_list:
                    # 如果机器人位于能够卖出的工作台附近，判断能否工作台能否购买
                    if at_machine_type != -1:
                        if at_machine.receive(take_obj):
                            # 如果工作台可以购买，立即卖出
                            # # sys.stderr.write('hhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhh\n')
                            robot.sell()
                            if take_obj in at_machine.lock_list:
                                at_machine.unlock(take_obj)
                            robot.target1 = None
                        else:
                            # 如果机器人所处工作台不能够购买该物品
                            # if robot.target1 != None:
                            #     robot.move(robot.target1)
                            # else:
                            # 如果机器人没有目标，寻找一个最近的
                            # # sys.stderr.write('hhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhh\n')
                            buyer = robot.find_buyer(machine_sort_by_receive)
                            if buyer != None:
                                robot.move(buyer)
                                robot.target1 = buyer
                                if take_obj in [4, 5, 6, 7]:
                                    buyer.lock(take_obj)
                                # sys.stderr.write('buyer is to'+ str(robot.target1.type) + '\n')
                                # sys.stderr.write('buyer_id is to: '+str(robot.target1.id) + '\n')
                            # else:
                            #     if take_obj in [1, 2, 3]:
                            #         robot.destroy()
                                # robot.unlock()
                    else:
                        # 如果机器人不在任何工作台，寻找最近的
                        if robot.target1 != None:
                            robot.move(robot.target1)
                        else:
                            # 如果机器人没有目标，寻找一个最近的
                            # # sys.stderr.write('hhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhh\n')
                            buyer = robot.find_buyer(machine_sort_by_receive)
                            
                            if buyer != None:
                                # behavior = 'sell' + str(buyer.id) + str(take_obj)
                                # if behavior 
                                robot.move(buyer)
                                robot.target1 = buyer
                                if take_obj in [4, 5, 6, 7]:
                                    buyer.lock(take_obj)
                                # buyer.buy_status = buyer.buy_status + pow(2, int(take_obj))
                                # sys.stderr.write('buyer is to'+ str(robot.target1.type) + '\n')
                                # sys.stderr.write('buyer_id is to: '+str(robot.target1.id) + '\n')

        
