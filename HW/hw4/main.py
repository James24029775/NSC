import copy
import pprint
UR = 999


def main():
    link_cost = [
        [0, 2, 5, 1, UR, UR],
        [2, 0, 3, 2, UR, UR],
        [5, 3, 0, 3, 1, 5],
        [1, 2, 3, 0, 1, UR],
        [UR, UR, 1, 1, 0, 2],
        [UR, UR, 5, UR, 2, 0]
    ]
    # link_cost = [[0, 4, 1, UR], 
    #  [4, 0, 2, UR], 
    #  [1, 2, 0, 3], 
    #  [UR, UR, 3, 0]]
    pprint.pprint(run_ospf(link_cost))
    # pprint.pprint(run_rip(link_cost))

# return (點到點的最短距離矩陣, flooding紀錄)
def run_ospf(link_cost: list) -> tuple[list, list]:
    result = []
    switch_record = []
    router_num = len(link_cost)
    msg_queue = [[i] for i in range(router_num)]
    
    while True:
        finish_flg = True
        for i in range(router_num):
            if len(msg_queue[i]) != router_num:
                finish_flg = False
                break
        if finish_flg:
            break

        # every router pass information
        # tmp_msg_queue = copy.deepcopy(msg_queue)
        tmp_pool = [[] for _ in range(router_num)]
        for i in range(router_num):
            # pass info to neighbors
            
            for j in range(router_num):
                if i == j:
                    continue
                if link_cost[i][j] != UR:
                    # traverse msg queue information
                    
                    for k in range(len(msg_queue[i])):
                        original = msg_queue[i][k]
                        # if neighbor doesn't have the msg, then queue it
                        if original not in msg_queue[j]:
                            # check if "original" is in tmp_pool[j]
                            dup_flg = False
                            for tup in tmp_pool[j]:
                                source, origin = tup
                                if origin == original:
                                    dup_flg = True
                                    break
                            if not dup_flg:
                                tmp_pool[j].append((i, original))

        all_tmp_pool = []
        for i in range(router_num):
            for tup in tmp_pool[i]:
                source, origin = tup
                all_tmp_pool.append((source, origin, i))

        all_tmp_pool = sorted(all_tmp_pool)

        for i in range(len(all_tmp_pool)):
            src, origin, dest = all_tmp_pool[i]
            msg_queue[dest].append(origin)
            switch_record.append(all_tmp_pool[i])

    for i in range(router_num):
        # Link-state algorithm
        p = [None] * router_num
        n = [i]
        d = [UR] * router_num
        for j in range(router_num):
            if link_cost[i][j] != UR:
                d[j] = link_cost[i][j]
                p[j] = i

        d[i] += UR
        while True:
            if len(n) == router_num:
                break
            w = d.index(min(d))
            n.append(w)
            for j in range(router_num):
                if link_cost[w][j] != UR and not j in n:
                    new_path = d[w]+link_cost[w][j]
                    if new_path < d[j]: 
                        d[j] = new_path
                        p[j] = w

            d[w] += UR
        d = [d[i] - UR for i in range(router_num)]
        result.append(d)

    return result, switch_record

def run_rip(link_cost: list) -> tuple[list, list]:
    result = []
    switch_record = []
    distance_vector = {}
    router_num = len(link_cost)
    for i in range(router_num):
        tmp_dict = {}
        for j in range(router_num):
            distance = link_cost[i][j] if link_cost[i][j] != UR else UR
            tmp_dict[j] = distance
        distance_vector[i] = tmp_dict

    for i in range(router_num):
        for j in range(router_num):
            if i == j:
                continue
            if link_cost[i][j] != UR:
                switch_record.append((i, j))

    while True:
        old_distance_vector = copy.deepcopy(distance_vector)
        distance_vector = update_distance_vector(distance_vector, link_cost)

        for i in range(router_num):
            if old_distance_vector[i] != distance_vector[i]:
                # append i's neighbors
                for j in range(router_num):
                    if i == j:
                        continue
                    if link_cost[i][j] != UR:
                        switch_record.append((i, j))

        if old_distance_vector == distance_vector:
            break
    
    for i in range(router_num):
        tmp = []
        for key, value in distance_vector[i].items():
            tmp.append(value)
        result.append(tmp)
    return result, switch_record


def update_distance_vector(distance_vector, link_cost):
    for router in distance_vector.keys():
        for destination in distance_vector[router].keys():
            if router == destination:
                continue
            # update DV
            distance_vector[router][destination] = link_cost[router][destination]

            # Bellman-Ford
            for neighbor in distance_vector[router].keys():
                if neighbor == router:
                    continue
                distance = distance_vector[neighbor][destination] + link_cost[router][neighbor]
                if distance < distance_vector[router][destination]:
                    distance_vector[router][destination] = distance

    return distance_vector


if __name__ == '__main__':
    main()
