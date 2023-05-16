from mininet.net import Mininet
from mininet.node import CPULimitedHost
from mininet.link import TCLink
from mininet.node import OVSKernelRouter

def create_network():
    # 建立 Mininet 拓撲
    net = Mininet(host=CPULimitedHost, link=TCLink)

    # 建立節點（主機、路由器和交換機）
    h1 = net.addHost('h1')
    h2 = net.addHost('h2')
    router = net.addHost('router', cls=OVSKernelRouter)
    switch = net.addSwitch('switch')

    # 建立連接
    net.addLink(h1, switch)
    net.addLink(h2, switch)
    net.addLink(router, switch)

    # 設置 IP 地址
    h1.setIP('192.168.0.1/24')
    h2.setIP('192.168.0.2/24')
    router.setIP('192.168.0.3/24')

    # 啟動 Mininet 網絡
    net.start()

    # 啟動命令行介面
    net.interact()

    # 停止 Mininet 網絡
    net.stop()

# 執行程式
if __name__ == '__main__':
    create_network()
