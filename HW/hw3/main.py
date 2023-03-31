from protocols import *
from setting import Setting

# SPEC's settings
TIMES = 100
HOST_NUM = 3
TOTAL_TIME = 100
PACKET_NUM = 4
MAX_COL = 21
P_RESEND = 0.3
PACKET_SIZE = 3
LINK_DELAY = 1
SEED = 4


def main():
    env_setting = Setting(host_num=HOST_NUM, packet_num=PACKET_NUM, total_time=TOTAL_TIME, link_delay=LINK_DELAY,
                          max_colision_wait_time=MAX_COL, packet_size=PACKET_SIZE, seed=SEED, p_resend=P_RESEND)
    print('aloha')
    show(aloha(env_setting, True))
    print('slotted_aloha')
    show(slotted_aloha(env_setting, True))
    print('csma')
    show(csma(env_setting, True))
    print('csma_cd')
    show(csma_cd(env_setting, True))


def show(tuple):
    success_rate, idle_rate, collision_rate = tuple
    print('Success rate:', success_rate)
    print('Idle rate:', idle_rate)
    print('Collision rate:', collision_rate)
    print()

if '__main__' == __name__:
    main()
