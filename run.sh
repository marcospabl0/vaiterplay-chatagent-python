#!/bin/bash

# Script para executar o projeto Genia Quadras
# Uso: ./run.sh [comando]

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para imprimir mensagens coloridas
print_message() {
    echo -e "${GREEN}[GENIA-QUADRAS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

# Verifica se o Python está instalado
check_python() {
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 não está instalado!"
        exit 1
    fi
    
    python_version=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
    if [[ $(echo "$python_version < 3.8" | bc -l) -eq 1 ]]; then
        print_error "Python 3.8+ é necessário. Versão atual: $python_version"
        exit 1
    fi
    
    print_info "Python $python_version detectado ✓"
}

# Instala dependências
install_deps() {
    print_message "Instalando dependências..."
    
    if [ ! -f "requirements.txt" ]; then
        print_error "Arquivo requirements.txt não encontrado!"
        exit 1
    fi
    
    pip3 install -r requirements.txt
    print_message "Dependências instaladas ✓"
}

# Verifica arquivo .env
check_env() {
    if [ ! -f ".env" ]; then
        print_warning "Arquivo .env não encontrado!"
        print_info "Copiando env.example para .env..."
        cp env.example .env
        print_warning "Configure suas variáveis no arquivo .env antes de continuar!"
        print_info "Edite o arquivo .env com suas credenciais do MongoDB e Twilio"
        exit 1
    fi
    
    print_info "Arquivo .env encontrado ✓"
}

# Executa a aplicação
run_app() {
    print_message "Iniciando aplicação Genia Quadras..."
    print_info "Acesse: http://localhost:8000"
    print_info "Documentação: http://localhost:8000/docs"
    print_info "Para parar: Ctrl+C"
    echo ""
    
    python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
}

# Executa testes
run_tests() {
    print_message "Executando testes..."
    
    # Teste básico da API
    print_info "Testando endpoint de health check..."
    curl -s http://localhost:8000/health || print_error "API não está respondendo!"
    
    print_info "Testando endpoint raiz..."
    curl -s http://localhost:8000/ || print_error "API não está respondendo!"
    
    print_message "Testes concluídos ✓"
}

# Popula banco com dados de exemplo
populate_db() {
    print_message "Populando banco de dados com dados de exemplo..."
    python3 populate_db.py
    print_message "Banco populado ✓"
}

# Executa testes completos do sistema
test_system() {
    print_message "Executando testes completos do sistema..."
    python3 test_system.py
    print_message "Testes do sistema concluídos ✓"
}

# Mostra ajuda
show_help() {
    echo "Genia Quadras - Script de Execução"
    echo ""
    echo "Uso: ./run.sh [comando]"
    echo ""
    echo "Comandos disponíveis:"
    echo "  install    - Instala dependências Python"
    echo "  run        - Executa a aplicação (padrão)"
    echo "  test       - Executa testes básicos"
    echo "  populate   - Popula banco com dados de exemplo"
    echo "  test-system - Executa testes completos do sistema"
    echo "  help       - Mostra esta ajuda"
    echo ""
    echo "Exemplos:"
    echo "  ./run.sh install"
    echo "  ./run.sh run"
    echo "  ./run.sh test"
}

# Função principal
main() {
    local command=${1:-run}
    
    print_message "=== Genia Quadras - Agente WhatsApp ==="
    echo ""
    
    case $command in
        "install")
            check_python
            install_deps
            ;;
        "run")
            check_python
            check_env
            run_app
            ;;
        "test")
            run_tests
            ;;
        "populate")
            check_python
            check_env
            populate_db
            ;;
        "test-system")
            check_python
            test_system
            ;;
        "help"|"-h"|"--help")
            show_help
            ;;
        *)
            print_error "Comando desconhecido: $command"
            show_help
            exit 1
            ;;
    esac
}

# Executa função principal
main "$@"
