#!/usr/bin/env python3
"""
Script para limpar arquivos desnecessários do projeto
Mantém apenas os arquivos essenciais para produção
"""

import os
import shutil

def remove_file_or_dir(path):
    """Remove arquivo ou diretório"""
    try:
        if os.path.exists(path):
            if os.path.isdir(path):
                shutil.rmtree(path)
                print(f"✅ Diretório removido: {path}")
            else:
                os.remove(path)
                print(f"✅ Arquivo removido: {path}")
        else:
            print(f"ℹ️  Não encontrado: {path}")
    except Exception as e:
        print(f"❌ Erro ao remover {path}: {e}")

def main():
    print("🧹 Limpando arquivos desnecessários do projeto...")
    
    # Arquivos essenciais para manter
    essential_files = [
        "main_flask_single.py",  # Arquivo principal
        "requirements-flask.txt",  # Dependências
        "render.yaml",  # Configuração do Render
        "runtime.txt",  # Versão do Python
        "Procfile",  # Comando de start
        "README.md",  # Documentação
        ".env.example",  # Exemplo de variáveis
    ]
    
    # Arquivos/diretórios para remover
    files_to_remove = [
        # Scripts de migração e teste (já executados)
        "migrate_simple.py",
        "migrate_to_multi_tenant.py", 
        "refactor_system.py",
        "simplify_system.py",
        "clean_and_recreate.py",
        "analyze_courts.py",
        "validate_data.py",
        "test_multi_tenant.py",
        "test_simplified_logic.py",
        "test_system.py",
        "test_groq_integration.py",
        
        # Arquivos antigos do FastAPI
        "app/",
        "populate_db.py",
        
        # Múltiplos requirements (manter apenas flask)
        "requirements.txt",
        "requirements-basic.txt",
        "requirements-minimal.txt",
        "requirements-render.txt",
        "requirements-stable.txt",
        "requirements-ultra-minimal.txt",
        
        # Configurações antigas do Render
        "render-build.config",
        "render-simple.config", 
        "render.config",
        
        # Scripts de start antigos
        "run.sh",
        "start.sh",
        
        # Documentação de troubleshooting (não necessária em produção)
        "COMPATIBILIDADE_PYTHON.md",
        "CONFLITO_DEPENDENCIAS.md",
        "CORRECAO_IMPORT.md",
        "DEPLOY_GUIDE.md",
        "DEPLOY.md",
        "MONGODB_INTEGRADO.md",
        "RENDER_TROUBLESHOOTING.md",
        "RUST_ERROR_SOLUTION.md",
        "SOLUCAO_DEFINITIVA.md",
        "SOLUCAO_FINAL_FLASK.md",
        "SOLUCAO_FINAL.md",
        "SOLUCAO_FLASK.md",
        "VERSOES_INEXISTENTES.md",
        
        # Cache do Python
        "__pycache__/",
    ]
    
    print(f"\n📋 Arquivos essenciais mantidos:")
    for file in essential_files:
        if os.path.exists(file):
            print(f"   ✅ {file}")
        else:
            print(f"   ⚠️  {file} (não encontrado)")
    
    print(f"\n🗑️  Removendo arquivos desnecessários:")
    for file in files_to_remove:
        remove_file_or_dir(file)
    
    # Verificar estrutura final
    print(f"\n📊 Estrutura final do projeto:")
    remaining_files = []
    for item in os.listdir("."):
        if os.path.isfile(item) and not item.startswith("."):
            remaining_files.append(item)
        elif os.path.isdir(item) and not item.startswith("."):
            remaining_files.append(f"{item}/")
    
    remaining_files.sort()
    for item in remaining_files:
        print(f"   📁 {item}")
    
    print(f"\n✅ Limpeza concluída!")
    print(f"🎯 Projeto agora contém apenas arquivos essenciais:")
    print(f"   - main_flask_single.py (aplicação principal)")
    print(f"   - requirements-flask.txt (dependências)")
    print(f"   - render.yaml (configuração deploy)")
    print(f"   - runtime.txt (versão Python)")
    print(f"   - Procfile (comando start)")
    print(f"   - README.md (documentação)")
    print(f"   - .env.example (exemplo variáveis)")

if __name__ == "__main__":
    main()
