#!/bin/bash

# Atualizar pip
pip install --upgrade pip

# Instalar dependências ausentes
pip install sqlalchemy pydantic-settings

# Resolver problema com distutils
sudo apt-get update && sudo apt-get install -y python3-distutils

# Aviso de configuração SMTP
cat <<EOL

ATENÇÃO: Configure o SMTP no arquivo de configuração para habilitar notificações por email.
Consulte a documentação para mais detalhes.

EOL

# Reiniciar o backend
bash start.sh
