#include <stdlib.h>
#include <string.h>

#include <iostream>
#include <vector>

#define DICTIONARY "--interface", "-i", "--count", "-c", "--filter", "-f"
#define DIC_LENGTH 6
#define FILTER_DICTIONARY "udp", "tcp", "icmp", "all"
#define FDIC_LENGTH 4
#define STRING_LENGTH 100
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
bool check_command_valid(struct command);

int main(int argc, const char* argv[]) {
    command cmd;
    initial_command(&cmd);
    save_command(&cmd, argc, argv);

    if (!check_command_valid(cmd)) {
        fprintf(stderr, "Error: Filter \"%s\" is invalid.\n", cmd.filter);
        exit(EXIT_FAILURE);
    }
    show_command(cmd);
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