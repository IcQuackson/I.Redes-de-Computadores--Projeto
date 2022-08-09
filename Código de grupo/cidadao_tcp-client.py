import socket

server_ip = "127.0.0.1"
server_port = 9992
input_type = 1


# create an ipv4 (AF_INET) socket object using the tcp protocol (SOCK_STREAM)
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# connect the client
# client.connect((target, port))
try:
    client.connect((server_ip, server_port))
except ConnectionRefusedError:
    print("O servidor encontra-se fechado!")
    exit()
# msg = 'GET /index.html HTTP/1.1\r\nHost: {}.{}\r\n\r\n'.format(sld, tld)

try:
    while True:
      if(input_type):
          user_msg = input("Operação do Utente: ")
      elif not (input_type):
          user_msg = input(msg_from_client)
      if(user_msg==""):
          user_msg="ERRO"
      msg_to_send = user_msg.encode()	
      # send some data (in this case a HTTP GET request)
      #client.send('GET /index.html HTTP/1.1\r\nHost: {}.{}\r\n\r\n'.format(sld, tld))
      client.send(msg_to_send)
      # receive the response data (4096 is recommended buffer size)
      response = client.recv(4096)
      msg_from_client=response.decode()
      if(msg_from_client=="Quit"):
          client.close()
          break
      elif(msg_from_client[-1]==":"):
          msg_from_client = msg_from_client[:-1]
          input_type = 0
      else:
          input_type = 1
          print (msg_from_client)
except KeyboardInterrupt:
    print("\n")
    user_msg = "Quit"
    msg_to_send = user_msg.encode()	
    client.send(msg_to_send)
    response = client.recv(4096)
    client.close()
