import random
from typing import List, Dict, Tuple

# 定义物品和工厂的类
class Item:
    def __init__(self, id: int, source: int, time: int, value: int):
        self.id = id # 物品编号
        self.source = source # 生产该物品的工厂编号
        self.time = time # 生产该物品所需时间
        self.value = value # 该物品的利润

class Factory:
    def __init__(self, id: int, location: Tuple[int, int]):
        self.id = id # 工厂编号
        self.location = location # 工厂的位置

# 定义全局变量
ITEMS = {} # 物品字典，key为物品编号，value为Item对象
FACTORIES = {} # 工厂字典，key为工厂编号，value为Factory对象
ROBOTS = [] # 机器人列表，存储所有机器人的位置

# 读取地图信息，初始化ITEMS、FACTORIES、ROBOTS
def read_map_info(map_info: Dict) -> None:
    # 遍历所有物品
    for item in map_info["items"]:
        id = item["id"]
        source = item["source"]
        time = item["time"]
        value = item["value"]
        ITEMS[id] = Item(id, source, time, value)

    # 遍历所有工厂
    for factory in map_info["factories"]:
        id = factory["id"]
        location = (factory["x"], factory["y"])
        FACTORIES[id] = Factory(id, location)

        # 如果是机器人，将其加入ROBOTS列表
        if id >= 10:
            ROBOTS.append(location)

# 判断工厂类型
for i in range(50):
    if node_type[i] == 1 or node_type[i] == 2 or node_type[i] == 3:
        # if i <= 2:
            raw_fac.append(i)
        # else:
        #     manu_fac.append(i)
    elif node_type[i] >= 4 and node_type[i] <= 6:
        pro_fac[node_type[i]-4] = i
    elif node_type[i] == 7:
        product_fac = i
    elif node_type[i] == 8:
        buy_fac = i
    elif node_type[i] == 9:
        buy_all_fac = i
    else:
        pass

# 建图
graph = defaultdict(list)
for i in range(50):
    for j in range(i+1, 50):
        dist = math.sqrt((x[i]-x[j])**2 + (y[i]-y[j])**2)
        if i in raw_fac and j in pro_fac:
            graph[i].append((j, dist+1))
            graph[j].append((i, dist+1))
        # elif i in manu_fac and j in pro_fac:
        #     if j == pro_fac[i-3]:
        #         graph[i].append((j, dist+10))
        #         graph[j].append((i, dist+10))
        elif i == product_fac and j in pro_fac:
            graph[i].append((j, dist+20))
            graph[j].append((i, dist+20))
        elif i == buy_fac and j == product_fac:
            graph[i].append((j, dist))
            graph[j].append((i, dist))
        elif i == buy_all_fac and (j in raw_fac or j == product_fac):
            graph[i].append((j, dist))
            graph[j].append((i, dist))
        else:
            pass
def dijkstra(start, end, graph):
  
    # 初始化dist和visited
    dist = {node: float('inf') for node in graph.keys()}
    visited = {node: False for node in graph.keys()}
    dist[start] = 0

    # Dijkstra算法
    while not visited[end]:
        # 找到当前未访问节点中距离起点最近的节点
        current_node = min(dist, key=dist.get)

        # 如果当前节点是终点，则直接返回最短路径
        if current_node == end:
            path = []
            while current_node != start:
                path.append(current_node)
                current_node = graph[current_node]['prev']
            path.append(start)
            return list(reversed(path)), dist[end]

        # 更新当前节点的邻居节点的距离
        for neighbor, weight in graph[current_node]['neighbors'].items():
            if not visited[neighbor]:
                new_dist = dist[current_node] + weight
                if new_dist < dist[neighbor]:
                    dist[neighbor] = new_dist
                    graph[neighbor]['prev'] = current_node

        # 将当前节点标记为已访问
        visited[current_node] = True

    return None, None

# 找到每个工厂的位置和类型
factory_positions = {}
factory_types = {}
for i in range(len(map_data)):  #map_data是个50*50
    for j in range(len(map_data[i])):
        if map_data[i][j] >= 1 and map_data[i][j] <= 9:
            factory_positions[map_data[i][j]] = (i, j)  #key是map_data[i][j]，那么就是一个字符串，但是每次factory_positions[map_data[i][j]]都会被新的工作台的位置覆盖，有bug
            factory_types[map_data[i][j]] = 'raw_material' if map_data[i][j] <= 3 else ('processing' if map_data[i][j] >= 4 and map_data[i][j] <= 6 else 'purchasing')

# 构建图
graph = {}
for i in range(1, 10): #工作天类型，读图看看有几种类型的工作台，建立graph
    if i in factory_positions: #i  factory_positions的key是一个字符串,需要int转一下
        graph[i] = {'neighbors': {}, 'prev': None} #graph的key就是工作台类型(i)
for i in range(1, 8): #1~7
    if i in factory_positions:
        if factory_types[i] == 'raw_material':
            graph[i]['neighbors'][i+3] = 1
        elif factor
        y_types[i] == 'processing':
            if i == 4:
                graph[i]['neighbors'][7] = 1
            elif i == 5:
                graph[i]['neighbors'][7] = 1
            elif i == 6:
                graph[i]['neighbors'][7] = 1
        elif factory_types[i] == 'purchasing':
            if i == 8:
                graph[i]['neighbors'][7] = 1
            elif i == 9:
                for j in range(1, 8):
                    if j in factory_positions:
                        graph[i]['neighbors'][j] = 1
# 计算总利润
def calculate_total_profit(path):
    
    # 创造工厂的字典
    factories_copy = copy.deepcopy(factories)
    # 初始化
    total_profit = 0
   
    for i in range(len(path)-1):
        # 找到起始工厂和终点工厂
        start_factory = factories[path[i]]
        end_factory = factories[path[i+1]]
       
        item = start_factory['item']
        # 如果初始工厂是加工工厂，要先确定它的原材料是否已经备齐
        if start_factory['type'] in processing_factories:
            for material in start_factory['materials']:
                if factories_copy[material]['quantity'] == 0:
                    # If a required material is missing, return 0 profit
                    return 0
                else:
                    factories_copy[material]['quantity'] -= 1
       
        if item in [1, 2, 3]:
            total_profit += 3000
        elif item in [4, 5, 6]:
            total_profit += 8000
        elif item == 7:
            total_profit += 3000
        # 更新接收物品工厂的情况
        factories_copy[end_factory['name']]['item'] = item
        factories_copy[end_factory['name']]['quantity'] += 1
    return total_profit


