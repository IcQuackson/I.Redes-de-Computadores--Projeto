import os
import subprocess
import sys


os.system("gnome-terminal -e 'bash -c \"python3 db.py; exec bash\"'")
os.system("gnome-terminal -e 'bash -c \"python3 tcp-server-owners.py; exec bash\"'")
os.system("gnome-terminal -e 'bash -c \"python3 cidadao_tcp-server.py; exec bash\"'")
os.system("gnome-terminal -e 'bash -c \"python3 gestor_tcp-server.py; exec bash\"'")

try:
    while (True):
        command = input('Which server do you want to access?\n1.Owners\n2.Users\n3.Managers\n(Press 1, 2 or 3)\n')
        if (command == '1'):
            os.system("gnome-terminal -e 'bash -c \"python3 owner-tcp-client.py; exec bash\"'")
        if (command == '2'):
            os.system("gnome-terminal -e 'bash -c \"python3 cidadao_tcp-client.py; exec bash\"'")
        if (command == '3'):
            os.system("gnome-terminal -e 'bash -c \"python3 gestor_tcp-client.py; exec bash\"'")
except KeyboardInterrupt:
    pass