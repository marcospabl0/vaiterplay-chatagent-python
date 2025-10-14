"""
Modelos Pydantic para Quadras
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from bson import ObjectId


class Endereco(BaseModel):
    """Modelo para endereço da quadra"""
    logradouro: str
    bairro: str
    cidade: str


class Court(BaseModel):
    """Modelo para Quadra"""
    id: Optional[str] = Field(alias="_id", default=None)
    nome: str
    tipo: str  # Futebol Society, Futsal, Vôlei, etc.
    endereco: Endereco
    valor_hora: float
    horarios_disponiveis: List[datetime] = []
    
    class Config:
        populate_by_name = True
        json_encoders = {
            ObjectId: str,
            datetime: lambda v: v.isoformat()
        }


class CourtCreate(BaseModel):
    """Modelo para criação de quadra"""
    nome: str
    tipo: str
    endereco: Endereco
    valor_hora: float
    horarios_disponiveis: List[datetime] = []


class CourtUpdate(BaseModel):
    """Modelo para atualização de quadra"""
    nome: Optional[str] = None
    tipo: Optional[str] = None
    endereco: Optional[Endereco] = None
    valor_hora: Optional[float] = None
    horarios_disponiveis: Optional[List[datetime]] = None
