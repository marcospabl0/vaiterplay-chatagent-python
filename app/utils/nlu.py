"""
Utilitário para Processamento de Linguagem Natural (NLU)
"""
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dateutil import parser
import logging

logger = logging.getLogger(__name__)


class NLUProcessor:
    """Processador de linguagem natural para extrair intenções e dados"""
    
    def __init__(self):
        # Padrões para identificar intenções
        self.intent_patterns = {
            "reservar": [
                r"reservar", r"quero reservar", r"fazer reserva", r"agendar",
                r"marcar", r"reservar uma quadra", r"quero uma quadra"
            ],
            "confirmar": [
                r"confirmar", r"confirmar reserva", r"sim", r"ok", r"aceito",
                r"confirmo", r"pode confirmar", r"confirma"
            ],
            "consultar": [
                r"minhas reservas", r"consultar", r"ver reservas", r"listar",
                r"quais são minhas", r"mostrar reservas"
            ],
            "cancelar": [
                r"cancelar", r"desmarcar", r"quero cancelar", r"remover reserva"
            ],
            "disponibilidade": [
                r"disponível", r"horários livres", r"que horas", r"quando posso",
                r"horários disponíveis"
            ],
            "ajuda": [
                r"ajuda", r"help", r"como usar", r"o que posso", r"comandos"
            ],
            "saudacao": [
                r"oi", r"olá", r"bom dia", r"boa tarde", r"boa noite", r"hello"
            ]
        }
        
        # Padrões para tipos de quadra
        self.court_types = {
            "futebol": ["futebol", "soccer", "futebol society", "society"],
            "futsal": ["futsal", "futebol de salão", "futebol sala"],
            "volei": ["vôlei", "volei", "volleyball"],
            "basquete": ["basquete", "basketball", "basquete"],
            "tenis": ["tênis", "tenis", "tennis"]
        }
        
        # Padrões para quantidade de horas
        self.hours_patterns = [
            r"(\d+)\s*hora[s]?",
            r"por\s+(\d+)\s*hora[s]?",
            r"durante\s+(\d+)\s*hora[s]?",
            r"(\d+)\s*h\b",
            r"(\d+)\s*horas?\s*seguidas?",
            r"(\d+)\s*horas?\s*consecutivas?"
        ]
        
        # Padrões para datas e horários
        self.time_patterns = [
            r"(\d{1,2})[h:](\d{2})",  # 18:00 ou 18h00
            r"(\d{1,2})h",  # 18h
            r"às (\d{1,2})[h:]?(\d{2})?",  # às 18:00
            r"(\d{1,2}) horas",  # 18 horas
        ]
        
        self.date_patterns = [
            r"hoje",
            r"amanhã",
            r"depois de amanhã",
            r"(\d{1,2})/(\d{1,2})",  # 14/10
            r"(\d{1,2}) de (\w+)",  # 14 de outubro
        ]
    
    def extract_intent(self, message: str) -> str:
        """
        Extrai a intenção principal da mensagem
        
        Args:
            message: Mensagem do usuário
            
        Returns:
            str: Intenção identificada ou 'indefinida'
        """
        message_lower = message.lower().strip()
        
        # Remove pontuação excessiva
        message_clean = re.sub(r'[^\w\s]', ' ', message_lower)
        
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, message_clean):
                    logger.info(f"Intenção identificada: {intent}")
                    return intent
        
        return "indefinida"
    
    def extract_court_type(self, message: str) -> Optional[str]:
        """
        Extrai o tipo de quadra da mensagem
        
        Args:
            message: Mensagem do usuário
            
        Returns:
            str: Tipo de quadra identificado ou None
        """
        message_lower = message.lower()
        
        for court_type, keywords in self.court_types.items():
            for keyword in keywords:
                if keyword in message_lower:
                    logger.info(f"Tipo de quadra identificado: {court_type}")
                    return court_type
        
        return None
    
    def extract_hours_quantity(self, message: str) -> int:
        """
        Extrai quantidade de horas da mensagem
        
        Args:
            message: Mensagem do usuário
            
        Returns:
            int: Quantidade de horas (padrão: 1)
        """
        message_lower = message.lower()
        
        for pattern in self.hours_patterns:
            match = re.search(pattern, message_lower)
            if match:
                hours = int(match.group(1))
                logger.info(f"Quantidade de horas identificada: {hours}")
                return hours
        
        # Padrão padrão: 1 hora
        return 1
    
    def extract_time(self, message: str) -> Optional[str]:
        """
        Extrai horário da mensagem
        
        Args:
            message: Mensagem do usuário
            
        Returns:
            str: Horário no formato HH:MM ou None
        """
        message_lower = message.lower()
        
        for pattern in self.time_patterns:
            match = re.search(pattern, message_lower)
            if match:
                groups = match.groups()
                if len(groups) >= 2 and groups[1]:
                    # Formato completo HH:MM
                    hour = int(groups[0])
                    minute = int(groups[1])
                    time_str = f"{hour:02d}:{minute:02d}"
                else:
                    # Apenas hora
                    hour = int(groups[0])
                    time_str = f"{hour:02d}:00"
                
                logger.info(f"Horário extraído: {time_str}")
                return time_str
        
        return None
    
    def extract_date(self, message: str) -> Optional[datetime]:
        """
        Extrai data da mensagem
        
        Args:
            message: Mensagem do usuário
            
        Returns:
            datetime: Data extraída ou None
        """
        message_lower = message.lower()
        today = datetime.now().date()
        
        # Verifica palavras-chave de data
        if "hoje" in message_lower:
            return datetime.combine(today, datetime.min.time())
        elif "amanhã" in message_lower or "amanha" in message_lower:
            tomorrow = today + timedelta(days=1)
            return datetime.combine(tomorrow, datetime.min.time())
        elif "depois de amanhã" in message_lower:
            day_after = today + timedelta(days=2)
            return datetime.combine(day_after, datetime.min.time())
        
        # Tenta extrair data no formato DD/MM
        date_match = re.search(r'(\d{1,2})/(\d{1,2})', message_lower)
        if date_match:
            day = int(date_match.group(1))
            month = int(date_match.group(2))
            year = today.year
            
            # Se o mês já passou, assume próximo ano
            if month < today.month or (month == today.month and day < today.day):
                year += 1
            
            try:
                return datetime(year, month, day)
            except ValueError:
                pass
        
        # Tenta usar dateutil para parsing mais complexo
        try:
            parsed_date = parser.parse(message_lower, fuzzy=True, default=today)
            if parsed_date.date() >= today:
                return parsed_date
        except:
            pass
        
        return None
    
    def extract_reservation_datetime(self, message: str) -> Optional[datetime]:
        """
        Extrai data e hora completas para reserva
        
        Args:
            message: Mensagem do usuário
            
        Returns:
            datetime: Data e hora combinadas ou None
        """
        date = self.extract_date(message)
        time_str = self.extract_time(message)
        
        if not date:
            return None
        
        if time_str:
            hour, minute = map(int, time_str.split(':'))
            return date.replace(hour=hour, minute=minute)
        
        # Se não tem horário específico, assume horário padrão (18h)
        return date.replace(hour=18, minute=0)
    
    def extract_user_name(self, message: str) -> Optional[str]:
        """
        Extrai nome do usuário da mensagem (se mencionado)
        
        Args:
            message: Mensagem do usuário
            
        Returns:
            str: Nome extraído ou None
        """
        # Padrões simples para extrair nome
        patterns = [
            r"meu nome é (\w+)",
            r"eu sou (\w+)",
            r"sou (\w+)",
            r"chamo (\w+)"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, message.lower())
            if match:
                return match.group(1).title()
        
        return None
    
    def process_message(self, message: str) -> Dict:
        """
        Processa mensagem completa extraindo todos os dados
        
        Args:
            message: Mensagem do usuário
            
        Returns:
            Dict: Dados extraídos da mensagem
        """
        result = {
            "intent": self.extract_intent(message),
            "court_type": self.extract_court_type(message),
            "datetime": self.extract_reservation_datetime(message),
            "time": self.extract_time(message),
            "date": self.extract_date(message),
            "hours_quantity": self.extract_hours_quantity(message),
            "user_name": self.extract_user_name(message),
            "original_message": message
        }
        
        logger.info(f"Dados extraídos: {result}")
        return result


# Instância global do processador NLU
nlu_processor = NLUProcessor()
