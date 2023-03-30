from protocols import *
from setting import Setting

# TIMES = 100
# HOST_NUM = 3
# PACKET_NUM = 500
# TOTAL_TIME = 10000
# LINK_DELAY = 1

# Setting(host_num=3, total_time=100, packet_num=4, max_colision_wait_time=20, p_resend=0.3, packet_size=3, link_delay=1, seed=<studen_id>)


TIMES = 100
HOST_NUM = 3
TOTAL_TIME = 100
PACKET_NUM = 4
MAX_COL=21
P_RESEND = 0.3
PACKET_SIZE = 3
LINK_DELAY = 1


def main():
    # env_setting = Setting(host_num=HOST_NUM, packet_num=PACKET_NUM,
    #                       total_time=TOTAL_TIME, link_delay=LINK_DELAY, seed=1)
    # print(slotted_aloha(env_setting, True))

    # env_setting = Setting(host_num=HOST_NUM, packet_num=PACKET_NUM,
    #                       total_time=TOTAL_TIME, link_delay=LINK_DELAY, max_colision_wait_time=MAX_COL, packet_size=PACKET_SIZE, seed=4, p_resend=P_RESEND)
    # print(aloha(env_setting, True))

    # env_setting = Setting(host_num=HOST_NUM, packet_num=PACKET_NUM,
    #                       total_time=TOTAL_TIME, link_delay=LINK_DELAY, max_colision_wait_time=MAX_COL, packet_size=PACKET_SIZE, seed=4, p_resend=P_RESEND)
    # print(slotted_aloha(env_setting, True))

    env_setting = Setting(host_num=HOST_NUM, packet_num=PACKET_NUM,
                          total_time=TOTAL_TIME, link_delay=LINK_DELAY, max_colision_wait_time=MAX_COL, packet_size=PACKET_SIZE, seed=4, p_resend=P_RESEND)
    print(csma(env_setting, True))

    # print('ALOHA')
    # sum_success = sum_idle = sum_collision = 0
    # for i in range(TIMES):
    #     env_setting = Setting(host_num=HOST_NUM, packet_num=PACKET_NUM,
    #                           total_time=TOTAL_TIME, link_delay=LINK_DELAY, seed=i)
    #     success, idle, collision = aloha(env_setting, False)
    #     sum_success += success
    #     sum_idle += idle
    #     sum_collision += collision
    # print('\tsuccess_rate:', round(sum_success/TIMES, 2))
    # print('\tidle_rate:', round(sum_idle/TIMES, 2))
    # print('\tcollision_rate:', round(sum_collision/TIMES, 2))

    # print('SLOTTED_ALOHA')
    # sum_success = sum_idle = sum_collision = 0
    # for i in range(TIMES):
    #     env_setting = Setting(host_num=HOST_NUM, packet_num=PACKET_NUM,
    #                           total_time=TOTAL_TIME, link_delay=LINK_DELAY, seed=i)
    #     success, idle, collision = slotted_aloha(env_setting, False)
    #     sum_success += success
    #     sum_idle += idle
    #     sum_collision += collision
    # print('\tsuccess_rate:', round(sum_success/TIMES, 2))
    # print('\tidle_rate:', round(sum_idle/TIMES, 2))
    # print('\tcollision_rate:', round(sum_collision/TIMES, 2))

    # print('CSMA')
    # sum_success = sum_idle = sum_collision = 0
    # for i in range(TIMES):
    #     env_setting = Setting(host_num=HOST_NUM, packet_num=PACKET_NUM,
    #                           total_time=TOTAL_TIME, link_delay=LINK_DELAY, seed=i)
    #     success, idle, collision = csma(env_setting, False)
    #     sum_success += success
    #     sum_idle += idle
    #     sum_collision += collision
    # print('\tsuccess_rate:', round(sum_success/TIMES, 2))
    # print('\tidle_rate:', round(sum_idle/TIMES, 2))
    # print('\tcollision_rate:', round(sum_collision/TIMES, 2))

    # print('CSMA/CD')
    # sum_success = sum_idle = sum_collision = 0
    # for i in range(TIMES):
    #     env_setting = Setting(host_num=HOST_NUM, packet_num=PACKET_NUM,
    #                           total_time=TOTAL_TIME, link_delay=LINK_DELAY, seed=i)
    #     success, idle, collision = csma_cd(env_setting, False)
    #     sum_success += success
    #     sum_idle += idle
    #     sum_collision += collision

    # print('\tsuccess_rate:', round(sum_success/TIMES, 2))
    # print('\tidle_rate:', round(sum_idle/TIMES, 2))
    # print('\tcollision_rate:', round(sum_collision/TIMES, 2))


if '__main__' == __name__:
    main()
