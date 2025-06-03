# Makefile para SynapScale Backend
# Criado por José - O melhor Full Stack do mundo

.PHONY: help install install-dev install-prod test lint format clean build run dev migrate

# Variáveis
PYTHON := python3
PIP := pip3
PYTEST := pytest
BLACK := black
ISORT := isort
FLAKE8 := flake8
MYPY := mypy

# Ajuda
help:
	@echo "SynapScale Backend - Comandos Disponíveis:"
	@echo ""
	@echo "Instalação:"
	@echo "  install      - Instala dependências básicas"
	@echo "  install-dev  - Instala dependências de desenvolvimento"
	@echo "  install-prod - Instala dependências de produção"
	@echo ""
	@echo "Desenvolvimento:"
	@echo "  dev          - Inicia servidor de desenvolvimento"
	@echo "  test         - Executa todos os testes"
	@echo "  test-cov     - Executa testes com coverage"
	@echo "  lint         - Executa linting (flake8, mypy)"
	@echo "  format       - Formata código (black, isort)"
	@echo "  format-check - Verifica formatação"
	@echo ""
	@echo "Banco de dados:"
	@echo "  migrate      - Executa migrações"
	@echo "  migrate-auto - Gera migração automática"
	@echo "  migrate-down - Desfaz última migração"
	@echo ""
	@echo "Produção:"
	@echo "  build        - Constrói imagem Docker"
	@echo "  run          - Executa em produção"
	@echo "  clean        - Limpa arquivos temporários"

# Instalação
install:
	$(PIP) install -r requirements.txt

install-dev:
	$(PIP) install -r requirements-dev.txt
	pre-commit install

install-prod:
	$(PIP) install -r requirements-prod.txt

# Desenvolvimento
dev:
	uvicorn src.synapse.main:app --reload --host 0.0.0.0 --port 8000

test:
	$(PYTEST) tests/ -v

test-cov:
	$(PYTEST) tests/ --cov=src/synapse --cov-report=html --cov-report=term

test-unit:
	$(PYTEST) tests/unit/ -v

test-integration:
	$(PYTEST) tests/integration/ -v

test-performance:
	$(PYTEST) tests/performance/ -v

# Qualidade de código
lint:
	$(FLAKE8) src/ tests/
	$(MYPY) src/
	bandit -r src/

format:
	$(BLACK) src/ tests/
	$(ISORT) src/ tests/

format-check:
	$(BLACK) --check src/ tests/
	$(ISORT) --check-only src/ tests/

# Banco de dados
migrate:
	cd src && alembic upgrade head

migrate-auto:
	cd src && alembic revision --autogenerate -m "Auto migration"

migrate-down:
	cd src && alembic downgrade -1

migrate-history:
	cd src && alembic history

# Docker
build:
	docker build -t synapscale-backend .

run-docker:
	docker run -p 8000:8000 synapscale-backend

# Limpeza
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type f -name ".coverage" -delete
	find . -type d -name "htmlcov" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +

# Segurança
security:
	safety check
	bandit -r src/
	detect-secrets scan --all-files

# Documentação
docs:
	cd docs && make html

docs-serve:
	cd docs && python -m http.server 8080

# Profiling
profile:
	pyinstrument -m uvicorn src.synapse.main:app --host 0.0.0.0 --port 8000

# Backup
backup-db:
	pg_dump $(DATABASE_URL) > backup_$(shell date +%Y%m%d_%H%M%S).sql

# Logs
logs:
	tail -f logs/app.log

# Health check
health:
	curl -f http://localhost:8000/health || exit 1

# Setup completo para desenvolvimento
setup-dev: install-dev migrate
	@echo "✅ Setup de desenvolvimento concluído!"
	@echo "Execute 'make dev' para iniciar o servidor"

# Setup completo para produção
setup-prod: install-prod migrate
	@echo "✅ Setup de produção concluído!"
	@echo "Execute 'make run' para iniciar o servidor"

