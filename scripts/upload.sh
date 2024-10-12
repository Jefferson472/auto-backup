#!/bin/bash

# Carregar variáveis do arquivo .env
if [ -f .env ]; then
    source .env
else
    echo "Arquivo .env não encontrado. O script será interrompido."
    exit 1  # Saída com código de erro 1
fi

source /home/$USUARIO/auto-backup/venv/bin/activate  # Ativa o ambiente virtual

python /home/$USUARIO/auto-backup/upload_files.py  # Executa o script Python dentro do ambiente virtual
