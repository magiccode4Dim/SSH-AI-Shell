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



   

 
    