#interstive shell
from __future__ import print_function
from rich import print as pt
import sys
import select
import socket
import termios
import tty
import traceback
import time

import paramiko
import re
import json
import os
import subprocess
from pathlib import Path



import pyperclip
import typer
from rich.prompt import Confirm, Prompt

import openai
import requests

#from .utils import detectOperationSystem
#utils.py
def loading(t=10):
    print("Carregando...", end='', flush=True)
    for _ in range(t):
        print(".", end='', flush=True)
        time.sleep(0.2)  # Aguarda 0.2 segundos entre cada ponto
    print(" Concluído!")

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
#aimodels.pys
class GeminiModel(BaseGenie):
    def __init__(self, 
    api_key: str, 
    os_fullname: str, 
    shell: str, 
    kernel_release: str):

        self.os_fullname = os_fullname
        self.shell = shell
        self.kernel_release = kernel_release
        self.gemini_api_key = api_key

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
        #,
        API_KEY = self.gemini_api_key
        url = "https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent?key=" + API_KEY

        headers = {
            "Content-Type": "application/json"
        }

        data = {
            "contents": [
                {
                    "role": "system",
                    "parts": [
                        {
                            "text": "voçê é um ferramenta de linha de comando, gere comandos de CLI para o utilizador."
                        }
                    ],
                    "role": "user",
                    "parts": [
                        {
                            "text": prompt
                        }
                    ]
                }
            ]
        }

        response = requests.post(url, headers=headers, json=data, timeout=15)
        data = response.json()
        text_content = data['candidates'][0]['content']['parts'][0]['text']
        ar = text_content.split("\n")
        descri=None
        command=ar[0].split(":")[1]
        if len(ar)>2:
            descri=ar[1].split(":")[1]
        return command,descri

        
#aimodels.pys
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

    def __init__(self, host, user, psw,port,look_for_keys=False):
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.connect(host, username=user, password=psw, port=port,look_for_keys=look_for_keys)

        channel = self.ssh.invoke_shell()
        self.stdin = channel.makefile('wb')
        self.stdout = channel.makefile('r')
    def getConnection(self):
        return self.ssh

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
#core.py
def ask(wish,explain,path,config_file_name):
    config_path = Path(path) / config_file_name

    with open(config_path, "r") as f:
        config = json.load(f)

    genie = get_backend(**config)
    try:
        command, description = genie.ask(wish, explain)
    except Exception as e:
        pt(f"[red]Error: {e}[/red]")
        #traceback.print_exc()
        command, description = None,None
    if command:
        pt(f"[bold] Command:[/bold] [yellow]{command}[/yellow]")

    if description:
        pt(f"[bold]Description:[/bold] {description}")
    return command

    """execute = Confirm.ask("Voçê quer executar este comando?")
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
            )"""


#interative_shell.py
def open_shell(connection, remote_name,confFilePath,confFile):
    # get the current TTY attributes to reapply after
    # the remote shell is closed
    oldtty_attrs = termios.tcgetattr(sys.stdin)
    # invoke_shell with default options is vt100 compatible
    # which is exactly what you want for an OpenSSH imitation
    channel = connection.invoke_shell()

    def resize_pty():
        # resize to match terminal size
        tty_height, tty_width = \
                subprocess.check_output(['stty', 'size']).split()

        # try to resize, and catch it if we fail due to a closed connection
        try:
            channel.resize_pty(width=int(tty_width), height=int(tty_height))
        except paramiko.ssh_exception.SSHException:
            pass

    # wrap the whole thing in a try/finally construct to ensure
    # that exiting code for TTY handling runs
    
    try:
        stdin_fileno = sys.stdin.fileno()
        tty.setraw(stdin_fileno)
        tty.setcbreak(stdin_fileno)

        channel.settimeout(0.0)
        user_input_buffer = ""

        is_alive = True

        while is_alive:
            # resize on every iteration of the main loop
            resize_pty()

            # use a unix select call to wait until the remote shell
            # and stdin are ready for reading
            # this is the block until data is ready
            read_ready, write_ready, exception_list = \
                    select.select([channel, sys.stdin], [], [])

            # if the channel is one of the ready objects, print
            # it out 1024 chars at a time
            if channel in read_ready:
                # try to do a read from the remote end and print to screen
                try:
                    out = channel.recv(1024)

                    # remote close
                    if len(out) == 0:
                        is_alive = False
                    else:
                        decoded_output = out.decode('utf-8')
                        # imprima a string decodificada
                        print(decoded_output, end='')
                        sys.stdout.flush()

                # do nothing on a timeout, as this is an ordinary condition
                except socket.timeout:
                    pass

            # if stdin is ready for reading
            if sys.stdin in read_ready and is_alive:
                # send a single character out at a time
                # this is typically human input, so sending it one character at
                # a time is the only correct action we can take

                char = os.read(stdin_fileno, 1024)

                # Se algum caractere foi lido
                if char:
                    c = char.decode('utf-8')
                    #pt(char)

                    # Se o caractere for Enter (\n)
                    if c == '\n':
                        user_input_buffer = ""
                        channel.send(c)

                    # Se o caractere for Backspace (\x08)
                    elif char == b'\x7f':
                        if user_input_buffer:  # Verifica se a variável não está vazia
                            user_input_buffer = user_input_buffer[:-1]  # Remove o último caractere
                        channel.send(c)

                    # Se o caractere for $
                    elif ">shellask" in user_input_buffer:
                        # Processa o comando até $
                        try:
                            #Pega a ultima instrucao entre aspas
                            arr = user_input_buffer.split('"')
                            instru = arr[len(arr)-2]
                            #pt(f"\n[yellow]{instru}[/yellow]")
                            r = ask(instru,False,confFilePath,confFile)
                            if r:
                                channel.send("\r\n"+r)
                            user_input_buffer = ""
                        except Exception as e:
                            pt(f"\n[red]{e}[/red]")

                    # Adiciona o caractere ao buffer
                    else:
                        user_input_buffer += c

                        # Envia os caracteres para o canal SSH
                        channel.send(c)
                    
                    

        # close down the channel for send/recv
        # this is an explicit call most likely redundant with the operations
        # that caused an exit from the REPL, but unusual exit conditions can
        # cause this to be reached uncalled
        channel.shutdown(2)

    # regardless of errors, restore the TTY to working order
    # upon exit and print that connection is closed
    finally:
        termios.tcsetattr(sys.stdin, termios.TCSAFLUSH, oldtty_attrs)
        print('Paramiko channel to %s closed.' % remote_name)

# core.py
def init(sh, newdevice=False):
    backend = Prompt.ask(
        "Selecione a IA:", choices=["openai-gpt-3.5-turbo", "alpaca", "llama3","google-gemini"]
    )
    additional_params = {}

    # A escolha de qual modelo usar
    if backend == "openai-gpt-3.5-turbo":
        additional_params["openai_api_key"] = Prompt.ask("Introduza Chave da OpenAI API")
    if backend == "google-gemini":
        additional_params["gemini_api_key"] = Prompt.ask("Introduza Chave do Google Gemini")

    if backend == "alpaca":
        pt(
            "[red]Ainda em Desenvolvimento[/red]"
        )
        return
    if backend == "llama3":
        pt(
            "[red]Ainda em Desenvolvimento[/red]"
        )
        return
    # faz a deteccao de qual linux se trata
    if newdevice:
        os_info = None
    else:
        os_info = detectOperationSystem(sh)
    

    if os_info:
        if not Confirm.ask(f"O seu sistema operativo é {os_info['description']}?"):
            os_info["description"] = Prompt.ask("Qual é o seu sistema operativo e a versão (ex: Ubuntu 22.04)")
    else:
        os_info = dict()
        pt(
            "[yellow]Não foi possivel Detectar o sistema operativo.[/yellow]"
        )
        os_info["description"] = Prompt.ask("Qual é o seu sistema operativo e a versão (ex: Ubuntu 22.04)")
        os_info["kernel_release"] = Prompt.ask("Qual é a arquitetura do seu Sistema ? (ex: x86_64 )")
        os_info["shell"] = Prompt.ask("Qual é o seu Shell ? (ex: bash )")
    os_info["backend"]=backend
    os_info.update(additional_params)
    

    name = Prompt.ask("Introduza o nome do arquivo de configuração (ex: ubuntu22.json)")
    path = Prompt.ask("Introduza o caminho onde do ficheiro de configuração")
    config_path = Path(path) / name

    pt("O arquivo de configuração será salvo com as seguintes configurações:")
    pt(os_info)

    #config_path.parent.mkdir(parents=True, exist_ok=True)

    if config_path.exists():
        overwrite = Confirm.ask(
            "Este ficheiro de configuração já existe. Pretende reescreve-lo?"
        )
        if not overwrite:
            pt("Ficheiro não sobre-escrito.")
            return

    with open(config_path, "w") as f:
        json.dump(os_info, f)

    pt(f"[bold green]Ficheiro salvo em {config_path}[/bold green]")

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
    if backend_name == "google-gemini":
        return GeminiModel(
            api_key=config["gemini_api_key"],
            os_fullname=config["description"],
            shell=config["shell"],
            kernel_release=config["kernel_release"]
        )
    else:
        raise ValueError(f"Unknown backend: {backend_name}")

#



if __name__=="__main__":
   #host = Prompt.ask("Introduza o Ip  ")
   #user = Prompt.ask("Introduza o utilizador  ")
   #passwd = Prompt.ask("Introduza a Senha  ")
   #port = Prompt.ask("Introduza a Porta  ")
   #
   host ="192.168.154.200"
   user="admin"
   passwd="2001"
   port = 2223
   #r = ask("liste os ficheiros desde directorio",False,"/home/vscode/PythonProjects/CopilotShell","debianlocal.json",sh)
   #print(r)
   #init(None,newdevice=True)
   
   co = Confirm.ask("Deseja fazer a connecção SSH com a máquina?")
   if co:
    pt("[yellow]Conectando...[/yellow]") 
    sh = ShellHandler(host,user,passwd,int(port))
    pt(f"[green]Conectado a {host} [/green]")
    #r = ask("liste os ficheiros desde directorio",False,"/home/vscode/PythonProjects/CopilotShell","microtik.json")
    #print(r)
    #print(sh.execute(r))
    ssh_client = sh.getConnection()
    open_shell(ssh_client,"Ssh Server","/home/vscode/PythonProjects/CopilotShell","microtik.json")
 
    