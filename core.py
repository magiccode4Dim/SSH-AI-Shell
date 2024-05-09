import re
import json
import os
import subprocess
from pathlib import Path

import pyperclip
import typer
from rich import print
from rich.prompt import Confirm, Prompt
from .ShellHandler import ShellHandler

from .utils import detectOperationSystem
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