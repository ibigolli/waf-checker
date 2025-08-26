# Makefile para Sistema de Verificação de WAF
# Uso: make [target]

.PHONY: help install test clean build run docker-test format lint

# Variáveis
PYTHON = python3
PIP = pip3
DOCKER = docker
DOCKER_COMPOSE = docker-compose

# Cores para output
GREEN = \033[0;32m
YELLOW = \033[1;33m
RED = \033[0;31m
NC = \033[0m # No Color

help: ## Mostra esta ajuda
	@echo "$(GREEN)Sistema de Verificação de WAF - Comandos Disponíveis$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-15s$(NC) %s\n", $$1, $$2}'
	@echo ""

install: ## Instala dependências Python
	@echo "$(YELLOW)📦 Instalando dependências...$(NC)"
	$(PIP) install -r requirements.txt
	@echo "$(GREEN)✅ Dependências instaladas!$(NC)"

install-dev: ## Instala dependências de desenvolvimento
	@echo "$(YELLOW)🔧 Instalando dependências de desenvolvimento...$(NC)"
	$(PIP) install -r requirements.txt
	$(PIP) install black flake8 isort pytest
	@echo "$(GREEN)✅ Dependências de desenvolvimento instaladas!$(NC)"

test: ## Executa testes locais
	@echo "$(YELLOW)🧪 Executando testes...$(NC)"
	$(PYTHON) test_local.py
	@echo "$(GREEN)✅ Testes concluídos!$(NC)"

test-docker: ## Executa testes via Docker
	@echo "$(YELLOW)🐳 Executando testes via Docker...$(NC)"
	./run_docker.sh test
	@echo "$(GREEN)✅ Testes Docker concluídos!$(NC)"

clean: ## Limpa arquivos temporários e de saída
	@echo "$(YELLOW)🧹 Limpando arquivos...$(NC)"
	rm -rf output/* input/* __pycache__/ .pytest_cache/ .coverage
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	@echo "$(GREEN)✅ Limpeza concluída!$(NC)"

build: ## Constrói imagem Docker
	@echo "$(YELLOW)🔨 Construindo imagem Docker...$(NC)"
	$(DOCKER_COMPOSE) build
	@echo "$(GREEN)✅ Imagem construída!$(NC)"

run: ## Executa sistema via Docker (ajuda)
	@echo "$(YELLOW)🚀 Executando sistema...$(NC)"
	./run_docker.sh run --help

run-local: ## Executa sistema localmente (ajuda)
	@echo "$(YELLOW)🚀 Executando sistema localmente...$(NC)"
	$(PYTHON) waf_checker.py --help

docker-test: ## Executa teste via Docker
	@echo "$(YELLOW)🐳 Executando teste Docker...$(NC)"
	./run_docker.sh test

format: ## Formata código com Black
	@echo "$(YELLOW)🎨 Formatando código...$(NC)"
	black .
	@echo "$(GREEN)✅ Código formatado!$(NC)"

lint: ## Executa linting com Flake8
	@echo "$(YELLOW)🔍 Executando linting...$(NC)"
	flake8 . --max-line-length=88 --extend-ignore=E203,W503
	@echo "$(GREEN)✅ Linting concluído!$(NC)"

sort-imports: ## Organiza imports com isort
	@echo "$(YELLOW)📦 Organizando imports...$(NC)"
	isort .
	@echo "$(GREEN)✅ Imports organizados!$(NC)"

check: ## Executa todas as verificações de código
	@echo "$(YELLOW)🔍 Executando verificações de código...$(NC)"
	@make format
	@make sort-imports
	@make lint
	@echo "$(GREEN)✅ Todas as verificações passaram!$(NC)"

setup: ## Configura ambiente completo
	@echo "$(YELLOW)⚙️  Configurando ambiente...$(NC)"
	@make install-dev
	@make clean
	mkdir -p output input
	@echo "$(GREEN)✅ Ambiente configurado!$(NC)"

docker-clean: ## Limpa containers e imagens Docker
	@echo "$(YELLOW)🐳 Limpando Docker...$(NC)"
	$(DOCKER_COMPOSE) down --rmi all --volumes --remove-orphans
	$(DOCKER) system prune -f
	@echo "$(GREEN)✅ Docker limpo!$(NC)"

logs: ## Mostra logs do Docker
	@echo "$(YELLOW)📋 Mostrando logs...$(NC)"
	$(DOCKER_COMPOSE) logs -f

status: ## Mostra status dos containers
	@echo "$(YELLOW)📊 Status dos containers...$(NC)"
	$(DOCKER_COMPOSE) ps

# Comando padrão
.DEFAULT_GOAL := help
