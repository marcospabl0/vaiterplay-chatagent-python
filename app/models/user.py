"""
Modelos Pydantic para Usuários
"""
from pydantic import BaseModel, Field, validator
from typing import Optional
from bson import ObjectId
import re


class User(BaseModel):
    """Modelo para Usuário"""
    id: Optional[str] = Field(alias="_id", default=None)
    nome: str
    telefone: str
    criado_em: Optional[str] = None
    
    @validator('telefone')
    def validate_telefone(cls, v):
        """Valida formato do telefone"""
        # Remove caracteres não numéricos
        telefone_limpo = re.sub(r'[^\d+]', '', v)
        
        # Verifica se tem formato internacional
        if not telefone_limpo.startswith('+'):
            # Se não tem +, assume Brasil (+55)
            if telefone_limpo.startswith('55'):
                telefone_limpo = '+' + telefone_limpo
            else:
                telefone_limpo = '+55' + telefone_limpo
        
        return telefone_limpo
    
    class Config:
        populate_by_name = True
        json_encoders = {
            ObjectId: str
        }


class UserCreate(BaseModel):
    """Modelo para criação de usuário"""
    nome: str
    telefone: str
    
    @validator('telefone')
    def validate_telefone(cls, v):
        """Valida formato do telefone"""
        telefone_limpo = re.sub(r'[^\d+]', '', v)
        
        if not telefone_limpo.startswith('+'):
            if telefone_limpo.startswith('55'):
                telefone_limpo = '+' + telefone_limpo
            else:
                telefone_limpo = '+55' + telefone_limpo
        
        return telefone_limpo


class UserUpdate(BaseModel):
    """Modelo para atualização de usuário"""
    nome: Optional[str] = None
    telefone: Optional[str] = None
    
    @validator('telefone')
    def validate_telefone(cls, v):
        """Valida formato do telefone"""
        if v is None:
            return v
            
        telefone_limpo = re.sub(r'[^\d+]', '', v)
        
        if not telefone_limpo.startswith('+'):
            if telefone_limpo.startswith('55'):
                telefone_limpo = '+' + telefone_limpo
            else:
                telefone_limpo = '+55' + telefone_limpo
        
        return telefone_limpo
