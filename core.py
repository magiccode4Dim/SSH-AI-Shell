from __future__ import print_function
from rich import print as pt
import re
import json
import os
import subprocess
from pathlib import Path
import pyperclip
import typer
from rich.prompt import Confirm, Prompt
from ShellHandler import ShellHandler
from utils import *

#core.py
def explainOut(promptdata,config_file_path):
    config_path = config_file_path

    with open(config_path, "r") as f:
        config = json.load(f)

    genie = get_backend(**config)
    try:
        description = genie.explainOut(promptdata)
    except Exception as e:
        pt(f"[red]Error: {e}[/red]")
        #traceback.print_exc()
        description = None
    if  description :
        d= description.replace("\n"," ")
        pt(f" [bold]Explanation:[/bold] {d} ")

#core.py
def ask(wish,explain,config_file_path):
    config_path = config_file_path

    with open(config_path, "r") as f:
        config = json.load(f)

    genie = get_backend(**config)
    try:
        command, description = genie.ask(wish, explain)
    except Exception as e:
        pt(f"[red]Error: {e}[/red]")
        #traceback.print_exc()
        command, description = None,None
    if command and description :
        d= description.replace("\n"," ")
        pt(f"[bold] Command:[/bold] [yellow]{command}[/yellow]. [bold]Description:[/bold] {d} ")
    elif command:
        pt(f"[bold] Command:[/bold] [yellow]{command}[/yellow]")

    return command

# core.py
def init(sh, newdevice=False):
    backend = Prompt.ask(
        "Selecione a IA:", choices=["openai-gpt-3.5-turbo","google-gemini"]
    )
    additional_params = {}
    # A escolha de qual modelo usar
    if backend == "openai-gpt-3.5-turbo":
        additional_params["openai_api_key"] = Prompt.ask("Introduza Chave da OpenAI API")
    elif backend == "google-gemini":
        additional_params["gemini_api_key"] = Prompt.ask("Introduza Chave do Google Gemini")
    else:
        pt(
            "[yellow]Backend Invalido.[/yellow]"
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

