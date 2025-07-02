# 🧪 Guia de Testes - SynapScale Backend

## 📋 Visão Geral

Este guia cobre todas as estratégias e ferramentas de teste implementadas no SynapScale Backend.

## 🎯 **Tipos de Teste**

### 🔧 **Testes Unitários**
```bash
# Executar testes unitários
pytest tests/unit/

# Com coverage
pytest --cov=src/synapse tests/unit/
```

### 🔗 **Testes de Integração**
```bash
# Testes de integração
pytest tests/integration/

# Apenas testes LLM
pytest tests/integration/test_llm_*
```

### 🌐 **Testes de API**
```bash
# Testes completos de endpoints
pytest tests/api/

# Testes específicos
pytest tests/api/test_auth.py
pytest tests/api/test_llm_endpoints.py
```

## 📊 **Sistema de Testes Automatizado**

### ✅ **Descoberta Automática via OpenAPI**
O sistema de testes utiliza o schema OpenAPI para descobrir e testar automaticamente todos os endpoints:

```python
# Exemplo de teste automático
async def test_all_endpoints():
    """Testa todos os 242 endpoints descobertos via OpenAPI"""
    endpoints = await discover_endpoints_from_openapi()
    
    for endpoint in endpoints:
        response = await test_endpoint(endpoint)
        assert response.status_code in [200, 201, 204, 400, 401, 403, 404]
```

### 📈 **Métricas Atuais**
- **242 Endpoints Testados**: Cobertura completa da API
- **Taxa de Sucesso: 70.7%**: Monitoramento contínuo
- **Sistema LLM: 77.8%**: Performance superior do core
- **Tempo Execução: ~2 minutos**: Testes rápidos

## 🤖 **Testes de LLM**

### 🧠 **Provedores Testados**
```python
# Teste de múltiplos provedores
@pytest.mark.parametrize("provider", ["openai", "anthropic", "google"])
async def test_llm_provider(provider):
    response = await llm_client.generate(
        provider=provider,
        model="default",
        prompt="Test prompt"
    )
    assert response.status_code == 200
```

### 🔑 **Testes de API Keys**
```python
# Teste de API keys específicas por usuário
async def test_user_api_keys():
    # Configurar API key do usuário
    await set_user_api_key("openai", "sk-test-key")
    
    # Verificar uso da chave específica
    response = await llm_generate(provider="openai")
    assert response.used_user_key == True
```

## 🔐 **Testes de Autenticação**

### 🎫 **JWT e Refresh Tokens**
```python
async def test_auth_flow():
    # Login
    login_response = await auth_client.login(email, password)
    access_token = login_response.json()["access_token"]
    
    # Usar token
    protected_response = await api_client.get(
        "/protected",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert protected_response.status_code == 200
    
    # Refresh token
    refresh_response = await auth_client.refresh(refresh_token)
    assert refresh_response.status_code == 200
```

## 📁 **Testes de Arquivos**

### 📤 **Upload e Download**
```python
async def test_file_operations():
    # Upload
    upload_response = await files_client.upload(
        file=test_file,
        metadata={"type": "document"}
    )
    file_id = upload_response.json()["file_id"]
    
    # Download
    download_response = await files_client.download(file_id)
    assert download_response.status_code == 200
```

## 📊 **Testes de Analytics**

### 📈 **Métricas e Relatórios**
```python
async def test_analytics():
    # Gerar dados de teste
    await create_test_usage_data()
    
    # Testar métricas
    metrics_response = await analytics_client.get_metrics()
    assert len(metrics_response.json()["metrics"]) > 0
    
    # Testar relatórios
    report_response = await analytics_client.generate_report()
    assert report_response.status_code == 200
```

## 🛠️ **Configuração de Testes**

### 🗄️ **Banco de Dados de Teste**
```bash
# Configurar banco de teste
export DATABASE_URL="postgresql://test:test@localhost:5432/synapscale_test"

# Executar migrações
alembic upgrade head

# Executar testes
pytest
```

### 🔧 **Fixtures Comuns**
```python
@pytest.fixture
async def test_user():
    """Cria usuário de teste"""
    user = await create_test_user()
    yield user
    await cleanup_test_user(user.id)

@pytest.fixture
async def auth_headers(test_user):
    """Headers de autenticação"""
    token = await generate_test_token(test_user)
    return {"Authorization": f"Bearer {token}"}
```

## 🚀 **CI/CD Integration**

### ⚙️ **GitHub Actions**
```yaml
# .github/workflows/tests.yml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      - name: Run tests
        run: pytest --cov=src/synapse
```

## 📋 **Comandos Úteis**

```bash
# Testes completos com coverage
pytest --cov=src/synapse --cov-report=html

# Testes específicos por tag
pytest -m "not slow"  # Pular testes lentos
pytest -m "integration"  # Apenas integração

# Testes com output detalhado
pytest -v -s

# Testes paralelos (mais rápido)
pytest -n auto

# Apenas testes que falharam na última execução
pytest --lf
```

## 📊 **Relatórios e Métricas**

### 📈 **Coverage Report**
```bash
# Gerar relatório HTML
pytest --cov=src/synapse --cov-report=html
open htmlcov/index.html
```

### 📋 **Test Report**
```bash
# Relatório JUnit (para CI)
pytest --junitxml=test-results.xml

# Relatório detalhado
pytest --html=report.html --self-contained-html
```

## 🆘 **Troubleshooting**

### ❌ **Problemas Comuns**

**Testes lentos:**
```bash
# Identificar testes lentos
pytest --durations=10
```

**Banco de dados:**
```bash
# Resetar banco de teste
dropdb synapscale_test
createdb synapscale_test
alembic upgrade head
```

**Cache de testes:**
```bash
# Limpar cache do pytest
pytest --cache-clear
```

## 🔗 **Links Relacionados**

- **[Development Setup](./setup_guide.md)** - Configuração do ambiente
- **[API Documentation](../api/README.md)** - Documentação da API
- **[Contributing Guide](../CONTRIBUTING.md)** - Como contribuir
