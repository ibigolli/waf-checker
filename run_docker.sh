#!/bin/bash

# Script para execução do sistema via Docker
# Uso: ./run_docker.sh [comando] [opções]

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para mostrar ajuda
show_help() {
    echo -e "${BLUE}Sistema de Verificação de WAF - Execução Docker${NC}"
    echo ""
    echo "Uso: $0 [comando] [opções]"
    echo ""
    echo "Comandos:"
    echo "  build     - Constrói a imagem Docker"
    echo "  run       - Executa o sistema (padrão)"
    echo "  test      - Executa teste local"
    echo "  help      - Mostra esta ajuda"
    echo ""
    echo "Exemplos:"
    echo "  $0 build                    # Constrói imagem"
    echo "  $0 run --help               # Mostra ajuda do sistema"
    echo "  $0 run --local-storage      # Executa salvando localmente"
    echo "  $0 run --urls-file example_urls.txt --max-urls 5"
    echo ""
}

# Função para construir imagem
build_image() {
    echo -e "${YELLOW}🔨 Construindo imagem Docker...${NC}"
    docker-compose build
    echo -e "${GREEN}✅ Imagem construída com sucesso!${NC}"
}

# Função para executar sistema
run_system() {
    echo -e "${YELLOW}🚀 Executando sistema de verificação de WAF...${NC}"
    
    # Criar diretórios necessários
    mkdir -p output input
    
    # Executar com docker-compose
    docker-compose run --rm waf-checker "$@"
}

# Função para teste local
run_test() {
    echo -e "${YELLOW}🧪 Executando teste local...${NC}"
    docker-compose run --rm waf-checker python test_local.py
}

# Verificar se Docker está rodando
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        echo -e "${RED}❌ Docker não está rodando ou não está instalado${NC}"
        exit 1
    fi
}

# Função principal
main() {
    check_docker
    
    case "${1:-run}" in
        "build")
            build_image
            ;;
        "run")
            shift
            run_system "$@"
            ;;
        "test")
            run_test
            ;;
        "help"|"--help"|"-h")
            show_help
            ;;
        *)
            echo -e "${RED}❌ Comando inválido: $1${NC}"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# Executar função principal
main "$@"
