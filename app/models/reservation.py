"""
Modelos Pydantic para Reservas
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from bson import ObjectId
from app.models.user import User


class Reservation(BaseModel):
    """Modelo para Reserva"""
    id: Optional[str] = Field(alias="_id", default=None)
    usuario: User
    quadra_id: str
    data_reserva: datetime
    quantidade_horas: int = 1  # Quantidade de horas reservadas
    status: str = "confirmada"  # confirmada, cancelada, concluida
    criado_em: Optional[datetime] = None
    
    class Config:
        populate_by_name = True
        json_encoders = {
            ObjectId: str,
            datetime: lambda v: v.isoformat()
        }


class ReservationCreate(BaseModel):
    """Modelo para criação de reserva"""
    usuario: User
    quadra_id: str
    data_reserva: datetime
    quantidade_horas: int = 1
    status: str = "confirmada"


class ReservationUpdate(BaseModel):
    """Modelo para atualização de reserva"""
    status: Optional[str] = None


class ReservationResponse(BaseModel):
    """Modelo para resposta de reserva com dados da quadra"""
    id: str
    usuario: User
    quadra_nome: str
    quadra_tipo: str
    data_reserva: datetime
    quantidade_horas: int
    status: str
    criado_em: datetime
    valor_hora: float
    valor_total: float  # valor_hora * quantidade_horas
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
