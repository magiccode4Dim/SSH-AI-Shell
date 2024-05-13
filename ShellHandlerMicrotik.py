import paramiko

# Informações de conexão SSH
hostname = '192.168.180.200'
port = 2223
username = 'admin'
password = '2001'

# Cria uma instância do cliente SSH
ssh_client = paramiko.SSHClient()

# Ignora a verificação de chave host (não é recomendado em produção)
ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    # Conecta ao roteador MikroTik
    ssh_client.connect(hostname, port=port, username=username, password=password,look_for_keys=False)

    print("Conexão SSH estabelecida com sucesso!")

    # Aqui você pode adicionar comandos para serem executados no roteador MikroTik
    # Por exemplo:
    # stdin, stdout, stderr = ssh_client.exec_command('system resource print')
    # for line in stdout:
    #     print(line.strip())

    # Desconecta do roteador MikroTik
    ssh_client.close()

except paramiko.AuthenticationException:
    print("Erro de autenticação. Verifique suas credenciais de login.")
except paramiko.SSHException as e:
    print("Erro ao estabelecer a conexão SSH:", str(e))
except Exception as e:
    print("Erro:", str(e))