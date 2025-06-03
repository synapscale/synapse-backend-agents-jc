# SynapScale Backend 🚀

Backend completo para plataforma de automação e IA com agentes inteligentes, workflows visuais e marketplace integrado.

## 🌟 Funcionalidades

### 🔐 Autenticação & Autorização
- Sistema JWT completo com refresh tokens
- Registro e verificação de email
- Redefinição de senha
- Controle de permissões por roles

### 🤖 Agentes de IA
- Múltiplos provedores LLM (OpenAI, Claude, Gemini, Grok, DeepSeek, Llama)
- Agentes personalizáveis com instruções específicas
- Sistema de ferramentas (tools) extensível
- Configurações avançadas (temperatura, max_tokens, etc.)

### 🔄 Workflows
- Editor visual de workflows
- Execução em tempo real
- Versionamento automático
- Compartilhamento público/privado
- Sistema de categorias e tags

### 🧩 Marketplace de Nodes
- Biblioteca de componentes reutilizáveis
- Sistema de avaliações e downloads
- Categorização por tipo e funcionalidade
- Documentação integrada

### 💬 Conversações
- Chat em tempo real com agentes
- Histórico persistente
- Suporte a anexos
- Metadados de execução (tokens, tempo, etc.)

### 📁 Gerenciamento de Arquivos
- Upload seguro de múltiplos formatos
- Processamento automático
- Armazenamento flexível
- Validação de tipos e tamanhos

### 🌐 WebSockets
- Comunicação em tempo real
- Notificações push
- Status de execução ao vivo
- Sincronização automática

## 🛠️ Tecnologias

- **FastAPI** - Framework web moderno e rápido
- **SQLAlchemy** - ORM para banco de dados
- **Pydantic** - Validação de dados
- **JWT** - Autenticação segura
- **WebSockets** - Comunicação em tempo real
- **Python 3.8+** - Linguagem principal

## 🚀 Instalação Rápida

### 1. Clonar e Instalar
```bash
# Extrair o repositório
unzip synapse-backend.zip
cd synapse-backend

# Instalar dependências
pip install -r requirements.txt
```

### 2. Configurar Ambiente
```bash
# Copiar arquivo de configuração
cp .env.example .env

# Editar configurações necessárias
nano .env
```

### 3. Executar
```bash
# Iniciar servidor
./start.sh

# Ou manualmente
uvicorn src.synapse.main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. Acessar
- **API**: http://localhost:8000
- **Documentação**: http://localhost:8000/docs
- **WebSocket**: ws://localhost:8000/ws

## ⚙️ Configuração

### Variáveis de Ambiente Essenciais

```env
# Segurança
SECRET_KEY=your-super-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here

# Banco de Dados
DATABASE_URL=sqlite:///./synapse.db

# Provedores LLM
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-claude-api-key
GOOGLE_API_KEY=your-gemini-api-key

# CORS
FRONTEND_URL=http://localhost:3000
BACKEND_CORS_ORIGINS=http://localhost:3000

# Email (opcional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

## 📚 Documentação da API

### Endpoints Principais

#### Autenticação
- `POST /api/v1/auth/register` - Registrar usuário
- `POST /api/v1/auth/login` - Login
- `POST /api/v1/auth/refresh` - Renovar token
- `POST /api/v1/auth/logout` - Logout

#### Workflows
- `GET /api/v1/workflows` - Listar workflows
- `POST /api/v1/workflows` - Criar workflow
- `GET /api/v1/workflows/{id}` - Obter workflow
- `PUT /api/v1/workflows/{id}` - Atualizar workflow
- `POST /api/v1/workflows/{id}/execute` - Executar workflow

#### Agentes
- `GET /api/v1/agents` - Listar agentes
- `POST /api/v1/agents` - Criar agente
- `GET /api/v1/agents/{id}` - Obter agente
- `PUT /api/v1/agents/{id}` - Atualizar agente
- `POST /api/v1/agents/{id}/activate` - Ativar agente

#### Conversações
- `GET /api/v1/conversations` - Listar conversações
- `POST /api/v1/conversations` - Criar conversação
- `GET /api/v1/conversations/{id}/messages` - Listar mensagens
- `POST /api/v1/conversations/{id}/messages` - Enviar mensagem

#### Nodes
- `GET /api/v1/nodes` - Listar nodes
- `POST /api/v1/nodes` - Criar node
- `GET /api/v1/nodes/{id}` - Obter node
- `POST /api/v1/nodes/{id}/download` - Baixar node

#### Arquivos
- `POST /api/v1/files/upload` - Upload de arquivo
- `GET /api/v1/files` - Listar arquivos
- `GET /api/v1/files/{id}` - Obter arquivo
- `DELETE /api/v1/files/{id}` - Deletar arquivo

### Documentação Interativa
Acesse http://localhost:8000/docs para documentação completa com Swagger UI.

## 🏗️ Arquitetura

```
src/synapse/
├── api/                    # Endpoints da API
│   ├── v1/
│   │   ├── endpoints/      # Endpoints organizados por funcionalidade
│   │   └── router.py       # Roteador principal
│   └── deps.py            # Dependências (autenticação, etc.)
├── core/                  # Funcionalidades centrais
│   ├── auth/              # Sistema de autenticação
│   ├── email/             # Serviço de email
│   └── websockets/        # WebSocket manager
├── models/                # Modelos SQLAlchemy
├── schemas/               # Schemas Pydantic
├── config.py             # Configurações
├── database.py           # Configuração do banco
└── main.py              # Aplicação principal
```

## 🧪 Testes

```bash
# Executar todos os testes
pytest

# Testes com coverage
pytest --cov=src/synapse

# Testes específicos
pytest tests/unit/
pytest tests/integration/
```

## 🔒 Segurança

- **JWT** com refresh tokens seguros
- **Rate limiting** configurável
- **Validação rigorosa** de entrada
- **CORS** configurado
- **Sanitização** de dados
- **Criptografia** de senhas com bcrypt

## 📈 Performance

- **Async/await** para operações não-bloqueantes
- **Pool de conexões** do banco de dados
- **Cache** opcional com Redis
- **Compressão gzip** automática
- **Paginação** em todas as listagens

## 🚀 Deploy

### Docker (Recomendado)
```bash
# Build da imagem
docker build -t synapse-backend .

# Executar container
docker run -p 8000:8000 synapse-backend
```

### Produção
```bash
# Instalar servidor ASGI
pip install gunicorn uvicorn[standard]

# Executar em produção
gunicorn src.synapse.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo LICENSE para detalhes.

## 🆘 Suporte

- **Documentação**: http://localhost:8000/docs
- **Issues**: Reporte bugs e solicite features
- **Email**: suporte@synapscale.com

---

**Desenvolvido com ❤️ pela equipe SynapScale**
