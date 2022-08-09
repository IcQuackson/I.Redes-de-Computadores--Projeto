
import socket, sys
import threading
import os
import random
from select import select
import ast


def send_and_recv(msg, client_socket):
    client_socket.send(msg.encode())
    return client_socket.recv(1024).decode()

def get_account(username):
    # Gets account corresponding to given username
    with open(accounts_filename, 'r') as file:
        for line in file:
            account = line.strip().split(':')
            if (username == account[ACCOUNT_USERNAME]):
                return account
    return []

def add_account(username, password, name):
    # Adds acount to file where users are stored
    with open(accounts_filename, 'a') as file:
        file.write(f'{username}:{password}:{name}\n') 

def get_local(value, field):
    # Gets local based on the field given
    lst = ast.literal_eval(send_and_recv(f'GET_LOCAL {value} {field}', database_server))
    return lst


def get_activity(id):
    return ast.literal_eval(send_and_recv(f'GET_ACTIVITY {id}', database_server))

def register_local(request, username, client_socket):

    if (len(request) != 1):
        return 'This command takes no arguments.'

    # Checks if user already has a local
    local = get_local(username, 'owner')
    if (local != []):
        return 'You already have a local!'   

    # Get local data to complete registration
    local = send_and_recv('Insert local name: ', client_socket)

    if (' ' in local or not local.isalnum()):
        return 'Bad argument:\n\'local_name\' must be one word and must contain alphanumeric characters.'


    capacity = send_and_recv('Insert capacity: ', client_socket)

    if (not capacity.isdigit() or int(capacity) < 1):
        return 'Bad argument:\n\'capacity\' must be an integer greater than 1.'

    stay_time = send_and_recv('Insert stay time: ', client_socket)

    if (not stay_time.isdigit() or int(stay_time) < 1):
        return 'Bad argument:\n\'t_permanencia\' must be an integer greater than 1.'

    balance = send_and_recv('Insert balance: ', client_socket)

    if (not balance.isdigit() or int(balance) < 1):
        return 'Bad argument:\n\'saldo\' must be an integer greater than 1.'

    id = send_and_recv(f'ADD_LOCAL {username} {local} {capacity} {stay_time} {balance}', database_server)

    if (id == '0'):
        return "There was an error registering the local!"

    return 'Your local was registered successfully. Your local ID is: ' + id

def check_saldo(username):
    local = get_local(username, 'owner')
    
    if (local == []):
        return 'You don\'t have a local!'

    return 'Your current balance is ' + local[LOCAL_BALANCE] + ' euros.'

def cancel_local(username):

    if (send_and_recv(f'CANCEL_LOCAL {username}', database_server) == '0'):
        return 'There was an error deleting your local!'

    return 'Your local was deleted successfully.'

def check_local(username):
    local = get_local(username, 'owner')
    
    if (local == []):
        return 'You don\'t have a local!'
    
    local_id = local[LOCAL_ID]
    local_name = local[LOCAL_NAME]
    capacity = local[LOCAL_CAPACITY]
    stay_time = local[LOCAL_STAY_TIME]
    balance = local[LOCAL_BALANCE]
    
    return f'owner = {username}\nlocal id = {local_id}\nlocal name = {local_name}\ncapacity = {capacity}\nstay time = {stay_time}\nbalance = {balance}'
   
    
def create_activity(request, username, client_socket):

    if (len(request) != 1):
        return 'This command takes no arguments.'

    # Checks if user already has a local
    local = get_local(username, 'owner')
    if (local == []):
        return 'You don\'t have a local!' 

    activity_type = send_and_recv('Insert activity\'s type: ', client_socket)

    target_user = send_and_recv('Insert target user: ', client_socket)

    capacity = send_and_recv('Insert capacity: ', client_socket)

    if (not capacity.isdigit() or int(capacity) < 1):
        return 'Bad argument:\n\'capacity\' must be an integer greater than 1.'

    duration = send_and_recv('Insert activity\'s duration: ', client_socket)

    if (not duration.isdigit() or int(duration) < 1):
        return 'Bad argument:\n\'duration\' must be an integer greater than 1.' 

    points = send_and_recv('Insert points to subtract from client: ', client_socket)

    if (not points.isdigit() or int(points) < 0):
        return 'Bad argument:\n\'points\' must be an integer greater than 0.'

    cost = send_and_recv('Insert cost: ', client_socket)

    if (not cost.isdigit()):
        return 'Bad argument:\n\'cost\' must be an integer.'

    # Adds new activity
    id = send_and_recv(f'ADD_ACTIVITY {local[LOCAL_NAME]}:{activity_type}:{target_user}:{capacity}:{duration}:{points}:{cost}', database_server)
    if (id == '0'):
        return 'There was an error creating the activity'

    return 'Your activity was successfully created. Your activity ID is: ' + str(id)

def mod_activity(request, username, client_socket):

    if (len(request) != 2):
        return 'This command takes one argument: <activity_id>'

    activity_id = request[1]
    
    if (not activity_id.isdigit() or int(activity_id) < 0):
        return 'Bad argument:\n\'activity_id\' must be an integer greater than 0'

    new_capacity = '0'
    new_points = '0'
    new_cost = '0'
    answer = ''
    fields = [0, 0, 0]      # fields to be edited (capacity, points, cost)

    while (answer != 'y' and answer != 'n'):
        answer = send_and_recv('Change the capacity? [y/n]: ', client_socket)

    if (answer == 'y'):
        new_capacity = send_and_recv('Insert new capacity: ', client_socket)

        if (not new_capacity.isdigit() or int(new_capacity) < 1):
            return 'Bad argument:\n\'capacity\' must be an integer greater than 1.'
        fields[0] = 1
    
    answer = ''
    
    while (answer != 'y' and answer != 'n'):
        answer = send_and_recv('Change the points? [y/n]: ', client_socket)

    if (answer == 'y'):
        new_points = send_and_recv('Insert new points: ', client_socket)

        if (not new_points.isdigit() or int(new_points) < 0):
            return 'Bad argument:\n\'points\' must be an integer greater than 0.'
        fields[1] = 1

    answer = ''
    
    while (answer != 'y' and answer != 'n'):
        answer = send_and_recv('Change cost? [y/n]: ', client_socket)

    if (answer == 'y'):
        new_cost = send_and_recv('Insert new cost: ', client_socket)
        if (not new_cost.isdigit()):
            return 'Bad argument:\n\'cost\' must be an integer.'
        fields[2] = 1

    # set up arguments to be sent to database server
    values = f'[{new_capacity},{new_points},{new_cost}]'
    fields = f'[{fields[0]},{fields[1]},{fields[2]}]'

    # Sends mod activity command to database server
    if (send_and_recv(F'MOD_ACTIVITY {username} {activity_id} {fields} {values}', database_server) == '0'):
        return "There was an error editing the activity!"

    return 'Values edited successfully.'

def remove_activity(request, username, client_socket):
    if (len(request) != 2):
        return 'This command takes one arguments: <activity_id>'
    
    activity_id = request[1]

    if (send_and_recv(f'REMOVE_ACTIVITY {username} {activity_id}', database_server) == '0'):
        return 'There was an error removing the activity!'
        
    return 'Activity successfully removed.'
    

def iam(request, client_socket, client_addr):
    
    if (len(request) != 2):
        return 'Command only takes argument <username>'

    username = request[1]
    # Checks if account exists
    account = get_account(username)
    if (account != []):
        # Starts authentication
        # User has 3 tries
        for i in range(3):
            password = send_and_recv('Insert password: ', client_socket)
            username = account[ACCOUNT_USERNAME]
            if (password == account[ACCOUNT_PASSWORD]):
                name = account[ACCOUNT_NAME]
                # Deletes entry if he's already logged in
                username = find_user(client_addr)
                if (username != NULL):
                    active_users.pop(username)
                # Adds logged in user to active users
                active_users[request[1]] = client_addr
                #unlock
                return 'Logged in successfully!\nHello ' + name
            #unlock
            client_socket.send('Wrong password!\n'.encode())
    return 'Username not found.'

def registar_user(request, client_socket, client_addr):

    if (len(request) != 1):
        return 'This command takes no arguments.'

    username = send_and_recv('Insert username: ', client_socket)
    # Checks if user exists
    if (get_account(username) != []):
        return 'User already exists.'

    password = send_and_recv('Insert password: ', client_socket)
    name = send_and_recv('Insert your name: ', client_socket)

    # Deletes entry if he's already logged in
    user = find_user(client_addr)
    if (user != NULL):
        active_users.pop(user)
    # Register the user
    add_account(username, password, name)
    active_users[username] = client_addr
    return 'Registration successful\nHello ' + name

def reply_hello(client_socket, client_addr):
    username = find_user(client_addr)
    if (username == NULL):
        return 'Hello stranger'
    else:
        # Returns user's name
        return 'Hello ' + get_account(username)[ACCOUNT_NAME]

def log_out(username, client_socket, client_addr):
    # Deletes user from active users
    if (username != NULL):
        active_users.pop(username)
        return 'Logged out successfully!'
    else:
        return "Something went wrong"

def process_user_request(request, client_socket, client_addr):
    request = request.split()
    command = request[0]

    if (command == 'HELLO'):
        return reply_hello(client_socket, client_addr)
    
    if (command == 'IAM'):
        return iam(request, client_socket, client_addr)
    
    if (command == 'SIGN_UP'):
        return registar_user(request, client_socket, client_addr)

    # Checks if client is logged in
    username = find_user(client_addr)
    if (username != NULL):

        if (command == 'HELP'):
            return 'Commands available:\n\t•HELLO\n\t•IAM\n\t•SIGN_UP\n\t•REGISTER_LOCAL\n\t•DELETE_LOCAL\n\t•CHECK_BALANCE\n\t•CREATE_ACTIVITY\n\t•MOD_ACTIVITY\n\t•DELETE_ACTIVITY\n\t•LOGOUT'

        if (command == 'REGISTER_LOCAL'):
            return register_local(request, username, client_socket)
        
        if (command == 'VER_LOCAL'):
            return check_local(username)
        
        if (command == 'DELETE_LOCAL'):
            return cancel_local(username)
        
        if (command == 'CHECK_BALANCE'):
            return check_saldo(username)

        if (command == 'CREATE_ACTIVITY'):
            return create_activity(request, username, client_socket)
        
        if (command == 'MOD_ACTIVITY'):
            return mod_activity(request, username, client_socket)

        if (command == 'DELETE_ACTIVITY'):
            return remove_activity(request, username, client_socket)
        
        if (command == 'LOGOUT'):
            return log_out(username, client_socket, client_addr)

    if (command == 'HELP'):
        return 'Commands available:\n\t•HELLO\n\t•IAM\n\t•SIGN_UP'

    return 'Unknown command: please try again. Type HELP for more details.'


# Returns username from address
def find_user (addr):
    for key, val in list(active_users.items()):
        if val == addr:
            return key
    return NULL


def tcp_handle_client_connection(client_socket, client_addr):
    terminal_string = 'LocalOwnersServer:$ '

    client_socket.send(terminal_string.encode())
    while True:
        # Receive command from client
        msg_from_client = client_socket.recv(1024)
        request = msg_from_client.decode()
        
        # Check if request is empty
        if (len(request.split()) == 0 or request == 'QUIT'):
            break

        # Returns command output and sends to client
        msg_to_client = process_user_request(request, client_socket, client_addr)
        client_socket.send((msg_to_client + '\n' + terminal_string).encode())

    # Closes connection with client
    msg_to_client = 'Connection terminated.'.encode()
    client_socket.send(msg_to_client)
    client_socket.close()

    
# main code

server_ip = '127.0.0.1'
tcp_server_port = 9990
database_server_port = 9996

# create tcp socket
tcp_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
tcp_server.bind((server_ip, tcp_server_port))
tcp_server.listen(5)  # max backlog of connections

# create database socket
database_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
database_server.connect((server_ip, database_server_port))

inputs = [tcp_server, database_server]

print ('OWNERS\nListening on {}:{}'.format(server_ip, tcp_server_port))

NULL = ''

active_users = {}   #dict: key: user_name; val:user_address info: example:'maria'= ('127.0.0.1',17234)

LOCAL_OWNER = 0
LOCAL_ID = 1
LOCAL_NAME = 2
LOCAL_CAPACITY = 3
LOCAL_STAY_TIME = 4
LOCAL_BALANCE = 5

ACTIVITY_ID = 0
ACTIVITY_LOCAL = 1
ACTIVITY_TYPE = 2
ACTIVITY_TARGET_USER = 3
ACTIVITY_CAPACITY = 4
ACTIVITY_DURATION = 5
ACTIVITY_POINTS = 6
ACTIVITY_COST = 7
ACTIVITY_STATE = 8
ACTIVITY_AVAILABILITY = 9
ACTIVITY_TIME = 10

ACCOUNT_USERNAME = 0
ACCOUNT_PASSWORD = 1
ACCOUNT_NAME = 2
ACCOUNT_LOCAL_ID = 3

activities_filename = 'activities.txt'
activities_lock = threading.Lock()

locals_filename = 'locals.txt'
locals_lock = threading.Lock()

accounts_filename = 'owner_accounts'
accounts_lock = threading.Lock()

active_users_lock = threading.Lock()

filenames = [accounts_filename]
for f in filenames:
    file = open(f, 'a+')
    file.close()


try:
    
    while True:
        ins, outs, excs = select(inputs, [], [])
        for socket in ins:
            if (socket == tcp_server):
                client_socket, client_addr = tcp_server.accept()
                print ('Accepted TCP connection from {}:{}'.format(client_addr[0], client_addr[1]))
                tcp_client_handler = threading.Thread(
                    target=tcp_handle_client_connection,
                    args=(client_socket, client_addr,)  # without comma you'd get a... TypeError: handle_client_connection() argument after * must be a sequence, not _socketobject
                )
                tcp_client_handler.start()

except (KeyboardInterrupt):
    tcp_server.close()

finally:
    print("Server terminated.")




