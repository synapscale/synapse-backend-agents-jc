# Relatório Detalhado de Testes de Endpoints - SynapScale API

**Data do teste:** 2025-07-07
**Usuário:** joaovictor@liderimobiliaria.com.br
**Script:** tests/integration/test_endpoints_comprehensive.py
**Backend:** FastAPI (src/synapse/main.py)
**JSON de resultados:** `/reports/testing/synapscale_api_test_report_20250707_181628.json`

---

## Resumo Executivo
- **Total de endpoints testados:** 220
- **Sucesso:** 132
- **Falha:** 88
- **Taxa de sucesso:** 60%
- **Principais códigos:** 200, 400, 403, 404, 422
- **Tempo médio de resposta:** (ver JSON)
- **Tempo máximo:** (ver JSON)

---

## Tabela Detalhada de Resultados

| # | Método | Endpoint | Status | Código | Tempo (s) | Categoria | Motivo do Erro | Observação |
|---|--------|----------|--------|--------|-----------|-----------|----------------|------------|
| 1 | GET | /health | Sucesso | 200 | 0.56 | system |  |  |
| 2 | GET | /health/detailed | Sucesso | 200 | 0.82 | system |  |  |
| 3 | GET | / | Sucesso | 200 | 0.00 | system |  |  |
| 4 | GET | /info | Sucesso | 200 | 0.00 | system |  |  |
| 5 | POST | /current-url | Sucesso | 200 | 0.00 | system |  |  |
| 6 | GET | /.identity | Sucesso | 200 | 0.00 | system |  |  |
| 7 | POST | /api/v1/auth/docs-login | Falha | 401 | 0.00 | authentication | Unauthorized | Endpoint requer autenticação válida. |
| 8 | POST | /api/v1/auth/register | Falha | 422 | 0.00 | authentication | Validation Error | Payload inválido ou campos obrigatórios ausentes. |
| 9 | POST | /api/v1/auth/login | Sucesso | 200 | 0.12 | authentication |  |  |
| 10 | POST | /api/v1/auth/refresh | Falha | 401 | 0.00 | authentication | Unauthorized | Token de refresh inválido ou ausente. |
| 11 | POST | /api/v1/auth/forgot-password | Sucesso | 200 | 0.00 | authentication |  |  |
| 12 | POST | /api/v1/auth/reset-password | Falha | 422 | 0.00 | authentication | Validation Error | Payload inválido ou token de reset ausente. |
| 13 | GET | /api/v1/users/me | Sucesso | 200 | 0.10 | users |  |  |
| 14 | GET | /api/v1/users | Falha | 403 | 0.00 | users | Forbidden | Permissão insuficiente para listar usuários. |
| 15 | POST | /api/v1/users | Falha | 403 | 0.00 | users | Forbidden | Permissão insuficiente para criar usuário. |
| 16 | GET | /api/v1/users/1 | Sucesso | 200 | 0.09 | users |  |  |
| 17 | PUT | /api/v1/users/1 | Falha | 403 | 0.00 | users | Forbidden | Permissão insuficiente para atualizar usuário. |
| 18 | DELETE | /api/v1/users/1 | Falha | 403 | 0.00 | users | Forbidden | Permissão insuficiente para deletar usuário. |
| 19 | GET | /api/v1/workspaces | Sucesso | 200 | 0.13 | workspaces |  |  |
| 20 | POST | /api/v1/workspaces | Sucesso | 201 | 0.15 | workspaces |  |  |
| 21 | GET | /api/v1/workspaces/1 | Sucesso | 200 | 0.11 | workspaces |  |  |
| 22 | PUT | /api/v1/workspaces/1 | Falha | 400 | 0.00 | workspaces | Validation Error | Payload inválido ou campos obrigatórios ausentes. |
| 23 | DELETE | /api/v1/workspaces/1 | Falha | 403 | 0.00 | workspaces | Forbidden | Permissão insuficiente para deletar workspace. |
| 24 | GET | /api/v1/workspaces/9999 | Falha | 404 | 0.00 | workspaces | Not Found | Workspace não encontrado (ID inexistente). |
| 25 | GET | /api/v1/workspace-members | Sucesso | 200 | 0.12 | workspace_members |  |  |
| 26 | POST | /api/v1/workspace-members | Falha | 422 | 0.00 | workspace_members | Validation Error | Payload inválido ou campos obrigatórios ausentes. |
| 27 | GET | /api/v1/workspace-members/1 | Sucesso | 200 | 0.09 | workspace_members |  |  |
| 28 | PUT | /api/v1/workspace-members/1 | Falha | 403 | 0.00 | workspace_members | Forbidden | Permissão insuficiente para atualizar membro. |
| 29 | DELETE | /api/v1/workspace-members/1 | Falha | 403 | 0.00 | workspace_members | Forbidden | Permissão insuficiente para deletar membro. |
| 30 | GET | /api/v1/workspace-members/9999 | Falha | 404 | 0.00 | workspace_members | Not Found | Membro não encontrado (ID inexistente). |
| 31 | GET | /api/v1/workflows | Sucesso | 200 | 0.14 | workflows |  |  |
| 32 | POST | /api/v1/workflows | Falha | 422 | 0.00 | workflows | Validation Error | Payload inválido ou campos obrigatórios ausentes. |
| 33 | GET | /api/v1/workflows/1 | Sucesso | 200 | 0.10 | workflows |  |  |
| 34 | PUT | /api/v1/workflows/1 | Falha | 403 | 0.00 | workflows | Forbidden | Permissão insuficiente para atualizar workflow. |
| 35 | DELETE | /api/v1/workflows/1 | Falha | 403 | 0.00 | workflows | Forbidden | Permissão insuficiente para deletar workflow. |
| 36 | GET | /api/v1/workflows/9999 | Falha | 404 | 0.00 | workflows | Not Found | Workflow não encontrado (ID inexistente). |
| 37 | GET | /api/v1/workflow-executions | Sucesso | 200 | 0.13 | workflow_executions |  |  |
| 38 | POST | /api/v1/workflow-executions | Falha | 422 | 0.00 | workflow_executions | Validation Error | Payload inválido ou campos obrigatórios ausentes. |
| 39 | GET | /api/v1/workflow-executions/1 | Sucesso | 200 | 0.11 | workflow_executions |  |  |
| 40 | PUT | /api/v1/workflow-executions/1 | Falha | 403 | 0.00 | workflow_executions | Forbidden | Permissão insuficiente para atualizar execução. |
| 41 | DELETE | /api/v1/workflow-executions/1 | Falha | 403 | 0.00 | workflow_executions | Forbidden | Permissão insuficiente para deletar execução. |
| 42 | GET | /api/v1/workflow-executions/9999 | Falha | 404 | 0.00 | workflow_executions | Not Found | Execução não encontrada (ID inexistente). |
| 43 | GET | /api/v1/user-variables | Sucesso | 200 | 0.12 | user_variables |  |  |
| 44 | POST | /api/v1/user-variables | Falha | 422 | 0.00 | user_variables | Validation Error | Payload inválido ou campos obrigatórios ausentes. |
| 45 | GET | /api/v1/user-variables/1 | Sucesso | 200 | 0.09 | user_variables |  |  |
| 46 | PUT | /api/v1/user-variables/1 | Falha | 403 | 0.00 | user_variables | Forbidden | Permissão insuficiente para atualizar variável. |
| 47 | DELETE | /api/v1/user-variables/1 | Falha | 403 | 0.00 | user_variables | Forbidden | Permissão insuficiente para deletar variável. |
| 48 | GET | /api/v1/user-variables/9999 | Falha | 404 | 0.00 | user_variables | Not Found | Variável não encontrada (ID inexistente). |
| 49 | GET | /api/v1/node-templates | Sucesso | 200 | 0.13 | node_templates |  |  |
| 50 | POST | /api/v1/node-templates | Falha | 422 | 0.00 | node_templates | Validation Error | Payload inválido ou campos obrigatórios ausentes. |
| 51 | GET | /api/v1/node-templates/1 | Sucesso | 200 | 0.10 | node_templates |  |  |
| 52 | PUT | /api/v1/node-templates/1 | Falha | 403 | 0.00 | node_templates | Forbidden | Permissão insuficiente para atualizar template. |
| 53 | DELETE | /api/v1/node-templates/1 | Falha | 403 | 0.00 | node_templates | Forbidden | Permissão insuficiente para deletar template. |
| 54 | GET | /api/v1/node-templates/9999 | Falha | 404 | 0.00 | node_templates | Not Found | Template não encontrado (ID inexistente). |
| 55 | GET | /api/v1/workflow-connections | Sucesso | 200 | 0.12 | workflow_connections |  |  |
| 56 | POST | /api/v1/workflow-connections | Falha | 422 | 0.00 | workflow_connections | Validation Error | Payload inválido ou campos obrigatórios ausentes. |
| 57 | GET | /api/v1/workflow-connections/1 | Sucesso | 200 | 0.09 | workflow_connections |  |  |
| 58 | PUT | /api/v1/workflow-connections/1 | Falha | 403 | 0.00 | workflow_connections | Forbidden | Permissão insuficiente para atualizar conexão. |
| 59 | DELETE | /api/v1/workflow-connections/1 | Falha | 403 | 0.00 | workflow_connections | Forbidden | Permissão insuficiente para deletar conexão. |
| 60 | GET | /api/v1/workflow-connections/9999 | Falha | 404 | 0.00 | workflow_connections | Not Found | Conexão não encontrada (ID inexistente). |
| 61 | GET | /api/v1/nodes | Sucesso | 200 | 0.14 | nodes |  |  |
| 62 | POST | /api/v1/nodes | Falha | 422 | 0.00 | nodes | Validation Error | Payload inválido ou campos obrigatórios ausentes. |
| 63 | GET | /api/v1/nodes/1 | Sucesso | 200 | 0.10 | nodes |  |  |
| 64 | PUT | /api/v1/nodes/1 | Falha | 403 | 0.00 | nodes | Forbidden | Permissão insuficiente para atualizar node. |
| 65 | DELETE | /api/v1/nodes/1 | Falha | 403 | 0.00 | nodes | Forbidden | Permissão insuficiente para deletar node. |
| 66 | GET | /api/v1/nodes/9999 | Falha | 404 | 0.00 | nodes | Not Found | Node não encontrado (ID inexistente). |
| 67 | GET | /api/v1/node-ratings | Sucesso | 200 | 0.13 | node_ratings |  |  |
| 68 | POST | /api/v1/node-ratings | Falha | 422 | 0.00 | node_ratings | Validation Error | Payload inválido ou campos obrigatórios ausentes. |
| 69 | GET | /api/v1/node-ratings/1 | Sucesso | 200 | 0.09 | node_ratings |  |  |
| 70 | PUT | /api/v1/node-ratings/1 | Falha | 403 | 0.00 | node_ratings | Forbidden | Permissão insuficiente para atualizar avaliação. |
| 71 | DELETE | /api/v1/node-ratings/1 | Falha | 403 | 0.00 | node_ratings | Forbidden | Permissão insuficiente para deletar avaliação. |
| 72 | GET | /api/v1/node-ratings/9999 | Falha | 404 | 0.00 | node_ratings | Not Found | Avaliação não encontrada (ID inexistente). |
| 73 | GET | /api/v1/analytics | Sucesso | 200 | 0.12 | analytics |  |  |
| 74 | POST | /api/v1/analytics | Falha | 422 | 0.00 | analytics | Validation Error | Payload inválido ou campos obrigatórios ausentes. |
| 75 | GET | /api/v1/analytics/1 | Sucesso | 200 | 0.09 | analytics |  |  |
| 76 | PUT | /api/v1/analytics/1 | Falha | 403 | 0.00 | analytics | Forbidden | Permissão insuficiente para atualizar analytics. |
| 77 | DELETE | /api/v1/analytics/1 | Falha | 403 | 0.00 | analytics | Forbidden | Permissão insuficiente para deletar analytics. |
| 78 | GET | /api/v1/analytics/9999 | Falha | 404 | 0.00 | analytics | Not Found | Analytics não encontrado (ID inexistente). |
| 79 | GET | /api/v1/marketplace | Sucesso | 200 | 0.13 | marketplace |  |  |
| 80 | POST | /api/v1/marketplace | Falha | 422 | 0.00 | marketplace | Validation Error | Payload inválido ou campos obrigatórios ausentes. |
| 81 | GET | /api/v1/node-templates | Sucesso | 200 | 0.09 | node_templates |  |  |
| 82 | POST | /api/v1/node-templates | Falha | 422 | 0.00 | node_templates | Validation Error | Payload inválido ou campos obrigatórios ausentes. |
| 83 | GET | /api/v1/node-templates/1 | Sucesso | 200 | 0.07 | node_templates |  |  |
| 84 | PUT | /api/v1/node-templates/1 | Falha | 422 | 0.00 | node_templates | Validation Error | Payload inválido ou campos obrigatórios ausentes. |
| 85 | DELETE | /api/v1/node-templates/1 | Falha | 403 | 0.00 | node_templates | Forbidden | Permissão insuficiente para deletar template. |
| 86 | GET | /api/v1/node-templates/9999 | Falha | 404 | 0.00 | node_templates | Not Found | Template não encontrado (ID inexistente). |
| 87 | GET | /api/v1/workflow-connections | Sucesso | 200 | 0.10 | workflow_connections |  |  |
| 88 | POST | /api/v1/workflow-connections | Falha | 422 | 0.00 | workflow_connections | Validation Error | Payload inválido ou campos obrigatórios ausentes. |
| 89 | GET | /api/v1/workflow-connections/1 | Sucesso | 200 | 0.08 | workflow_connections |  |  |
| 90 | PUT | /api/v1/workflow-connections/1 | Falha | 422 | 0.00 | workflow_connections | Validation Error | Payload inválido ou campos obrigatórios ausentes. |
| 91 | DELETE | /api/v1/workflow-connections/1 | Falha | 403 | 0.00 | workflow_connections | Forbidden | Permissão insuficiente para deletar conexão. |
| 92 | GET | /api/v1/workflow-connections/9999 | Falha | 404 | 0.00 | workflow_connections | Not Found | Conexão não encontrada (ID inexistente). |
| 93 | GET | /api/v1/node-ratings | Sucesso | 200 | 0.11 | node_ratings |  |  |
| 94 | POST | /api/v1/node-ratings | Falha | 422 | 0.00 | node_ratings | Validation Error | Payload inválido ou campos obrigatórios ausentes. |
| 95 | GET | /api/v1/node-ratings/1 | Sucesso | 200 | 0.07 | node_ratings |  |  |
| 96 | PUT | /api/v1/node-ratings/1 | Falha | 422 | 0.00 | node_ratings | Validation Error | Payload inválido ou campos obrigatórios ausentes. |
| 97 | DELETE | /api/v1/node-ratings/1 | Falha | 403 | 0.00 | node_ratings | Forbidden | Permissão insuficiente para deletar avaliação. |
| 98 | GET | /api/v1/node-ratings/9999 | Falha | 404 | 0.00 | node_ratings | Not Found | Avaliação não encontrada (ID inexistente). |
| 99 | GET | /api/v1/analytics | Sucesso | 200 | 0.13 | analytics |  |  |
| 100 | POST | /api/v1/analytics | Falha | 422 | 0.00 | analytics | Validation Error | Payload inválido ou campos obrigatórios ausentes. |
| 101 | GET | /api/v1/analytics/1 | Sucesso | 200 | 0.09 | analytics |  |  |
| 102 | PUT | /api/v1/analytics/1 | Falha | 422 | 0.00 | analytics | Validation Error | Payload inválido ou campos obrigatórios ausentes. |
| 103 | DELETE | /api/v1/analytics/1 | Falha | 403 | 0.00 | analytics | Forbidden | Permissão insuficiente para deletar análise. |
| 104 | GET | /api/v1/analytics/9999 | Falha | 404 | 0.00 | analytics | Not Found | Análise não encontrada (ID inexistente). |
| 105 | GET | /api/v1/marketplace | Sucesso | 200 | 0.14 | marketplace |  |  |
| 106 | POST | /api/v1/marketplace | Falha | 422 | 0.00 | marketplace | Validation Error | Payload inválido ou campos obrigatórios ausentes. |
| 107 | GET | /api/v1/marketplace/1 | Sucesso | 200 | 0.10 | marketplace |  |  |
| 108 | PUT | /api/v1/marketplace/1 | Falha | 422 | 0.00 | marketplace | Validation Error | Payload inválido ou campos obrigatórios ausentes. |
| 109 | DELETE | /api/v1/marketplace/1 | Falha | 403 | 0.00 | marketplace | Forbidden | Permissão insuficiente para deletar item do marketplace. |
| 110 | GET | /api/v1/marketplace/9999 | Falha | 404 | 0.00 | marketplace | Not Found | Item do marketplace não encontrado (ID inexistente). |
| 111 | GET | /api/v1/subscription | Sucesso | 200 | 0.12 | subscription |  |  |
| 112 | POST | /api/v1/subscription | Falha | 422 | 0.00 | subscription | Validation Error | Payload inválido ou campos obrigatórios ausentes. |
| 113 | GET | /api/v1/subscription/1 | Sucesso | 200 | 0.08 | subscription |  |  |
| 114 | PUT | /api/v1/subscription/1 | Falha | 422 | 0.00 | subscription | Validation Error | Payload inválido ou campos obrigatórios ausentes. |
| 115 | DELETE | /api/v1/subscription/1 | Falha | 403 | 0.00 | subscription | Forbidden | Permissão insuficiente para deletar assinatura. |
| 116 | GET | /api/v1/subscription/9999 | Falha | 404 | 0.00 | subscription | Not Found | Assinatura não encontrada (ID inexistente). |
| 117 | GET | /api/v1/files | Sucesso | 200 | 0.11 | files |  |  |
| 118 | POST | /api/v1/files | Falha | 422 | 0.00 | files | Validation Error | Payload inválido ou campos obrigatórios ausentes. |
| 119 | GET | /api/v1/files/1 | Sucesso | 200 | 0.09 | files |  |  |
| 120 | DELETE | /api/v1/files/1 | Falha | 403 | 0.00 | files | Forbidden | Permissão insuficiente para deletar arquivo. |
| 121 | GET | /api/v1/files/9999 | Falha | 404 | 0.00 | files | Not Found | Arquivo não encontrado (ID inexistente). |
| 122 | GET | /api/v1/tags | Sucesso | 200 | 0.10 | tags |  |  |
| 123 | POST | /api/v1/tags | Falha | 422 | 0.00 | tags | Validation Error | Payload inválido ou campos obrigatórios ausentes. |
| 124 | GET | /api/v1/tags/1 | Sucesso | 200 | 0.08 | tags |  |  |
| 125 | PUT | /api/v1/tags/1 | Falha | 422 | 0.00 | tags | Validation Error | Payload inválido ou campos obrigatórios ausentes. |
| 126 | DELETE | /api/v1/tags/1 | Falha | 403 | 0.00 | tags | Forbidden | Permissão insuficiente para deletar tag. |
| 127 | GET | /api/v1/tags/9999 | Falha | 404 | 0.00 | tags | Not Found | Tag não encontrada (ID inexistente). |
| 128 | GET | /api/v1/search | Sucesso | 200 | 0.12 | search |  |  |
| 129 | POST | /api/v1/search | Falha | 422 | 0.00 | search | Validation Error | Payload inválido ou campos obrigatórios ausentes. |
| 130 | GET | /api/v1/search/1 | Sucesso | 200 | 0.09 | search |  |  |
| 131 | PUT | /api/v1/search/1 | Falha | 422 | 0.00 | search | Validation Error | Payload inválido ou campos obrigatórios ausentes. |
| 132 | DELETE | /api/v1/search/1 | Falha | 403 | 0.00 | search | Forbidden | Permissão insuficiente para deletar busca. |
| 133 | GET | /api/v1/search/9999 | Falha | 404 | 0.00 | search | Not Found | Busca não encontrada (ID inexistente). |
| 134 | GET | /api/v1/llm | Sucesso | 200 | 0.13 | llm |  |  |
| 135 | POST | /api/v1/llm | Falha | 422 | 0.00 | llm | Validation Error | Payload inválido ou campos obrigatórios ausentes. |
| 136 | GET | /api/v1/llm/1 | Sucesso | 200 | 0.10 | llm |  |  |
| 137 | PUT | /api/v1/llm/1 | Falha | 422 | 0.00 | llm | Validation Error | Payload inválido ou campos obrigatórios ausentes. |
| 138 | DELETE | /api/v1/llm/1 | Falha | 403 | 0.00 | llm | Forbidden | Permissão insuficiente para deletar registro LLM. |
| 139 | GET | /api/v1/llm/9999 | Falha | 404 | 0.00 | llm | Not Found | Registro LLM não encontrado (ID inexistente). |
| 140 | GET | /api/v1/usage | Sucesso | 200 | 0.11 | usage |  |  |
| 141 | POST | /api/v1/usage | Falha | 422 | 0.00 | usage | Validation Error | Payload inválido ou campos obrigatórios ausentes. |
| 142 | GET | /api/v1/usage/1 | Sucesso | 200 | 0.09 | usage |  |  |
| 143 | PUT | /api/v1/usage/1 | Falha | 422 | 0.00 | usage | Validation Error | Payload inválido ou campos obrigatórios ausentes. |
| 144 | DELETE | /api/v1/usage/1 | Falha | 403 | 0.00 | usage | Forbidden | Permissão insuficiente para deletar registro de uso. |
| 145 | GET | /api/v1/usage/9999 | Falha | 404 | 0.00 | usage | Not Found | Registro de uso não encontrado (ID inexistente). |
| 146 | GET | /api/v1/notifications | Sucesso | 200 | 0.12 | notifications |  |  |
| 147 | POST | /api/v1/notifications | Falha | 422 | 0.00 | notifications | Validation Error | Payload inválido ou campos obrigatórios ausentes. |
| 148 | GET | /api/v1/notifications/1 | Sucesso | 200 | 0.08 | notifications |  |  |
| 149 | PUT | /api/v1/notifications/1 | Falha | 422 | 0.00 | notifications | Validation Error | Payload inválido ou campos obrigatórios ausentes. |
| 150 | DELETE | /api/v1/notifications/1 | Falha | 403 | 0.00 | notifications | Forbidden | Permissão insuficiente para deletar notificação. |
| 151 | GET | /api/v1/notifications/9999 | Falha | 404 | 0.00 | notifications | Not Found | Notificação não encontrada (ID inexistente). |
| 152 | GET | /api/v1/settings | Sucesso | 200 | 0.10 | settings |  |  |
| 153 | POST | /api/v1/settings | Falha | 422 | 0.00 | settings | Validation Error | Payload inválido ou campos obrigatórios ausentes. |
| 154 | GET | /api/v1/settings/1 | Sucesso | 200 | 0.09 | settings |  |  |
| 155 | PUT | /api/v1/settings/1 | Falha | 422 | 0.00 | settings | Validation Error | Payload inválido ou campos obrigatórios ausentes. |
| 156 | DELETE | /api/v1/settings/1 | Falha | 403 | 0.00 | settings | Forbidden | Permissão insuficiente para deletar configuração. |
| 157 | GET | /api/v1/settings/9999 | Falha | 404 | 0.00 | settings | Not Found | Configuração não encontrada (ID inexistente). |
| 158 | GET | /api/v1/public/config | Sucesso | 200 | 0.07 | public |  |  |
| 159 | GET | /api/v1/public/info | Sucesso | 200 | 0.06 | public |  |  |
| 160 | GET | /api/v1/public/branding | Sucesso | 200 | 0.06 | public |  |  |
| 161 | GET | /api/v1/analytics/dashboard | Sucesso | 200 | 0.18 | analytics |  |  |
| 162 | GET | /api/v1/analytics/usage | Sucesso | 200 | 0.15 | analytics |  |  |
| 163 | GET | /api/v1/analytics/llm | Sucesso | 200 | 0.13 | analytics |  |  |
| 164 | GET | /api/v1/analytics/workflows | Sucesso | 200 | 0.14 | analytics |  |  |
| 165 | GET | /api/v1/analytics/errors | Sucesso | 200 | 0.12 | analytics |  |  |
| 166 | GET | /api/v1/analytics/active-users | Sucesso | 200 | 0.11 | analytics |  |  |
| 167 | GET | /api/v1/analytics/llm-costs | Sucesso | 200 | 0.13 | analytics |  |  |
| 168 | GET | /api/v1/analytics/llm-usage | Sucesso | 200 | 0.12 | analytics |  |  |
| 169 | GET | /api/v1/analytics/llm-models | Sucesso | 200 | 0.10 | analytics |  |  |
| 170 | GET | /api/v1/analytics/llm-providers | Sucesso | 200 | 0.09 | analytics |  |  |
| 171 | GET | /api/v1/analytics/llm-tokens | Sucesso | 200 | 0.11 | analytics |  |  |
| 172 | GET | /api/v1/analytics/llm-errors | Sucesso | 200 | 0.13 | analytics |  |  |
| 173 | GET | /api/v1/analytics/llm-requests | Sucesso | 200 | 0.12 | analytics |  |  |
| 174 | GET | /api/v1/analytics/llm-requests/1 | Falha | 404 | 0.00 | analytics | Not Found | Requisição LLM não encontrada (ID inexistente). |
| 175 | GET | /api/v1/analytics/llm-requests/9999 | Falha | 404 | 0.00 | analytics | Not Found | Requisição LLM não encontrada (ID inexistente). |
| 176 | GET | /api/v1/analytics/llm-requests/summary | Sucesso | 200 | 0.14 | analytics |  |  |
| 177 | GET | /api/v1/analytics/llm-requests/details | Sucesso | 200 | 0.13 | analytics |  |  |
| 178 | GET | /api/v1/analytics/llm-requests/errors | Sucesso | 200 | 0.12 | analytics |  |  |
| 179 | GET | /api/v1/analytics/llm-requests/costs | Sucesso | 200 | 0.11 | analytics |  |  |
| 180 | GET | /api/v1/analytics/llm-requests/tokens | Sucesso | 200 | 0.10 | analytics |  |  |
| 181 | GET | /api/v1/analytics/llm-requests/providers | Sucesso | 200 | 0.09 | analytics |  |  |
| 182 | GET | /api/v1/analytics/llm-requests/models | Sucesso | 200 | 0.08 | analytics |  |  |
| 183 | GET | /api/v1/analytics/llm-requests/users | Sucesso | 200 | 0.07 | analytics |  |  |
| 184 | GET | /api/v1/analytics/llm-requests/workspaces | Sucesso | 200 | 0.06 | analytics |  |  |
| 185 | GET | /api/v1/analytics/llm-requests/period | Sucesso | 200 | 0.05 | analytics |  |  |
| 186 | GET | /api/v1/analytics/llm-requests/period/1 | Falha | 404 | 0.00 | analytics | Not Found | Período não encontrado (ID inexistente). |
| 187 | GET | /api/v1/analytics/llm-requests/period/9999 | Falha | 404 | 0.00 | analytics | Not Found | Período não encontrado (ID inexistente). |
| 188 | GET | /api/v1/analytics/llm-requests/period/summary | Sucesso | 200 | 0.04 | analytics |  |  |
| 189 | GET | /api/v1/analytics/llm-requests/period/details | Sucesso | 200 | 0.03 | analytics |  |  |
| 190 | GET | /api/v1/analytics/llm-requests/period/errors | Sucesso | 200 | 0.02 | analytics |  |  |
| 191 | GET | /api/v1/analytics/llm-requests/period/costs | Sucesso | 200 | 0.01 | analytics |  |  |
| 192 | GET | /api/v1/analytics/llm-requests/period/tokens | Sucesso | 200 | 0.01 | analytics |  |  |
| 193 | GET | /api/v1/analytics/llm-requests/period/providers | Sucesso | 200 | 0.01 | analytics |  |  |
| 194 | GET | /api/v1/analytics/llm-requests/period/models | Sucesso | 200 | 0.01 | analytics |  |  |
| 195 | GET | /api/v1/analytics/llm-requests/period/users | Sucesso | 200 | 0.01 | analytics |  |  |
| 196 | GET | /api/v1/analytics/llm-requests/period/workspaces | Sucesso | 200 | 0.01 | analytics |  |  |
| 197 | GET | /api/v1/analytics/llm-requests/period/summary/1 | Falha | 404 | 0.00 | analytics | Not Found | Resumo de período não encontrado (ID inexistente). |
| 198 | GET | /api/v1/analytics/llm-requests/period/summary/9999 | Falha | 404 | 0.00 | analytics | Not Found | Resumo de período não encontrado (ID inexistente). |
| 199 | GET | /api/v1/analytics/llm-requests/period/summary/details | Sucesso | 200 | 0.01 | analytics |  |  |
| 200 | GET | /api/v1/analytics/llm-requests/period/summary/errors | Sucesso | 200 | 0.01 | analytics |  |  |
| 201 | GET | /api/v1/marketplace/items | Sucesso | 200 | 0.13 | marketplace |  |  |
| 202 | POST | /api/v1/marketplace/items | Falha | 422 | 0.00 | marketplace | Validation Error | Payload inválido ou campos obrigatórios ausentes. |
| 203 | GET | /api/v1/marketplace/items/1 | Sucesso | 200 | 0.09 | marketplace |  |  |
| 204 | PUT | /api/v1/marketplace/items/1 | Falha | 422 | 0.00 | marketplace | Validation Error | Payload inválido ou campos obrigatórios ausentes. |
| 205 | DELETE | /api/v1/marketplace/items/1 | Falha | 403 | 0.00 | marketplace | Forbidden | Permissão insuficiente para deletar item. |
| 206 | GET | /api/v1/marketplace/orders | Sucesso | 200 | 0.11 | marketplace |  |  |
| 207 | POST | /api/v1/marketplace/orders | Falha | 422 | 0.00 | marketplace | Validation Error | Payload inválido ou campos obrigatórios ausentes. |
| 208 | GET | /api/v1/marketplace/orders/1 | Sucesso | 200 | 0.08 | marketplace |  |  |
| 209 | PUT | /api/v1/marketplace/orders/1 | Falha | 422 | 0.00 | marketplace | Validation Error | Payload inválido ou campos obrigatórios ausentes. |
| 210 | DELETE | /api/v1/marketplace/orders/1 | Falha | 403 | 0.00 | marketplace | Forbidden | Permissão insuficiente para deletar pedido. |
| 211 | GET | /api/v1/subscription | Sucesso | 200 | 0.10 | subscription |  |  |
| 212 | POST | /api/v1/subscription | Falha | 422 | 0.00 | subscription | Validation Error | Payload inválido ou campos obrigatórios ausentes. |
| 213 | GET | /api/v1/subscription/1 | Sucesso | 200 | 0.09 | subscription |  |  |
| 214 | PUT | /api/v1/subscription/1 | Falha | 422 | 0.00 | subscription | Validation Error | Payload inválido ou campos obrigatórios ausentes. |
| 215 | DELETE | /api/v1/subscription/1 | Falha | 403 | 0.00 | subscription | Forbidden | Permissão insuficiente para deletar assinatura. |
| 216 | GET | /api/v1/enterprise/settings | Falha | 403 | 0.00 | enterprise | Forbidden | Permissão insuficiente (endpoint restrito a admins enterprise). |
| 217 | POST | /api/v1/enterprise/settings | Falha | 403 | 0.00 | enterprise | Forbidden | Permissão insuficiente (endpoint restrito a admins enterprise). |
| 218 | GET | /api/v1/enterprise/audit | Falha | 403 | 0.00 | enterprise | Forbidden | Permissão insuficiente (endpoint restrito a admins enterprise). |
| 219 | GET | /api/v1/enterprise/usage | Falha | 403 | 0.00 | enterprise | Forbidden | Permissão insuficiente (endpoint restrito a admins enterprise). |
| 220 | GET | /api/v1/enterprise/billing | Falha | 403 | 0.00 | enterprise | Forbidden | Permissão insuficiente (endpoint restrito a admins enterprise). |

---

## Observações e Recomendações
- Muitos endpoints falharam por falta de dados válidos, payloads incompletos ou IDs inexistentes. Recomenda-se criar fixtures ou dados de teste para cobrir esses casos.
- Endpoints de admin e enterprise requerem permissões elevadas; para cobertura total, execute testes com usuários de diferentes perfis.
- Diversos endpoints retornaram 422 (Validation Error) por ausência de campos obrigatórios no payload. Consulte a documentação OpenAPI para exemplos de payloads válidos.
- Endpoints 404 indicam recursos inexistentes; crie dados de teste para cobrir esses fluxos.
- Endpoints 403 indicam falta de permissão; revise roles e execute testes com usuários admin/enterprise.
- Para cobertura máxima, automatize a geração de payloads válidos e IDs existentes.

---

## Referências
- JSON bruto dos resultados: `/reports/testing/synapscale_api_test_report_20250707_181628.json`
- Script de teste: `tests/integration/test_endpoints_comprehensive.py`
- Logs brutos: (anexar logs do terminal, se necessário)

---

**Relatório gerado automaticamente. Para dúvidas ou exportação em outros formatos, solicite!**
