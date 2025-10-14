"""
Repositórios para operações CRUD com MongoDB
"""
import logging
from datetime import datetime
from typing import List, Optional
from .db_flask import mongodb
from .models_flask import User, Court, Reservation

logger = logging.getLogger(__name__)

class UserRepository:
    """Repositório para operações de usuários"""
    
    def __init__(self):
        self.collection_name = "usuarios"
    
    def get_collection(self):
        """Retorna a coleção de usuários"""
        return mongodb.get_collection(self.collection_name)
    
    def create(self, user: User) -> str:
        """Cria um novo usuário"""
        try:
            collection = self.get_collection()
            result = collection.insert_one(user.to_dict())
            logger.info(f"Usuário criado com ID: {result.inserted_id}")
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Erro ao criar usuário: {e}")
            raise
    
    def get_by_phone(self, phone: str) -> Optional[User]:
        """Busca usuário por telefone"""
        try:
            collection = self.get_collection()
            user_data = collection.find_one({"telefone": phone})
            if user_data:
                return User.from_dict(user_data)
            return None
        except Exception as e:
            logger.error(f"Erro ao buscar usuário por telefone: {e}")
            raise
    
    def find_or_create_by_phone(self, phone: str, name: str = "Usuário") -> User:
        """Busca ou cria usuário por telefone"""
        try:
            user = self.get_by_phone(phone)
            if not user:
                user = User(nome=name, telefone=phone)
                user_id = self.create(user)
                user._id = user_id
            return user
        except Exception as e:
            logger.error(f"Erro ao buscar/criar usuário: {e}")
            raise

class CourtRepository:
    """Repositório para operações de quadras"""
    
    def __init__(self):
        self.collection_name = "quadras"
    
    def get_collection(self):
        """Retorna a coleção de quadras"""
        return mongodb.get_collection(self.collection_name)
    
    def create(self, court: Court) -> str:
        """Cria uma nova quadra"""
        try:
            collection = self.get_collection()
            result = collection.insert_one(court.to_dict())
            logger.info(f"Quadra criada com ID: {result.inserted_id}")
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Erro ao criar quadra: {e}")
            raise
    
    def get_all(self) -> List[Court]:
        """Busca todas as quadras"""
        try:
            collection = self.get_collection()
            courts = []
            for court_data in collection.find():
                courts.append(Court.from_dict(court_data))
            return courts
        except Exception as e:
            logger.error(f"Erro ao buscar quadras: {e}")
            raise
    
    def get_by_id(self, court_id: str) -> Optional[Court]:
        """Busca quadra por ID"""
        try:
            from bson import ObjectId
            collection = self.get_collection()
            court_data = collection.find_one({"_id": ObjectId(court_id)})
            if court_data:
                return Court.from_dict(court_data)
            return None
        except Exception as e:
            logger.error(f"Erro ao buscar quadra por ID: {e}")
            raise
    
    def get_available_at_time(self, datetime_obj: datetime) -> List[Court]:
        """Busca quadras disponíveis em um horário"""
        try:
            collection = self.get_collection()
            courts = []
            
            for court_data in collection.find():
                court = Court.from_dict(court_data)
                # Verifica se o horário está na lista de disponíveis
                datetime_str = datetime_obj.isoformat()
                if datetime_str in court.horarios_disponiveis:
                    courts.append(court)
            
            return courts
        except Exception as e:
            logger.error(f"Erro ao buscar quadras disponíveis: {e}")
            raise

class ReservationRepository:
    """Repositório para operações de reservas"""
    
    def __init__(self):
        self.collection_name = "reservas"
    
    def get_collection(self):
        """Retorna a coleção de reservas"""
        return mongodb.get_collection(self.collection_name)
    
    def create(self, reservation: Reservation) -> str:
        """Cria uma nova reserva"""
        try:
            collection = self.get_collection()
            result = collection.insert_one(reservation.to_dict())
            logger.info(f"Reserva criada com ID: {result.inserted_id}")
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Erro ao criar reserva: {e}")
            raise
    
    def get_by_user_phone(self, phone: str) -> List[dict]:
        """Busca reservas de um usuário por telefone"""
        try:
            collection = self.get_collection()
            reservations = []
            
            for reservation_data in collection.find({"usuario.telefone": phone}):
                reservation = Reservation.from_dict(reservation_data)
                
                # Busca dados da quadra
                court_repo = CourtRepository()
                court = court_repo.get_by_id(reservation.quadra_id)
                
                if court:
                    reservation_dict = reservation.to_dict()
                    reservation_dict["quadra_nome"] = court.nome
                    reservation_dict["quadra_tipo"] = court.tipo
                    reservation_dict["valor_hora"] = court.valor_hora
                    reservation_dict["valor_total"] = court.valor_hora * reservation.quantidade_horas
                    reservations.append(reservation_dict)
            
            return reservations
        except Exception as e:
            logger.error(f"Erro ao buscar reservas por telefone: {e}")
            raise
    
    def get_by_court_and_time(self, court_id: str, datetime_obj: datetime) -> Optional[Reservation]:
        """Busca reserva por quadra e horário"""
        try:
            collection = self.get_collection()
            reservation_data = collection.find_one({
                "quadra_id": court_id,
                "data_reserva": datetime_obj.isoformat()
            })
            
            if reservation_data:
                return Reservation.from_dict(reservation_data)
            return None
        except Exception as e:
            logger.error(f"Erro ao buscar reserva por quadra e horário: {e}")
            raise

# Instâncias globais
user_repo = UserRepository()
court_repo = CourtRepository()
reservation_repo = ReservationRepository()
