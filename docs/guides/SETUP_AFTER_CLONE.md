# Configuração Inicial após Clonar o Repositório

Após clonar o repositório SynapScale Backend, siga estes passos para configurar seu ambiente de desenvolvimento:

## 1. Configuração do Ambiente

Execute o script de setup:

```bash
# Setup básico (para desenvolvimento rápido)
./setup.sh

# OU

# Setup completo (automático e detalhado)
./setup.sh --complete
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

## 5. Problemas Comuns

Se enfrentar problemas com a configuração:

1. Verifique se todas as variáveis de ambiente estão configuradas corretamente
2. Execute `python tools/utils/validate_setup.py` para diagnóstico
3. Consulte a documentação em `docs/` para mais informações

---

Veja a documentação completa em `docs/` para instruções detalhadas.
