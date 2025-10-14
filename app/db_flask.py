"""
Conexão MongoDB para Flask
"""
import os
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
import asyncio

logger = logging.getLogger(__name__)

class MongoDBConnection:
    """Classe para gerenciar conexão MongoDB"""
    
    def __init__(self):
        self.client = None
        self.db = None
        self.async_client = None
        self.async_db = None
        
    def connect_sync(self):
        """Conecta ao MongoDB de forma síncrona (para Flask)"""
        try:
            mongodb_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
            mongodb_db = os.getenv("MONGODB_DB", "vaiterplay")
            
            self.client = MongoClient(mongodb_uri)
            self.db = self.client[mongodb_db]
            
            # Testa a conexão
            self.client.admin.command('ping')
            logger.info("Conectado ao MongoDB (sync) com sucesso!")
            
        except Exception as e:
            logger.error(f"Erro ao conectar ao MongoDB (sync): {e}")
            raise
    
    async def connect_async(self):
        """Conecta ao MongoDB de forma assíncrona"""
        try:
            mongodb_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
            mongodb_db = os.getenv("MONGODB_DB", "vaiterplay")
            
            self.async_client = AsyncIOMotorClient(mongodb_uri)
            self.async_db = self.async_client[mongodb_db]
            
            # Testa a conexão
            await self.async_client.admin.command('ping')
            logger.info("Conectado ao MongoDB (async) com sucesso!")
            
        except Exception as e:
            logger.error(f"Erro ao conectar ao MongoDB (async): {e}")
            raise
    
    def close_sync(self):
        """Fecha conexão síncrona"""
        if self.client:
            self.client.close()
            logger.info("Conexão MongoDB (sync) fechada")
    
    async def close_async(self):
        """Fecha conexão assíncrona"""
        if self.async_client:
            self.async_client.close()
            logger.info("Conexão MongoDB (async) fechada")
    
    def get_collection(self, collection_name: str):
        """Retorna uma coleção MongoDB"""
        if not self.db:
            raise RuntimeError("Database não foi inicializada. Chame connect_sync() primeiro.")
        return self.db[collection_name]
    
    async def get_async_collection(self, collection_name: str):
        """Retorna uma coleção MongoDB assíncrona"""
        if not self.async_db:
            raise RuntimeError("Database async não foi inicializada. Chame connect_async() primeiro.")
        return self.async_db[collection_name]

# Instância global
mongodb = MongoDBConnection()
