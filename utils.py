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
from aimodels import *

#from .utils import detectOperationSystem
#utils.py
def loading(t=10):
    print("Carregando...", end='', flush=True)
    for _ in range(t):
        print(".", end='', flush=True)
        time.sleep(0.2)  # Aguarda 0.2 segundos entre cada ponto
    print(" Concluído!")

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

