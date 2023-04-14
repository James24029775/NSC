import copy
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
    run_ospf(link_cost)

# ospf is link-state(Dijkstra)
# return (點到點的最短距離矩陣, flooding紀錄)
# 試試看使用seq num的方式，自己方送過就不要收

def run_ospf(link_cost: list) -> tuple[list, list]:
    result = []
    switch_record = []
    router_num = len(link_cost)
    msg_queue = [[i] for i in range(router_num)]
    
    z = 0
    while True:
        finish_flg = True
        for i in range(router_num):
            if len(msg_queue[i]) != router_num:
                finish_flg = False
                break
        if finish_flg:
            break

        # print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
        # every router switch information
        tmp_msg_queue = copy.deepcopy(msg_queue)
        for i in range(router_num):
            # pass info to neighbors
            print('---------------------------------------------------------------------')
            for j in range(router_num):
                if i == j:
                    continue
                if link_cost[i][j] != UR:
                    # switch information
                    for k in range(len(msg_queue[i])):
                        original = msg_queue[i][k]
                        # if neighbor doesn't have the msg, then queue it
                        if original not in msg_queue[j]:
                            print("msg", msg_queue)
                            print("TMP", tmp_msg_queue)
                            tmp_msg_queue[j].append(original)
                            switch_record.append((i, original, j))
        if z == 1:
            raise Exception
        z+= 1
        msg_queue = copy.deepcopy(tmp_msg_queue)

    # print(switch_record)




    return result, switch_record

#


def run_rip(link_cost: list) -> tuple[list, list]:
    pass


if __name__ == '__main__':
    main()
