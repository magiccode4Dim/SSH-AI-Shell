#!/bin/bash

# Verifica se Python e pip estão instalados
check_command() {
    if ! command -v "$1" &> /dev/null; then
        echo "$1 não está instalado. Instale e volte a tentar."
        exit 1
    fi
}

# Função para verificar a presença de um comando
check_command python3
check_command pip

if [ -f "requirements.txt" ]; then
    echo "Instalando dependências..."
    pip install -r requirements.txt
else
    echo "Arquivo requirements.txt não encontrado."
    exit 1
fi

# Cria o diretório bin se não existir
INSTALL_DIR="/usr/local/bin"
if [ ! -d "$INSTALL_DIR" ]; then
    echo "Criando diretório $INSTALL_DIR..."
    sudo mkdir -p "$INSTALL_DIR"
fi

# Caminho para o script Python e o script Bash
SCRIPT_NAME="ssh_ai_shell.sh"
PYTHON_SCRIPT="main.py"
BIN_SCRIPT_PATH="$INSTALL_DIR/ssh_ai_shell"

# Verifica se o script Python existe
if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo "O script $PYTHON_SCRIPT não foi encontrado no diretório atual."
    exit 1
fi

# Verifica se o script Bash existe
if [ ! -f "$SCRIPT_NAME" ]; then
    echo "O script $SCRIPT_NAME não foi encontrado no diretório atual."
    exit 1
fi

# Cria um script Bash que aponta para o código Python
echo "Install script on $INSTALL_DIR..."
sudo ln -sf "$(realpath "$SCRIPT_NAME")" "$BIN_SCRIPT_PATH"

# Torna o script Bash executável
sudo chmod +x "$BIN_SCRIPT_PATH"

echo "Instalação concluída com sucesso!"