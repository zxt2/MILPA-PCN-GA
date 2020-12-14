import related
import copy
import random
import heapq

def Genetic_Algorithm(G, k, start, end, totalAmount, itertime):
    # 生成初始种群 若失败 individual=0
    individual = related.Generate_initial_population(G, k, start, end, totalAmount)
    # print("初始种群：")
    # for i in range(len(individual)):
    #     print(individual[i])
    FeeCost = 0
    averpathl = 0
    sumpathl = 0

    if individual != 0:
        for i in range(itertime):   # 迭代次数
            individual = Genetic_iteration(G, k, individual, totalAmount)

        GA_cost = []
        print('最后种群：')
        for i in range(len(individual)):
            GA_cost.append(1)
            GA_cost[i] = related.CalculateCost(G, k, individual[i], individual[i]['amount'])
            print(individual[i], 'cost:', GA_cost[i])
        FeeCost = min(GA_cost)
        mini = GA_cost.index(min(GA_cost))
        for i in range(k):
            sumpathl = sumpathl + len(individual[mini][i])
        averpathl = round((sumpathl/k), 2)
        print(averpathl)

    resultlist = [FeeCost, averpathl]
    return resultlist


def Genetic_iteration(G, k, individual, totalAmount):

    # 计算适应度
    fit = []
    if individual != 0:
        for i in range(len(individual)):
            fit.append(1)
            fit[i] = related.Calculatefitness(G, k, individual[i], individual[i]['amount'])

    # 选择父辈
    percent = 0.5  # 选择比例
    if individual != 0:
        father = related.selectfathers(individual, fit, percent)

    individual = copy.deepcopy(father)

    # 交叉
    son = {}
    for i in range(len(father)):
        son[i] = related.Crossover_Operator(G, k, father[i])

    j = len(individual)
    for i in range(len(son)):              # 将子辈加入种群
        individual.update({j: son[i]})
        j = j + 1

    if len(individual) < k+1:
        dif = k+1-len(individual)
        for i in range(dif):
            j = len(individual)
            u = int(random.uniform(0, len(father)-1))
            individual.update({j: father[u]})
            j = j + 1

    if len(individual) > k+1:
        fit1 = []
        for i in range(len(individual)):
            fit1.append(1)
            fit1[i] = related.Calculatefitness(G, k, individual[i], individual[i]['amount'])
        re1 = map(fit1.index, heapq.nsmallest(k+1, fit1))
        index = list(re1)
        individual1 = {}
        j = 0
        for i in index:
            individual1[j] = individual[i]
            j = j + 1
        individual = individual1


    # 变异
    percent1 = 0.5  # 变异比例1
    percent2 = 0.8  # 变异比例2
    individual = related.Variation_Operator(G, individual, k, percent1, totalAmount)
    individual = related.Variation_Operator2(G, individual, k, percent2)

    return individual
