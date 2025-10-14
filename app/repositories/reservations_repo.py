"""
Repositório CRUD para Reservas
"""
from typing import List, Optional
from bson import ObjectId
from datetime import datetime
import logging

from app.db import get_database
from app.models.reservation import Reservation, ReservationCreate, ReservationUpdate, ReservationResponse
from app.models.user import User

logger = logging.getLogger(__name__)


class ReservationsRepository:
    """Repositório para operações com reservas"""
    
    def __init__(self):
        self.collection_name = "reservas"
    
    def _get_collection(self):
        """Retorna a coleção de reservas"""
        db = get_database()
        return db[self.collection_name]
    
    async def create(self, reservation_data: ReservationCreate) -> Reservation:
        """Cria uma nova reserva"""
        try:
            collection = self._get_collection()
            reservation_dict = reservation_data.dict()
            reservation_dict["criado_em"] = datetime.now()
            
            result = await collection.insert_one(reservation_dict)
            reservation_dict["_id"] = str(result.inserted_id)
            
            logger.info(f"Reserva criada para {reservation_dict['usuario']['nome']}")
            return Reservation(**reservation_dict)
            
        except Exception as e:
            logger.error(f"Erro ao criar reserva: {e}")
            raise
    
    async def get_by_id(self, reservation_id: str) -> Optional[Reservation]:
        """Busca reserva por ID"""
        try:
            collection = self._get_collection()
            reservation_doc = await collection.find_one({"_id": ObjectId(reservation_id)})
            
            if reservation_doc:
                reservation_doc["_id"] = str(reservation_doc["_id"])
                return Reservation(**reservation_doc)
            
            return None
            
        except Exception as e:
            logger.error(f"Erro ao buscar reserva {reservation_id}: {e}")
            raise
    
    async def get_by_user_phone(self, phone: str) -> List[ReservationResponse]:
        """Busca reservas por telefone do usuário"""
        try:
            collection = self._get_collection()
            reservations = []
            
            # Busca reservas do usuário
            async for reservation_doc in collection.find({
                "usuario.telefone": phone,
                "status": {"$ne": "cancelada"}
            }).sort("data_reserva", 1):
                
                reservation_doc["_id"] = str(reservation_doc["_id"])
                reservation = Reservation(**reservation_doc)
                
                # Busca dados da quadra
                from app.repositories.courts_repo import courts_repo
                court = await courts_repo.get_by_id(reservation.quadra_id)
                
                if court:
                    reservation_response = ReservationResponse(
                        id=reservation.id,
                        usuario=reservation.usuario,
                        quadra_nome=court.nome,
                        quadra_tipo=court.tipo,
                        data_reserva=reservation.data_reserva,
                        quantidade_horas=getattr(reservation, 'quantidade_horas', 1),
                        status=reservation.status,
                        criado_em=reservation.criado_em,
                        valor_hora=court.valor_hora,
                        valor_total=court.valor_hora * getattr(reservation, 'quantidade_horas', 1)
                    )
                    reservations.append(reservation_response)
            
            return reservations
            
        except Exception as e:
            logger.error(f"Erro ao buscar reservas por telefone {phone}: {e}")
            raise
    
    async def get_by_court_and_time(self, court_id: str, datetime_reservation: datetime) -> Optional[Reservation]:
        """Busca reserva por quadra e horário"""
        try:
            collection = self._get_collection()
            
            # Busca reserva no mesmo horário
            reservation_doc = await collection.find_one({
                "quadra_id": court_id,
                "data_reserva": {
                    "$gte": datetime_reservation,
                    "$lt": datetime_reservation.replace(hour=datetime_reservation.hour + 1)
                },
                "status": {"$ne": "cancelada"}
            })
            
            if reservation_doc:
                reservation_doc["_id"] = str(reservation_doc["_id"])
                return Reservation(**reservation_doc)
            
            return None
            
        except Exception as e:
            logger.error(f"Erro ao buscar reserva por quadra e horário: {e}")
            raise
    
    async def get_all(self) -> List[Reservation]:
        """Lista todas as reservas"""
        try:
            collection = self._get_collection()
            reservations = []
            
            async for reservation_doc in collection.find():
                reservation_doc["_id"] = str(reservation_doc["_id"])
                reservations.append(Reservation(**reservation_doc))
            
            return reservations
            
        except Exception as e:
            logger.error(f"Erro ao listar reservas: {e}")
            raise
    
    async def update(self, reservation_id: str, reservation_data: ReservationUpdate) -> Optional[Reservation]:
        """Atualiza uma reserva"""
        try:
            collection = self._get_collection()
            update_data = {k: v for k, v in reservation_data.dict().items() if v is not None}
            
            if not update_data:
                return await self.get_by_id(reservation_id)
            
            await collection.update_one(
                {"_id": ObjectId(reservation_id)},
                {"$set": update_data}
            )
            
            logger.info(f"Reserva atualizada: {reservation_id}")
            return await self.get_by_id(reservation_id)
            
        except Exception as e:
            logger.error(f"Erro ao atualizar reserva {reservation_id}: {e}")
            raise
    
    async def cancel_by_user_and_time(self, phone: str, datetime_reservation: datetime) -> bool:
        """Cancela reserva por telefone e horário"""
        try:
            collection = self._get_collection()
            
            result = await collection.update_one(
                {
                    "usuario.telefone": phone,
                    "data_reserva": {
                        "$gte": datetime_reservation,
                        "$lt": datetime_reservation.replace(hour=datetime_reservation.hour + 1)
                    },
                    "status": "confirmada"
                },
                {"$set": {"status": "cancelada"}}
            )
            
            if result.modified_count > 0:
                logger.info(f"Reserva cancelada para {phone}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Erro ao cancelar reserva: {e}")
            raise
    
    async def delete(self, reservation_id: str) -> bool:
        """Remove uma reserva"""
        try:
            collection = self._get_collection()
            result = await collection.delete_one({"_id": ObjectId(reservation_id)})
            
            if result.deleted_count > 0:
                logger.info(f"Reserva removida: {reservation_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Erro ao remover reserva {reservation_id}: {e}")
            raise


# Instância global do repositório
reservations_repo = ReservationsRepository()
