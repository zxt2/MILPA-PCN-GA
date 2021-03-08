import math
import OnePath
import related


def K_path_Average(G, k, start, end, totalAmount):
    amount = math.ceil(totalAmount / k)  # 初始每条路径平均分配金额
    tmpG = G.copy()
    path = {}
    for i in range(k):
        path[i] = OnePath.Dijkstra(tmpG, start, end, amount)
        if path[i] == 0:
            return 0
        else:
            for j in range(len(path[i]) - 1):
                f = related.Calculatefee(G, path[i], amount, j + 1)
                tmpG[path[i][j]][path[i][j + 1]]['balance'] = tmpG[path[i][j]][path[i][j + 1]]['balance'] - (amount + f)  # 减去balance+fee
    amount_array = []
    for i in range(k):
        amount_array.append(amount)
    amount_array[k - 1] = totalAmount - sum(amount_array) + amount_array[k - 1]

    result = {}
    for i in range(k):
        result.update({i: path[i]})
    result.update({'amount': amount_array})
    return result
