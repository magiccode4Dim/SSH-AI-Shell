def pp():
    print("aaaa")

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


