def detectOperationSystem(sh):
    output = "".join(sh.execute("uname -a && lsb_release -a")[1])
    info_sistema = {}
    for linha in output.split('\n'):
        chave, valor = linha.split(':')
        info_sistema[chave.strip()] = valor.strip()
    info_sistema["Shell"]="".join(sh.execute("echo $SHELL")[1])
    return info_sistema
