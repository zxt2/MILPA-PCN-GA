import networkx as nx
import random
import xlrd
import related
import GA
import OnePath
import K_path_Average_Amount
import time
import csv


# 输入LN网络数据
G = nx.DiGraph()

data = xlrd.open_workbook('LNdata/LNchannels.xls', encoding_override='utf-8')
table = data.sheets()[0]
nrows = table.nrows

for run in range(100):

    for i in range(0, nrows):
        channel = table.row_values(i)
        G.add_edge(int(channel[0]), int(channel[1]), balance=round(float(channel[2]) / 2, 3))
        G.add_edge(int(channel[0]), int(channel[1]), basis=round(random.uniform(0, 0.01), 4))
        G.add_edge(int(channel[0]), int(channel[1]), slope=round(random.uniform(0, 0.02), 4))

        G.add_edge(int(channel[1]), int(channel[0]), balance=round(float(channel[2]) / 2, 3))
        G.add_edge(int(channel[1]), int(channel[0]), basis=round(random.uniform(0, 0.01), 4))
        G.add_edge(int(channel[1]), int(channel[0]), slope=round(random.uniform(0, 0.02), 4))

    nodelist = []
    table1 = data.sheets()[1]
    nrows1 = table1.nrows
    for j in range(0, nrows1):
        capacity = table1.row_values(j)
        if capacity[1] > 100:
            nodelist = nodelist + [int(capacity[0])]

    number = len(nodelist)
    krange = 4

    writelist = []
    totalAmount = int(random.uniform(1, 30))
    start = nodelist[random.randint(0, number-1)]  # 起点
    end = nodelist[random.randint(0, number-1)]  # 终点
    while start == end:
        end = nodelist[random.randint(0, number-1)]  # 终点

    print(start, end)

    # One path
    print("单条路径")
    OP_start = time.time()
    OnePath_result = OnePath.Dijkstra(G, start, end, totalAmount)
    OP_time = time.time() - OP_start
    # print(OnePath_result)
    OnePath_cost = 0
    OP_pl = 0
    if OnePath_result != 0:
        OP_pl = len(OnePath_result)
        for i in range(len(OnePath_result) - 1):
            slope1 = G[OnePath_result[i]][OnePath_result[i + 1]]['slope']
            basis1 = G[OnePath_result[i]][OnePath_result[i + 1]]['basis']
            OnePath_cost = round((OnePath_cost + slope1 * totalAmount + basis1), 4)
    else:
        OnePath_cost = -1
    print("fee：", OnePath_cost)
    print('time：', OP_time)
    print('pathlenth：', OP_pl)
    writelist = writelist + [OnePath_cost, OP_time, OP_pl]

    # 遗传算法
    print('遗传算法')
    itertime = 50
    GA_start = time.time()
    GA_result = {}
    GA_pl = {}
    k1 = OnePath.Dijkstra(G, start, end, totalAmount)
    cost1 = 0
    pl1 = 0
    if k1 != 0:
        pl1 = len(k1)
        for i in range(len(k1) - 1):
            slope1 = G[k1[i]][k1[i + 1]]['slope']
            basis1 = G[k1[i]][k1[i + 1]]['basis']
            cost1 = round((cost1 + slope1 * totalAmount + basis1), 4)

    GA_result.update({1: cost1})
    GA_pl.update({1: pl1})

    for k in range(2, krange, 1):
        GA_return = GA.Genetic_Algorithm(G, k, start, end, totalAmount, itertime)
        GA_cost = GA_return[0]
        GA_pathl = GA_return[1]
        GA_result.update({k: GA_cost})
        GA_pl.update({k: GA_pathl})
    GA_time = time.time() - GA_start
    print(GA_result, GA_pl)
    if len(GA_result) != 0:
        mink = min(GA_result, key=GA_result.get)  # 最优解的k值
        while GA_result[mink] == 0:
            del GA_result[mink]
            if len(GA_result) != 0:
                mink = min(GA_result, key=GA_result.get)
            else:
                mink = 0
                GA_result[0] = -1
                GA_pl[0] = 0
                break
                break
    print('time：', GA_time)
    print("k：", mink, 'fee:', GA_result[mink], 'pathlenth:', GA_pl[mink])
    writelist = writelist+[mink, GA_result[mink], GA_time, GA_pl[mink]]

    # k条路径平均分配金额
    print("k条路径平均分配")
    aver_start = time.time()
    K_pl = 0
    K_sum = 0
    if mink != 0:
        K_path_Average = K_path_Average_Amount.K_path_Average(G, mink, start, end, totalAmount)
        print(K_path_Average)
        if K_path_Average != 0:
            K_cost = related.CalculateCost(G, mink, K_path_Average, K_path_Average['amount'])
            for i in range(mink):
                K_sum = K_sum + len(K_path_Average[i])
            K_pl = round((K_sum/mink),2)
        else:
            K_cost = -1
        print("fee：", K_cost)
    else:
        K_cost = -1
    aver_time = time.time() - aver_start
    print('time：', aver_time, 'pathlenth:', K_pl)
    writelist = writelist + [K_cost, aver_time, K_pl]

    # 输出结果
    print(writelist)
    with open("result_LNscale.csv", "a", newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(writelist)
        csvfile.close()

