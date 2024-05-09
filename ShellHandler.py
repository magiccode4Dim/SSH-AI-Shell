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

import openai
import requests

#from .utils import detectOperationSystem

#classes de conneccao com os modelos de AI
#aimodels.py
class BaseGenie:
    def __init__(self):
        pass

    def ask(self, wish: str, explain: bool = False):
        raise NotImplementedError

    def post_execute(
        self, wish: str, explain: bool, command: str, description: str, feedback: bool
    ):
        pass


class OpenAIModel(BaseGenie):
    def __init__(self, 
    api_key: str, 
    os_fullname: str, 
    shell: str, 
    kernel_release: str):

        self.os_fullname = os_fullname
        self.shell = shell
        self.kernel_release = kernel_release
        openai.api_key = api_key

    def _build_prompt(self, wish: str, explain: bool = False):
        explain_text = ""
        format_text = "Command: <escreva_o_comando_aqui>"

        if explain:
            explain_text = (
                "Escreva detalhadamente a descrição por detrás do comando que me enviou."
            )
            format_text += "\nDescri: <escreva_a_descrição_do_comando_aqui>\nA descrição do comando deve ser na mesma lingua que o utilizador está usando."
        format_text += "\nNão inclua paretenses, chavetas ou aspas desnecessárias para o comando funcionar."

        prompt_list = [
            f"Intrução: Escreva um comando para o terminal que faz o seguinte: {wish}. Certifique-se de que este comando vai funcionar no sistema {self.os_fullname} com o shell {self.shell} e esta versão do kernel {self.kernel_release}. {explain_text}",
            "Format:",
            format_text,
            "Certifique-se de que o formato da sua resposta seja exatamente essa que eu lhe passei.",
        ]
        prompt = "\n\n".join(prompt_list)
        return prompt

    def ask(self, wish: str, explain: bool = False):
        prompt = self._build_prompt(wish, explain)

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "voçê é um ferramenta de linha de comando, gere comandos de CLI para o utilizador.",
                },
                {"role": "user", "content": prompt},
            ],
            max_tokens=300 if explain else 180,
            temperature=0,
        )
        responses_processed = (
            response["choices"][0]["message"]["content"].strip().split("\n")
        )
        responses_processed = [
            x.strip() for x in responses_processed if len(x.strip()) > 0
        ]
        command = responses_processed[0].replace("Command:", "").strip()

        if command[0] == command[-1] and command[0] in ["'", '"', "`"]:
            command = command[1:-1]

        description = None
        if explain:
            description = responses_processed[1].split("Descri: ")[1]

        return command, description

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
    os_info["backend"]=backend

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

#utils.py
def get_backend(**config: dict):
    backend_name = config["backend"]
    if backend_name == "openai-gpt-3.5-turbo":
        return OpenAIModel(
            api_key=config["openai_api_key"],
            os_fullname=config["description"],
            shell=config["shell"],
            kernel_release=config["kernel_release"]
        )
    else:
        raise ValueError(f"Unknown backend: {backend_name}")


#core.py
def ask(wish,explain,path,config_file_name):
    config_path = Path(path) / config_file_name

    with open(config_path, "r") as f:
        config = json.load(f)

    genie = get_backend(**config)
    try:
        command, description = genie.ask(wish, explain)
    except Exception as e:
        print(f"[red]Error: {e}[/red]")
        return

    print(f"[bold]Command:[/bold] [yellow]{command}[/yellow]")

    if description:
        print(f"[bold]Description:[/bold] {description}")

    execute = Confirm.ask("Voçê quer executar este comando?")
    if execute:
        subprocess.run(command, shell=True)
        feedback = False
        try:
            if config["training-feedback"]:
                feedback = Confirm.ask("O comando funcionou?")
        except KeyError:
            pass
        genie.post_execute(
                wish=wish,
                explain=explain,
                command=command,
                description=description,
                feedback=feedback,
            )


if __name__=="__main__":

   ask("ver a lista dos ficheiros desde directorio",False,"/home/vscode/PythonProjects/CopilotShell","debian.json")
   """
   host ="localhost"
   user="nany"
   passwd="2001"
   sh = ShellHandler(host,user,passwd)
   pwd = ""
   init(sh)
   
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