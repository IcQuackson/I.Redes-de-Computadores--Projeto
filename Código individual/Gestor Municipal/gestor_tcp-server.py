
from select import select
import socket, sys
import threading
import random

bind_ip = "127.0.0.1"
client_port = 9993
database_server_port = 9996

cl_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
cl_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
cl_server.bind((bind_ip, client_port))
cl_server.listen(5)

db_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
db_server.connect((bind_ip, database_server_port))

inputs = [cl_server, db_server] 

#return codes
cabecalho = "IdServico;NomeServico;IdLocal;NomeLocal;TipoServico;PrecoCobranca\n"
HELP = "\nLista de operações disponíveis:\n    •Consulta de Locais\n    •Consulta de Reclamacoes\n    •Criacao de Servicos\n    •Cobranca\n    •Terminacao de Servico\n"


#generic functions


def connection_handler():
    while True:
        ins, outs, excs = select(inputs, [], [])
        for socket in ins:
            if(socket == cl_server):
                client_socket, client_address = cl_server.accept()
                print ("Accepted connection from {}:{}".format(client_address[0],   	client_address[1]))
                client_handler = threading.Thread(
                    target=handle_client_connection,
                    args=(client_socket,)  
                )
                client_handler.start()
         
def send_and_receive(msg,socket):
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
    if(request == "Consulta de Locais"):
        return consulta_de_locais(client_socket)
    elif(request == "Consulta de Reclamacoes"):
        return consulta_de_reclamacoes(client_socket)
    elif(request == "Criacao de Servicos"):
        return criacao_de_servicos(client_socket)
    elif(request == "Cobranca"):
        return cobranca(client_socket)
    elif(request == "Terminacao de Servico"):
        return terminacao_de_servico(client_socket)
    elif(request == "Help"):
        return HELP  
    else:
    	return "\nOperação incorreta, para mais destalhes escreva 'Help'."


#outros servidores functions     
#IdLocal;NomeLocal;Lotacao;Tempo_Permanencia;Saldo;Reclamacao;Ranking;Numero_de_Utentes

#Gestor functions

 
def criacao_de_servicos(client_socket):
    nome = pedir_nome(client_socket)
    id_local = pedir_id_local(client_socket)
    tipo_de_servico = pedir_tipo_de_servico(client_socket)
    preco = pedir_preco(client_socket)
    text="{} {};{};{};{}".format("SERVICE_CREATION",nome,id_local,tipo_de_servico,preco)
    r = send_and_receive(text,db_server)
    	#return "\nServico criado com sucesso! ID do servico:{}.\n".format(str(r))
    return r
    
def consulta_de_locais(client_socket):
    id_local = pedir_id_local(client_socket)
    text="{} {}".format("GET_LOCAL_S",id_local)
    r = send_and_receive(text,db_server)
    if(r != "0"):
        return r
    return "\nLocal nao existente, ID_Local errado!\n"

    
def consulta_de_reclamacoes(client_socket):
    id_local = pedir_id_local(client_socket)
    text="{} {}".format("GET_COMPLAINT",id_local)
    r = send_and_receive(text,db_server)
    r = eval(r)
    if(r != () and len(r)!=1):
        return "\nNumero de Reclamacoes: " + str(r[0]) + "\n" "Utentes Registados no Local: "+ str(r[1]) + "\n"
    elif(r != () and len(r) == 1):
    	return r[0]
    return "\nLocal nao registado, ID_Local errado!\n"
    
def terminacao_de_servico(client_socket):
    id_servico = pedir_id_servico(client_socket) 
    text="{} {}".format("SERVICE_END",id_servico)
    r = send_and_receive(text,db_server)
    if(r!="0"):
        return "\n" +r + ". Servico apagado com sucesso!"
    return "\n" +r + ". Erro! Servico nao existente."
    
def cobranca(client_socket):
    id_servico = pedir_id_servico(client_socket)
    #valor = pedir_valor(client_socket)
    text="{} {}".format("COBRANCA", id_servico)
    r = send_and_receive(text,db_server)
    if(r != "0"):
        return r
    return "\n0. Cobranca nao foi feita com sucesso.\n" 

#asking for parameters functions
def pedir_id_local(client_socket):
    client_socket.send(("Local::").encode())
    return (client_socket.recv(1024)).decode()
 
def pedir_nome(client_socket):   
    client_socket.send(("Nome::").encode())
    return (client_socket.recv(1024)).decode()

def pedir_tipo_de_servico(client_socket):
    client_socket.send(("Tipo de Servico::").encode())
    return (client_socket.recv(1024)).decode()

def pedir_preco(client_socket):
    client_socket.send(("Preco::").encode())
    return (client_socket.recv(1024)).decode()
    
def pedir_valor(client_socket):
    client_socket.send(("Valor::").encode())
    return (client_socket.recv(1024)).decode()    
    
def pedir_id_servico(client_socket):
    client_socket.send(("Id Servico::").encode())
    return (client_socket.recv(1024)).decode()


#main code
print ("GESTOR: Listening on {}:{}".format(bind_ip, client_port))

try:
    connection_handler()
except KeyboardInterrupt:
    print("\n")
    cl_server.close()
    
