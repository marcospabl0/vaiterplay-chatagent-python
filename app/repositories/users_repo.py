"""
Repositório CRUD para Usuários
"""
from typing import List, Optional
from bson import ObjectId
import logging

from app.db import get_database
from app.models.user import User, UserCreate, UserUpdate

logger = logging.getLogger(__name__)


class UsersRepository:
    """Repositório para operações com usuários"""
    
    def __init__(self):
        self.collection_name = "usuarios"
    
    def _get_collection(self):
        """Retorna a coleção de usuários"""
        db = get_database()
        return db[self.collection_name]
    
    async def create(self, user_data: UserCreate) -> User:
        """Cria um novo usuário"""
        try:
            collection = self._get_collection()
            user_dict = user_data.dict()
            
            result = await collection.insert_one(user_dict)
            user_dict["_id"] = str(result.inserted_id)
            
            logger.info(f"Usuário criado: {user_dict['nome']}")
            return User(**user_dict)
            
        except Exception as e:
            logger.error(f"Erro ao criar usuário: {e}")
            raise
    
    async def get_by_id(self, user_id: str) -> Optional[User]:
        """Busca usuário por ID"""
        try:
            collection = self._get_collection()
            user_doc = await collection.find_one({"_id": ObjectId(user_id)})
            
            if user_doc:
                user_doc["_id"] = str(user_doc["_id"])
                return User(**user_doc)
            
            return None
            
        except Exception as e:
            logger.error(f"Erro ao buscar usuário {user_id}: {e}")
            raise
    
    async def get_by_phone(self, phone: str) -> Optional[User]:
        """Busca usuário por telefone"""
        try:
            collection = self._get_collection()
            user_doc = await collection.find_one({"telefone": phone})
            
            if user_doc:
                user_doc["_id"] = str(user_doc["_id"])
                return User(**user_doc)
            
            return None
            
        except Exception as e:
            logger.error(f"Erro ao buscar usuário por telefone {phone}: {e}")
            raise
    
    async def get_all(self) -> List[User]:
        """Lista todos os usuários"""
        try:
            collection = self._get_collection()
            users = []
            
            async for user_doc in collection.find():
                user_doc["_id"] = str(user_doc["_id"])
                users.append(User(**user_doc))
            
            return users
            
        except Exception as e:
            logger.error(f"Erro ao listar usuários: {e}")
            raise
    
    async def update(self, user_id: str, user_data: UserUpdate) -> Optional[User]:
        """Atualiza um usuário"""
        try:
            collection = self._get_collection()
            update_data = {k: v for k, v in user_data.dict().items() if v is not None}
            
            if not update_data:
                return await self.get_by_id(user_id)
            
            await collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": update_data}
            )
            
            logger.info(f"Usuário atualizado: {user_id}")
            return await self.get_by_id(user_id)
            
        except Exception as e:
            logger.error(f"Erro ao atualizar usuário {user_id}: {e}")
            raise
    
    async def delete(self, user_id: str) -> bool:
        """Remove um usuário"""
        try:
            collection = self._get_collection()
            result = await collection.delete_one({"_id": ObjectId(user_id)})
            
            if result.deleted_count > 0:
                logger.info(f"Usuário removido: {user_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Erro ao remover usuário {user_id}: {e}")
            raise
    
    async def find_or_create_by_phone(self, phone: str, name: str = "Usuário") -> User:
        """Busca usuário por telefone ou cria um novo"""
        try:
            # Tenta buscar usuário existente
            user = await self.get_by_phone(phone)
            
            if user:
                return user
            
            # Se não encontrou, cria um novo
            # Garante que o nome não seja None
            user_name = name if name is not None else "Usuário"
            user_data = UserCreate(nome=user_name, telefone=phone)
            return await self.create(user_data)
            
        except Exception as e:
            logger.error(f"Erro ao buscar/criar usuário por telefone {phone}: {e}")
            raise


# Instância global do repositório
users_repo = UsersRepository()
