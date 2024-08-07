from __future__ import print_function
from rich import print as pt
import paramiko
import sys
import os
import subprocess
import select
import socket
import termios
import tty
from core import *

#interative_shell.py
def open_shell(connection, remote_name,config_file_path):
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
        #aquilo que o usuario escreve
        user_input_buffer = ""
        #aquilo que o terminal imprime
        lastoutput = ""

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
                        lastoutput+= decoded_output
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
                            r = ask(instru,False,config_file_path)
                            if r:
                                channel.send("\r\n"+r)
                        except Exception as e:
                            pt(f"\n[red]{e}[/red]")
                            channel.send("\r\n")
                        finally:
                            user_input_buffer = ""
                            lastoutput = ""
                            
                    elif ">shellexplain" in user_input_buffer:
                        try:
                            #Pega a ultima instrucao entre aspas
                            arr = user_input_buffer.split('"')
                            instru = arr[len(arr)-2]
                            #pt(f"\n[yellow]{instru}[/yellow]")
                            r = ask(instru,True,config_file_path)
                            if r:
                                channel.send("\r\n"+r)
                        except Exception as e:
                            pt(f"\n[red]{e}[/red]")
                            channel.send("\r\n")
                        finally:
                            user_input_buffer = ""
                            lastoutput = ""
                            
                    elif ">explainoutput" in user_input_buffer:
                        try:
                            lastoutput = lastoutput.replace(">explainoutput","")
                            #print(f"[{lastoutput}]")
                            explainOut(lastoutput,config_file_path)
                            #o output sera limpo somente quando o codigo for executado com sucesso
                            lastoutput = ""
                        except Exception as e:
                            pt(f"\n[red]{e}[/red]")
                        finally:
                            user_input_buffer = ""
                            channel.send("\r\n")
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
