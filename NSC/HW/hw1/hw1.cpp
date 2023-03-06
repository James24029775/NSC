

#include <netinet/ether.h>
#include <netinet/in.h>
#include <netinet/ip.h>
#include <netinet/ip_icmp.h>
#include <netinet/tcp.h>
#include <netinet/udp.h>
#include <pcap/pcap.h>
#include <stdlib.h>
#include <string.h>

#include <iostream>
#include <vector>

#define DICTIONARY "--interface", "-i", "--count", "-c", "--filter", "-f"
#define DIC_LENGTH 6
#define FILTER_DICTIONARY "udp", "tcp", "icmp", "all"
#define FDIC_LENGTH 4
#define STRING_LENGTH 100
#define ETH_HEADER_SIZE 14
#define UDP_HEADER_SIZE 8
#define MSG_BUF_SIZE 65535
using namespace std;

struct command {
    char interface[STRING_LENGTH];
    char filter[STRING_LENGTH];
    int count;
};

int toDigit(const char*);
void initial_command(struct command*);
void show_command(struct command);
void save_command(struct command*, int, const char*[]);
void show_ascii(uint8_t[], int);
void show_udp(struct iphdr*, struct udphdr*, u_int8_t*);
void show_icmp(struct iphdr*, struct icmphdr*);
void show_tcp(struct iphdr*, struct tcphdr*, u_int8_t*);
void show_port(uint16_t, uint16_t);
bool check_command_valid(struct command);

uint8_t msg_buffer[MSG_BUF_SIZE];

int main(int argc, const char* argv[]) {
    pcap_if_t* devices = NULL;
    char errbuf[PCAP_ERRBUF_SIZE];
    char ntop_buf[256];
    vector<pcap_if_t*> vec;  // vec is a vector of pointers pointing to pcap_if_t

    // My variable
    command cmd;
    struct pcap_pkthdr pkthdr;
    struct ethhdr* eptr;
    struct iphdr* iptr;
    struct tcphdr* tptr;
    struct udphdr* uptr;
    struct icmphdr* cptr;
    int i, ip_header_size, tcp_header_size;
    u_int8_t* payload;
    uint8_t transport_protocol;
    uint16_t h_proto;
    initial_command(&cmd);
    save_command(&cmd, argc, argv);

    if (!check_command_valid(cmd)) {
        fprintf(stderr, "Error: Filter \"%s\" is invalid.\n", cmd.filter);
        exit(EXIT_FAILURE);
    }

    // get all devices
    if (-1 == pcap_findalldevs(&devices, errbuf)) {
        fprintf(stderr, "pcap_findalldevs: %s\n", errbuf);  // if error, fprint error message --> errbuf
        exit(1);
    }

    // list all device
    int cnt = 0;
    for (pcap_if_t* d = devices; d; d = d->next, cnt++) {
        vec.push_back(d);
        cout << "Name: " << d->name << endl;
    }

    struct bpf_program fp;  // for filter, compiled in "pcap_compile"
    pcap_t* handle;
    handle = pcap_open_live(cmd.interface, 65535, 1, 1, errbuf);
    // pcap_open_live(device, snaplen, promise, to_ms, errbuf), interface is your interface, type is "char *"

    if (!handle || handle == NULL) {
        fprintf(stderr, "pcap_open_live(): %s\n", errbuf);
        exit(1);
    }

    if (-1 == pcap_compile(handle, &fp, cmd.filter, 1, PCAP_NETMASK_UNKNOWN))  // compile "your filter" into a filter program, type of {your_filter} is "char *"
    {
        pcap_perror(handle, "pkg_compile compile error\n");
        exit(1);
    }
    if (-1 == pcap_setfilter(handle, &fp)) {  // make it work
        pcap_perror(handle, "set filter error\n");
        exit(1);
    }

    i = 0;
    while (i++ < cmd.count) {
        memset(&pkthdr, 0, sizeof(struct pcap_pkthdr));
        memset(msg_buffer, 0, sizeof(msg_buffer));

        const unsigned char* packet = pcap_next(handle, &pkthdr);
        eptr = (struct ethhdr*)(packet);
        h_proto = ntohs(eptr->h_proto);
        switch (h_proto) {
            case 0x0800:  // IPv4
                iptr = (struct iphdr*)(packet + ETH_HEADER_SIZE);
                break;
            case 0x0806:  // ARP
                printf("ARP packet detected\n");
                continue;
                break;
            default:
                printf("Unknown packet type\n");
                continue;
                break;
        }

        ip_header_size = iptr->ihl * 4;
        transport_protocol = iptr->protocol;
        switch (transport_protocol) {
            case 0x01:
                cptr = (struct icmphdr*)(packet + ETH_HEADER_SIZE + ip_header_size);
                show_icmp(iptr, cptr);
                break;
            case 0x06:
                tptr = (struct tcphdr*)(packet + ETH_HEADER_SIZE + ip_header_size);
                tcp_header_size = tptr->doff * 4;
                payload = (u_int8_t*)(packet + ETH_HEADER_SIZE + ip_header_size + tcp_header_size);
                show_tcp(iptr, tptr, payload);
                break;
            case 0x11:
                uptr = (struct udphdr*)(packet + ETH_HEADER_SIZE + ip_header_size);
                payload = (u_int8_t*)(packet + ETH_HEADER_SIZE + ip_header_size + UDP_HEADER_SIZE);
                show_udp(iptr, uptr, payload);
                break;
        }
    }

    pcap_freealldevs(devices);

    return 0;
}

void show_ip(struct iphdr* iptr) {
    struct in_addr in;
    char* str_ip;
    uint32_t src_ip, dest_ip;
    src_ip = iptr->saddr;
    dest_ip = iptr->daddr;
    in.s_addr = src_ip;
    str_ip = inet_ntoa(in);
    cout << "Source IP: " << str_ip << endl;
    in.s_addr = dest_ip;
    str_ip = inet_ntoa(in);
    cout << "Destination IP: " << str_ip << endl;
}

void show_tcp(struct iphdr* iptr, struct tcphdr* tptr, u_int8_t* payload) {
    int tcp_header_size, payload_len;
    uint16_t src_port, dest_port;

    tcp_header_size = tptr->doff * 4;
    payload_len = ntohs(iptr->tot_len) - iptr->ihl * 4 -tcp_header_size;
    src_port = ntohs(tptr->source);
    dest_port = ntohs(tptr->dest);

    memcpy(msg_buffer, payload, payload_len);
    printf("Transport type: TCP\n");
    show_ip(iptr);
    show_port(src_port, dest_port);
    show_ascii(msg_buffer, payload_len);
}

void show_icmp(struct iphdr* iptr, struct icmphdr* cptr) {
    printf("Transport type: ICMP\n");
    show_ip(iptr);
    printf("ICMP type value: %d\n\n", cptr->type);
}

void show_port(uint16_t src_port, uint16_t dest_port) {
    printf("Source port: %u\n", src_port);
    printf("Destination port: %u\n", dest_port);
}

void show_udp(struct iphdr* iptr, struct udphdr* uptr, u_int8_t* payload) {
    int payload_len;
    uint16_t len, src_port, dest_port;

    len = ntohs(uptr->len);
    payload_len = len - UDP_HEADER_SIZE;
    src_port = ntohs(uptr->source);
    dest_port = ntohs(uptr->dest);
    memcpy(msg_buffer, payload, payload_len);
    printf("Transport type: UDP\n");
    show_ip(iptr);
    show_port(src_port, dest_port);
    show_ascii(msg_buffer, payload_len);
}

void show_ascii(uint8_t msg_buffer[], int payload_len) {
    int i;
    printf("Payload: ");
    for (i = 0; i < 16; i++) {
        if (msg_buffer[i] != 0){
            printf("%x ", msg_buffer[i]);
        }
    }
    printf("\n\n");
}

void save_command(struct command* cmd, int argc, const char* argv[]) {
    int i, j, cmd_idx;
    const char* dictionary[] = {DICTIONARY};
    bool cmd_flg;
    for (i = 1; i < argc; i++) {
        cmd_flg = false;
        for (j = 0; j < DIC_LENGTH; j++) {
            if (!strcmp(argv[i], dictionary[j])) {
                cmd_idx = j;
                cmd_flg = true;
                break;
            }
        }
        if (cmd_flg) {
            i++;
            switch (cmd_idx) {
                case 0:
                case 1:
                    strcpy(cmd->interface, argv[i]);
                    break;
                case 2:
                case 3:
                    cmd->count = toDigit(argv[i]);
                    break;
                case 4:
                case 5:
                    strcpy(cmd->filter, argv[i]);
                    break;
            }
        }
    }
}

int toDigit(const char* str) {
    int i, sum;
    sum = 0;
    for (i = 0; i < strlen(str); i++) {
        sum = (str[i] - '0') + sum * 10;
    }
    return sum;
}

void initial_command(struct command* cmd) {
    memset(cmd, 0, sizeof(struct command));
    cmd->count = -1;
    strcpy(cmd->filter, "all");
}

void show_command(struct command cmd) {
    cout << "interface: " << cmd.interface << endl;
    cout << "count: " << cmd.count << endl;
    cout << "filter: " << cmd.filter << endl;
}

bool check_command_valid(struct command cmd) {
    int i, valid_flg;
    const char* filter_dictionary[] = {FILTER_DICTIONARY};
    valid_flg = false;
    for (i = 0; i < FDIC_LENGTH; i++) {
        if (strcmp(cmd.filter, filter_dictionary[i])) {
            valid_flg = true;
            break;
        }
    }
    return valid_flg;
}