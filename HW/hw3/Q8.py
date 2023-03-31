from protocols import *
from setting import Setting
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

# Q1 settings
TIMES = 20
PACKET_SIZE = 3
CASE_NUM = 2
LINK_DELAY = 1
HOST_NUM = 3
PACKET_NUM = 500
C = 10


def my_settings(host_num=None, packet_num=None, link_delay=None, packet_size=None, seed=None, c=None):
    max_colision_wait_time = 20
    p_resend = 1 / host_num / c * 10
    env_setting = Setting(host_num=host_num, packet_num=packet_num, packet_size=packet_size, link_delay=link_delay,
                          max_colision_wait_time=max_colision_wait_time, p_resend=p_resend, seed=seed)

    return env_setting


def main():
    link_delay_list = [0, 1, 2, 3]
    packet_size_list = [7, 5, 3, 1]

    record = [[[] for i in range(3)] for j in range(CASE_NUM)]

    for i in range(CASE_NUM):
        for l,p in zip(link_delay_list, packet_size_list):
            sum_success_rate = sum_idle_rate = sum_collision_rate = 0
            for j in range(TIMES):
                env_setting = my_settings(packet_num=PACKET_NUM, host_num=HOST_NUM,
                                          packet_size=p, link_delay=l, seed=j, c=C)
                if i == 0:
                    success_rate, idle_rate, collision_rate = csma(
                        env_setting, False)
                elif i == 1:
                    success_rate, idle_rate, collision_rate = csma_cd(
                        env_setting, False)

                sum_success_rate += success_rate
                sum_idle_rate += idle_rate
                sum_collision_rate += collision_rate

            record[i][0].append(sum_success_rate/TIMES)
            record[i][1].append(sum_idle_rate/TIMES)
            record[i][2].append(sum_collision_rate/TIMES)

    plt.clf()
    x = link_delay_list
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
    plt.title("Infulence of Link Delay")
    plt.ylabel("Success rate")
    plt.xlabel("Link Delay")
    plt.legend()
    plt.savefig('Question/Q8_success.png')

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
    plt.title("Infulence of Link Delay")
    plt.ylabel("Idle rate")
    plt.xlabel("Link Delay")
    plt.legend()
    plt.savefig('Question/Q8_idle.png')

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
    plt.title("Infulence of Link Delay")
    plt.ylabel("Collision rate")
    plt.xlabel("Link Delay")
    plt.legend()
    plt.savefig('Question/Q8_collision.png')

    # csma
    y1 = [0.831, 0.823, 0.818, 0.797]
    # csma/cd
    y2 = [0.85, 0.834, 0.826, 0.811]
    plt.clf()
    plt.plot(x, y1, 'o-', label='csma')
    plt.plot(x, y2, 'o-', label='csma/cd')

    plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))
    plt.title("Infulence of Link Delay")
    plt.ylabel("Success rate")
    plt.xlabel("Link Delay")
    plt.legend()
    plt.savefig('Question/Q8_success.png')

    # csma
    y1 = [0.1466, 0.151, 0.1526, 0.1645]
    # csma/cd
    y2 = [0.1477, 0.153, 0.1619, 0.1688]
    plt.clf()
    plt.plot(x, y1, 'o-', label='csma')
    plt.plot(x, y2, 'o-', label='csma/cd')

    plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))
    plt.title("Infulence of Link Delay")
    plt.ylabel("Idle rate")
    plt.xlabel("Link Delay")
    plt.legend()
    plt.savefig('Question/Q8_idle.png')

    
    # csma
    y1 = [0.021, 0.026, 0.029, 0.033]
    # csma/cd
    y2 = [0.003, 0.008, 0.014, 0.023]
    plt.clf()
    plt.plot(x, y1, 'o-', label='csma')
    plt.plot(x, y2, 'o-', label='csma/cd')

    plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))
    plt.title("Infulence of Link Delay")
    plt.ylabel("Collision rate")
    plt.xlabel("Link Delay")
    plt.legend()
    plt.savefig('Question/Q8_collision.png')

if '__main__' == __name__:
    main()
