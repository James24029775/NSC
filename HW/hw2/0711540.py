from setting import get_hosts, get_switches, get_links, get_ip, get_mac


class host:
    def __init__(self, name, ip, mac):
        self.name = name
        self.ip = ip
        self.mac = mac
        self.port_to = None
        self.arp_table = dict()  # maps IP addresses to MAC addresses

    def add(self, node):
        self.port_to = node

    def show_table(self):
        # display ARP table entries for this host
        print('----------------', self.name)
        for key, value in self.arp_table.items():
            print(str(key) + ' : ' + str(value))

    def clear(self):
        # clear ARP table entries for this host
        self.arp_table = dict()

    def update_arp(self, ip, mac):
        # update ARP table with a new entry
        self.arp_table[ip] = mac

    def handle_packet(self, pkt, name):  # handle incoming packets
        mac1, mac2, ip1, ip2, flg = pkt
        # check if the receiver is me or not.
        if ip2 != self.ip:
            pass
        else:
            self.update_arp(ip1, mac1)

            if flg == 'request':
                pkt = (self.mac, mac1, self.ip, ip1, 'reply')
                self.send(pkt, self.name)
            elif flg == 'reply':
                pass

    def ping(self, dst_ip):  # handle a ping request
        if dst_ip in self.arp_table:
            dest_mac = self.arp_table[dst_ip]
        else:
            dest_mac = 'FFFFFF'

        pkt = (self.mac, dest_mac, self.ip, dst_ip, "request")
        self.send(pkt, self.name)

    def send(self, pkt, name):
        node = self.port_to  # get node connected to this host
        node.handle_packet(pkt, name)  # send packet to the connected node


class switch:
    def __init__(self, name, port_n):
        self.name = name
        self.mac_table = dict()  # maps MAC addresses to port numbers
        self.port_n = port_n  # number of ports on this switch
        self.port_to = list()

    def add(self, node):  # link with other hosts or switches
        self.port_to.append(node)

    def show_table(self):
        # display MAC table entries for this switch
        print('----------------', self.name)
        for key, value in self.mac_table.items():
            print(str(key) + ' : ' + str(value))

    def clear(self):
        # clear MAC table entries for this switch
        self.mac_table = dict()

    def update_mac(self, mac, port):
        # update MAC table with a new entry
        self.mac_table[mac] = port
        # print(self.mac_table)

    def get_port_from(self, name):
        for i in range(self.port_n):
            if self.port_to[i].name == name:
                port = i
                break
        return port

    def send(self, idx, pkt):  # send to the specified port
        node = self.port_to[idx]
        node.handle_packet(pkt, self.name)

    def flood(self, skip_nport, pkt):
        for i in range(self.port_n):
            if i == skip_nport:
                continue
            else:
                self.send(i, pkt)

    def handle_packet(self, pkt, name):  # handle incoming packets
        mac1, mac2, ip1, ip2, flg = pkt
        nport_from = self.get_port_from(name)
        self.update_mac(mac1, nport_from)

        if mac2 in self.mac_table:
            nport_to = self.mac_table[mac2]
            if nport_from == nport_to:
                pass
            else:
                self.send(nport_to, pkt)
        # If mac2 miss or mac2 is FFFFFF, then flood.
        else:
            self.flood(nport_from, pkt)


def add_link(tmp1, tmp2):  # create a link between two nodes
    node1 = host_dict[tmp1] if tmp1[0] == 'h' else switch_dict[tmp1]
    node2 = host_dict[tmp2] if tmp2[0] == 'h' else switch_dict[tmp2]
    node1.add(node2)
    node2.add(node1)


def set_topology():
    global host_dict, switch_dict
    hostlist = get_hosts().split(' ')
    switchlist = get_switches().split(' ')
    link_command = get_links().split(' ')
    ip_dic = get_ip()
    mac_dic = get_mac()

    host_dict = dict()  # maps host names to host objects
    switch_dict = dict()  # maps switch names to switch objects

    # ... create nodes and links
    for name in hostlist:
        host_dict[name] = host(name, ip_dic[name], mac_dic[name])

    for name in switchlist:
        if name == 's7':
            port_n = 2
        else:
            port_n = 3
        switch_dict[name] = switch(name, port_n)

    for link in link_command:
        name1, name2 = link.split(',')
        add_link(name1, name2)

    # for name in switchlist:
    #     obj = switch_dict[name]
    #     print(obj.name,":", end='')
    #     for i in range(len(obj.port_to)):
    #         print(obj.port_to[i].name, end='')
    #     print()


def ping(tmp1, tmp2):  # initiate a ping between two hosts
    global host_dict, switch_dict

    if tmp1 in host_dict and tmp2 in host_dict:
        node1 = host_dict[tmp1]
        node2 = host_dict[tmp2]
        node1.ping(node2.ip)
    else:
        # invalid command
        print('Invalid request.')


def show_table(tmp):  # display the ARP or MAC table of a node
    global host_dict, switch_dict
    if tmp == 'all_hosts':
        print('ip : mac')
        for key, value in host_dict.items():
            value.show_table()
    elif tmp == 'all_switches':
        print('mac : port')
        for key, value in switch_dict.items():
            value.show_table()
    elif tmp[0] == 'h':
        print('ip : mac')
        node = host_dict[tmp]
        node.show_table()
    elif tmp[0] == 's':
        print('mac : port')
        node = switch_dict[tmp]
        node.show_table()
    else:
        print("Invalid node:", tmp)


def clear(tmp):
    global host_dict, switch_dict
    node = host_dict[tmp] if tmp[0] == 'h' else switch_dict[tmp]
    node.clear()


def run_net():
    while(1):
        command_line = input(">> ")
        # ... handle user commands
        terms = command_line.split(' ')
        if len(terms) == 2 and terms[0] == 'show_table':
            show_table(terms[1])
        elif len(terms) == 3 and terms[1] == 'ping':
            ping(terms[0], terms[2])

        elif len(terms) == 2 and terms[0] == 'clear':
            clear(terms[1])
        else:
            print('A wrong command')


def main():
    set_topology()
    run_net()


if __name__ == '__main__':
    main()
