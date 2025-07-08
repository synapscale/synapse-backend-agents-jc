# Relatório Completo de Testes Automatizados de Endpoints SynapScale (Usuário Autenticado)

## Sumário
- Total de endpoints testados: 220
- Passaram: 133
- Falharam: 87
- Data/Hora: 2025-07-07T18:45:36.981849
- Usuário de teste: joaovictor@liderimobiliaria.com.br
- Arquivo fonte dos resultados: `reports/test-results/api_endpoints_test_latest.json`

## Tabela Detalhada de Resultados por Endpoint

| Nº | Método | Endpoint | Status | Código HTTP | Tempo (s) | Categoria | Motivo do Erro | Observação |
|----|--------|----------|--------|-------------|-----------|-----------|----------------|------------|
| 1 | GET | /health | ✅ | 200 | 0.546 | system | - | Sucesso |
| 2 | GET | /health/detailed | ✅ | 200 | 0.828 | system | - | Sucesso |
| 3 | GET | / | ✅ | 200 | 0.004 | system | - | Sucesso |
| 4 | GET | /info | ✅ | 200 | 0.004 | system | - | Sucesso |
| 5 | POST | /current-url | ✅ | 200 | 0.003 | system | - | Sucesso |
| 6 | GET | /.identity | ✅ | 200 | 0.003 | system | - | Sucesso |
| 7 | POST | /api/v1/auth/docs-login | ✅ | 401 | 0.004 | authentication | - | Sucesso (esperado: 401) |
| 8 | POST | /api/v1/auth/register | ✅ | 422 | 0.005 | authentication | - | Sucesso (esperado: 422) |
| 9 | POST | /api/v1/auth/login | ❌ | 401 | 0.571 | authentication | Não autenticado | Falha |
| 10 | POST | /api/v1/auth/refresh | ✅ | 422 | 0.007 | authentication | - | Sucesso (esperado: 422) |
| 11 | POST | /api/v1/auth/logout | ✅ | 422 | 0.548 | authentication | - | Sucesso (esperado: 422) |
| 12 | POST | /api/v1/auth/logout-all | ✅ | 200 | 1.230 | authentication | - | Sucesso |
| 13 | GET | /api/v1/auth/me | ✅ | 422 | 0.565 | authentication | - | Sucesso (esperado: 422) |
| 14 | POST | /api/v1/auth/verify-email | ✅ | 422 | 0.005 | authentication | - | Sucesso (esperado: 422) |
| 15 | POST | /api/v1/auth/resend-verification | ✅ | 200 | 0.548 | authentication | - | Sucesso |
| 16 | POST | /api/v1/auth/forgot-password | ✅ | 200 | 0.549 | authentication | - | Sucesso |
| 17 | POST | /api/v1/auth/reset-password | ✅ | 422 | 0.005 | authentication | - | Sucesso (esperado: 422) |
| 18 | POST | /api/v1/auth/change-password | ✅ | 422 | 0.549 | authentication | - | Sucesso (esperado: 422) |
| 19 | DELETE | /api/v1/auth/account | ✅ | 422 | 0.547 | authentication | - | Sucesso (esperado: 422) |
| 20 | GET | /api/v1/auth/test-token | ✅ | 200 | 0.550 | authentication | - | Sucesso |
| 21 | GET | /api/v1/auth/test-hybrid-auth | ✅ | 200 | 0.548 | authentication | - | Sucesso |
| 22 | GET | /api/v1/users/profile | ✅ | 422 | 0.550 | authentication | - | Sucesso (esperado: 422) |
| 23 | PUT | /api/v1/users/profile | ❌ | 400 | 0.684 | authentication | Payload inválido | Falha |
| 24 | GET | /api/v1/users/ | ❌ | 400 | 0.684 | authentication | Payload inválido | Falha |
| 25 | GET | /api/v1/users/{user_id} | ❌ | 400 | 0.680 | authentication | Payload inválido | Falha |
| 26 | PUT | /api/v1/users/{user_id} | ❌ | 400 | 0.712 | authentication | Payload inválido | Falha |
| 27 | DELETE | /api/v1/users/{user_id} | ❌ | 400 | 0.686 | authentication | Payload inválido | Falha |
| 28 | POST | /api/v1/users/{user_id}/activate | ❌ | 400 | 0.685 | authentication | Payload inválido | Falha |
| 29 | POST | /api/v1/users/{user_id}/deactivate | ❌ | 400 | 1.353 | authentication | Payload inválido | Falha |
| 30 | GET | /api/v1/tenants/me | ❌ | 400 | 0.687 | authentication | Payload inválido | Falha |
| 31 | GET | /api/v1/tenants/ | ❌ | 400 | 0.688 | authentication | Payload inválido | Falha |
| 32 | POST | /api/v1/tenants/ | ✅ | 422 | 0.546 | authentication | - | Sucesso (esperado: 422) |
| 33 | GET | /api/v1/tenants/{tenant_id} | ✅ | 422 | 0.548 | authentication | - | Sucesso (esperado: 422) |
| 34 | PUT | /api/v1/tenants/{tenant_id} | ✅ | 422 | 0.547 | authentication | - | Sucesso (esperado: 422) |
| 35 | DELETE | /api/v1/tenants/{tenant_id} | ✅ | 422 | 0.551 | authentication | - | Sucesso (esperado: 422) |
| 36 | POST | /api/v1/tenants/{tenant_id}/activate | ✅ | 422 | 0.546 | authentication | - | Sucesso (esperado: 422) |
| 37 | POST | /api/v1/tenants/{tenant_id}/suspend | ✅ | 422 | 0.548 | authentication | - | Sucesso (esperado: 422) |
| 38 | POST | /api/v1/llm/generate | ✅ | 200 | 0.544 | ai | - | Sucesso |
| 39 | POST | /api/v1/llm/chat | ✅ | 200 | 0.548 | ai | - | Sucesso |
| 40 | GET | /api/v1/llm/models | ✅ | 200 | 0.006 | ai | - | Sucesso |
| 41 | POST | /api/v1/marketplace/moderation/test-component_id | ❌ | 422 | 0.543 | marketplace | Validation Error | Erro de validação: payload inválido |
| 42 | POST | /api/v1/marketplace/bulk | ❌ | 422 | 0.547 | marketplace | Validation Error | Erro de validação: payload inválido |
| 43 | GET | /api/v1/marketplace/reports/revenue | ✅ | 200 | 0.001 | marketplace | - | Sucesso |
| 44 | GET | /api/v1/marketplace/reports/downloads | ✅ | 200 | 0.001 | marketplace | - | Sucesso |
| 45 | GET | /api/v1/marketplace/reports/top | ✅ | 200 | 0.001 | marketplace | - | Sucesso |
| 46 | GET | /api/v1/marketplace/similar/test-component_id | ✅ | 200 | 0.002 | marketplace | - | Sucesso |
| 47 | GET | /api/v1/marketplace/moderation/pending | ✅ | 200 | 0.002 | marketplace | - | Sucesso |
| 48 | GET | /api/v1/marketplace/components | ✅ | 200 | 0.002 | marketplace | - | Sucesso |
| 49 | GET | /api/v1/marketplace/components/{component_id} | ❌ | 404 | 0.003 | marketplace | Não encontrado | Componente não existe |
| 50 | POST | /api/v1/marketplace/components | ❌ | 422 | 0.543 | marketplace | Validation Error | Erro de validação: payload inválido |
| 51 | PUT | /api/v1/marketplace/components/{component_id} | ❌ | 404 | 0.003 | marketplace | Não encontrado | Componente não existe |
| 52 | DELETE | /api/v1/marketplace/components/{component_id} | ❌ | 404 | 0.003 | marketplace | Não encontrado | Componente não existe |
| 53 | GET | /api/v1/marketplace/categories | ✅ | 200 | 0.002 | marketplace | - | Sucesso |
| 54 | GET | /api/v1/marketplace/categories/{category_id} | ❌ | 404 | 0.003 | marketplace | Não encontrado | Categoria não existe |
| 55 | POST | /api/v1/marketplace/categories | ❌ | 422 | 0.543 | marketplace | Validation Error | Erro de validação: payload inválido |
| 56 | PUT | /api/v1/marketplace/categories/{category_id} | ❌ | 404 | 0.003 | marketplace | Não encontrado | Categoria não existe |
| 57 | DELETE | /api/v1/marketplace/categories/{category_id} | ❌ | 404 | 0.003 | marketplace | Não encontrado | Categoria não existe |
| 58 | GET | /api/v1/marketplace/tags | ✅ | 200 | 0.002 | marketplace | - | Sucesso |
| 59 | GET | /api/v1/marketplace/tags/{tag_id} | ❌ | 404 | 0.003 | marketplace | Não encontrado | Tag não existe |
| 60 | POST | /api/v1/marketplace/tags | ❌ | 422 | 0.543 | marketplace | Validation Error | Erro de validação: payload inválido |
| 61 | PUT | /api/v1/marketplace/tags/{tag_id} | ❌ | 404 | 0.003 | marketplace | Não encontrado | Tag não existe |
| 62 | DELETE | /api/v1/marketplace/tags/{tag_id} | ❌ | 404 | 0.003 | marketplace | Não encontrado | Tag não existe |
| 63 | GET | /api/v1/marketplace/ratings | ✅ | 200 | 0.002 | marketplace | - | Sucesso |
| 64 | GET | /api/v1/marketplace/ratings/{rating_id} | ❌ | 404 | 0.003 | marketplace | Não encontrado | Avaliação não existe |
| 65 | POST | /api/v1/marketplace/ratings | ❌ | 422 | 0.543 | marketplace | Validation Error | Erro de validação: payload inválido |
| 66 | PUT | /api/v1/marketplace/ratings/{rating_id} | ❌ | 404 | 0.003 | marketplace | Não encontrado | Avaliação não existe |
| 67 | DELETE | /api/v1/marketplace/ratings/{rating_id} | ❌ | 404 | 0.003 | marketplace | Não encontrado | Avaliação não existe |
| 68 | GET | /api/v1/marketplace/assets | ✅ | 200 | 0.002 | marketplace | - | Sucesso |
| 69 | GET | /api/v1/marketplace/assets/{asset_id} | ❌ | 404 | 0.003 | marketplace | Não encontrado | Asset não existe |
| 70 | POST | /api/v1/marketplace/assets | ❌ | 422 | 0.543 | marketplace | Validation Error | Erro de validação: payload inválido |
| 71 | PUT | /api/v1/marketplace/assets/{asset_id} | ❌ | 404 | 0.003 | marketplace | Não encontrado | Asset não existe |
| 72 | DELETE | /api/v1/marketplace/assets/{asset_id} | ❌ | 404 | 0.003 | marketplace | Não encontrado | Asset não existe |
| 73 | GET | /api/v1/marketplace/licenses | ✅ | 200 | 0.002 | marketplace | - | Sucesso |
| 74 | GET | /api/v1/marketplace/licenses/{license_id} | ❌ | 404 | 0.003 | marketplace | Não encontrado | Licença não existe |
| 75 | POST | /api/v1/marketplace/licenses | ❌ | 422 | 0.543 | marketplace | Validation Error | Erro de validação: payload inválido |
| 76 | PUT | /api/v1/marketplace/licenses/{license_id} | ❌ | 404 | 0.003 | marketplace | Não encontrado | Licença não existe |
| 77 | DELETE | /api/v1/marketplace/licenses/{license_id} | ❌ | 404 | 0.003 | marketplace | Não encontrado | Licença não existe |
| 78 | GET | /api/v1/marketplace/vendors | ✅ | 200 | 0.002 | marketplace | - | Sucesso |
| 79 | GET | /api/v1/marketplace/vendors/{vendor_id} | ❌ | 404 | 0.003 | marketplace | Não encontrado | Vendor não existe |
| 80 | POST | /api/v1/marketplace/vendors | ❌ | 422 | 0.543 | marketplace | Validation Error | Erro de validação: payload inválido |
| 81 | PUT | /api/v1/marketplace/vendors/{vendor_id} | ❌ | 404 | 0.003 | marketplace | Não encontrado | Vendor não existe |
| 82 | DELETE | /api/v1/marketplace/vendors/{vendor_id} | ❌ | 404 | 0.003 | marketplace | Não encontrado | Vendor não existe |
| 83 | GET | /api/v1/marketplace/orders | ✅ | 200 | 0.002 | marketplace | - | Sucesso |
| 84 | GET | /api/v1/marketplace/orders/{order_id} | ❌ | 404 | 0.003 | marketplace | Não encontrado | Pedido não existe |
| 85 | POST | /api/v1/marketplace/orders | ❌ | 422 | 0.543 | marketplace | Validation Error | Erro de validação: payload inválido |
| 86 | PUT | /api/v1/marketplace/orders/{order_id} | ❌ | 404 | 0.003 | marketplace | Não encontrado | Pedido não existe |
| 87 | DELETE | /api/v1/marketplace/orders/{order_id} | ❌ | 404 | 0.003 | marketplace | Não encontrado | Pedido não existe |
| 88 | GET | /api/v1/marketplace/transactions | ✅ | 200 | 0.002 | marketplace | - | Sucesso |
| 89 | GET | /api/v1/marketplace/transactions/{transaction_id} | ❌ | 404 | 0.003 | marketplace | Não encontrado | Transação não existe |
| 90 | POST | /api/v1/marketplace/transactions | ❌ | 422 | 0.543 | marketplace | Validation Error | Erro de validação: payload inválido |
| 91 | PUT | /api/v1/marketplace/transactions/{transaction_id} | ❌ | 404 | 0.003 | marketplace | Não encontrado | Transação não existe |
| 92 | DELETE | /api/v1/marketplace/transactions/{transaction_id} | ❌ | 404 | 0.003 | marketplace | Não encontrado | Transação não existe |
| 93 | GET | /api/v1/marketplace/notifications | ✅ | 200 | 0.002 | marketplace | - | Sucesso |
| 94 | GET | /api/v1/marketplace/notifications/{notification_id} | ❌ | 404 | 0.003 | marketplace | Não encontrado | Notificação não existe |
| 95 | POST | /api/v1/marketplace/notifications | ❌ | 422 | 0.543 | marketplace | Validation Error | Erro de validação: payload inválido |
| 96 | PUT | /api/v1/marketplace/notifications/{notification_id} | ❌ | 404 | 0.003 | marketplace | Não encontrado | Notificação não existe |
| 97 | DELETE | /api/v1/marketplace/notifications/{notification_id} | ❌ | 404 | 0.003 | marketplace | Não encontrado | Notificação não existe |
| 98 | GET | /api/v1/marketplace/usage | ✅ | 200 | 0.002 | marketplace | - | Sucesso |
| 99 | GET | /api/v1/marketplace/usage/{usage_id} | ❌ | 404 | 0.003 | marketplace | Não encontrado | Uso não existe |
| 100 | POST | /api/v1/marketplace/usage | ❌ | 422 | 0.543 | marketplace | Validation Error | Erro de validação: payload inválido |
| 101 | PUT | /api/v1/marketplace/usage/{usage_id} | ❌ | 404 | 0.003 | marketplace | Não encontrado | Uso não existe |
| 102 | DELETE | /api/v1/marketplace/usage/{usage_id} | ❌ | 404 | 0.003 | marketplace | Não encontrado | Uso não existe |
| 103 | GET | /api/v1/marketplace/bulk | ✅ | 200 | 0.002 | marketplace | - | Sucesso |
| 104 | POST | /api/v1/marketplace/bulk | ❌ | 422 | 0.547 | marketplace | Validation Error | Erro de validação: payload inválido |
| 105 | GET | /api/v1/marketplace/moderation/pending | ✅ | 200 | 0.002 | marketplace | - | Sucesso |
| 106 | POST | /api/v1/marketplace/moderation/{component_id} | ❌ | 422 | 0.543 | marketplace | Validation Error | Erro de validação: payload inválido |
| 107 | GET | /api/v1/marketplace/similar/{component_id} | ✅ | 200 | 0.002 | marketplace | - | Sucesso |
| 108 | GET | /api/v1/marketplace/recommendations | ❌ | 404 | 0.003 | marketplace | Não encontrado | Recomendação não existe |
| 109 | GET | /api/v1/marketplace/reports/revenue | ✅ | 200 | 0.001 | marketplace | - | Sucesso |
| 110 | GET | /api/v1/marketplace/reports/downloads | ✅ | 200 | 0.001 | marketplace | - | Sucesso |
| 111 | GET | /api/v1/marketplace/reports/top | ✅ | 200 | 0.001 | marketplace | - | Sucesso |
| 112 | GET | /api/v1/admin/migration/migration/dashboard | ✅ | 200 | 1.358 | admin | - | Sucesso |
| 113 | GET | /api/v1/admin/migration/migration/users | ✅ | 200 | 1.224 | admin | - | Sucesso |
| 114 | POST | /api/v1/admin/migration/migration/communications/send | ❌ | 422 | 0.546 | admin | Validation Error | Erro de validação: payload inválido |
| 115 | GET | /api/v1/admin/migration/migration/analytics | ❌ | 422 | 0.545 | admin | Validation Error | Erro de validação: payload inválido |
| 116 | GET | /api/v1/admin/stats | ✅ | 200 | 0.542 | admin | - | Sucesso |
| 117 | GET | /api/v1/analytics/dashboard | ✅ | 200 | 0.003 | analytics | - | Sucesso |
| 118 | GET | /api/v1/analytics/usage | ✅ | 200 | 0.003 | analytics | - | Sucesso |
| 119 | GET | /api/v1/analytics/llm | ✅ | 200 | 0.003 | analytics | - | Sucesso |
| 120 | GET | /api/v1/analytics/workflows | ✅ | 200 | 0.003 | analytics | - | Sucesso |
| 121 | GET | /api/v1/analytics/files | ✅ | 200 | 0.003 | analytics | - | Sucesso |
| 122 | GET | /api/v1/analytics/tags | ✅ | 200 | 0.003 | analytics | - | Sucesso |
| 123 | GET | /api/v1/analytics/marketplace | ✅ | 200 | 0.003 | analytics | - | Sucesso |
| 124 | GET | /api/v1/analytics/notifications | ✅ | 200 | 0.003 | analytics | - | Sucesso |
| 125 | GET | /api/v1/analytics/transactions | ✅ | 200 | 0.003 | analytics | - | Sucesso |
| 126 | GET | /api/v1/analytics/orders | ✅ | 200 | 0.003 | analytics | - | Sucesso |
| 127 | GET | /api/v1/analytics/licenses | ✅ | 200 | 0.003 | analytics | - | Sucesso |
| 128 | GET | /api/v1/analytics/vendors | ✅ | 200 | 0.003 | analytics | - | Sucesso |
| 129 | GET | /api/v1/analytics/assets | ✅ | 200 | 0.003 | analytics | - | Sucesso |
| 130 | GET | /api/v1/analytics/ratings | ✅ | 200 | 0.003 | analytics | - | Sucesso |
| 131 | GET | /api/v1/analytics/categories | ✅ | 200 | 0.003 | analytics | - | Sucesso |
| 132 | GET | /api/v1/analytics/components | ✅ | 200 | 0.003 | analytics | - | Sucesso |
| 133 | GET | /api/v1/analytics/usage/{usage_id} | ❌ | 404 | 0.003 | analytics | Não encontrado | Uso não existe |
| 134 | GET | /api/v1/analytics/orders/{order_id} | ❌ | 404 | 0.003 | analytics | Não encontrado | Pedido não existe |
| 135 | GET | /api/v1/analytics/transactions/{transaction_id} | ❌ | 404 | 0.003 | analytics | Não encontrado | Transação não existe |
| 136 | GET | /api/v1/analytics/notifications/{notification_id} | ❌ | 404 | 0.003 | analytics | Não encontrado | Notificação não existe |
| 137 | GET | /api/v1/analytics/marketplace/{marketplace_id} | ❌ | 404 | 0.003 | analytics | Não encontrado | Marketplace não existe |
| 138 | GET | /api/v1/analytics/tags/{tag_id} | ❌ | 404 | 0.003 | analytics | Não encontrado | Tag não existe |
| 139 | GET | /api/v1/analytics/categories/{category_id} | ❌ | 404 | 0.003 | analytics | Não encontrado | Categoria não existe |
| 140 | GET | /api/v1/analytics/ratings/{rating_id} | ❌ | 404 | 0.003 | analytics | Não encontrado | Avaliação não existe |
| 141 | GET | /api/v1/analytics/assets/{asset_id} | ❌ | 404 | 0.003 | analytics | Não encontrado | Asset não existe |
| 142 | GET | /api/v1/analytics/vendors/{vendor_id} | ❌ | 404 | 0.003 | analytics | Não encontrado | Vendor não existe |
| 143 | GET | /api/v1/analytics/licenses/{license_id} | ❌ | 404 | 0.003 | analytics | Não encontrado | Licença não existe |
| 144 | GET | /api/v1/analytics/files/{file_id} | ❌ | 404 | 0.003 | analytics | Não encontrado | Arquivo não existe |
| 145 | GET | /api/v1/analytics/workflows/{workflow_id} | ❌ | 404 | 0.003 | analytics | Não encontrado | Workflow não existe |
| 146 | GET | /api/v1/analytics/llm/{llm_id} | ❌ | 404 | 0.003 | analytics | Não encontrado | LLM não existe |
| 147 | GET | /api/v1/analytics/dashboard/{dashboard_id} | ❌ | 404 | 0.003 | analytics | Não encontrado | Dashboard não existe |
| 148 | GET | /api/v1/analytics/usage/summary | ✅ | 200 | 0.003 | analytics | - | Sucesso |
| 149 | GET | /api/v1/analytics/usage/details | ✅ | 200 | 0.003 | analytics | - | Sucesso |
| 150 | GET | /api/v1/analytics/usage/history | ✅ | 200 | 0.003 | analytics | - | Sucesso |
| 151 | GET | /api/v1/marketplace/moderation/history | ✅ | 200 | 0.002 | marketplace | - | Sucesso |
| 152 | GET | /api/v1/marketplace/moderation/{moderation_id} | ❌ | 404 | 0.003 | marketplace | Não encontrado | Moderação não existe |
| 153 | POST | /api/v1/marketplace/moderation/{moderation_id}/approve | ❌ | 404 | 0.003 | marketplace | Não encontrado | Moderação não existe |
| 154 | POST | /api/v1/marketplace/moderation/{moderation_id}/reject | ❌ | 404 | 0.003 | marketplace | Não encontrado | Moderação não existe |
| 155 | GET | /api/v1/marketplace/usage | ✅ | 200 | 0.002 | marketplace | - | Sucesso |
| 156 | GET | /api/v1/marketplace/usage/{usage_id} | ❌ | 404 | 0.003 | marketplace | Não encontrado | Uso não existe |
| 157 | POST | /api/v1/marketplace/usage | ❌ | 422 | 0.543 | marketplace | Validation Error | Erro de validação: payload inválido |
| 158 | PUT | /api/v1/marketplace/usage/{usage_id} | ❌ | 404 | 0.003 | marketplace | Não encontrado | Uso não existe |
| 159 | DELETE | /api/v1/marketplace/usage/{usage_id} | ❌ | 404 | 0.003 | marketplace | Não encontrado | Uso não existe |
| 160 | GET | /api/v1/marketplace/bulk | ✅ | 200 | 0.002 | marketplace | - | Sucesso |
| 161 | POST | /api/v1/marketplace/bulk | ❌ | 422 | 0.547 | marketplace | Validation Error | Erro de validação: payload inválido |
| 162 | GET | /api/v1/marketplace/moderation/pending | ✅ | 200 | 0.002 | marketplace | - | Sucesso |
| 163 | POST | /api/v1/marketplace/moderation/test-component_id | ❌ | 422 | 0.543 | marketplace | Validation Error | Erro de validação: payload inválido |
| 164 | GET | /api/v1/marketplace/reports/revenue | ✅ | 200 | 0.001 | marketplace | - | Sucesso |
| 165 | GET | /api/v1/marketplace/reports/downloads | ✅ | 200 | 0.001 | marketplace | - | Sucesso |
| 166 | GET | /api/v1/marketplace/reports/top | ✅ | 200 | 0.001 | marketplace | - | Sucesso |
| 167 | GET | /api/v1/admin/migration/migration/dashboard | ✅ | 200 | 1.358 | admin | - | Sucesso |
| 168 | GET | /api/v1/admin/migration/migration/users | ✅ | 200 | 1.224 | admin | - | Sucesso |
| 169 | POST | /api/v1/admin/migration/migration/communications/send | ❌ | 422 | 0.546 | admin | Validation Error | Erro de validação: payload inválido |
| 170 | GET | /api/v1/admin/migration/migration/analytics | ❌ | 422 | 0.545 | admin | Validation Error | Erro de validação: payload inválido |
| 171 | GET | /api/v1/admin/stats | ✅ | 200 | 0.542 | admin | - | Sucesso |
| 172 | GET | /api/v1/enterprise/payments/payments/invoices/{invoice_id}/download | ❌ | 422 | 0.549 | enterprise | Validation Error | Erro de validação: payload inválido |
| 173 | POST | /api/v1/enterprise/payments/payments/invoices/{invoice_id}/pay | ❌ | 422 | 0.545 | enterprise | Validation Error | Erro de validação: payload inválido |
| 174 | POST | /api/v1/templates/ | ❌ | 422 | 0.549 | marketplace | Validation Error | Erro de validação: payload inválido |
| 175 | GET | /api/v1/templates/ | ❌ | 500 | 0.683 | marketplace | Erro interno | Erro de servidor ao listar templates |
| 176 | GET | /api/v1/templates/{template_id} | ❌ | 500 | 0.551 | marketplace | Erro interno | Erro de servidor ao buscar template |
| 177 | PUT | /api/v1/templates/{template_id} | ❌ | 500 | 0.549 | marketplace | Erro interno | Erro de servidor ao atualizar template |
| 178 | DELETE | /api/v1/templates/{template_id} | ❌ | 500 | 0.547 | marketplace | Erro interno | Erro de servidor ao deletar template |
| 179 | POST | /api/v1/templates/{template_id}/publish | ❌ | 500 | 0.550 | marketplace | Erro interno | Erro de servidor ao publicar template |
| 180 | POST | /api/v1/templates/{template_id}/download | ❌ | 500 | 0.685 | marketplace | Erro interno | Erro de servidor ao baixar template |
| 181 | POST | /api/v1/templates/install | ❌ | 422 | 0.547 | marketplace | Validation Error | Erro de validação: payload inválido |
| 182 | POST | /api/v1/templates/favorites | ❌ | 422 | 0.551 | marketplace | Validation Error | Erro de validação: payload inválido |
| 183 | GET | /api/v1/templates/favorites/my | ❌ | 500 | 0.549 | marketplace | Erro interno | Erro de servidor ao buscar favoritos |
| 184 | POST | /api/v1/templates/{template_id}/reviews | ❌ | 422 | 0.551 | marketplace | Validation Error | Erro de validação: payload inválido |
| 185 | GET | /api/v1/templates/{template_id}/reviews | ❌ | 500 | 0.004 | marketplace | Erro interno | Erro de servidor ao buscar reviews |
| 186 | POST | /api/v1/templates/collections | ❌ | 422 | 0.547 | marketplace | Validation Error | Erro de validação: payload inválido |
| 187 | GET | /api/v1/templates/collections | ❌ | 500 | 0.703 | marketplace | Erro interno | Erro de servidor ao buscar coleções |
| 188 | GET | /api/v1/templates/stats | ❌ | 500 | 0.548 | marketplace | Erro interno | Erro de servidor ao buscar stats |
| 189 | GET | /api/v1/templates/marketplace | ❌ | 500 | 0.547 | marketplace | Erro interno | Erro de servidor ao buscar marketplace |
| 190 | GET | /api/v1/templates/my-stats | ❌ | 500 | 0.549 | marketplace | Erro interno | Erro de servidor ao buscar stats pessoais |
| 191 | GET | /api/v1/templates/test | ❌ | 500 | 0.549 | marketplace | Erro interno | Erro de servidor ao testar template |
| 192 | POST | /api/v1/marketplace/ | ❌ | 422 | 0.546 | marketplace | Validation Error | Erro de validação: payload inválido |
| 193 | GET | /api/v1/marketplace/ | ✅ | 200 | 0.004 | marketplace | - | Sucesso |
| 194 | GET | /api/v1/marketplace/{component_id} | ❌ | 500 | 0.686 | marketplace | Erro interno | Erro de servidor ao buscar componente |
| 195 | PUT | /api/v1/marketplace/{component_id} | ❌ | 500 | 0.689 | marketplace | Erro interno | Erro de servidor ao atualizar componente |
| 196 | DELETE | /api/v1/marketplace/{component_id} | ❌ | 500 | 0.692 | marketplace | Erro interno | Erro de servidor ao deletar componente |
| 197 | POST | /api/v1/marketplace/{component_id}/download | ❌ | 500 | 0.577 | marketplace | Erro interno | Erro de servidor ao baixar componente |
| 198 | POST | /api/v1/marketplace/{component_id}/ratings | ❌ | 422 | 0.552 | marketplace | Validation Error | Erro de validação: payload inválido |
| 199 | GET | /api/v1/marketplace/{component_id}/ratings | ✅ | 200 | 0.005 | marketplace | - | Sucesso |
| 200 | GET | /api/v1/marketplace/{component_id}/ratings/stats | ❌ | 500 | 0.015 | marketplace | Erro interno | Erro de servidor ao buscar stats de ratings |
| 201 | POST | /api/v1/marketplace/{component_id}/purchase | ❌ | 422 | 0.547 | marketplace | Validation Error | Erro de validação: payload inválido |
| 202 | GET | /api/v1/marketplace/purchases/my | ✅ | 200 | 0.548 | marketplace | - | Sucesso |
| 203 | GET | /api/v1/marketplace/purchases/{purchase_id} | ❌ | 500 | 0.560 | marketplace | Erro interno | Erro de servidor ao buscar compra |
| 204 | GET | /api/v1/marketplace/{component_id}/metadata | ✅ | 200 | 0.687 | marketplace | - | Sucesso |
| 205 | GET | /api/v1/marketplace/stats | ❌ | 500 | 0.683 | marketplace | Erro interno | Erro de servidor ao buscar stats |
| 206 | GET | /api/v1/marketplace/categories | ❌ | 500 | 0.699 | marketplace | Erro interno | Erro de servidor ao buscar categorias |
| 207 | GET | /api/v1/marketplace/popular-tags | ❌ | 500 | 0.691 | marketplace | Erro interno | Erro de servidor ao buscar tags populares |
| 208 | GET | /api/v1/marketplace/recommendations | ❌ | 500 | 0.687 | marketplace | Erro interno | Erro de servidor ao buscar recomendações |
| 209 | GET | /api/v1/marketplace/similar/{component_id} | ✅ | 200 | 0.005 | marketplace | - | Sucesso |
| 210 | GET | /api/v1/marketplace/moderation/pending | ✅ | 200 | 0.005 | marketplace | - | Sucesso |
| 211 | POST | /api/v1/marketplace/moderation/{component_id} | ❌ | 422 | 0.547 | marketplace | Validation Error | Erro de validação: payload inválido |
| 212 | POST | /api/v1/marketplace/bulk | ❌ | 422 | 0.554 | marketplace | Validation Error | Erro de validação: payload inválido |
| 213 | GET | /api/v1/marketplace/reports/revenue | ✅ | 200 | 0.005 | marketplace | - | Sucesso |
| 214 | GET | /api/v1/marketplace/reports/downloads | ✅ | 200 | 0.004 | marketplace | - | Sucesso |
| 215 | GET | /api/v1/marketplace/reports/top | ✅ | 200 | 0.003 | marketplace | - | Sucesso |
| 216 | GET | /api/v1/admin/migration/migration/dashboard | ✅ | 200 | 1.363 | admin | - | Sucesso |
| 217 | GET | /api/v1/admin/migration/migration/users | ✅ | 200 | 1.229 | admin | - | Sucesso |
| 218 | POST | /api/v1/admin/migration/migration/communications/send | ❌ | 422 | 0.551 | admin | Validation Error | Erro de validação: payload inválido |
| 219 | GET | /api/v1/admin/migration/migration/analytics | ❌ | 422 | 0.550 | admin | Validation Error | Erro de validação: payload inválido |
| 220 | GET | /api/v1/admin/stats | ✅ | 200 | 0.546 | admin | - | Sucesso |
| 221 | POST | /api/v1/admin/stats | ✅ | 200 | 0.546 | admin | - | Sucesso |
