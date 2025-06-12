# 🛠️ Scripts de Setup do SynapScale Backend

Este documento explica os scripts de configuração disponíveis no projeto.

## 📋 Resumo

O SynapScale Backend possui dois modos de setup:

1. **Setup Básico** - Configuração manual simples
2. **Setup Completo** - Configuração automatizada e detalhada

## 🔧 Modo Básico

Para iniciar uma configuração básica, execute:

```bash
./setup.sh
```

Este modo:
- Cria um ambiente virtual Python
- Instala dependências do arquivo requirements.txt
- Cria um arquivo .env a partir do .env.example (se não existir)
- Exige configuração manual das variáveis no .env

## ⚙️ Modo Completo

Para uma configuração completa e automatizada, execute:

```bash
./setup.sh --complete
# ou
./setup.sh -c
```

Este modo utiliza o script `setup_complete.py` que:
- Automatiza todo o processo de configuração
- Gera chaves seguras automaticamente
- Cria estrutura de diretórios
- Configura banco de dados
- Oferece um assistente interativo para personalização

## 🤔 Qual escolher?

- **Setup Básico**: Ideal para desenvolvedores que querem controle manual ou para configurações simples.
- **Setup Completo**: Melhor para novos usuários ou para garantir uma configuração correta e completa.

## 📄 Arquivo setup_complete.py

O arquivo `setup_complete.py` é um script Python avançado que automatiza todo o processo de configuração. Ele oferece:

- Validação de ambiente
- Geração segura de chaves
- Configuração de banco de dados
- Verificação de dependências
- Criação de estrutura de diretórios
- Configuração dos arquivos de ambiente

Para executá-lo diretamente:

```bash
python setup_complete.py
```
