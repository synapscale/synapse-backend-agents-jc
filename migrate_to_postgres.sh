#!/bin/bash

# Atualizar dependências no requirements.txt
sed -i 's/sqlite3/psycopg2-binary/' requirements.txt

# Substituir diretamente as linhas no .env usando echo e redirecionamento
cat <<EOL > .env
DB_ENGINE=postgresql
DB_NAME=seu_banco
DB_USER=seu_usuario
DB_PASSWORD=sua_senha
DB_HOST=localhost
DB_PORT=5432
EOL

# Instalar dependências do PostgreSQL
pip install psycopg2-binary

# Atualizar scripts de inicialização e migração
find . -type f -name "*.py" -exec sed -i 's/sqlite3/psycopg2/g' {} +
find . -type f -name "*.py" -exec sed -i 's/sqlite:///g' {} +

# Mensagem de conclusão
echo "Migração para PostgreSQL concluída. Verifique os arquivos atualizados e reinicie o backend."
