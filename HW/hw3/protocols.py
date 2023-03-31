# �٬O���ӽT�w�P�_�O�_collision�n��packet_time�٬Opacket_size+link_delay
# �ثe�ϥ�packet_time
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
            # �Yhost���観�o�e�ݨD�A�N�����pending�ާ@
            if (pkt_index[the_host] < setting.packet_num and packets_time[the_host][pkt_index[the_host]] == t):
                pending[the_host] += 1
                pkt_index[the_host] += 1
                # �Yremaining_seg�O0�A�N�i�H�i��s�@�����ǿ�F�_�h�n���⤧�e�ǿ������
                if remaining_seg[the_host] == 0:
                    remaining_seg[the_host] = setting.packet_time

            if (pending[the_host] > 0 and remaining_seg[the_host] == setting.packet_time):
                pending_flg = True

            # �Y�O�٦bfreeze�˼ơA����idle���L
            if freeze[the_host] > 0:
                status[the_host].append('.')
                freeze[the_host] -= 1
                continue

            if pending_flg:
                status[the_host].append('<')
                remaining_seg[the_host] = setting.packet_time - 1

            # �~��e���|���������ʥ]�ǿ�
            elif 1 < remaining_seg[the_host] and remaining_seg[the_host] <= setting.packet_time - 1:
                status[the_host].append('-')
                remaining_seg[the_host] -= 1

            elif remaining_seg[the_host] == 1:
                status[the_host].append('>')

            # �S������ǿ鼤��
            else:
                status[the_host].append('.')

        # CSMA�S���A�PCSMA/CD�P�_�覡���P�C�ˬd�����ǿ�O�_�X�k�A�O->pending-1�F�_->pending����
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

            # ���sremaining_seg�A�Ypending�|���A�N��]��packet_size�Ϩ�}�l�s�@�����ǿ�
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
            # �Yhost���観�o�e�ݨD�A�N�����pending�ާ@
            if (pkt_index[the_host] < setting.packet_num and packets_time[the_host][pkt_index[the_host]] == t):
                pending[the_host] += 1
                pkt_index[the_host] += 1
                # �Yremaining_seg�O0�A�N�i�H�i��s�@�����ǿ�F�_�h�n���⤧�e�ǿ������
                if remaining_seg[the_host] == 0:
                    remaining_seg[the_host] = setting.packet_time

            if (pending[the_host] > 0 and remaining_seg[the_host] == setting.packet_time):
                pending_flg = True

            # �Y�O�٦bfreeze�˼ơA����idle���L
            if freeze[the_host] > 0:
                status[the_host].append('.')
                freeze[the_host] -= 1
                # �Y�w�g�˼Ƶ����A�n�M�w�U��slot�O�_�o�e
                if freeze[the_host] == 0:
                    if random.random() > setting.p_resend:
                        freeze[the_host] = setting.packet_time
                continue

            if pending_flg and slot_flg:
                status[the_host].append('<')
                remaining_seg[the_host] = setting.packet_time - 1

            # �~��e���|���������ʥ]�ǿ�
            elif 1 < remaining_seg[the_host] and remaining_seg[the_host] <= setting.packet_time - 1:
                status[the_host].append('-')
                remaining_seg[the_host] -= 1

            elif remaining_seg[the_host] == 1:
                status[the_host].append('>')
                remaining_seg[the_host] -= 1

            # �S������ǿ鼤��
            else:
                status[the_host].append('.')

        # CSMA�S���A�PCSMA/CD�P�_�覡���P�C�ˬd�����ǿ�O�_�X�k�A�O->pending-1�F�_->pending����
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

            # ���sremaining_seg�A�Ypending�|���A�N��]��packet_size�Ϩ�}�l�s�@�����ǿ�
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
            # �Yhost���観�o�e�ݨD�A�N�����pending�ާ@(������freeze�B�z)
            if (pkt_index[the_host] < setting.packet_num and packets_time[the_host][pkt_index[the_host]] == t):
                pending[the_host] += 1
                pkt_index[the_host] += 1
                # �Yremaining_seg�O0�A�N�i�H�i��s�@�����ǿ�F�_�h�n���⤧�e�ǿ������
                if remaining_seg[the_host] == 0:
                    remaining_seg[the_host] = setting.packet_time

            if (pending[the_host] > 0 and remaining_seg[the_host] == setting.packet_time):
                pending_flg = True

            # �Y�O�٦bfreeze�˼ơA����idle���L
            if freeze[the_host] > 0:
                status[the_host].append('.')
                freeze[the_host] -= 1
                continue

            # CS�B�z
            if pending_flg:
                # ��Lhosts��t-1-link_delay��status�Y�D"."or ">"�A��ܥe�Τ�
                busy_flg = False
                if t - 1 - setting.link_delay >= 0:
                    for other_host in range(setting.host_num):
                        if the_host == other_host:
                            continue

                        if status[other_host][t - 1 - setting.link_delay] != '.' and status[other_host][t - 1 - setting.link_delay] != '>':
                            busy_flg = True
                            break

                # �Ybusy_flg�����h�o�e����"<"�F�_�hstatus�]�w"."�U���~��CS
                if busy_flg:
                    status[the_host].append('.')
                    freeze[the_host] = random.randint(
                        1, setting.max_colision_wait_time)-1
                    remaining_seg[the_host] = setting.packet_time
                else:
                    status[the_host].append('<')
                    remaining_seg[the_host] = setting.packet_time - 1

            # �~��e���|���������ʥ]�ǿ�
            elif remaining_seg[the_host] > 1:
                status[the_host].append('-')
                remaining_seg[the_host] -= 1

            elif remaining_seg[the_host] == 1:
                status[the_host].append('>')

            # �S������ǿ鼤��
            else:
                status[the_host].append('.')

        # CSMA�S���A�PCSMA/CD�P�_�覡���P�C�ˬd�����ǿ�O�_�X�k�A�O->pending-1�F�_->pending����
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

            # ���sremaining_seg�A�Ypending�|���A�N��]��packet_size�Ϩ�}�l�s�@�����ǿ�
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
            # �Yhost���観�o�e�ݨD�A�N�����pending�ާ@(������freeze�B�z)
            if (pkt_index[the_host] < setting.packet_num and packets_time[the_host][pkt_index[the_host]] == t):
                pending[the_host] += 1
                pkt_index[the_host] += 1
                # �Yremaining_seg�O0�A�N�i�H�i��s�@�����ǿ�F�_�h�n���⤧�e�ǿ������
                if remaining_seg[the_host] == 0:
                    remaining_seg[the_host] = setting.packet_time

            if (pending[the_host] > 0 and remaining_seg[the_host] == setting.packet_time):
                pending_flg = True

            # �Y�O�٦bfreeze�˼ơA����idle���L
            if freeze[the_host] > 0:
                status[the_host].append('.')
                freeze[the_host] -= 1
                continue

            # CS�B�z
            if pending_flg:
                # ��Lhosts��t-1-link_delay��status�Y�D"."�A��ܥe�Τ�
                busy_flg = False
                if t - 1 - setting.link_delay >= 0:
                    for other_host in range(setting.host_num):
                        if the_host == other_host:
                            continue

                        if status[other_host][t - 1 - setting.link_delay] != '.' and status[other_host][t - 1 - setting.link_delay] != '>':
                            busy_flg = True
                            break

                # �Ybusy_flg�����h�o�e����"<"�F�_�hstatus�]�w"."�U���~��CS
                if busy_flg:
                    status[the_host].append('.')
                    remaining_seg[the_host] = setting.packet_time
                    freeze[the_host] = random.randint(
                        1, setting.max_colision_wait_time)-1
                else:
                    status[the_host].append('<')
                    remaining_seg[the_host] = setting.packet_time - 1

            # �~��e���|���������ʥ]�ǿ�
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
                # �p�G�w�g�o��collision�A�h���_
                if busy_flg:
                    status[the_host].append('|')
                    remaining_seg[the_host] = setting.packet_time
                    freeze[the_host] = random.randint(
                        1, setting.max_colision_wait_time)-1
                # �_�h�~�򥼧������ǿ�
                else:
                    if remaining_seg[the_host] > 1:
                        status[the_host].append('-')
                        remaining_seg[the_host] -= 1

                    elif remaining_seg[the_host] == 1:
                        status[the_host].append('>')
                        remaining_seg[the_host] = 0
                        pending[the_host] -= 1

                        # ���sremaining_seg�A�Ypending�|���A�N��]��packet_size�Ϩ�}�l�s�@�����ǿ�
                        if pending[the_host] != 0:
                            remaining_seg[the_host] = setting.packet_time
                        else:
                            remaining_seg[the_host] = 0

            # �S������ǿ鼤��
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
