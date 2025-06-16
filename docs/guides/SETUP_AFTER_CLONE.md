# 🚨 NOTA IMPORTANTE
> Scripts antigos como `auto_setup.sh`, `setup.sh --complete`, etc. não são mais utilizados. Use apenas `dev.sh`, `prod.sh` e `setup.sh` (se existir).

# Configuração Inicial após Clonar o Repositório

Após clonar o repositório SynapScale Backend, siga estes passos para configurar seu ambiente de desenvolvimento:

## 1. Configuração do Ambiente

```bash
rm -rf venv .venv env ENV
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install torch
pip install -r requirements.txt
```

## 2. Configuração das Variáveis de Ambiente

O setup criará um arquivo `.env` baseado no `.env.example`. Certifique-se de configurar:

- Credenciais de banco de dados
- Chaves secretas
- URLs de serviços externos
- Credenciais de API de inteligência artificial (se necessário)

## 3. Estrutura de Diretórios

Alguns diretórios importantes são mantidos vazios no repositório usando `.gitkeep`:

- `storage/` - Armazenamento de arquivos enviados e processados
- `config/environments/` - Configurações específicas de ambiente
- `deployment/production/` - Arquivos de configuração de produção

## 4. Desenvolvimento

Para iniciar o servidor em modo de desenvolvimento:

```bash
./dev.sh
```

Para iniciar em modo de produção:

```bash
./prod.sh
```

## 5. Migrações de Banco de Dados

- Migrações **não são mais automáticas**. Rode manualmente se necessário:
  ```bash
  alembic upgrade head
  ```

## 6. Problemas Comuns

Se enfrentar problemas com a configuração:

1. Verifique se todas as variáveis de ambiente estão configuradas corretamente
2. Consulte a documentação em `docs/` para mais informações

---

Veja a documentação completa em `docs/` para instruções detalhadas.
