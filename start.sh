#!/bin/bash
# Script de inicialização para produção no Render

echo "🚀 Iniciando Genia Quadras em produção..."

# Instala dependências
echo "📦 Instalando dependências..."
pip install -r requirements.txt

# Popula banco de dados se necessário
echo "🗄️ Verificando banco de dados..."
python3 -c "
import asyncio
import os
from app.db import connect_to_mongo, close_mongo_connection
from app.repositories.courts_repo import courts_repo

async def check_db():
    await connect_to_mongo()
    courts = await courts_repo.get_all()
    if not courts:
        print('📋 Populando banco com dados iniciais...')
        os.system('python3 populate_db.py')
    else:
        print(f'✅ Banco já possui {len(courts)} quadras')
    await close_mongo_connection()

asyncio.run(check_db())
"

# Inicia a aplicação
echo "🏃 Iniciando aplicação..."
uvicorn app.main:app --host 0.0.0.0 --port $PORT
