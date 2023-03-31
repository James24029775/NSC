from protocols import *
from setting import Setting
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

# Q4 settings
TIMES = 20
PACKET_SIZE = 3
CASE_NUM = 4
LINK_DELAY = 1
HOST_NUM = 3
PACKET_NUM = 500

def my_settings(host_num=None, packet_num=None, link_delay=None, seed=None, c=None):
    max_colision_wait_time = host_num * link_delay * 2 * c
    p_resend = 1 / host_num / c / 5
    env_setting = Setting(host_num=host_num, packet_num=packet_num,
                          max_colision_wait_time=max_colision_wait_time, p_resend=p_resend, seed=seed)

    return env_setting

def main():
    record = [[[] for i in range(CASE_NUM)] for j in range(CASE_NUM)]

    for i in range(CASE_NUM):
        for C in range(1, 31):
            sum_success_rate = sum_idle_rate = sum_collision_rate = 0
            for j in range(TIMES):
                env_setting = my_settings(
                    packet_num=PACKET_NUM, host_num=HOST_NUM, link_delay=LINK_DELAY, seed=j, c=C)
                if i == 0:
                    success_rate, idle_rate, collision_rate = aloha(
                        env_setting, False)
                elif i == 1:
                    success_rate, idle_rate, collision_rate = slotted_aloha(
                        env_setting, False)
                elif i == 2:
                    success_rate, idle_rate, collision_rate = csma(
                        env_setting, False)
                elif i == 3:
                    success_rate, idle_rate, collision_rate = csma_cd(
                        env_setting, False)

                sum_success_rate += success_rate
                sum_idle_rate += idle_rate
                sum_collision_rate += collision_rate

            record[i][0].append(sum_success_rate/TIMES)
            record[i][1].append(sum_idle_rate/TIMES)
            record[i][2].append(sum_collision_rate/TIMES)

    plt.clf()
    x = range(1, 31)
    for i in range(CASE_NUM):
        if i == 0:
            label = 'aloha'
        elif i == 1:
            label = 'slotted_aloha'
        elif i == 2:
            label = 'csma'
        elif i == 3:
            label = 'csma/cd'
        plt.plot(x, record[i][0], 'o-', label=label)

    plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))
    plt.title("Infulence of Coefficient")
    plt.ylabel("Success rate")
    plt.xlabel("Coefficient")
    plt.legend()
    plt.savefig('Question/Q4_success.png')

    plt.clf()
    for i in range(CASE_NUM):
        if i == 0:
            label = 'aloha'
        elif i == 1:
            label = 'slotted_aloha'
        elif i == 2:
            label = 'csma'
        elif i == 3:
            label = 'csma/cd'
        plt.plot(x, record[i][1], 'o-', label=label)

    plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))
    plt.title("Infulence of Coefficient")
    plt.ylabel("Idle rate")
    plt.xlabel("Coefficient")
    plt.legend()
    plt.savefig('Question/Q4_idle.png')

    plt.clf()
    for i in range(CASE_NUM):
        if i == 0:
            label = 'aloha'
        elif i == 1:
            label = 'slotted_aloha'
        elif i == 2:
            label = 'csma'
        elif i == 3:
            label = 'csma/cd'
        plt.plot(x, record[i][2], 'o-', label=label)

    plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))
    plt.title("Infulence of Coefficient")
    plt.ylabel("Collision rate")
    plt.xlabel("Coefficient")
    plt.legend()
    plt.savefig('Question/Q4_collision.png')


if '__main__' == __name__:
    main()
