from __future__ import print_function
from rich import print as pt
from rich.prompt import Confirm, Prompt
from core import init
from ShellHandler import ShellHandler
from interactive_shell import open_shell



host ="192.168.162.200"
user="admin"
passwd="2001"
port = 2223

#init new devices
sh = ShellHandler(host,user,passwd,int(port))
#sh = None
#init(sh,newdevice=True)

#use shell 

co = Confirm.ask("Deseja fazer a connecção SSH com a máquina?")
if co:
    pt("[yellow]Conectando...[/yellow]") 
    sh = ShellHandler(host,user,passwd,int(port))
    pt(f"[green]Conectado a {host} [/green]")
    ssh_client = sh.getConnection()
    open_shell(ssh_client,"MicrotikRouterOs7","./","microtikrouterOs7.json")
