"""
Conexão com MongoDB usando Motor (async driver)
"""
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.settings import settings
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Cliente MongoDB global
client: Optional[AsyncIOMotorClient] = None
database: Optional[AsyncIOMotorDatabase] = None


async def connect_to_mongo():
    """Conecta ao MongoDB"""
    global client, database
    
    try:
        client = AsyncIOMotorClient(settings.MONGODB_URI)
        database = client[settings.MONGODB_DB]
        
        # Testa a conexão
        await client.admin.command('ping')
        logger.info("Conectado ao MongoDB com sucesso!")
        
    except Exception as e:
        logger.error(f"Erro ao conectar ao MongoDB: {e}")
        raise


async def close_mongo_connection():
    """Fecha a conexão com MongoDB"""
    global client
    
    if client:
        client.close()
        logger.info("Conexão com MongoDB fechada")


def get_database() -> AsyncIOMotorDatabase:
    """Retorna a instância do banco de dados"""
    if database is None:
        raise RuntimeError("Database não foi inicializada. Chame connect_to_mongo() primeiro.")
    return database
