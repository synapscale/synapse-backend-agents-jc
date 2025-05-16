# Projeto Integrado: Agente AI com Editor de Workflow Visual (Canvas)

Este projeto combina um agente de IA vertical com um editor de workflow visual avançado (estilo canvas), documentação técnica e uma interface de chat interativa. O frontend é construído com Next.js 15, React 19, e Tailwind CSS, utilizando múltiplos contextos para gerenciamento de estado. O backend para o chat é uma API Python/Flask.

## Estrutura do Projeto

```
/ai_agents_canvas_integrated
|-- /api                 # Backend Python/Flask para o chat
|   |-- chat.py
|   `-- requirements.txt
|-- /frontend            # Frontend Next.js
|   |-- /app             # Rotas do App Router (canvas, docs, chat)
|   |-- /components      # Componentes React reutilizáveis (incluindo Sidebar, WorkflowEditor, etc.)
|   |-- /context         # Contextos React para gerenciamento de estado do canvas e UI
|   |-- /content/docs    # Arquivos Markdown da documentação
|   |-- /lib             # Funções utilitárias (ex: docs.ts)
|   |-- /public          # Arquivos estáticos
|   |-- package.json
|   |-- next.config.mjs
|   |-- tailwind.config.ts
|   `-- tsconfig.json
|-- .gitignore
|-- vercel.json          # Configuração de deploy para Vercel
`-- README.md            # Este arquivo
```

## Funcionalidades Principais

1.  **Editor de Workflow Visual (Canvas):**
    *   Interface drag-and-drop para criar e conectar nós de workflow.
    *   Painéis para adicionar nós e configurar detalhes de nós selecionados.
    *   Paleta de comandos para acesso rápido a ações.
    *   Zoom, pan, minimapa e atalhos de teclado para navegação eficiente.
    *   Menus de contexto para nós, conexões e o canvas.
    *   Gerenciamento de estado complexo através de múltiplos provedores de contexto React.

2.  **Documentação Técnica:**
    *   Seção `/docs` para visualizar a documentação do projeto e do agente.
    *   Conteúdo carregado a partir de arquivos Markdown.

3.  **Chat Interativo:**
    *   Interface `/chat` para interagir com o backend do agente de IA.
    *   Comunicação com a API Python (`/api/chat`).

## Configuração e Deploy (Vercel)

Este projeto está configurado para ser implantado na Vercel.

1.  **Repositório Git:**
    *   Coloque este projeto em um repositório Git (GitHub, GitLab, etc.).

2.  **Conta na Vercel:**
    *   Acesse sua conta na Vercel.

3.  **Novo Projeto na Vercel:**
    *   Crie um novo projeto e importe o seu repositório Git.

4.  **Configurações do Projeto na Vercel:**
    *   **Root Directory:** Deve ser a raiz do projeto (onde o `vercel.json` está localizado).
    *   **Framework Preset:** A Vercel deve detectar "Next.js" para o frontend. O `vercel.json` cuidará do build da API Python.
    *   O arquivo `vercel.json` incluído no projeto instrui a Vercel sobre como construir o frontend Next.js (da pasta `frontend`) e a API Python (da pasta `api`).

5.  **Variáveis de Ambiente:**
    *   Configure todas as variáveis de ambiente necessárias para o backend do chat (API keys de LLMs, credenciais de Redis, Supabase, etc.) nas configurações do seu projeto na Vercel. Consulte o arquivo `.env.example` do template original do agente para a lista completa de variáveis esperadas.

6.  **Deploy:**
    *   Inicie o processo de deploy através da interface da Vercel.

7.  **Testar:**
    *   Após o deploy, acesse a URL pública fornecida pela Vercel e teste todas as funcionalidades: editor de workflow, documentação e chat.

## Desenvolvimento Local

1.  **Clonar o Repositório (se aplicável).**
2.  **Instalar Dependências do Frontend:**
    ```bash
    cd frontend
    pnpm install # ou npm install / yarn install
    ```
3.  **Instalar Dependências do Backend (API Python):**
    *   Recomenda-se criar um ambiente virtual Python para a pasta `api`.
    ```bash
    cd api
    python -m venv venv
    source venv/bin/activate # ou .\venv\Scripts\activate no Windows
    pip install -r requirements.txt
    ```
4.  **Configurar Variáveis de Ambiente (Local):**
    *   Crie um arquivo `.env.local` na pasta `frontend` para as variáveis de ambiente do Next.js (se houver alguma específica para o frontend).
    *   Para o backend Python, configure as variáveis de ambiente diretamente no seu terminal ou através de um arquivo `.env` na pasta `api` (certifique-se que ele não seja comitado se contiver segredos, use o `.gitignore`).

5.  **Executar o Frontend (Modo de Desenvolvimento):**
    ```bash
    cd frontend
    pnpm dev
    ```
    O frontend estará acessível em `http://localhost:3000` (ou outra porta, se especificada).

6.  **Executar o Backend (API Python - Flask):**
    *   Navegue até a pasta `api`.
    *   Execute o servidor Flask (o `chat.py` provavelmente usa Flask). A forma de executar pode variar, mas geralmente é algo como:
    ```bash
    cd api
    flask --app chat run --port 5001 # Ou python chat.py, dependendo de como está configurado
    ```
    A API estará acessível em `http://localhost:5001` (ou a porta configurada).
    *   **Importante:** O frontend Next.js, por padrão, tentará se comunicar com `/api/chat`. Em desenvolvimento local, você pode precisar configurar um proxy no Next.js (`next.config.mjs`) para redirecionar chamadas `/api/*` para o servidor Flask rodando em `http://localhost:5001/api/*`, ou ajustar as URLs de fetch no frontend para desenvolvimento.

## Considerações

*   **Estrutura de Contextos:** O frontend utiliza múltiplos contextos React para gerenciar o estado do editor de workflow, temas, e outras funcionalidades. A ordem de aninhamento dos provedores em `app/layout.tsx` é importante.
*   **Tailwind CSS:** A estilização é feita primariamente com Tailwind CSS. Consulte `tailwind.config.ts` para configurações de tema e plugins.
*   **Ícones:** `lucide-react` é usado para ícones.

Este README fornece uma visão geral. Consulte o código e os arquivos de configuração para detalhes mais específicos.

