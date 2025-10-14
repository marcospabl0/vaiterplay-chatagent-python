"""
Repositório CRUD para Quadras
"""
from typing import List, Optional
from bson import ObjectId
from datetime import datetime
import logging

from app.db import get_database
from app.models.court import Court, CourtCreate, CourtUpdate

logger = logging.getLogger(__name__)


class CourtsRepository:
    """Repositório para operações com quadras"""
    
    def __init__(self):
        self.collection_name = "quadras"
    
    def _get_collection(self):
        """Retorna a coleção de quadras"""
        db = get_database()
        return db[self.collection_name]
    
    async def create(self, court_data: CourtCreate) -> Court:
        """Cria uma nova quadra"""
        try:
            collection = self._get_collection()
            court_dict = court_data.dict()
            
            result = await collection.insert_one(court_dict)
            court_dict["_id"] = str(result.inserted_id)
            
            logger.info(f"Quadra criada: {court_dict['nome']}")
            return Court(**court_dict)
            
        except Exception as e:
            logger.error(f"Erro ao criar quadra: {e}")
            raise
    
    async def get_by_id(self, court_id: str) -> Optional[Court]:
        """Busca quadra por ID"""
        try:
            collection = self._get_collection()
            court_doc = await collection.find_one({"_id": ObjectId(court_id)})
            
            if court_doc:
                court_doc["_id"] = str(court_doc["_id"])
                return Court(**court_doc)
            
            return None
            
        except Exception as e:
            logger.error(f"Erro ao buscar quadra {court_id}: {e}")
            raise
    
    async def get_all(self) -> List[Court]:
        """Lista todas as quadras"""
        try:
            collection = self._get_collection()
            courts = []
            
            async for court_doc in collection.find():
                court_doc["_id"] = str(court_doc["_id"])
                courts.append(Court(**court_doc))
            
            return courts
            
        except Exception as e:
            logger.error(f"Erro ao listar quadras: {e}")
            raise
    
    async def get_by_type(self, court_type: str) -> List[Court]:
        """Busca quadras por tipo"""
        try:
            collection = self._get_collection()
            courts = []
            
            async for court_doc in collection.find({"tipo": {"$regex": court_type, "$options": "i"}}):
                court_doc["_id"] = str(court_doc["_id"])
                courts.append(Court(**court_doc))
            
            return courts
            
        except Exception as e:
            logger.error(f"Erro ao buscar quadras por tipo {court_type}: {e}")
            raise
    
    async def get_available_at_time(self, datetime_reservation: datetime) -> List[Court]:
        """Busca quadras disponíveis em um horário específico"""
        try:
            collection = self._get_collection()
            courts = []
            
            # Busca quadras que têm o horário na lista de disponíveis
            async for court_doc in collection.find({
                "horarios_disponiveis": {
                    "$elemMatch": {
                        "$gte": datetime_reservation,
                        "$lt": datetime_reservation.replace(hour=datetime_reservation.hour + 1)
                    }
                }
            }):
                court_doc["_id"] = str(court_doc["_id"])
                courts.append(Court(**court_doc))
            
            return courts
            
        except Exception as e:
            logger.error(f"Erro ao buscar quadras disponíveis: {e}")
            raise
    
    async def update(self, court_id: str, court_data: CourtUpdate) -> Optional[Court]:
        """Atualiza uma quadra"""
        try:
            collection = self._get_collection()
            update_data = {k: v for k, v in court_data.dict().items() if v is not None}
            
            if not update_data:
                return await self.get_by_id(court_id)
            
            await collection.update_one(
                {"_id": ObjectId(court_id)},
                {"$set": update_data}
            )
            
            logger.info(f"Quadra atualizada: {court_id}")
            return await self.get_by_id(court_id)
            
        except Exception as e:
            logger.error(f"Erro ao atualizar quadra {court_id}: {e}")
            raise
    
    async def delete(self, court_id: str) -> bool:
        """Remove uma quadra"""
        try:
            collection = self._get_collection()
            result = await collection.delete_one({"_id": ObjectId(court_id)})
            
            if result.deleted_count > 0:
                logger.info(f"Quadra removida: {court_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Erro ao remover quadra {court_id}: {e}")
            raise


# Instância global do repositório
courts_repo = CourtsRepository()
