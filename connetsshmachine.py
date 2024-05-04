import paramiko
import sys

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

def interactive_shell(client):
    try:
        # Abre um canal de sessão SSH
        channel = client.invoke_shell()

        print("Conexão SSH aberta. Pressione Ctrl+D para sair.")

        while True:
            # Recebe a entrada do usuário
            command = input("$ ")

            if command.strip() == 'exit':
                break

            # Envia o comando para o servidor remoto
            channel.send(command.strip() + "\n")

            # Recebe a saída do comando
            while not channel.recv_ready():
                pass
            output = channel.recv(1024).decode()

            # Imprime a saída
            print(output, end='')

    except KeyboardInterrupt:
        print("\nEncerrando conexão SSH...")
    finally:
        # Fecha a conexão SSH
        client.close()

if __name__ == "__main__":
    # Informações de conexão SSH
    hostname = input("Hostname: ")
    port = int(input("Porta: "))
    username = input("Username: ")
    password = input("Password: ")

    # Estabelece a conexão SSH
    ssh_client = ssh_connect(hostname, port, username, password)

    # Inicia o terminal interativo
    interactive_shell(ssh_client)