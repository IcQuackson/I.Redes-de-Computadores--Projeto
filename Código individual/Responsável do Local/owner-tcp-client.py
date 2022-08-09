import socket
import sys, getopt
import time

server_ip = '127.0.0.1'
server_port = 9990

commands = []
# Reads of commands from a file if program was executed with an argument containing the name of the file
if (len(sys.argv) != 1):
    file = open(sys.argv[1], 'r')
    commands = file.readlines()
    file.close()

# create an ipv4 (AF_INET) socket object using the tcp protocol (SOCK_STREAM)
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# connect the client
client.connect((server_ip, server_port))

try:
    terminal_string = (client.recv(4096).decode()).strip()
    print(terminal_string, end='')
    i = 0
    while True:
        # Reads command from file while they still exist
        if (i < len(commands)):
            msg = commands[i].strip('\n')
        # Reads from user input after commands from file have been executed or if file argument was never given
        else:
            msg = ''
            j = 0
            while (len(msg) == 0):
                if (j >= 1):
                    print(terminal_string, end='')
                msg = input()
                j += 1

        if (msg == 'QUIT'):
            raise KeyboardInterrupt

        msg_to_send = msg.encode()
        
        # send a message
        client.send(msg_to_send)

        # receive the response data (4096 is recommended buffer size)
        response = client.recv(4096)
        msg_from_server = response.decode()
        if (i < len(commands)):
            print('\n ' + msg_from_server, end='')
        else:
            print(msg_from_server, end='')
        i += 1
        
except KeyboardInterrupt:
    client.shutdown(socket.SHUT_WR)
    response = client.recv(4096)
    msg_from_server = response.decode()
    print('\n' + msg_from_server + '\n')

client.close()