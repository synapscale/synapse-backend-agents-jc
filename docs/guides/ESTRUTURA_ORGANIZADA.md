# 📄 GUIA DE ESTRUTURA DO REPOSITÓRIO

## 1. Estrutura Organizada 🗂️

O repositório foi reorganizado para uma estrutura limpa e organizada:

```bash
synapse-backend/
├── 📦 setup/           # Scripts de configuração
│   ├── scripts/        # Scripts automatizados
│   ├── templates/      # Templates de .env
│   └── configs/        # Configurações de setup
├── 🚀 deployment/      # Deploy e produção
│   ├── docker/         # Containerização
│   ├── render/         # Deploy Render.com
│   └── scripts/        # Scripts de deploy
├── 🔧 tools/           # Ferramentas e utilitários
│   ├── testing/        # Scripts de teste
│   ├── database/       # Ferramentas de DB
│   ├── utilities/      # Utilitários diversos
│   └── legacy/         # Scripts antigos
├── ⚙️ config/          # Configurações
│   ├── requirements.txt
│   ├── alembic.ini
│   └── pyproject.toml
├── 📚 docs/            # Documentação
│   ├── guides/         # Guias de uso
│   ├── api/            # Docs da API
│   └── architecture/   # Arquitetura
├── 💻 src/             # Código fonte principal
├── 🧪 tests/           # Testes automatizados
└── 📝 Scripts raiz     # Conveniência
    ├── setup.sh        # Configuração (se existir)
    ├── dev.sh          # Desenvolvimento
    └── prod.sh         # Produção
```

## 2. Scripts de Conveniência na Raiz 🚀

Para facilitar seu dia a dia, os scripts mais importantes estão disponíveis diretamente na raiz:

| Script | Função | Comando |
|--------|--------|---------|
| `setup.sh` | Setup inicial completo | `./setup.sh` |
| `dev.sh` | Desenvolvimento com reload | `./dev.sh` |
| `prod.sh` | Produção otimizada | `./prod.sh` |

## 3. Ferramentas e Utilitários 🔧

Todas as ferramentas foram organizadas por função:

### 3.1 Testes (`tools/testing/`)
- Scripts de teste de diversos componentes
- Diagnósticos do sistema
- Validadores de configuração

### 3.2 Banco de Dados (`tools/database/`)
- Ferramentas de criação/configuração de DB
- Scripts para checar schema
- Utilitários de criação de usuários

### 3.3 Utilitários Gerais (`tools/utilities/`)
- Scripts para mascaramento de env
- Ferramentas de segurança
- Scripts de conveniência

### 3.4 Scripts Legados (`tools/legacy/`)
- Scripts mantidos para compatibilidade
- Arquivo de referência histórica

## 4. Configurações Centralizadas ⚙️

Todas as configurações estão agora em `config/`:

- `requirements.txt` - Dependências do projeto
- `alembic.ini` - Configuração de migrações
- `pyproject.toml` - Configuração do Python

## 5. Fluxo de trabalho completo 🔄

1. **Primeira vez**: Execute `./setup.sh` (se existir) ou siga o guia de setup manual
2. **Desenvolvimento**: Execute `./dev.sh` para servidor com reload
3. **Produção**: Execute `./prod.sh` para servidor otimizado
4. **Configurações**: Edite apenas o `.env` na raiz

---

> Scripts antigos como `auto_setup.sh`, `start_master.sh`, etc. não são mais utilizados.

## 6. Documentação Completa 📚

Toda a documentação está agora organizada em `docs/`:

- **Guias**: Manuais passo-a-passo (`docs/guides/`)
- **API**: Documentação de endpoints (`docs/api/`)
- **Arquitetura**: Estrutura do sistema (`docs/architecture/`)

---

## 7. Benefícios da Nova Estrutura 🌟

1. ✅ **Mais limpa** - Raiz do projeto sem poluição
2. ✅ **Organizada** - Arquivos agrupados por função
3. ✅ **Fácil de usar** - Scripts de conveniência na raiz
4. ✅ **Manutenível** - Estrutura escalável e organizada
5. ✅ **Profissional** - Padrões modernos de organização
