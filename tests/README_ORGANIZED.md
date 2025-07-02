# Testes Organizados - SynapScale Backend

## Estrutura Reorganizada (Automatizada v3.0)

### 🔗 Integration Tests (`tests/integration/`)
Testes que verificam a integração entre componentes do sistema:

- **test_endpoints_comprehensive.py** - Teste abrangente de endpoints via OpenAPI
- **test_endpoints_functional.py** - Testes funcionais de endpoints específicos
- **test_llm_endpoints.py** - Testes específicos dos endpoints LLM
- **test_complete_llm_system.py** - Teste completo do sistema LLM integrado
- **test_auth_endpoints.py** - Testes de autenticação e autorização
- **test_agents_system.py** - Testes do sistema completo de agentes
- **test_error_handling_system.py** - Testes do sistema de tratamento de erros
- **test_service_layer_integration.py** - Integração da camada de serviços
- **test_service_architecture.py** - Testes de arquitetura de serviços
- **test_registration_debug.py** - Debug do processo de registro
- **test_llm_endpoint.py** - Teste simples de endpoint LLM
- **test_llm_endpoint_simple.py** - Teste básico de endpoint LLM

### ✅ Validation Tests (`tests/validation/`)
Scripts que validam a integridade e consistência do sistema:

- **comprehensive_validation.py** - Validação abrangente de todo o sistema
- **test_model_validation.py** - Validação específica de modelos de dados
- **validate_complete_structure.py** - Validação da estrutura completa
- **validate_models_comprehensive.py** - Validação abrangente de modelos
- **final_database_alignment_test.py** - Teste de alinhamento do banco de dados
- **final_relationship_test.py** - Teste final de relacionamentos
- **comprehensive_model_test.py** - Teste abrangente de modelos
- **verify_models_detailed.py** - Verificação detalhada de modelos
- **validate_no_hardcoded_final.py** - Validação contra valores hardcoded

### 📊 Analysis Scripts (`tests/analysis/`)
Scripts para análise e diagnóstico do sistema:

- **check_database_structure.py** - Análise detalhada da estrutura do banco
- **analyze_remaining_models.py** - Análise de modelos restantes/pendentes
- **test_cleanup_analysis.py** - Análise de limpeza e otimização
- **endpoint_database_sync_analysis.py** - Análise de sincronia endpoints/DB
- **check_missing_models.py** - Verificação de modelos faltantes

### ⚙️ Setup Scripts (`tests/setup/`)
Scripts para configuração e preparação do ambiente de teste:

- **setup_test_user_api_keys.py** - Configuração de API keys para testes
- **setup_improved_testing.py** - Setup melhorado do ambiente de teste

## Estrutura de Relatórios

```
reports/
├── database/       # Análises de estrutura do banco
├── testing/        # Resultados de testes e análises
├── endpoints/      # Análises de endpoints e APIs
├── performance/    # Métricas de performance
└── temp/          # Relatórios temporários

docs/
├── api/           # Documentação da API (existente)
├── database/      # Documentação do banco (existente)
├── configuration/ # Documentação de configuração (existente)
├── development/   # Guias de desenvolvimento (existente)
├── deployment/    # Guias de deploy (existente)
├── architecture/  # Documentação de arquitetura (existente)
└── reports/       # Relatórios e análises (novo)
```

## Como Usar

```bash
# Executar teste principal de endpoints
python tests/integration/test_endpoints_comprehensive.py

# Validação completa do sistema
python tests/validation/comprehensive_validation.py

# Análise da estrutura do banco
python tests/analysis/check_database_structure.py

# Setup do ambiente de teste
python tests/setup/setup_test_user_api_keys.py
```

## Conformidade com Regras

Esta reorganização segue as regras estabelecidas em:
- `.cursor/rules/new_tests_scripts_rules.mdc`
- `.cursor/rules/new_json_reports.mdc`
- `.cursor/rules/new_markdown_documents.mdc`

> **Princípio:** "REUTILIZAR ANTES DE CRIAR" - Scripts redundantes foram removidos.
