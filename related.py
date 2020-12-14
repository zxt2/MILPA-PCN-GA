import math
import heapq
import operator
import random
import numpy
import copy


# write data to file
# for glpk
def WriteData(G, totalAmount, start, end):
    with open('data.txt', 'w') as datafile:
        datafile.write("\ndata;\n\n")

        # 节点
        datafile.write("set N:=")
        for i in range(G.number_of_nodes()):
            datafile.write(" " + str(i))
        datafile.write(";\n\n")

        # 通道余额
        datafile.write("param r:=\n")
        for u, v in G.edges():
            if G[u][v]['balance'] > 0:
                datafile.write("[" + str(u) + "," + str(v) + "] " + str(G[u][v]['balance']) + " ")
        datafile.write(";\n\n")

        # 基础费用
        datafile.write("param baseFee:=\n")
        for u, v in G.edges():
            if G[u][v]['balance'] > 0:
                datafile.write("[" + str(u) + "," + str(v) + "] " + str(G[u][v]['basis']) + " ")
        datafile.write(";\n\n")

        # 比例费用
        datafile.write("param slope:=\n")
        for u, v in G.edges():
            if G[u][v]['balance'] > 0:
                datafile.write("[" + str(u) + "," + str(v) + "] " + str(G[u][v]['slope']) + " ")
        datafile.write(";\n\n")

        datafile.write("\nparam source := " + str(start) + ";\n\n")
        datafile.write("\nparam destination := " + str(end) + ";\n\n")
        datafile.write("param P := " + str(totalAmount) + ";\n\n")
        datafile.write("end;\n\n")

        datafile.close()


# Dijkstra 有容量限制条件下求最短路径
def Dijkstra(G, start, end, amount):
    RG = G.reverse()
    dist = {}
    previous = {}
    fee = {}
    path = []
    for v in RG.nodes():
        dist[v] = float('inf')
        previous[v] = 'none'
        fee[v] = 0
    dist[end] = 0
    u = end

    while u != start:
        u = min(dist, key=dist.get)
        distu = dist[u]
        feeu = fee[u]
        del dist[u]
        for u, v in RG.edges(u):
            if v in dist:
                slope = RG[u][v]['slope']
                basis = RG[u][v]['basis']
                alt = round((distu + slope * amount + basis), 4)
                f = round((feeu + slope * amount + basis), 4)
                if RG[u][v]['balance'] < amount + f:
                    alt = float('inf')
                if alt < dist[v]:
                    dist[v] = alt
                    previous[v] = u
                    fee[v] = f
    path.append(start)
    last = start
    while last != end:
        if previous[last] == 'none':
            path = 0
            break
        else:
            nxt = previous[last]
            path.append(nxt)
            last = nxt
    if path == 0:
        print('未找到路径')
    return path


# 生成初始种群
def Generate_initial_population(G, k, start, end, totalAmount):
    amount = math.ceil(totalAmount / k)  # 初始每条路径平均分配金额
    tmpG = copy.deepcopy(G)
    path = {}
    for i in range(k + 1):
        path[i] = Dijkstra(tmpG, start, end, amount)
        if path[i] == 0:
            return 0
        else:
            bal = float('inf')
            pre = 0
            for j in range(len(path[i]) - 1):
                if bal > tmpG[path[i][j]][path[i][j + 1]]['balance']:    # 选择一条路径里面最小的边 置为0 以免找到相同路径
                    bal = tmpG[path[i][j]][path[i][j + 1]]['balance']
                    pre = j
            tmpG[path[i][pre]][path[i][pre + 1]]['balance'] = 0

            for p in range(len(path[i]) - 1):
                if p != pre:
                    f = Calculatefee(G, path[i], amount, p+1)
                    tmpG[path[i][p]][path[i][p + 1]]['balance'] = tmpG[path[i][p]][path[i][p + 1]]['balance'] - (amount+f)  # 减余额+fee

    tmpindividual = {}
    individual = {}
    for i in range(k + 1):
        individual[i] = {}
    amount_array = []
    for i in range(k):
        amount_array.append(amount)

    for i in range(k + 1):
        tmpindividual[i] = copy.deepcopy(path)
        del tmpindividual[i][i]
        j = 0
        for key, value in tmpindividual[i].items():
            if key != 'amount':
                individual[i][j] = value
                j += 1
        individual[i].update({'amount': amount_array})

    # 调整初始种群amount总数正确
    for i in range(len(individual)):
        individual[i]['amount'][k - 1] = totalAmount - sum(individual[i]['amount']) + individual[i]['amount'][k - 1]

    return individual


# 计算个体适应度——计算每个个体支付费用
# 传参：path--一个个体 {0: [路径0], 1: [路径1], ……, 'amount': []}
def Calculatefitness(G, k, path, amount):
    fitness = 0
    for i in range(k):
        for j in range(len(path[i]) - 1):
            slope1 = G[path[i][j]][path[i][j + 1]]['slope']
            basis1 = G[path[i][j]][path[i][j + 1]]['basis']
            fitness = round((fitness + slope1 * amount[i] + basis1), 4)
    return fitness


# 计算cost
def CalculateCost(G, k, path, amount):
    Cost = []
    for i in range(k):
        Cost.append(1)
        Cost[i] = 0
        for j in range(len(path[i]) - 1):
            slope1 = G[path[i][j]][path[i][j + 1]]['slope']
            basis1 = G[path[i][j]][path[i][j + 1]]['basis']
            Cost[i] = round((Cost[i] + slope1 * amount[i] + basis1), 4)
        if amount[i] == 0:
            Cost[i] = 0

    return round(sum(Cost), 4)


# 选择父辈 适者生存
# 输入 上一代种群 适应度 选择比例
def selectfathers(individual, fit, percent):
    n = len(individual)  # 个体数量
    fathern = int(n * percent)
    re1 = map(fit.index, heapq.nsmallest(fathern, fit))
    fatherindex = list(re1)

    father = {}
    j = 0
    for i in fatherindex:
        father[j] = individual[i]
        j = j + 1
    return father


# 交叉操作
# 每个个体里 随机选两条路 进行交叉
def Crossover_Operator(G, k, father):
    lenth = []
    for i in range(k):
        lenth = lenth + [i]
    pathindex = random.sample(lenth, 2)

    path1 = father[pathindex[0]]
    path2 = father[pathindex[1]]
    path3 = []      # 保存公共点
    for i in path1:
        for j in path2:
            if i == j:
                path3.append(i)

    if len(path3) == 2:
        # print("没有交叉点")
        newpath1 = path1
        newpath2 = path2
    else:
        path3 = path3[1:len(path3) - 1]
        if path3 != []:
            point = random.choice(path3)
            index1 = path1.index(point)
            index2 = path2.index(point)
            newpath1 = path1[0:index1] + path2[index2:len(path2)]
            newpath2 = path2[0:index2] + path1[index1:len(path1)]
        else:
            newpath1 = path1
            newpath2 = path2

    son = copy.deepcopy(father)

    son.update({pathindex[0]: newpath1, pathindex[1]: newpath2})

    # 如果路径上balance不够
    enough = BalanceEnough(G, son, k)
    if enough == 0:
        return father
    else:
        return son


# 变异操作1
# 随机加减每条路上的amount
def Variation_Operator(G, individual, k, percent, totalAmount):
    tmpindividual = copy.deepcopy(individual)
    VariationRange = 2   # 变异范围
    increment = round(random.uniform(0, VariationRange), 4)
    n = len(tmpindividual)  # 个体数量
    lenth = list(range(0, n))
    variationindex = random.sample(lenth, int(n * percent))

    for i in variationindex:
        tmpamount = copy.deepcopy(tmpindividual[i]['amount'])

        for j in range(k):
            sign = int(random.uniform(0, 2))
            tmpamount[j] = round(tmpamount[j] + numpy.power(-1, sign) * increment, 4)
            if tmpamount[j] < 0:
                tmpamount[j] = 0

        suma = sum(tmpamount)
        if suma == 0:
            return individual
        for v in range(k):
            tmpamount[v] = round(tmpamount[v] / suma * totalAmount, 4)

        max_index, max_number = max(enumerate(tmpamount), key=operator.itemgetter(1))
        tmpamount[max_index] = round(totalAmount - sum(tmpamount) + tmpamount[max_index], 4)

        tmpindividual[i].update({'amount': tmpamount})

    for i in range(len(tmpindividual)):
        if BalanceEnough(G, tmpindividual[i], k)==0:
            tmpindividual[i] = individual[i]

    return tmpindividual


# 变异操作2
# 随机变异一个节点 如果有足够多balance 就变异 重复k次
def Variation_Operator2(G, individual, k, percent):
    tmpindividual = copy.deepcopy(individual)
    n = len(tmpindividual)  # 个体数量
    lenth = list(range(0, n))
    variationindex = random.sample(lenth, int(n * percent))

    for i in variationindex:
        pnum = int(random.uniform(0, k))
        tmppath = copy.deepcopy(tmpindividual[i][pnum])
        nodenum = len(tmppath)
        if nodenum > 2:
            pnode = random.randint(1, nodenum-2)
            for j in range(k):
                tmp = int(random.uniform(0, len(G.nodes())-1))
                if tmp not in tmppath and (tmppath[pnode-1], tmp) in G.edges() and (tmp, tmppath[pnode+1]) in G.edges():
                    # if (G[tmppath[pnode - 1]][tmp]['balance'] > tmpindividual[i]['amount'][pnum] and
                    #     G[tmp][tmppath[pnode + 1]]['balance'] > tmpindividual[i]['amount'][pnum]):
                    tmppath[pnode] = tmp
            eq = 0   # 检查是否有相同路径
            for p in range(k):
                if p != pnum:
                    if tmpindividual[i][pnum] == tmpindividual[i][p]:
                        eq = 1
            if eq == 0:
                tmpindividual[i].update({pnum: tmppath})

    for i in range(len(tmpindividual)):
        if BalanceEnough(G, tmpindividual[i], k) == 0:
            tmpindividual[i] = individual[i]

    return tmpindividual


# calculate fee in one channel
def Calculatefee(G, path, amount, i):
    n = len(path)
    if i == n-1 | i == n:
        return 0
    if n > 1:
        fee = 0
        for j in range(i, n - 1):
            fee = round(fee + G[path[j]][path[j + 1]]['slope'] * amount + G[path[j]][path[j + 1]]['basis'], 4)
    return fee


# 输入一个个体，判断其balance是否满足 balance>amount+fee
def BalanceEnough(G, individual, k):
    fee = {}
    for i in range(k):
        for j in range(len(individual[i]) - 1):
            if (individual[i][j], individual[i][j + 1]) in fee.keys():
                fee[individual[i][j], individual[i][j + 1]] = round(fee[individual[i][j], individual[i][j + 1]] + Calculatefee(G, individual[i], individual['amount'][i], j + 1), 4)
            else:
                fee[individual[i][j], individual[i][j + 1]] = Calculatefee(G, individual[i],individual['amount'][i], j + 1)

    kamount = {}
    for i in range(k):
        for j in range(len(individual[i]) - 1):
            if (individual[i][j], individual[i][j + 1]) in kamount.keys():
                kamount[individual[i][j], individual[i][j + 1]] = kamount[individual[i][j], individual[i][j + 1]] + individual['amount'][i]
            else:
                kamount[individual[i][j], individual[i][j + 1]] = individual['amount'][i]

    balenough = 1
    for i in range(k):
        for j in range(len(individual[i]) - 1):
            if G[individual[i][j]][individual[i][j + 1]]['balance'] < kamount[individual[i][j], individual[i][j + 1]] + fee[individual[i][j], individual[i][j + 1]]:
                balenough = 0
                break
    return balenough
