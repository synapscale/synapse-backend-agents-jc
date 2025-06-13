# Guia de Deploy no Render - SynapScale Backend

## Problema Identificado

O erro `ModuleNotFoundError: No module named 'synapse'` ocorre porque o Render não está configurando corretamente o PYTHONPATH para incluir o diretório `src` onde estão os módulos Python.

## Soluções Implementadas

### 1. Script de Configuração Atualizado (`setup_render.sh`)

```bash
# Configurar PYTHONPATH para incluir o diretório src
export PYTHONPATH="/opt/render/project/src:$PYTHONPATH"
```

### 2. Script de Inicialização Específico (`start_render.sh`)

- Configura PYTHONPATH corretamente
- Muda para o diretório src antes de iniciar
- Executa verificações de importação
- Inicia o servidor com o caminho correto

### 3. Configuração do render.yaml

- Utiliza o script `start_render.sh` específico
- Configura permissões corretas
- Define variáveis de ambiente necessárias

### 4. Script de Teste (`test_imports.py`)

- Verifica todas as importações críticas
- Executa durante o build para detectar problemas cedo
- Fornece feedback detalhado sobre falhas

## Estrutura de Arquivos para Render

```
deployment/render/
├── setup_render.sh      # Configuração inicial
├── start_render.sh      # Script de inicialização
├── test_imports.py      # Teste de importações
├── .env.render         # Variáveis específicas do Render
└── render.yaml         # Configuração do serviço
```

## Comandos de Deploy

### Build Command
```bash
pip install --upgrade pip
pip install -r requirements.txt
chmod +x deployment/render/setup_render.sh
chmod +x deployment/render/start_render.sh
./deployment/render/setup_render.sh
```

### Start Command
```bash
./deployment/render/start_render.sh
```

## Variáveis de Ambiente Obrigatórias

- `SECRET_KEY` - Chave secreta da aplicação
- `JWT_SECRET_KEY` - Chave para JWT
- `DATABASE_URL` - URL do banco de dados
- `PORT` - Porta do servidor (gerada automaticamente pelo Render)

## Verificação de Problemas

### Teste Local
Execute o teste de importações localmente:
```bash
python deployment/render/test_imports.py
```

### Logs do Render
Verifique os logs para:
1. Configuração do PYTHONPATH
2. Execução dos testes de importação
3. Inicialização do servidor

## Troubleshooting

### Se ainda houver erro de importação:
1. Verifique se todos os arquivos `__init__.py` existem
2. Confirme a estrutura de diretórios no Render
3. Verifique se o PYTHONPATH está sendo configurado corretamente

### Comando de debug no Render:
```bash
echo $PYTHONPATH
ls -la /opt/render/project/src/
python -c "import sys; print(sys.path)"
```

## Próximos Passos

1. Fazer novo deploy no Render
2. Verificar logs de build e startup
3. Testar endpoints da API
4. Monitorar performance e logs
