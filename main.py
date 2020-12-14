import networkx as nx
import random
import related
import GA
import OnePath
import K_path_Average_Amount
import time
import csv
import os
import re

krange = 4
nodes = 50

# 循环次数 结果记录在result_small_scale.csv中
for run in range(500):
    totalAmount = int(random.uniform(1, 30))  # 总金额
    start = int(random.uniform(0, nodes))  # 起点
    end = int(random.uniform(0, nodes))  # 终点
    while start == end:
        end = int(random.uniform(0, nodes))  # 终点

    # 随机生成一个图
    G = nx.erdos_renyi_graph(nodes, 0.2)
    G = G.to_directed()
    for u, v in G.edges():
        # balance:通道余额
        G.add_edge(u, v, balance=int(random.uniform(1, 200)))
        # slope，basis：每个通道收费 fee=slope*Amount+basis
        G.add_edge(u, v, slope=round(random.uniform(0, 0.02), 4))
        G.add_edge(u, v, basis=round(random.uniform(0, 0.01), 4))

    # 精确算法
    print("精确算法")
    related.WriteData(G, totalAmount, start, end)
    d = os.popen("glpsol --model Modelnew.mod --data data.txt --output rr.sol")
    # print(d.read())
    ret = d.read()
    ret = ret.split('\n')
    for timeline in ret:
        t = re.search("Time", timeline)
        if t:
            accutime = re.findall(r"\d+\.?\d*", timeline)
            exact_time = float(accutime[0])
            print('time：', exact_time)

    solution_object = open('rr.sol')
    try:
        for costline in solution_object:
            g = re.search("Objective", costline)
            if g:
                accucost = re.findall(r"\d+\.?\d*", costline)
                exact_cost = float(accucost[0])
                print("cost：", exact_cost)
    finally:
        solution_object.close()
    writelist = [exact_time, exact_cost]

    # 遗传算法
    print('遗传算法')
    itertime = 50
    GA_start = time.time()
    GA_result = {}
    k1 = OnePath.Dijkstra(G, start, end, totalAmount)
    cost1 = 0
    if k1 != 0:
        for i in range(len(k1) - 1):
            slope1 = G[k1[i]][k1[i + 1]]['slope']
            basis1 = G[k1[i]][k1[i + 1]]['basis']
            cost1 = round((cost1 + slope1 * totalAmount + basis1), 4)
    GA_result.update({1: cost1})

    for k in range(2, krange, 1):
        GA_return = GA.Genetic_Algorithm(G, k, start, end, totalAmount, itertime)
        GA_cost = GA_return[0]
        GA_result.update({k: GA_cost})
    GA_time = time.time() - GA_start
    print(GA_result)
    if len(GA_result) != 0:
        mink = min(GA_result, key=GA_result.get)  # 最优解的k值
        while GA_result[mink] == 0:
            del GA_result[mink]
            if len(GA_result) != 0:
                mink = min(GA_result, key=GA_result.get)
            else:
                mink = 0
                GA_result[0] = -1
                break
                break
    print('time：', GA_time)
    print("k：", mink, 'fee:', GA_result[mink])
    writelist = writelist + [mink, GA_result[mink], GA_time]

    # One path
    print("单条路径")
    OP_start = time.time()
    OnePath_result = OnePath.Dijkstra(G, start, end, totalAmount)
    OP_time = time.time() - OP_start
    # print(OnePath_result)
    OnePath_cost = 0
    if OnePath_result != 0:
        for i in range(len(OnePath_result) - 1):
            slope1 = G[OnePath_result[i]][OnePath_result[i + 1]]['slope']
            basis1 = G[OnePath_result[i]][OnePath_result[i + 1]]['basis']
            OnePath_cost = round((OnePath_cost + slope1 * totalAmount + basis1), 4)
    else:
        OnePath_cost = -1
    print("fee：", OnePath_cost)
    print('time：', OP_time)
    writelist = writelist + [OnePath_cost, OP_time]

    # k条路径平均分配金额
    print("k条路径平均分配")
    aver_start = time.time()
    if mink != 0:
        K_path_Average = K_path_Average_Amount.K_path_Average(G, mink, start, end, totalAmount)
        if K_path_Average != 0:
            K_cost = related.CalculateCost(G, mink, K_path_Average, K_path_Average['amount'])
        else:
            K_cost = -1
        print("fee：", K_cost)
    else:
        K_cost = -1
    aver_time = time.time() - aver_start
    print('time：', aver_time)
    writelist = writelist + [K_cost, aver_time]

    # 输出结果
    print(writelist)
    with open("result_small_scale.csv", "a", newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(writelist)
        csvfile.close()
