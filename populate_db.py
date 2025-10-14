"""
Script para popular o banco de dados com dados iniciais
"""
import asyncio
from datetime import datetime, timedelta
from app.db import connect_to_mongo, close_mongo_connection
from app.repositories.courts_repo import courts_repo
from app.models.court import CourtCreate, Endereco

async def populate_courts():
    """Popula o banco com quadras de exemplo"""
    
    # Conecta ao banco
    await connect_to_mongo()
    
    # Dados das quadras
    courts_data = [
        {
            "nome": "Quadra 1 - Futebol Society",
            "tipo": "Futebol Society",
            "endereco": {
                "logradouro": "Av. das Flores, 100",
                "bairro": "Centro",
                "cidade": "Porto Alegre"
            },
            "valor_hora": 120.0,
            "horarios_disponiveis": []
        },
        {
            "nome": "Quadra 2 - Futsal",
            "tipo": "Futsal",
            "endereco": {
                "logradouro": "Rua da Paz, 250",
                "bairro": "Vila Nova",
                "cidade": "Porto Alegre"
            },
            "valor_hora": 100.0,
            "horarios_disponiveis": []
        },
        {
            "nome": "Quadra 3 - Vôlei",
            "tipo": "Vôlei",
            "endereco": {
                "logradouro": "Av. Brasil, 500",
                "bairro": "Cidade Baixa",
                "cidade": "Porto Alegre"
            },
            "valor_hora": 80.0,
            "horarios_disponiveis": []
        },
        {
            "nome": "Quadra 4 - Basquete",
            "tipo": "Basquete",
            "endereco": {
                "logradouro": "Rua dos Esportes, 75",
                "bairro": "Boa Vista",
                "cidade": "Porto Alegre"
            },
            "valor_hora": 90.0,
            "horarios_disponiveis": []
        }
    ]
    
    # Gera horários disponíveis para os próximos 7 dias (hora em hora)
    base_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    available_hours = list(range(8, 22))  # Horários de 8h às 21h (hora em hora)
    
    for court_data in courts_data:
        # Gera horários para os próximos 7 dias
        horarios = []
        for day in range(7):
            for hour in available_hours:
                horario = base_date + timedelta(days=day, hours=hour)
                horarios.append(horario)
        
        court_data["horarios_disponiveis"] = horarios
        
        # Cria a quadra
        court_create = CourtCreate(**court_data)
        court = await courts_repo.create(court_create)
        print(f"✅ Quadra criada: {court.nome}")
    
    print(f"\n🎉 {len(courts_data)} quadras criadas com sucesso!")
    print("📅 Horários disponíveis gerados para os próximos 7 dias")
    
    # Fecha conexão
    await close_mongo_connection()

if __name__ == "__main__":
    print("🏟️ Populando banco de dados com quadras de exemplo...")
    asyncio.run(populate_courts())
