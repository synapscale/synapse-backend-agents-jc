FROM python:3.9-slim

WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Instalar Poetry
RUN pip install --no-cache-dir poetry==1.5.1

# Copiar arquivos de configuração do Poetry
COPY pyproject.toml poetry.lock* ./

# Configurar Poetry para não criar ambiente virtual
RUN poetry config virtualenvs.create false

# Instalar dependências
RUN poetry install --no-dev --no-interaction --no-ansi

# Copiar código-fonte
COPY src/ ./src/
COPY alembic.ini ./
COPY alembic/ ./alembic/
COPY scripts/ ./scripts/

# Criar diretórios necessários
RUN mkdir -p ./storage/image ./storage/video ./storage/audio ./storage/document ./storage/archive

# Expor porta
EXPOSE 8000

# Comando para iniciar a aplicação
CMD ["uvicorn", "src.synapse.main:app", "--host", "0.0.0.0", "--port", "8000"]
