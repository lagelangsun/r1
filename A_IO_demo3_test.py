def calculateMap(staffLoc):  # 传入一个list,代表横纵坐标
    # 改动,五个参数分别是坐标x,y:
    locMachine = [staffLoc[1] * 0.5 + 0.25, staffLoc[0] * 0.5 + 0.25, 0, 0, 0]
    return locMachine


def calculateRobot(staffLoc):
    #所处工作台 ID 携带物品类型 时间价值系数 碰撞价值系数 角速度 线速度 朝向 坐标x 坐标y
    locRecord = [0, 0, 0, 0, 0, 0, 0, staffLoc[1]
                 * 0.5 + 0.25, staffLoc[0] * 0.5 + 0.25]
    return locRecord


def getInfo(server_info, machine_loc_dict, robot_state_list):  # 最后用self可以不传

    # 第一行输入 2 个整数，表示帧序号（从 1 开始递增）、当前金钱数。
    # 第二行输入 1 个整数，表示场上工作台的数量 K（K<=50）。
    # 紧接着 K 行数据，每一行表示一个工作台，分别由如下所示的数据构成，共计 6 个数字：
    # 接下来的 4 行数据，每一行表示一个机器人，分别由如下表格中所示的数据构成，每行 10 个数字。
    # 最后，判题器会输出一行 OK，表示所有数据已经写入完毕。

    data_line_0 = server_info[0].strip("\n").split()
    frame_id = int(data_line_0[0])
    current_money = int(data_line_0[1])
    k = int(server_info[1].strip("\n").split()[0])

    infoUpdateMachineDict(server_info[2: 2 + int(k)], machine_loc_dict) ######################3

    ##########################################
    #机器人行
    infoUpdateRobotList(server_info[2 + int(k): 2 + int(k) + 4], robot_state_list)

    server_info = []
    return robot_state_list



def infoUpdateMachineDict(server_info_machine, machine_loc_dict):
        
    for index_row, line in enumerate(server_info_machine):  # 接下来的行
        data_line = list(map(float, line.strip("\n").split())  #str转int
                        )  
        #到了工位行的时候
        #这里面从txt读的穿捡来的data_line全是文本，不知道到时候服务器传进来的是整数还是文本
        machine_type = data_line[0]  # 型号
        # print(machine_type)
        # 找到型号key:machineType对应的list[[x1,y1,0,0,0],[x2,y2,0,0,0],[x3,y3,0,0,0]....]
        machine_type_list = machine_loc_dict[machine_type]
        for i in range(len(machine_type_list)):  # 获取该型号机器人的个数，遍历该型号的list，找到对应的机器人
            if(data_line[1] == machine_type_list[i][0]):  # x坐标一样，所以这里要int()一下
                if(data_line[2] == machine_type_list[i][1]):  # y坐标一样
                    machine_type_list[i] = [data_line[1], data_line[2], data_line[3],
                                            data_line[4], data_line[5]]  # 对应的型号machinetype的机器人i更新
                    # 对应的型号machinetype更新
                    machine_loc_dict[machine_type] = machine_type_list
                    break
                else:
                    continue
            else:
                continue


#############################################################3
def infoUpdateRobotList(server_info_robot, robot_state_list):

    for index_row, line in enumerate(server_info_robot):  # 接下来的行
        data_line = list(map(float, line.strip("\n").split())  #str转int
                        )  
        robot_state_list[index_row] = data_line

    


def mapUpdateDict(MachineType, machine_loc_dict, indexRow, indexCal):

    Loc = machine_loc_dict[MachineType]
    locWithIndex = calculateMap([99-indexRow, indexCal])
    Loc.append(locWithIndex)  # 横纵坐标
    machine_loc_dict[MachineType] = Loc


lsm = open('maps/2.txt', mode='r')  # 最后换成读模块
content = lsm.readlines()

#
#
#
if __name__ == '__main__':

    robot_state_list = [] ################
    locMachine = []
    locWithIndex = []
    machine_loc_dict = {1: [], 2: [], 3: [],
                        4: [], 5: [], 6: [], 7: [], 8: [], 9: []}
    frame_id = 1
    current_money = 1
    k = 0

    for indexRow, line in enumerate(content):
        data_line = line.strip("\n").split()  # 去除首尾换行符，并按空格划分
        # print(data_line,'\n')
        for indexCal, mapChar in enumerate(data_line[0]):

            if(mapChar != '.'):
                if(mapChar == 'A'):
                    robot_state_list.append(calculateRobot([99-indexRow, indexCal]))
                else:
                    mapUpdateDict(int(mapChar), machine_loc_dict,
                                  indexRow, indexCal)

    for i in range(9):
        if(machine_loc_dict[i+1] == []):
            machine_loc_dict.pop(i+1, None)

    print(machine_loc_dict)
    print("*******************************")
    print(robot_state_list)

    lsm = open('5_in_test1.txt', mode='r')  # 最后换成读模块
    content = lsm.readlines()

    print("**************************************************************")



    # robot_state_list = getInfo(content, machine_loc_dict,robot_state_list)
    getInfo(content, machine_loc_dict,robot_state_list)
    print(machine_loc_dict)
    print("*******************************")
    print(robot_state_list)
