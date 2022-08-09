
from select import select
import socket, sys
import threading
import ast

bind_ip = "127.0.0.1"
client_port = 9992
database_server_port = 9996

client_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
client_server.bind((bind_ip, client_port))
client_server.listen(5)  # max backlog of connections

database_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

inputs=[client_server, database_server]

#return codes
cabecalho = "IdPessoa;NomePessoa;NomeLocal;Atividade;Profissao;Pontuacao;Saldo;Tempo_Permanencia\n"
HELP = "Lista de operações disponíveis:\n    •Registar utente\n    •Modificar perfil\n    •Remover utente\n    •Consultar atividades\n    •Pedir atividade\n    •Reclamação\n    •Quit\n"


def connection_handler():
    while True:
        ins, outs, excs = select(inputs, [], [])
        for socket in ins:
            if (socket == client_server):
                client_socket, client_addr = client_server.accept()
                print ('Accepted TCP connection from {}:{}'.format(client_addr[0], client_addr[1]))
                client_handler = threading.Thread(
                    target=handle_client_connection,
                    args=(client_socket,)  # without comma you'd get a... TypeError: handle_client_connection() argument after * must be a sequence, not _socketobject
                )
                client_handler.start()


def send_and_recv(msg, socket):
    socket.send(msg.encode())
    return socket.recv(1024).decode()

def handle_client_connection(client_socket):
    while True:
        msg_from_client = client_socket.recv(1024)
        request = msg_from_client.decode()
        if (request=="Quit"):
            print ("Closed connection from {}:{}".format((client_socket.getpeername())[0], (client_socket.getpeername())[1]))
            client_socket.send("Quit".encode())
            client_socket.close()
            break
        #print ('Received {}'.format(request))
        msg_to_client=(check_fuctions(request,client_socket)).encode()
        #print (msg_to_client)
        client_socket.send(msg_to_client)

def check_fuctions(request,client_socket):
    if(request == "Registar utente"):
        return registar_utente(client_socket)
    elif(request == "Modificar perfil"):
        return modificar_perfil(client_socket)
    elif(request == "Remover utente"):
        return remover_utente(client_socket)
    elif(request == "Consultar atividades"):
        return consultar_atividades(client_socket)
    elif(request == "Pedir atividade"):
        return pedir_atividade(client_socket)
    elif(request == "Reclamação"):
        return reclamacao(client_socket)
    elif(request == "Help"):
        return HELP
    else:
    	return "Operação incorreta, para mais destalhes escreva 'Help'.\n"


#cidadao functions
def registar_utente(client_socket):
    id_local = pedir_id_local(client_socket)
    nome = pedir_nome(client_socket)
    profissao = pedir_profissao(client_socket)
    tempo_permanencia = pedir_tempo_permanencia(client_socket)

    text="{} {};{};{};{}".format("REGISTER_USER",id_local,nome,profissao,tempo_permanencia)

    r=send_and_recv(text,database_server)
    return f"{r}\n"

def modificar_perfil(client_socket):
    client_socket.send(("Pretende editar:\n1)Profissão\n2)Tempo de permanência\n:").encode())
    opcao = (client_socket.recv(1024)).decode()
    id_utente = pedir_id_utente(client_socket)
    if (opcao=="1"):
        alteracao = pedir_profissao(client_socket)
    elif (opcao=="2"):
        alteracao = pedir_tempo_permanencia(client_socket)

    if (opcao=="1" or opcao=="2"):
        text="{} {};{};{}".format("MODIFY_USER",id_utente,opcao,alteracao)
        r = send_and_recv(text,database_server)
        return f"{r}\n"
    else:
        return "Opção selecionada incorreta!\n"

def remover_utente(client_socket):
    id_utente = pedir_id_utente(client_socket)
    text="{} {}".format("REMOVE_USER",id_utente)
    r = send_and_recv(text,database_server)
    return f"{r}\n"

def consultar_atividades(client_socket):
    text = "{} {}".format("CONSULT_ACTIVITY", 0)
    r = send_and_recv(text,database_server)
    return f"{r}\n"

def pedir_atividade(client_socket):
    id_utente = pedir_id_utente(client_socket)
    id_atividade = pedir_id_atividade(client_socket)
    text="{} {};{}".format("ASK_FOR_ACTIVITY",id_utente,id_atividade)
    r = send_and_recv(text,database_server)
    return f"{r}\n"

def reclamacao(client_socket):
    client_socket.send(("Pretende submeter uma reclamação sobre:\n1)Local\n2)Atividade\n:").encode())
    opcao = (client_socket.recv(1024)).decode()

    id_local = pedir_id_local(client_socket)
    id_atividade = 0
    if (opcao=="1"):
        tipo = "Local"
    elif(opcao=="2"):
        tipo = "Atividade"
        id_atividade = pedir_id_atividade(client_socket)
    descricao = pedir_descricao(client_socket)

    if ((opcao=="1" or opcao=="2")):
        text="{} {};{};{};{}".format("COMPLAINT", id_local, tipo, id_atividade, descricao)
        r = send_and_recv(text, database_server)
        return f"{r}\n"
    return "Opção selecionada incorreta!\n"


#asking for parameters functions
def pedir_id_local(client_socket):
    client_socket.send(("Local::").encode())
    return (client_socket.recv(1024)).decode()

def pedir_nome(client_socket):
    client_socket.send(("Nome::").encode())
    return (client_socket.recv(1024)).decode()

def pedir_profissao(client_socket):
    client_socket.send(("Profissão::").encode())
    return (client_socket.recv(1024)).decode()

def pedir_tempo_permanencia(client_socket):
    client_socket.send(("Tempo de permanência::").encode())
    return (client_socket.recv(1024)).decode()

def pedir_id_utente(client_socket):
    client_socket.send(("Id do utente::").encode())
    return (client_socket.recv(1024)).decode()

def pedir_id_atividade(client_socket):
    client_socket.send(("Id da atividade::").encode())
    return (client_socket.recv(1024)).decode()

def pedir_descricao(client_socket):
    client_socket.send(("Descrição da reclamação::").encode())
    return (client_socket.recv(1024)).decode()


#main code
try:
    database_server.connect((bind_ip, database_server_port))
except ConnectionRefusedError:
    print("The database is closed!")
    exit()
print("CIDADAO\nWaiting for connections from users.")
try:
    connection_handler()
except KeyboardInterrupt:
    print("\n")
    client_server.close()

