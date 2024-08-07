from __future__ import print_function
from rich import print as pt
from rich.prompt import Confirm, Prompt
from core import init
from ShellHandler import ShellHandler
from interactive_shell import open_shell
import typer
from getpass import getpass

app = typer.Typer(help="Está é uma ferramenta que conecta um  LLM a um terminal de uma máquina remota usando SSH.\n Com o modelo conectado, o usuario pode enviar promps, e as respostas virão sob a forma de comandos Linux\n. Para utilizar, crie primeiro um ficheiro de configuração, onde irá fornecer os dados sobre as caracteristicas da máquina, e depois conecte-se a maquina remota usando o comando 'connect'. Estando conectado, existem 3 modos de operação: \n 'prompt'>shellask - Envia um prompt para a IA e recebe a resposta em comando. \n 'prompt'>shellexplain - A IA deve explicar o que o comando do prompt deve fazer. \n >explainoutput - Explica o output do terminal.")

@app.command()
def newconfig(ssh: bool = typer.Option(False, help="Inicializa um ficheiro de configuração utilizando uma máquina remota.")):
    """
    Cria um novo ficheiro de configuração.
    """
    try:
        if ssh:
            pt("[green]INIT USING SSH----------------[/green]")
            host =Prompt.ask("IP")
            user=Prompt.ask("USER")
            passwd=getpass("PASSWORD: ")
            port = Prompt.ask("PORT")
            sh = ShellHandler(host,user,passwd,int(port))
            init(sh,newdevice=False)
        else:
            pt("[green]INIT MANUALY----------------[/green]")
            init(None,newdevice=True)
    except Exception as e:
        pt(f"[red]{e}[/red]")

@app.command()
def connect(config_file_path:str): 
    """
    Connecta-se a uma máquina via SSH, usando um ficheiro de configuração.
    """
    pt("[green]SSH CONECTION----------------[/green]")
    host =Prompt.ask("IP")
    user=Prompt.ask("USER")
    passwd=getpass("PASSWORD: ")
    port = Prompt.ask("PORT")
    pt("[yellow]Conectando...[/yellow]") 
    try:
        sh = ShellHandler(host,user,passwd,int(port))
        pt(f"[green]Conectado a {host} [/green]")
        ssh_client = sh.getConnection()
        open_shell(ssh_client,f"{host}:{port}",config_file_path)
    except Exception as e:
        pt(f"[red]{e}[/red]")

if __name__ == "__main__":
    app()