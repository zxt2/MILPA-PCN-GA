
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
