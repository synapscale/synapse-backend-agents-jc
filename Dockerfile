# Multi-stage Dockerfile para SynapScale Backend
# Otimizado para produção com segurança e performance

# Stage 1: Build dependencies
FROM python:3.11-slim as builder

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Configurar diretório de trabalho
WORKDIR /app

# Copiar arquivos de dependências
COPY requirements.txt .
COPY requirements-dev.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Stage 2: Production image
FROM python:3.11-slim as production

# Criar usuário não-root para segurança
RUN groupadd -r synapscale && useradd -r -g synapscale synapscale

# Instalar dependências mínimas do sistema
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Configurar diretório de trabalho
WORKDIR /app

# Copiar dependências do stage builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copiar código da aplicação
COPY . .

# Criar diretórios necessários
RUN mkdir -p /app/logs /app/uploads /app/temp && \
    chown -R synapscale:synapscale /app

# Configurar variáveis de ambiente
ENV PYTHONPATH=/app \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONIOENCODING=utf-8 \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

# Expor porta
EXPOSE 8000

# Mudar para usuário não-root
USER synapscale

# Comando de inicialização
CMD ["uvicorn", "src.synapse.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]

