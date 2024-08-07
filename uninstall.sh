#!/bin/bash

# Caminho para o script Bash e o diretório bin
BIN_SCRIPT_NAME="ssh_ai_shell"
INSTALL_DIR="/usr/local/bin"
SCRIPT_PATH="$INSTALL_DIR/$BIN_SCRIPT_NAME"

# Remove o script Bash
if [ -f "$SCRIPT_PATH" ]; then
    echo "Removendo $SCRIPT_PATH..."
    sudo rm "$SCRIPT_PATH"
else
    echo "$SCRIPT_PATH não encontrado."
fi

# Desinstala as dependências se o requirements.txt existir
if [ -f "requirements.txt" ]; then
    echo "Desinstalando dependências do requirements.txt..."
    while read -r line; do
        package=$(echo "$line" | awk '{print $1}')
        pip uninstall -y "$package"
    done < requirements.txt
else
    echo "Arquivo requirements.txt não encontrado."
fi

echo "Desinstalação concluída com sucesso!"