Para executar o projeto basta correr o ficheiro 'tcp-server-owners' e depois correr o ficheiro
'owner-tcp-client.py' que receberá o input do utilziador.
Pode correr 'owner-tcp-client.py' com um argumento(opcional) que é o nome de um ficheiro
em que cada linha é um comando.

HELP - Lista os comandos disponíveis (resposta varia dependendo se está logge in ou nao)

Inicialmente tem 3 comandos:

HELLO - o servidor responde 'Hello' de volta

IAM <username> - Faz log in com um username já registado. Cada username pode ter apenas um local.

SIGN_UP - É pedido um novo username, password e nome e regista uma nova conta com a qual pode
fazer log in e criar um local.

Só pode modificar ou apagar locais ou atividades registados na conta onde está logged in.

Quando estiver logged in estão disponíveis os seguintes comandos:

REGISTER_LOCAL - Cria um novo local.

CHECK_BALANCE - Obtem o saldo do local

CREATE_ACTIVITY - Cria uma atividade no local.

MOD_ACTIVITY - Modifica a lotação, a pontuação ou o custo de uma atividade.

DELETE_ACTIVITY - Remove atividade do local.

LOGOUT - Faz log out da conta