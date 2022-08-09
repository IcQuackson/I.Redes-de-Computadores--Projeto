import socket, sys
import threading
import os
import random
from select import select
import ast



#####################################################################################################################################################
# Seccao feita para os responsaveis dos locais (Pedro Goncalves)

def send_and_recv(msg, client_socket):
    client_socket.send(msg.encode())
    return client_socket.recv(1024).decode()


def add_local(args):
    owner = args[0]
    local_name = args[1]
    capacity = args[2]
    stay_time = args[3]
    balance = args[4]

    if (get_local(local_name, 'name') != []):
        return 0

    # Checks if max number of registered locals has been reached
    if (count_locals() >= 100):
        return 0

    # Checks for id duplication
    local_id = random.randint(1, 101)
    while (get_local(local_id, 'id') != []):
        local_id = random.randint(1, 101)

    with open(locals_filename, 'r') as file:
        entries = file.readlines()

    # Stores local info in a new line of the file where locals are stored
    with open(locals_filename, 'a') as file:
        file.write('{}:{}:{}:{}:{}:{}\n'.format(owner, local_id, local_name, capacity, stay_time, balance))

    return local_id

def get_local(value, field):
    # Gets local based on the field given
    field_types = {'owner': LOCAL_OWNER, 'id': LOCAL_ID, 'name': LOCAL_NAME}
    if (field not in field_types):
        print('Error: get_local')
        return []

    position = field_types[field]

    with open(locals_filename, 'r') as locals_file:
        for line in locals_file:
            entry = line.strip().split(':')
            if (str(value) == entry[position]):
                return entry
        return []

def get_activity_availability(id_activity):
    with open(users_filename, 'r') as file:
        entries = file.readlines()
    # Gets all users
    users = [l.split(";") for l in entries]
    activity = get_activity(id_activity)
    current_availability = int(activity[ACTIVITY_CAPACITY])

    # Subtracts current availability for each user registered in the activity
    for user in users:
        if (user[USER_ACTIVITY] == id_activity):
            current_availability -= 1
    return current_availability


def is_local_empty(local_name):
    local = get_local(local_name, 'name')

    with open(users_filename, 'r') as file:
        entries = file.readlines()

    users = [l.split(";") for l in entries]
    # Checks if users are registered in the local
    for user in users:
        if (user[USER_LOCAL_ID] == local[LOCAL_ID]):
            return False
    return True


def add_activity(args):
    local_name = args[0]
    activity_type = args[1]
    target_user = args[2]
    capacity = args[3]
    duration = args[4]
    points = args[5]
    cost = args[6]

    # Checks if there is already an activity in the same local with the same type
    with open(activities_filename, 'r') as file:
        for line in file:
            activity = line.split(':')
            if activity[ACTIVITY_LOCAL] == local_name and activity[ACTIVITY_TYPE] == activity_type:
                return 0

    # Checks for id duplication
    id = random.randint(1, 101)

    while (get_activity(id) != []):
        id = random.randint(1, 101)

    # Stores activity in a new line of the file where activities are stored
    with open(activities_filename, 'a') as file:
        file.write(f'{id}:{local_name}:{activity_type}:{target_user}:{capacity}:{duration}:{points}:{cost}:True:True:0\n')
        
    return id

def get_activity(id):
    # Gets activity from id
    with open(activities_filename, 'r') as file:
        for line in file:
            activity = line.strip().split(':')
            if (str(id) == activity[ACTIVITY_ID]):
                return  activity
    return []

def count_locals():
    # Counts number of locals
    with open(locals_filename, 'r') as locals_file:
        locals_file = open(locals_filename, "r")
        line_count = 0
        for line in locals_file:
            if line != "\n":
                line_count += 1
        return line_count

def cancel_local(username):
    local = get_local(username, 'owner')
    
    if (local == []):
        return 0
    
    # Checks if local has users in it
    if (not is_local_empty(local[LOCAL_NAME])):
        return 0

    with open(locals_filename, 'r') as file:
        entries = file.readlines()
        entries.remove(':'.join(local) + '\n')

    with open(locals_filename, 'w') as file:
        file.writelines(entries)

    return 1


def is_activity_empty(id):
    activity = get_activity(id)

    with open(users_filename, 'r') as file:
        entries = file.readlines()

    users = [l.split(";") for l in entries]
    for user in users:
        if (user[USER_ACTIVITY] == activity[ACTIVITY_ID]):
            return False
    return True


def remove_activity(username, id):

    local = get_local(username, 'owner')
    
    if (local == []):
        return 0

    activity = get_activity(id)
    # Checks if activity doesnt exist or if activity doesnt exist in the users local
    if (activity == [] or activity[ACTIVITY_LOCAL] != get_local(username, 'owner')[LOCAL_NAME]):
        return 0

    # Check if activity is being used
    if (not is_activity_empty(id)):
        return 0

    # Removes entry from file
    with open(activities_filename, 'r') as file:
        entries = file.readlines()
        entries.remove(':'.join(activity) + '\n')

    with open(activities_filename, 'w') as file:
        file.writelines(entries)
    
    return 1


def change_activity_field(args):
    username = args[0]
    activity_id = args[1]
    fields_edited = ast.literal_eval(args[2])
    values = ast.literal_eval(args[3])

    local = get_local(username, 'owner')
    
    if (local == []):
        return 0
    
    activity = get_activity(activity_id)
    # Checks if activity doesnt exist or if activity doesnt exist in the users local
    if (activity == [] or activity[ACTIVITY_LOCAL] != get_local(username, 'owner')[LOCAL_NAME]):
        print('activity doesnt exist or if activity doesnt exist in the users local')
        return 0

    # Check if activity is being used
    if (get_activity_availability(activity_id) != int(activity[ACTIVITY_CAPACITY])):
        print('activity is being used')
        return 0

    fields = {0: ACTIVITY_CAPACITY, 1: ACTIVITY_POINTS, 2: ACTIVITY_COST}
    for i in range(len(fields)):
        # Edits chosen fields
        if (fields_edited[i] == 1):
            activity[fields[i]] = values[i]


    line_counter = 0
    # Gets activity line
    with open(activities_filename, 'r') as file:
        for line in file:
            entry = line.strip().split(':')
            if (str(activity_id) == entry[ACTIVITY_ID]):
                break
            line_counter += 1

    with open(activities_filename, 'r') as file:
        entries = file.readlines()
    # Replaces old entry by new updated one

    entries[line_counter] = f'{activity[ACTIVITY_ID]}:{activity[ACTIVITY_LOCAL]}:{activity[ACTIVITY_TYPE]}:{activity[ACTIVITY_TARGET_USER]}:{activity[ACTIVITY_CAPACITY]}:{activity[ACTIVITY_DURATION]}:{activity[ACTIVITY_POINTS]}:{activity[ACTIVITY_COST]}:{activity[ACTIVITY_STATE]}:{activity[ACTIVITY_AVAILABILITY]}:{activity[ACTIVITY_TIME]}\n'
    
    with open(activities_filename, 'w') as file:
        file.writelines(entries)
    return 1

#####################################################################################################################################################
# Seccao feita para os utentes (Lucas Figueiredo)


def register_user(request):
    request = request.split(";")
    already_exists=0

    for r in request:
        if (r=="ERRO"):                             #Verificar se todos os argumentos sao validos
            return "0: Parametros inválidos!"  

    local=get_local(request[0], 'id')
    if (local==[]):                                 #Verificar se local existe
        return "0: Local inexistente!"

    local=int(local[LOCAL_CAPACITY])
    with open(users_filename, 'r') as file:
        data = file.readlines()
    lines = [l.split(";") for l in (data)]

    if (lines == []):
        with open(users_filename, 'a') as file:     #Verificar se a base de dados do utente está vazia
            file.write(f'1;{request[1]};{request[0]};False;{request[2]};0;0;{request[3]}\n')
        return "1: Utente registado com sucesso com o id:1!"

    total=0
    for l in lines:
        if(l[USER_LOCAL_ID]==request[0]):           #Verificar se ainda ha lotacao disponivel
            total+=1
    if not(total<local):
        return "0: Local já na lotação máxima!"

    for l in lines:
        last_id=l[USER_ID]
        if (l[USER_NAME]==request[1] and l[USER_LOCAL_ID]=="False"):
            already_exists=1
            l[USER_LOCAL_ID]=request[0]             #Verificar se utente ja esta registado na base de dados sem local
            l[USER_JOB]=request[2]
            l[USER_TIME_REMAINED]=f"{request[3]}\n"
            break
        elif (l[USER_NAME]==request[1] and l[USER_LOCAL_ID]!="False"):  #Verificar que utente ja se encontra num local
            return "0: Utente já registado em um local!"

    if(already_exists):                             #Colocar utente num local
        edit_file_user(lines)
        return f"{last_id}: Utente registado com sucesso com o id:{last_id}!"

    else:                                           #Adicionar utente à base de dados
        last_id=int(last_id)+1
        with open(users_filename, 'a') as file:
                file.write(f'{last_id};{request[1]};{request[0]};False;{request[2]};0;0;{request[3]}\n')
        return f"{last_id}: Utente registado com sucesso com o id:{last_id}!"

def modify_user(request):
    request = request.split(";")
    for r in request:
        if (r=="ERRO"):                             #Verificar se todos os argumentos sao validos
            return "0: Parametros inválidos!"  

    with open(users_filename, 'r') as file:
        data = file.readlines()
    lines = [l.split(";") for l in data]

    if (lines == []):                               #Verificar se a base de dados se encontra vazia
        return "0: Utente não registado!"

    for l in lines:
        if (l[USER_ID]== request[0] and l[USER_ACTIVITY]!="False"):           #Verificar se utente se encontra numa atividade
            return "0: Utente encontra-se numa atividade!"
        elif (l[USER_ID]== request[0] and l[USER_ACTIVITY]=="False"):
            if (request[1]=="1"):       #Alteracao profissao
                l[USER_JOB]=request[2]
                break
            elif (request[1]=="2"):     #Alteracao tempo de permanencia
                l[USER_TIME_REMAINED]=request[2]+"\n"
                break
        elif (l[USER_ID]==lines[-1][0]):            #Verificar se utente se encontra na base de dados
            return "0: Utente não registado!"

    edit_file_user(lines)                           #Modificar perfil
    return "1: Modificação do perfil com sucesso!"

def remove_user(request):
    request = request.split(";")
    for r in request:
        if (r=="ERRO"):                             #Verificar se todos os argumentos sao validos
            return "0: Parametros inválidos!"  

    with open(users_filename, 'r') as file:
        data = file.readlines()
    lines = [l.split(";") for l in data]

    if (lines == []):                               #Verificar se a base de dados se encontra vazia
        return "0: Utente não registado!"

    for l in lines:
        if (l[USER_ID]==request[0] and l[USER_ACTIVITY]=="False"):      #Verificar se utente nao se encontra numa atividade
            l[USER_LOCAL_ID]="False"
            break
        elif (l[USER_ID]==request[0] and l[USER_ACTIVITY]!="False"):    #Verificar se utente se encontra numa atividade
            return "0: Utente encontra-se numa atividade!"
        elif (l[USER_ID]==lines[-1][0]):            #Verificar se utente se encontra na base de dados
            return "0: Utente não registado!"

    edit_file_user(lines)                           #Remover utente do local
    return "1: Utente removido com sucesso!"

def consult_activity():
    with open(users_filename, 'r') as file:
        data_u= file.readlines()
    with open(activities_filename, 'r') as file:
        data_a= file.readlines()
    lines_u = [l.split(";") for l in data_u]
    lines_a = [l.split(":") for l in data_a]
    for l in lines_a:
        if (l[ACTIVITY_STATE]=='False'):
            l[ACTIVITY_STATE]="Fechado"
        elif (l[ACTIVITY_STATE]=='True'):
            l[ACTIVITY_STATE]="Aberto"
    for l in lines_u:
        if (l[USER_ACTIVITY]!=False):
            for l1 in lines_a:                      #Verificar qual a disponibilidade de cada atividade
                if (l1[ACTIVITY_ID]==l[USER_ACTIVITY]):
                    l1[ACTIVITY_CAPACITY]=int(l1[ACTIVITY_CAPACITY])
                    l1[ACTIVITY_CAPACITY]-=1
    text=""
    for l in lines_a:                                                                               
        text+="Id da atividade:{};  Local:{};  Tipo de atividade:{};  Estado:{};  Disponibilidade:{};  Custo:{};\n"\
        .format(l[ACTIVITY_ID], (get_local(l[ACTIVITY_LOCAL],"name"))[LOCAL_ID],\
        l[ACTIVITY_TYPE], l[ACTIVITY_STATE],l[ACTIVITY_CAPACITY],l[ACTIVITY_COST])
    text=text[:-1]
    return text       #PEDIR TODAS AS ATIVIDADES: id,local,tipo,estado,disponibilidade,custo

def ask_for_activity(request):
    request = request.split(";")
    for r in request:
        if (r=="ERRO"):                             #Verificar se todos os argumentos sao validos
            return "0: Parametros inválidos!"  

    with open(activities_filename, 'r') as file:
        activities = file.readlines()
    with open(users_filename, 'r') as file:
        users = file.readlines()

    activities = [l.split(":") for l in activities]
    users = [l.split(";") for l in users]
    if (users == []):
            return "0: Utente não registado!"  
    for l in users:
        if (l[USER_ID]==request[0]):                #Verificar se utente existe
            u=l                                     #u=lista com informacoes sobre o utente escolhido
            break
        if (l[USER_ID]==users[-1][0]):
            return "0: Utente não registado!"  
    if(request[1]!="0" and get_activity(request[1])==[]):
        return "0: Atividade inexistente!"  
        
    for l in users:
        if (l[USER_ACTIVITY]!=False):
            for l1 in activities:                                      #Verificar qual a disponibilidade de cada atividade
                if (l1[ACTIVITY_ID]==l[USER_ACTIVITY]):
                    l1[ACTIVITY_CAPACITY]=int(l1[ACTIVITY_CAPACITY])
                    l1[ACTIVITY_CAPACITY]-=1

    if (request[1] == "0"):                             #Caso a atividade seja randomica
        request[1]=random.randint(0, len(activities))
        for a in range(len(activities)):               
            if (a==request[1]):
                if(activities[a][ACTIVITY_CAPACITY]==0):    
                    return "0,0: Atividade já na lotação máxima!"
                elif (activities[a][ACTIVITY_STATE]==False):    #Verificar se atividade nao esta fechado
                    return "0,0: Atividade encontra-se fechada!"
                for l in users:
                    if (l==u):
                        l[USER_ACTIVITY]=activities[a][ACTIVITY_ID] #Adicionar atividade ao utente
                        break
                edit_file_user(users)              
                return f"{activities[a][ACTIVITY_ID]}, {(activities[a][ACTIVITY_TIME])[:-1]}: Atividade {activities[a][ACTIVITY_ID]} pedida com sucesso durante {(activities[a][ACTIVITY_TIME])[:-1]}!"
    else:                                               #Caso seja uma atividade especifica
        for a in activities:
            if (a[ACTIVITY_ID]==request[1]):
                if (a[ACTIVITY_CAPACITY]==0):           
                    return "0,0: Atividade já na lotação máxima!"
                elif (a[ACTIVITY_STATE]==False):        #Verificar se atividade nao esta fechado         
                    return "0,0: Atividade encontra-se fechada!" 
                for l in users:
                    if (l==u):                      
                        l[USER_ACTIVITY]=request[1]     #Adicionar atividade ao utente
                        break
                edit_file_user(users)               
                return f"{a[ACTIVITY_ID]}, {(a[ACTIVITY_TIME])[:-1]}: Atividade {a[ACTIVITY_ID]} pedida com sucesso durante {(a[ACTIVITY_TIME])[:-1]}!"


def complaint(request):
    text = request
    request = request.split(";")
    for r in request:
        if (r=="ERRO"):                                 #Verificar se todos os argumentos sao validos
            return "0: Parametros inválidos!"

    if (get_local(request[0],'id')==[]):                #Verificar se local existe
        return "0: Local inexistente!"

    if (request[1]=="Atividade"):
        if (get_activity(request[2])==[]):              #Verificar se reclamacao é sobre atividade e se ela existe
            return "0: Atividade inexistente!"

    with open(complaint_filename, 'r') as file:
        data = file.readlines()
    if (data==[]):
        last_id = 1
    else:
        lines = [l.split(";") for l in (data)]          #Verificar o id da reclamacao a adicionar
        for l in lines:
            last_id=int(l[COMPLAINT_ID])
        last_id+=1

    with open(complaint_filename, 'a') as file:         #Adicionar reclamacao
        file.write(f'{last_id};{text}\n')
    return f"{last_id}: Reclamação submetida com sucesso com o id:{last_id}!"

def edit_file_user(data):                                  
    new_data=[]                     
    for l in data:
        new_data.append("{};{};{};{};{};{};{};{}".format(l[0],l[1],l[2],l[3],l[4],l[5],l[6],l[7]))
    with open(users_filename, 'w') as file:
        file.writelines(new_data)

#####################################################################################################################################################
# Seccao feita para os gestores dos locais (Joao Galego)

def service_creation(request):
    request = request.split(";")
    name = request[0]
    local_id = request[1]
    service_type = request[2]
    cobr_price = request[3]

    if(name == "error" or local_id == "error" or service_type == "error" or cobr_price == "error"):
        return "\n0. Tem que inserir todos os parametros!\n"  
    if(local_id == "0"):
        local_name = "LOCAL_GLOBAL"
    elif(get_local(local_id, "id") != []):
        local_name = (get_local(local_id, "id"))[LOCAL_NAME]
    else:
        return "\n0. Local nao registado!\n"
    if(get_local(local_id,"id") != [] or local_id == "0"):
        with open(services_filename, 'r') as file:
            data = file.readlines()
        lines = [l.split(":") for l in data]
        if (lines == []):
            with open(services_filename, 'a') as file:
                file.write('{}:{}:{}:{}:{}:{}\n'.format("1", name, local_id, local_name, service_type, cobr_price))
            return "\nServico criado com sucesso! ID do servico: 1\n"
        for l in lines:
            if (l[1] == name):
                return "\n0. Ja existe um servico com o mesmo nome!"
        with open(services_filename, 'a') as file:
            file.write('{}:{}:{}:{}:{}:{}\n'.format(str(int(lines[-1][0])+1), name, local_id, local_name, service_type, cobr_price))
        return "\nServico criado com sucesso! ID do servico: " + str((int(lines[-1][0]))+1) + "\n"
    return "0. Servico nao criado!"	

    	

def get_local_s(request):
    if(request == "error"):
        return "\nLocal nao encontrado. Parametros em falta!\n"
    if(request != "0"):
        local = get_local(request, "id")
        if(local != []):
            local_id = local[LOCAL_ID]
            local_name = local[LOCAL_NAME]
            local_capacity = local[LOCAL_CAPACITY]
            #local_ranking = local[LOCAL_RANKING]
            return "\nIdentificador do Local:" + local_id + "\nNome do Local:" + local_name + "\n" + "Lotacao:" + local_capacity + "\n"   #FALTA RANKING
        return "0"

    with open(locals_filename, 'r') as file:
        data= file.readlines()
    lines = [l.split(":") for l in data]
    if(lines == []):
        return "Nenhum local registado!\n"
    total = ""
    for l in lines:
        total += "\nIdentificador do Local:" + l[1] + "\nNome do Local:" + l[2] + "\n" + "Lotacao:" + l[3] + "\n"   #FALTA RANKING
    return total

    

def get_complaint(request):
    if(request == "error"):
        return ("\nLocal nao encontrado. Parametros em falta!\n",)
    with open(complaint_filename, 'r') as file:
        data = file.readlines()
    lines = [l.split(";") for l in data]
    total = 0
    for l in lines:
        if(l[1] == request):
            total +=1
    if(total == 0):
        return ()
    with open(users_filename, 'r') as file:
        data = file.readlines()
    lines = [l.split(";") for l in data]
    usr_registed = 0
    for l in lines:
        if(l[2] == request):
            usr_registed += 1
    return total, usr_registed
        

def cobranca(request):
    id_servico = request    
    if(id_servico == "error"):
        return "\nServico nao encontrado. Parametros em falta!\n"
    with open(services_filename, 'r') as file:
        data = file.readlines()
    lines = [l.split(":") for l in data]
    if(lines == []):
    	return "\n0. Nao existe nenhum servico registado!\n"
    check = 0
    for l in lines:
        if(l[0] == id_servico):
            check += 1
            local_id = l[2]
            local_balance = (get_local(local_id, "id"))[LOCAL_BALANCE]
            service_price = l[5]
            if(get_complaint(local_id) == ()):
               complaints = 0
            else:
               complaints = get_complaint(local_id)[0]
            debt = int(complaints) * 5
            if(int(local_balance) - int(debt) - int(service_price)>0):
                novo_saldo = int(local_balance) - int(debt) - int(service_price)
            else:
                return "0"
            break
        else:
            continue
    if(check == 0):
        return "0"
    with open(locals_filename, 'r') as file:
        data = file.readlines()
    lines = [l.split(":") for l in data]
    if(lines == []):
        return 0
    for l in lines:
        if(l[1] == local_id):
            l[LOCAL_BALANCE] = str(novo_saldo) + "\n"
            break
    edit_file_local(lines)
    return "\n1. Cobranca feita com sucesso!\n"

   

               

def edit_file_local(new_data):
    count=0                               

    for l in new_data:
        new_data[count]="{}:{}:{}:{}:{}:{}".format(l[0],l[1],l[2],l[3],l[4],l[5])
        count=count+1
    with open(locals_filename, 'w') as file:
        file.writelines(new_data)

        

def edit_file_service(new_data):

    count=0                                        

    for l in new_data:
        new_data[count]="{}:{}:{}:{}:{}:{}".format(l[0],l[1],l[2],l[3],l[4],l[5])
        count=count+1
    with open(services_filename, 'w') as file:
        file.writelines(new_data)



def service_end(request):

    id_servico = request
    with open(services_filename, 'r') as file:
        data = file.readlines()
    lines = [l.split(":") for l in data]
    if(lines == []):
        return "0"
    for l in lines:
        if(l[0] == id_servico):
            lines.remove(l)
            break
        elif (l[0]==lines[-1][0]):
            return "0"
    edit_file_service(lines)    
    return "1"


####################################################################################################################################################

def process_server_request(request, client_socket, client_addr):
    request = request.split(" ",1)
    command = request[0]
    args = request[1]

    if (command == 'HELLO'):
        return 'Hello fellow server'

    if (command == 'ADD_LOCAL'):
        args = args.split()
        return str(add_local(args))
    if (command == 'GET_LOCAL'):
        args = args.split()
        return str(get_local(args[0], args[1]))
    if (command == 'CANCEL_LOCAL'):
        args = args.split()
        return str(cancel_local(args[0]))
    if (command == 'ADD_ACTIVITY'):
        args = args.split(':')
        return str(add_activity(args))
    if (command == 'MOD_ACTIVITY'):
        args = args.split()
        return str(change_activity_field(args))
    if (command == 'REMOVE_ACTIVITY'):
        args = args.split()
        return str(remove_activity(args[0], args[1]))
    
    if (command == 'REGISTER_USER'):
        return str(register_user(args))
    if (command == 'MODIFY_USER'):
        return str(modify_user(args))
    if (command == 'REMOVE_USER'):
        return str(remove_user(args))
    if (command == 'CONSULT_ACTIVITY'):
        return str(consult_activity())
    if (command == 'ASK_FOR_ACTIVITY'):
        return str(ask_for_activity(args))
    if (command == 'COMPLAINT'):
        return str(complaint(args))
    
    if(command == "SERVICE_CREATION"):
    	return str(service_creation(args))
    if(command == "GET_LOCAL_S"):
    	return str(get_local_s(args))
    if(command == "GET_COMPLAINT"):
    	return str(get_complaint(args))
    if(command == "COBRANCA"):
    	return str(cobranca(args))
    if(command == "SERVICE_END"):
    	return str(service_end(args))

    return 'Unknown command: please try again.'


def tcp_handle_client_connection(client_socket, client_addr):

    while True:
        # Receive command from client
        msg_from_client = client_socket.recv(1024)
        request = msg_from_client.decode()
        
        # Check if request is empty
        if (len(request.split()) == 0 or request == 'QUIT'):
            break

        # Returns command output and sends to client
        msg_to_client = process_server_request(request, client_socket, client_addr) 
        client_socket.send((msg_to_client).encode())

    # Closes connection with client
    msg_to_client = 'Connection terminated.'.encode()
    client_socket.send(msg_to_client)
    client_socket.close()

server_ip = '127.0.0.1'

database_server_port = 9996

# create database socket
database_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
database_server.bind((server_ip, database_server_port))
database_server.listen(100)  # max backlog of connections

inputs = [database_server]

print ('DATABASE: Listening on {}:{}'.format(server_ip, database_server_port))

NULL = ''

USER_ID = 0
USER_NAME = 1
USER_LOCAL_ID = 2
USER_ACTIVITY = 3
USER_JOB = 4
USER_SCORE = 5
USER_BALANCE = 6
USER_TIME_REMAINED = 7

COMPLAINT_ID = 0
COMPLAINT_ID_LOCAL = 1
COMPLAINT_TYPE = 2
COMPLAINT_ID_ACTIVITY = 3
COMPLAINT_DESCRIPTION = 4

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

users_filename = 'users.txt'                                                             
users_lock = threading.Lock()

complaint_filename = 'complaint.txt'
complaint_lock = threading.Lock()

services_filename = 'services.txt'
services_lock = threading.Lock()

active_users_lock = threading.Lock()

filenames = [activities_filename, locals_filename, accounts_filename, users_filename, complaint_filename, services_filename]      
for f in filenames:
    file = open(f, 'a+')                                                                  
    file.close()

try:
    
    while True:
        ins, outs, excs = select(inputs, [], [])
        for socket in ins:
            if (socket == database_server):
                print('message received')
                server_socket, server_addr = database_server.accept()
                print ('Accepted TCP connection from {}:{}'.format(server_addr[0], server_addr[1]))
                database_server_handler = threading.Thread(
                    target=tcp_handle_client_connection,
                    args=(server_socket, server_addr,)  # without comma you'd get a... TypeError: handle_client_connection() argument after * must be a sequence, not _socketobject
                )
                database_server_handler.start()

except (KeyboardInterrupt):
    database_server.close()

finally:
    print("Server terminated.")
