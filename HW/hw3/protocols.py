# 還是不太確定判斷是否collision要用packet_time還是packet_size+link_delay
# 目前使用packet_time
import numpy as np
import random


def aloha(setting, show_history=False):
    status = [[] for _ in range(setting.host_num)]
    pkt_index = [0 for _ in range(setting.host_num)]
    pending = [0 for _ in range(setting.host_num)]
    remaining_seg = [0 for _ in range(setting.host_num)]
    freeze = [0 for _ in range(setting.host_num)]

    packets_time = setting.gen_packets()
    for t in range(setting.total_time):
        for the_host in range(setting.host_num):

            pending_flg = False
            # 若host此刻有發送需求，將其視為pending操作
            if (pkt_index[the_host] < setting.packet_num and packets_time[the_host][pkt_index[the_host]] == t):
                pending[the_host] += 1
                pkt_index[the_host] += 1
                # 若remaining_seg是0，就可以進行新一輪的傳輸；否則要先把之前傳輸先完成
                if remaining_seg[the_host] == 0:
                    remaining_seg[the_host] = setting.packet_time

            if (pending[the_host] > 0 and remaining_seg[the_host] == setting.packet_time):
                pending_flg = True

            # 若是還在freeze倒數，直接idle跳過
            if freeze[the_host] > 0:
                status[the_host].append('.')
                freeze[the_host] -= 1
                continue

            if pending_flg:
                status[the_host].append('<')
                remaining_seg[the_host] = setting.packet_time - 1

            # 繼續前次尚未完成的封包傳輸
            elif 1 < remaining_seg[the_host] and remaining_seg[the_host] <= setting.packet_time - 1:
                status[the_host].append('-')
                remaining_seg[the_host] -= 1

            elif remaining_seg[the_host] == 1:
                status[the_host].append('>')

            # 沒有任何傳輸慾望
            else:
                status[the_host].append('.')

        # CSMA特有，與CSMA/CD判斷方式不同。檢查本次傳輸是否合法，是->pending-1；否->pending不變
        for the_host in range(setting.host_num):
            if status[the_host][t] != '>':
                continue

            NAK_flg = False
            for other_host in range(setting.host_num):
                if the_host == other_host:
                    continue
                for i in range(setting.packet_time):
                    if t-i >= 0 and status[other_host][t-i] != '.':
                        NAK_flg = True
                        break
                if NAK_flg:
                    break

            if NAK_flg:
                status[the_host][t] = '|'
                freeze[the_host] = random.randint(
                    1, setting.max_colision_wait_time)-1
            else:
                pending[the_host] -= 1

            # 重製remaining_seg，若pending尚有，將其設成packet_size使其開始新一輪的傳輸
            if pending[the_host] != 0:
                remaining_seg[the_host] = setting.packet_time
            else:
                remaining_seg[the_host] = 0

    if show_history:
        for i in range(setting.host_num):
            print('h'+str(i)+':', end='')
            for j in range(len(status[i])):
                print(status[i][j], end='')
            print()

    channel = ''
    for t in range(setting.total_time):
        less_cnt = 0
        large_cnt = 0
        minus_cnt = 0
        dot_cnt = 0
        for the_host in range(setting.host_num):
            if status[the_host][t] == '.':
                dot_cnt += 1
            elif status[the_host][t] == '<':
                less_cnt += 1
            elif status[the_host][t] == '>':
                large_cnt += 1
            elif status[the_host][t] == '-':
                minus_cnt += 1
        if less_cnt == 1 and large_cnt == 0 and minus_cnt == 0:
            channel += '<'
        elif less_cnt == 0 and large_cnt == 1 and minus_cnt == 0:
            channel += '>'
        elif less_cnt == 0 and large_cnt == 0 and minus_cnt == 1:
            channel += '-'
        elif dot_cnt == setting.host_num:
            channel += '.'
        else:
            channel += 'X'

    success_pattern = '<'+'-'*(setting.packet_time-2)+'>'
    success = channel.count(success_pattern) * len(success_pattern)
    idle = channel.count('.')
    collision = setting.total_time - idle - success

    return success/setting.total_time, idle/setting.total_time, collision/setting.total_time


def slotted_aloha(setting, show_history=False):
    status = [[] for _ in range(setting.host_num)]
    pkt_index = [0 for _ in range(setting.host_num)]
    pending = [0 for _ in range(setting.host_num)]
    remaining_seg = [0 for _ in range(setting.host_num)]
    freeze = [0 for _ in range(setting.host_num)]

    packets_time = setting.gen_packets()
    for t in range(setting.total_time):
        for the_host in range(setting.host_num):
            slot_flg = False
            if t % setting.packet_time == 0:
                slot_flg = True

            pending_flg = False
            # 若host此刻有發送需求，將其視為pending操作
            if (pkt_index[the_host] < setting.packet_num and packets_time[the_host][pkt_index[the_host]] == t):
                pending[the_host] += 1
                pkt_index[the_host] += 1
                # 若remaining_seg是0，就可以進行新一輪的傳輸；否則要先把之前傳輸先完成
                if remaining_seg[the_host] == 0:
                    remaining_seg[the_host] = setting.packet_time

            if (pending[the_host] > 0 and remaining_seg[the_host] == setting.packet_time):
                pending_flg = True

            # 若是還在freeze倒數，直接idle跳過
            if freeze[the_host] > 0:
                status[the_host].append('.')
                freeze[the_host] -= 1
                # 若已經倒數結束，要決定下個slot是否發送
                if freeze[the_host] == 0:
                    if random.random() > setting.p_resend:
                        freeze[the_host] = setting.packet_time
                continue

            if pending_flg and slot_flg:
                status[the_host].append('<')
                remaining_seg[the_host] = setting.packet_time - 1

            # 繼續前次尚未完成的封包傳輸
            elif 1 < remaining_seg[the_host] and remaining_seg[the_host] <= setting.packet_time - 1:
                status[the_host].append('-')
                remaining_seg[the_host] -= 1

            elif remaining_seg[the_host] == 1:
                status[the_host].append('>')
                remaining_seg[the_host] -= 1

            # 沒有任何傳輸慾望
            else:
                status[the_host].append('.')

        # CSMA特有，與CSMA/CD判斷方式不同。檢查本次傳輸是否合法，是->pending-1；否->pending不變
        for the_host in range(setting.host_num):
            if status[the_host][t] != '>':
                continue

            NAK_flg = False
            for other_host in range(setting.host_num):
                if the_host == other_host:
                    continue
                for i in range(setting.packet_time):
                    if t-i >= 0 and status[other_host][t-i] != '.':
                        NAK_flg = True
                        break
                if NAK_flg:
                    break

            if NAK_flg:
                status[the_host][t] = '|'
                if random.random() > setting.p_resend:
                    freeze[the_host] = setting.packet_time
            else:
                pending[the_host] -= 1

            # 重製remaining_seg，若pending尚有，將其設成packet_size使其開始新一輪的傳輸
            if pending[the_host] != 0:
                remaining_seg[the_host] = setting.packet_time
            else:
                remaining_seg[the_host] = 0

    if show_history:
        for i in range(setting.host_num):
            print('h'+str(i)+':', end='')
            for j in range(len(status[i])):
                print(status[i][j], end='')
            print()

    channel = ''
    for t in range(setting.total_time):
        less_cnt = 0
        large_cnt = 0
        minus_cnt = 0
        dot_cnt = 0
        for the_host in range(setting.host_num):
            if status[the_host][t] == '.':
                dot_cnt += 1
            elif status[the_host][t] == '<':
                less_cnt += 1
            elif status[the_host][t] == '>':
                large_cnt += 1
            elif status[the_host][t] == '-':
                minus_cnt += 1
        if less_cnt == 1 and large_cnt == 0 and minus_cnt == 0:
            channel += '<'
        elif less_cnt == 0 and large_cnt == 1 and minus_cnt == 0:
            channel += '>'
        elif less_cnt == 0 and large_cnt == 0 and minus_cnt == 1:
            channel += '-'
        elif dot_cnt == setting.host_num:
            channel += '.'
        else:
            channel += 'X'

    success_pattern = '<'+'-'*setting.packet_size+'>'
    success = channel.count(success_pattern) * len(success_pattern)
    idle = channel.count('.')
    collision = setting.total_time - idle - success

    return success/setting.total_time, idle/setting.total_time, collision/setting.total_time


def csma(setting, show_history=False):
    status = [[] for _ in range(setting.host_num)]
    pkt_index = [0 for _ in range(setting.host_num)]
    pending = [0 for _ in range(setting.host_num)]
    remaining_seg = [0 for _ in range(setting.host_num)]
    freeze = [0 for _ in range(setting.host_num)]

    packets_time = setting.gen_packets()
    for t in range(setting.total_time):
        for the_host in range(setting.host_num):

            pending_flg = False
            # 若host此刻有發送需求，將其視為pending操作(早先於freeze處理)
            if (pkt_index[the_host] < setting.packet_num and packets_time[the_host][pkt_index[the_host]] == t):
                pending[the_host] += 1
                pkt_index[the_host] += 1
                # 若remaining_seg是0，就可以進行新一輪的傳輸；否則要先把之前傳輸先完成
                if remaining_seg[the_host] == 0:
                    remaining_seg[the_host] = setting.packet_time

            if (pending[the_host] > 0 and remaining_seg[the_host] == setting.packet_time):
                pending_flg = True

            # 若是還在freeze倒數，直接idle跳過
            if freeze[the_host] > 0:
                status[the_host].append('.')
                freeze[the_host] -= 1
                continue

            # CS處理
            if pending_flg:
                # 其他hosts的t-1-link_delay的status若非"."or ">"，表示占用中
                busy_flg = False
                if t - 1 - setting.link_delay >= 0:
                    for other_host in range(setting.host_num):
                        if the_host == other_host:
                            continue

                        if status[other_host][t - 1 - setting.link_delay] != '.' and status[other_host][t - 1 - setting.link_delay] != '>':
                            busy_flg = True
                            break

                # 若busy_flg為假則發送類型"<"；否則status設定"."下次繼續CS
                if busy_flg:
                    status[the_host].append('.')
                    freeze[the_host] = random.randint(
                        1, setting.max_colision_wait_time)-1
                    remaining_seg[the_host] = setting.packet_time
                else:
                    status[the_host].append('<')
                    remaining_seg[the_host] = setting.packet_time - 1

            # 繼續前次尚未完成的封包傳輸
            elif remaining_seg[the_host] > 1:
                status[the_host].append('-')
                remaining_seg[the_host] -= 1

            elif remaining_seg[the_host] == 1:
                status[the_host].append('>')

            # 沒有任何傳輸慾望
            else:
                status[the_host].append('.')

        # CSMA特有，與CSMA/CD判斷方式不同。檢查本次傳輸是否合法，是->pending-1；否->pending不變
        for the_host in range(setting.host_num):
            if status[the_host][t] != '>':
                continue

            NAK_flg = False
            for other_host in range(setting.host_num):
                if the_host == other_host:
                    continue
                for i in range(setting.packet_time):
                    if t-i >= 0 and status[other_host][t-i] != '.':
                        NAK_flg = True
                        break
                if NAK_flg:
                    break

            if NAK_flg:
                status[the_host][t] = '|'
                freeze[the_host] = random.randint(
                    1, setting.max_colision_wait_time)-1
            else:
                pending[the_host] -= 1

            # 重製remaining_seg，若pending尚有，將其設成packet_size使其開始新一輪的傳輸
            if pending[the_host] != 0:
                remaining_seg[the_host] = setting.packet_time
            else:
                remaining_seg[the_host] = 0

    if show_history:
        for i in range(setting.host_num):
            print('h'+str(i)+':', end='')
            for j in range(len(status[i])):
                print(status[i][j], end='')
            print()

    channel = ''
    for t in range(setting.total_time):
        less_cnt = 0
        large_cnt = 0
        minus_cnt = 0
        dot_cnt = 0
        for the_host in range(setting.host_num):
            if status[the_host][t] == '.':
                dot_cnt += 1
            elif status[the_host][t] == '<':
                less_cnt += 1
            elif status[the_host][t] == '>':
                large_cnt += 1
            elif status[the_host][t] == '-':
                minus_cnt += 1
        if less_cnt == 1 and large_cnt == 0 and minus_cnt == 0:
            channel += '<'
        elif less_cnt == 0 and large_cnt == 1 and minus_cnt == 0:
            channel += '>'
        elif less_cnt == 0 and large_cnt == 0 and minus_cnt == 1:
            channel += '-'
        elif dot_cnt == setting.host_num:
            channel += '.'
        else:
            channel += 'X'

    success_pattern = '<'+'-'*setting.packet_size+'>'
    success = channel.count(success_pattern) * len(success_pattern)
    idle = channel.count('.')
    collision = setting.total_time - idle - success

    return success/setting.total_time, idle/setting.total_time, collision/setting.total_time


def csma_cd(setting, show_history=False):
    status = [[] for _ in range(setting.host_num)]
    pkt_index = [0 for _ in range(setting.host_num)]
    pending = [0 for _ in range(setting.host_num)]
    remaining_seg = [0 for _ in range(setting.host_num)]
    freeze = [0 for _ in range(setting.host_num)]

    packets_time = setting.gen_packets()
    for t in range(setting.total_time):
        for the_host in range(setting.host_num):

            pending_flg = False
            # 若host此刻有發送需求，將其視為pending操作(早先於freeze處理)
            if (pkt_index[the_host] < setting.packet_num and packets_time[the_host][pkt_index[the_host]] == t):
                pending[the_host] += 1
                pkt_index[the_host] += 1
                # 若remaining_seg是0，就可以進行新一輪的傳輸；否則要先把之前傳輸先完成
                if remaining_seg[the_host] == 0:
                    remaining_seg[the_host] = setting.packet_time

            if (pending[the_host] > 0 and remaining_seg[the_host] == setting.packet_time):
                pending_flg = True

            # 若是還在freeze倒數，直接idle跳過
            if freeze[the_host] > 0:
                status[the_host].append('.')
                freeze[the_host] -= 1
                continue

            # CS處理
            if pending_flg:
                # 其他hosts的t-1-link_delay的status若非"."，表示占用中
                busy_flg = False
                if t - 1 - setting.link_delay >= 0:
                    for other_host in range(setting.host_num):
                        if the_host == other_host:
                            continue

                        if status[other_host][t - 1 - setting.link_delay] != '.' and status[other_host][t - 1 - setting.link_delay] != '>':
                            busy_flg = True
                            break

                # 若busy_flg為假則發送類型"<"；否則status設定"."下次繼續CS
                if busy_flg:
                    status[the_host].append('.')
                    remaining_seg[the_host] = setting.packet_time
                    freeze[the_host] = random.randint(
                        1, setting.max_colision_wait_time)-1
                else:
                    status[the_host].append('<')
                    remaining_seg[the_host] = setting.packet_time - 1

            # 繼續前次尚未完成的封包傳輸
            elif remaining_seg[the_host] >= 1:
                # CD
                busy_flg = False
                if t - 1 - setting.link_delay >= 0:
                    for other_host in range(setting.host_num):
                        if the_host == other_host:
                            continue

                        if status[other_host][t - 1 - setting.link_delay] != '.':
                            busy_flg = True
                            break
                # 如果已經發生collision，則中斷
                if busy_flg:
                    status[the_host].append('|')
                    remaining_seg[the_host] = setting.packet_time
                    freeze[the_host] = random.randint(
                        1, setting.max_colision_wait_time)-1
                # 否則繼續未完成的傳輸
                else:
                    if remaining_seg[the_host] > 1:
                        status[the_host].append('-')
                        remaining_seg[the_host] -= 1

                    elif remaining_seg[the_host] == 1:
                        status[the_host].append('>')
                        remaining_seg[the_host] = 0
                        pending[the_host] -= 1

                        # 重製remaining_seg，若pending尚有，將其設成packet_size使其開始新一輪的傳輸
                        if pending[the_host] != 0:
                            remaining_seg[the_host] = setting.packet_time
                        else:
                            remaining_seg[the_host] = 0

            # 沒有任何傳輸慾望
            else:
                status[the_host].append('.')

    if show_history:
        for i in range(setting.host_num):
            print('h'+str(i)+':', end='')
            for j in range(len(status[i])):
                print(status[i][j], end='')
            print()

    channel = ''
    for t in range(setting.total_time):
        less_cnt = 0
        large_cnt = 0
        minus_cnt = 0
        dot_cnt = 0
        pipe_cnt = 0
        for the_host in range(setting.host_num):
            if status[the_host][t] == '.':
                dot_cnt += 1
            elif status[the_host][t] == '<':
                less_cnt += 1
            elif status[the_host][t] == '>':
                large_cnt += 1
            elif status[the_host][t] == '-':
                minus_cnt += 1
            elif status[the_host][t] == '|':
                pipe_cnt += 1
        if less_cnt == 1 and large_cnt == 0 and minus_cnt == 0:
            channel += '<'
        elif less_cnt == 0 and large_cnt == 1 and minus_cnt == 0:
            channel += '>'
        elif less_cnt == 0 and large_cnt == 0 and minus_cnt == 1:
            channel += '-'
        elif dot_cnt == setting.host_num:
            channel += '.'
        else:
            channel += 'X'

    success_pattern = '<'+'-'*setting.packet_size+'>'
    success = channel.count(success_pattern) * len(success_pattern)
    idle = channel.count('.')
    collision = setting.total_time - idle - success

    return success/setting.total_time, idle/setting.total_time, collision/setting.total_time
