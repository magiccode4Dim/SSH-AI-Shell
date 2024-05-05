import paramiko
import sys
import time

def ssh_connect(hostname, port, username, password):
    try:
        # Cria uma instância do cliente SSH
        client = paramiko.SSHClient()

        # Carrega as chaves do sistema
        client.load_system_host_keys()

        # Aceita automaticamente chaves desconhecidas
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Conecta ao host remoto
        client.connect(hostname, port=port, username=username, password=password)

        print("Conexão SSH estabelecida com sucesso!")

        # Retorna o cliente SSH
        return client

    except paramiko.AuthenticationException:
        print("Falha na autenticação. Verifique as credenciais.")
        sys.exit(1)
    except paramiko.SSHException as e:
        print("Erro na conexão SSH:", str(e))
        sys.exit(1)

def getOutput(channel):
    while True:
        if not channel.recv_ready():
            pass
        else:
            output = channel.recv(1024)
            return output.decode('utf-8')




def interactive_shell(client):
    try:
        # Abre um canal de sessão SSH
        channel = client.invoke_shell()

        print("Conexão SSH aberta. Pressione Enter para abrir o Shell.")

        while True:
            command = input("(AI::)")
            if command.strip() == 'exit':
                break
            # Envia o comando para o servidor remoto
            channel.send(command.strip() + "\n")
            time.sleep(2)
            print(getOutput(channel))
            

    except KeyboardInterrupt:
        print("\nEncerrando conexão SSH...")
    finally:
        # Fecha a conexão SSH
        client.close()

if __name__ == "__main__":
    # Informações de conexão SSH
    hostname = "localhost" #input("Hostname: ")
    port = 22 #int(input("Porta: "))
    username = "nany" #input("Username: ")
    password = "2001" #input("Password: ")

    # Estabelece a conexão SSH
    ssh_client = ssh_connect(hostname, port, username, password)

    # Inicia o terminal interativo
    interactive_shell(ssh_client)