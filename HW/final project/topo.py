#!/usr/bin/env python
from mininet.cli import CLI
from mininet.net import Mininet
from mininet.link import Link,TCLink
 
if '__main__' == __name__:
	net = Mininet(link=TCLink)

	h1 = net.addHost('h1')
	h2 = net.addHost('h2')
	h3 = net.addHost('h3')
	r1 = net.addHost('r1')
	r2 = net.addHost('r2')
	r3 = net.addHost('r3')

	Link(h1, r1)
	Link(r1, r2)
	Link(r2, r3)
	Link(r3, h2)
	Link(r3, h3)

	net.build()

	# set ethernet interface
	h1.cmd("ifconfig h1-eth0 0")
	h2.cmd("ifconfig h2-eth0 0")
	h3.cmd("ifconfig h3-eth0 0")
	r1.cmd("ifconfig r1-eth0 0")
	r1.cmd("ifconfig r1-eth1 0")
	r2.cmd("ifconfig r2-eth0 0")
	r2.cmd("ifconfig r2-eth1 0")
	r3.cmd("ifconfig r3-eth0 0")
	r3.cmd("ifconfig r3-eth1 0")
	r3.cmd("ifconfig r3-eth2 0")

	# set ip for each ethernet interface
	h1.cmd("ip addr add 192.168.1.1/24 brd + dev h1-eth0")
	h2.cmd("ip addr add 207.154.3.154/24 brd + dev h2-eth0")
	h3.cmd("ip addr add 207.154.4.176/24 brd + dev h3-eth0")
	r1.cmd("ip addr add 192.168.1.254/24 brd + dev r1-eth0")
	r1.cmd("ip addr add 10.0.0.1/24 brd + dev r1-eth1")
	r2.cmd("ip addr add 10.0.0.2/24 brd + dev r2-eth0")
	r2.cmd("ip addr add 192.168.2.254/24 brd + dev r2-eth1")
	r3.cmd("ip addr add 192.168.2.1/24 brd + dev r3-eth0")
	r3.cmd("ip addr add 207.154.3.1/24 brd + dev r3-eth1")
	r3.cmd("ip addr add 207.154.4.1/24 brd + dev r3-eth2")

	# set route rule for each node
	h1.cmd("ip route add default via 192.168.1.254")
	h2.cmd("ip route add default via 207.154.3.1")
	h3.cmd("ip route add default via 207.154.4.1")
	r1.cmd("ip route add default via 10.0.0.2")
	r2.cmd("ip route add default via 10.0.0.1")
	r2.cmd("ip route add 207.154.0.0/16 via 192.168.2.1")
	r3.cmd("ip route add default via 192.168.2.254")

	# enable route rule functioning
	r1.cmd("echo 1 > /proc/sys/net/ipv4/ip_forward")
	r2.cmd("echo 1 > /proc/sys/net/ipv4/ip_forward")
	r3.cmd("echo 1 > /proc/sys/net/ipv4/ip_forward")

	CLI(net)
	net.stop()