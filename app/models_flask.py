"""
Modelos básicos para Flask + MongoDB
"""
from datetime import datetime
from typing import Optional, List
import re

class User:
    """Modelo para Usuário"""
    
    def __init__(self, nome: str, telefone: str, criado_em: Optional[str] = None, _id: Optional[str] = None):
        self._id = _id
        self.nome = nome
        self.telefone = self._validate_phone(telefone)
        self.criado_em = criado_em or datetime.now().isoformat()
    
    def _validate_phone(self, phone: str) -> str:
        """Valida formato do telefone"""
        telefone_limpo = re.sub(r'[^\d+]', '', phone)
        
        if not telefone_limpo.startswith('+'):
            if telefone_limpo.startswith('55'):
                telefone_limpo = '+' + telefone_limpo
            else:
                telefone_limpo = '+55' + telefone_limpo
        
        return telefone_limpo
    
    def to_dict(self):
        """Converte para dicionário"""
        return {
            "_id": self._id,
            "nome": self.nome,
            "telefone": self.telefone,
            "criado_em": self.criado_em
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        """Cria instância a partir de dicionário"""
        return cls(
            _id=str(data.get("_id", "")),
            nome=data.get("nome", ""),
            telefone=data.get("telefone", ""),
            criado_em=data.get("criado_em")
        )

class Court:
    """Modelo para Quadra"""
    
    def __init__(self, nome: str, tipo: str, endereco: dict, valor_hora: float, 
                 horarios_disponiveis: Optional[List[datetime]] = None, _id: Optional[str] = None):
        self._id = _id
        self.nome = nome
        self.tipo = tipo
        self.endereco = endereco
        self.valor_hora = valor_hora
        self.horarios_disponiveis = horarios_disponiveis or []
    
    def to_dict(self):
        """Converte para dicionário"""
        return {
            "_id": self._id,
            "nome": self.nome,
            "tipo": self.tipo,
            "endereco": self.endereco,
            "valor_hora": self.valor_hora,
            "horarios_disponiveis": [h.isoformat() if isinstance(h, datetime) else h for h in self.horarios_disponiveis]
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        """Cria instância a partir de dicionário"""
        return cls(
            _id=str(data.get("_id", "")),
            nome=data.get("nome", ""),
            tipo=data.get("tipo", ""),
            endereco=data.get("endereco", {}),
            valor_hora=data.get("valor_hora", 0.0),
            horarios_disponiveis=data.get("horarios_disponiveis", [])
        )

class Reservation:
    """Modelo para Reserva"""
    
    def __init__(self, usuario: User, quadra_id: str, data_reserva: datetime, 
                 quantidade_horas: int = 1, status: str = "confirmada", 
                 criado_em: Optional[datetime] = None, _id: Optional[str] = None):
        self._id = _id
        self.usuario = usuario
        self.quadra_id = quadra_id
        self.data_reserva = data_reserva
        self.quantidade_horas = quantidade_horas
        self.status = status
        self.criado_em = criado_em or datetime.now()
    
    def to_dict(self):
        """Converte para dicionário"""
        return {
            "_id": self._id,
            "usuario": self.usuario.to_dict(),
            "quadra_id": self.quadra_id,
            "data_reserva": self.data_reserva.isoformat(),
            "quantidade_horas": self.quantidade_horas,
            "status": self.status,
            "criado_em": self.criado_em.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        """Cria instância a partir de dicionário"""
        usuario_data = data.get("usuario", {})
        usuario = User.from_dict(usuario_data)
        
        return cls(
            _id=str(data.get("_id", "")),
            usuario=usuario,
            quadra_id=data.get("quadra_id", ""),
            data_reserva=datetime.fromisoformat(data.get("data_reserva", datetime.now().isoformat())),
            quantidade_horas=data.get("quantidade_horas", 1),
            status=data.get("status", "confirmada"),
            criado_em=datetime.fromisoformat(data.get("criado_em", datetime.now().isoformat()))
        )
