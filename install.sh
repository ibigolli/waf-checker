#!/bin/bash

# Script de instalação rápida para o Sistema de Verificação de WAF
# Uso: ./install.sh [opção]

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para mostrar ajuda
show_help() {
    echo -e "${BLUE}Sistema de Verificação de WAF - Instalação${NC}"
    echo ""
    echo "Uso: $0 [opção]"
    echo ""
    echo "Opções:"
    echo "  local     - Instala dependências para execução local"
    echo "  docker    - Instala Docker e Docker Compose"
    echo "  all       - Instala tudo (padrão)"
    echo "  help      - Mostra esta ajuda"
    echo ""
    echo "Exemplos:"
    echo "  $0 local      # Instala apenas dependências Python"
    echo "  $0 docker     # Instala apenas Docker"
    echo "  $0 all        # Instala tudo"
    echo ""
}

# Função para verificar se comando existe
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Função para instalar dependências Python
install_python_deps() {
    echo -e "${YELLOW}🐍 Instalando dependências Python...${NC}"
    
    if ! command_exists python3; then
        echo -e "${RED}❌ Python 3 não encontrado. Instale Python 3.11+ primeiro.${NC}"
        return 1
    fi
    
    if ! command_exists pip3; then
        echo -e "${RED}❌ pip3 não encontrado. Instale pip primeiro.${NC}"
        return 1
    fi
    
    echo -e "${YELLOW}📦 Instalando dependências do requirements.txt...${NC}"
    pip3 install -r requirements.txt
    
    echo -e "${GREEN}✅ Dependências Python instaladas com sucesso!${NC}"
}

# Função para instalar Docker
install_docker() {
    echo -e "${YELLOW}🐳 Instalando Docker...${NC}"
    
    if command_exists docker; then
        echo -e "${GREEN}✅ Docker já está instalado${NC}"
    else
        echo -e "${YELLOW}📥 Baixando script de instalação do Docker...${NC}"
        curl -fsSL https://get.docker.com -o get-docker.sh
        sudo sh get-docker.sh
        sudo usermod -aG docker $USER
        rm get-docker.sh
        echo -e "${GREEN}✅ Docker instalado com sucesso!${NC}"
        echo -e "${YELLOW}⚠️  Você precisa fazer logout e login novamente para usar Docker sem sudo${NC}"
    fi
    
    if command_exists docker-compose; then
        echo -e "${GREEN}✅ Docker Compose já está instalado${NC}"
    else
        echo -e "${YELLOW}📥 Instalando Docker Compose...${NC}"
        sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
        sudo chmod +x /usr/local/bin/docker-compose
        echo -e "${GREEN}✅ Docker Compose instalado com sucesso!${NC}"
    fi
}

# Função para configurar ambiente
setup_environment() {
    echo -e "${YELLOW}⚙️  Configurando ambiente...${NC}"
    
    # Criar diretórios necessários
    mkdir -p output input
    
    # Copiar arquivo de exemplo de ambiente
    if [ ! -f .env ]; then
        cp env.example .env
        echo -e "${YELLOW}📝 Arquivo .env criado. Edite com suas credenciais AWS.${NC}"
    else
        echo -e "${GREEN}✅ Arquivo .env já existe${NC}"
    fi
    
    # Tornar scripts executáveis
    chmod +x run_docker.sh
    
    echo -e "${GREEN}✅ Ambiente configurado com sucesso!${NC}"
}

# Função para verificar instalação
verify_installation() {
    echo -e "${YELLOW}🔍 Verificando instalação...${NC}"
    
    # Verificar Python
    if command_exists python3; then
        echo -e "${GREEN}✅ Python 3: $(python3 --version)${NC}"
    else
        echo -e "${RED}❌ Python 3 não encontrado${NC}"
    fi
    
    # Verificar pip
    if command_exists pip3; then
        echo -e "${GREEN}✅ pip3: $(pip3 --version)${NC}"
    else
        echo -e "${RED}❌ pip3 não encontrado${NC}"
    fi
    
    # Verificar Docker
    if command_exists docker; then
        echo -e "${GREEN}✅ Docker: $(docker --version)${NC}"
    else
        echo -e "${RED}❌ Docker não encontrado${NC}"
    fi
    
    # Verificar Docker Compose
    if command_exists docker-compose; then
        echo -e "${GREEN}✅ Docker Compose: $(docker-compose --version)${NC}"
    else
        echo -e "${RED}❌ Docker Compose não encontrado${NC}"
    fi
    
    # Verificar arquivos de configuração
    if [ -f .env ]; then
        echo -e "${GREEN}✅ Arquivo .env configurado${NC}"
    else
        echo -e "${YELLOW}⚠️  Arquivo .env não encontrado${NC}"
    fi
    
    if [ -f requirements.txt ]; then
        echo -e "${GREEN}✅ requirements.txt encontrado${NC}"
    else
        echo -e "${RED}❌ requirements.txt não encontrado${NC}"
    fi
}

# Função para mostrar próximos passos
show_next_steps() {
    echo -e "${BLUE}🎯 Próximos Passos:${NC}"
    echo ""
    echo "1. Configure suas credenciais AWS:"
    echo "   - Edite o arquivo .env"
    echo "   - Ou configure via AWS CLI: aws configure"
    echo ""
    echo "2. Para execução local:"
    echo "   python3 waf_checker.py --local --local-storage --help"
    echo ""
    echo "3. Para execução Docker:"
    echo "   ./run_docker.sh build"
    echo "   ./run_docker.sh run --help"
    echo ""
    echo "4. Teste o sistema:"
    echo "   python3 test_local.py"
    echo "   ou"
    echo "   ./run_docker.sh test"
    echo ""
    echo "5. Consulte o README.md para mais informações"
}

# Função principal
main() {
    case "${1:-all}" in
        "local")
            echo -e "${BLUE}🚀 Instalando dependências para execução local...${NC}"
            install_python_deps
            setup_environment
            ;;
        "docker")
            echo -e "${BLUE}🚀 Instalando Docker...${NC}"
            install_docker
            setup_environment
            ;;
        "all")
            echo -e "${BLUE}🚀 Instalando tudo...${NC}"
            install_python_deps
            install_docker
            setup_environment
            ;;
        "help"|"--help"|"-h")
            show_help
            exit 0
            ;;
        *)
            echo -e "${RED}❌ Opção inválida: $1${NC}"
            echo ""
            show_help
            exit 1
            ;;
    esac
    
    echo ""
    verify_installation
    echo ""
    show_next_steps
    echo ""
    echo -e "${GREEN}🎉 Instalação concluída com sucesso!${NC}"
}

# Executar função principal
main "$@"
