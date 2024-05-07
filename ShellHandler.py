import paramiko
import re
import json
import os
import subprocess
from pathlib import Path

import pyperclip
import typer
from rich import print
from rich.prompt import Confirm, Prompt

#from .utils import detectOperationSystem

# utils.py
def detectOperationSystem(sh):
    dados = "".join(sh.execute("uname -a && lsb_release -a")[1])
    info_sistema = {}
    # Dividir os dados em linhas
    linhas = dados.split('\n')
    # Obter informações do kernel
    info_kernel = linhas[0].split(' ', 3)
    info_sistema['hostname'] = info_kernel[1]
    info_sistema['kernel_version'] = info_kernel[2]
    info_sistema['kernel_release'] = info_kernel[3]
    # Obter informações LSB (se disponíveis)
    for linha in linhas:
        if 'Distributor ID' in linha:
            info_lsb = linha.split(':')
            info_sistema['distributor_id'] = info_lsb[1].strip()
        elif 'Description' in linha:
            info_description = linha.split(':')
            info_sistema['description'] = info_description[1].strip()
        elif 'Release' in linha:
            info_release = linha.split(':')
            info_sistema['release'] = info_release[1].strip()
        elif 'Codename' in linha:
            info_codename = linha.split(':')
            info_sistema['codename'] = info_codename[1].strip()
    info_sistema["shell"]="".join(sh.execute("echo $SHELL")[1])
    return info_sistema

#here
class ShellHandler:

    def __init__(self, host, user, psw):
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.connect(host, username=user, password=psw, port=22)

        channel = self.ssh.invoke_shell()
        self.stdin = channel.makefile('wb')
        self.stdout = channel.makefile('r')

    def __del__(self):
        self.ssh.close()
    def execute(self, cmd):
        """

        :param cmd: the command to be executed on the remote computer
        :examples:  execute('ls')
                    execute('finger')
                    execute('cd folder_name')
        """
        cmd = cmd.strip('\n')
        self.stdin.write(cmd + '\n')
        finish = 'end of stdOUT buffer. finished with exit status'
        echo_cmd = 'echo {} $?'.format(finish)
        self.stdin.write(echo_cmd + '\n')
        shin = self.stdin
        self.stdin.flush()

        shout = []
        sherr = []
        exit_status = 0
        for line in self.stdout:
                if str(line).startswith(cmd) or str(line).startswith(echo_cmd):
                    # up for now filled with shell junk from stdin
                    shout = []
                elif str(line).startswith(finish):
                    # our finish command ends with the exit status
                    exit_status = int(str(line).rsplit(maxsplit=1)[1])
                    if exit_status:
                        # stderr is combined with stdout.
                        # thus, swap sherr with shout in a case of failure.
                        sherr = shout
                        shout = []
                    break
                else:
                    # get rid of 'coloring and formatting' special characters
                    shout.append(re.compile(r'(\x9B|\x1B\[)[0-?]*[ -/]*[@-~]').sub('', line).
                                replace('\b', '').replace('\r', ''))

        # first and last lines of shout/sherr contain a prompt
        if shout and echo_cmd in shout[-1]:
                shout.pop()
        if shout and cmd in shout[0]:
                shout.pop(0)
        if sherr and echo_cmd in sherr[-1]:
                sherr.pop()
        if sherr and cmd in sherr[0]:
                sherr.pop(0)

        return shin, shout, sherr

# core.py
def init(sh : ShellHandler):
    backend = Prompt.ask(
        "Selecione a IA:", choices=["openai-gpt-3.5-turbo", "alpaca", "llama3"]
    )
    additional_params = {}

    # A escolha de qual modelo usar
    if backend == "openai-gpt-3.5-turbo":
        additional_params["openai_api_key"] = Prompt.ask("Introduza Chave da OpenAI API")

    if backend == "alpaca":
        print(
            "[red]Ainda em Desenvolvimento[/red]"
        )
        return
    if backend == "llama3":
        print(
            "[red]Ainda em Desenvolvimento[/red]"
        )
        return
    # faz a deteccao de qual linux se trata
    os_info = detectOperationSystem(sh)

    if os_info:
        if not Confirm.ask(f"O seu sistema operativo é {os_info['description']}?"):
            os_info["description"] = Prompt.ask("Qual é o seu sistema operativo e a versão (ex: Ubuntu 22.04)")
    else:
        print(
            "[yellow]Não foi possivel Detectar o sistema operativo.[/yellow]"
        )
        os_info["description"] = Prompt.ask("Qual é o seu sistema operativo e a versão (ex: Ubuntu 22.04)")

    os_info.update(additional_params)
    

    name = Prompt.ask("Introduza o nome do arquivo de configuração (ex: ubuntu22.json)")
    path = Prompt.ask("Introduza o caminho onde do ficheiro de configuração")
    config_path = Path(path) / name

    print("O arquivo de configuração será salvo com as seguintes configurações:")
    print(os_info)

    #config_path.parent.mkdir(parents=True, exist_ok=True)

    if config_path.exists():
        overwrite = Confirm.ask(
            "Este ficheiro de configuração já existe. Pretende reescreve-lo?"
        )
        if not overwrite:
            print("Ficheiro não sobre-escrito.")
            return

    with open(config_path, "w") as f:
        json.dump(os_info, f)

    print(f"[bold green]Ficheiro salvo em {config_path}[/bold green]")


if __name__=="__main__":
   host ="localhost"
   user="nany"
   passwd="2001"
   sh = ShellHandler(host,user,passwd)
   pwd = ""
   init(sh)
   """
   while True:
        command = input(f"{user}@{host}=>{pwd}$ ")
        r = sh.execute(command)
        output= r[1]
        errout = r[2]
        pwd = "".join(sh.execute("pwd")[1])
        if len(output)>0:
            print("".join(output))
        if len(errout)>0:
            print("".join(errout))"""