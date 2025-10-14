"""
Aplicação Flask simples para o Agente de Reservas de Quadras
Versão com MongoDB integrado - Arquivo único para evitar problemas de import
"""
from flask import Flask, request, jsonify
import logging
import os
from datetime import datetime, timedelta
from pymongo import MongoClient
from bson import ObjectId
from typing import Optional, List, Tuple
import re
from twilio.twiml.messaging_response import MessagingResponse
from groq import Groq

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Configurações simples
class SimpleSettings:
    MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    MONGODB_DB = os.getenv("MONGODB_DB", "vaiterplay")
    TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
    TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
    TWILIO_WHATSAPP_FROM = os.getenv("TWILIO_WHATSAPP_FROM", "whatsapp:+14155238886")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
    USE_LLM = os.getenv("USE_LLM", "true").lower() == "true"
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

settings = SimpleSettings()

# Cliente Groq (opcional)
groq_client = None
if settings.USE_LLM and settings.GROQ_API_KEY:
    try:
        groq_client = Groq(api_key=settings.GROQ_API_KEY)
        logger.info("Groq LLM habilitado.")
    except Exception as e:
        logger.error(f"Falha ao inicializar Groq: {e}")
        groq_client = None

# Criação da aplicação Flask
app = Flask(__name__)

# ===== MODELOS =====
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
        """Converte para dicionário (omitindo _id quando None)"""
        data = {
            "nome": self.nome,
            "telefone": self.telefone,
            "criado_em": self.criado_em
        }
        if self._id:
            data["_id"] = self._id
        return data
    
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
        """Converte para dicionário (omitindo _id quando None)"""
        data = {
            "nome": self.nome,
            "tipo": self.tipo,
            "endereco": self.endereco,
            "valor_hora": self.valor_hora,
            "horarios_disponiveis": [h.isoformat() if isinstance(h, datetime) else h for h in self.horarios_disponiveis]
        }
        if self._id:
            data["_id"] = self._id
        return data
    
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

# ===== CONEXÃO MONGODB =====
class MongoDBConnection:
    """Classe para gerenciar conexão MongoDB"""
    
    def __init__(self):
        self.client = None
        self.db = None
        
    def connect_sync(self):
        """Conecta ao MongoDB de forma síncrona (para Flask)"""
        try:
            mongodb_uri = settings.MONGODB_URI
            mongodb_db = settings.MONGODB_DB
            
            self.client = MongoClient(mongodb_uri)
            self.db = self.client[mongodb_db]
            
            # Testa a conexão
            self.client.admin.command('ping')
            logger.info("Conectado ao MongoDB com sucesso!")
            
        except Exception as e:
            logger.error(f"Erro ao conectar ao MongoDB: {e}")
            raise
    
    def close_sync(self):
        """Fecha conexão síncrona"""
        if self.client:
            self.client.close()
            logger.info("Conexão MongoDB fechada")
    
    def get_collection(self, collection_name: str):
        """Retorna uma coleção MongoDB"""
        if self.db is None:
            raise RuntimeError("Database não foi inicializada. Chame connect_sync() primeiro.")
        return self.db[collection_name]

# Instância global
mongodb = MongoDBConnection()

# ===== REPOSITÓRIOS =====
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

# Instâncias globais
user_repo = UserRepository()
court_repo = CourtRepository()

class Reservation:
    """Modelo para Reserva"""

    def __init__(self, usuario: User, quadra_id: str, data_reserva: datetime,
                 quantidade_horas: int = 1, status: str = "pendente",
                 criado_em: Optional[datetime] = None, _id: Optional[str] = None):
        self._id = _id
        self.usuario = usuario
        self.quadra_id = quadra_id
        self.data_reserva = data_reserva
        self.quantidade_horas = quantidade_horas
        self.status = status
        self.criado_em = criado_em or datetime.now()

    def to_dict(self):
        data = {
            "usuario": self.usuario.to_dict(),
            "quadra_id": self.quadra_id,
            "data_reserva": self.data_reserva.isoformat(),
            "quantidade_horas": self.quantidade_horas,
            "status": self.status,
            "criado_em": self.criado_em.isoformat()
        }
        if self._id:
            data["_id"] = self._id
        return data

    @classmethod
    def from_dict(cls, data: dict):
        usuario = User.from_dict(data.get("usuario", {}))
        return cls(
            _id=str(data.get("_id", "")),
            usuario=usuario,
            quadra_id=data.get("quadra_id", ""),
            data_reserva=datetime.fromisoformat(data.get("data_reserva")),
            quantidade_horas=data.get("quantidade_horas", 1),
            status=data.get("status", "pendente"),
            criado_em=datetime.fromisoformat(data.get("criado_em")) if data.get("criado_em") else datetime.now()
        )

class ReservationRepository:
    def __init__(self):
        self.collection_name = "reservas"

    def get_collection(self):
        return mongodb.get_collection(self.collection_name)

    def create(self, reservation: Reservation) -> str:
        try:
            result = self.get_collection().insert_one(reservation.to_dict())
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Erro ao criar reserva: {e}")
            raise

    def get_by_user_phone(self, phone: str) -> List[dict]:
        try:
            items = []
            for doc in self.get_collection().find({"usuario.telefone": phone}).sort("data_reserva", 1):
                items.append(doc)
            return items
        except Exception as e:
            logger.error(f"Erro ao buscar reservas do usuário: {e}")
            raise

    def cancel_by_id(self, reservation_id: str) -> bool:
        try:
            res = self.get_collection().update_one({"_id": ObjectId(reservation_id)}, {"$set": {"status": "cancelada"}})
            return res.modified_count > 0
        except Exception as e:
            logger.error(f"Erro ao cancelar reserva: {e}")
            raise

class ConversationStateRepository:
    def __init__(self):
        self.collection_name = "estados_conversa"

    def get_collection(self):
        return mongodb.get_collection(self.collection_name)

    def get_state(self, phone: str) -> Optional[dict]:
        return self.get_collection().find_one({"phone": phone})

    def set_state(self, phone: str, state: dict):
        state["phone"] = phone
        self.get_collection().update_one({"phone": phone}, {"$set": state}, upsert=True)

    def clear_state(self, phone: str):
        self.get_collection().delete_one({"phone": phone})

class ConversationMessage:
    """Modelo para mensagem individual da conversa"""
    def __init__(self, role: str, content: str, timestamp: Optional[datetime] = None):
        self.role = role  # "user" ou "assistant"
        self.content = content
        self.timestamp = timestamp or datetime.now()

    def to_dict(self):
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.isoformat()
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            role=data.get("role", "user"),
            content=data.get("content", ""),
            timestamp=datetime.fromisoformat(data.get("timestamp")) if data.get("timestamp") else datetime.now()
        )

class ConversationHistoryRepository:
    """Repositório para histórico de conversas (janela de 24h)"""
    def __init__(self):
        self.collection_name = "conversation_history"

    def get_collection(self):
        return mongodb.get_collection(self.collection_name)

    def add_message(self, phone: str, message: ConversationMessage):
        """Adiciona mensagem ao histórico do usuário"""
        try:
            # Busca ou cria documento do usuário
            user_doc = self.get_collection().find_one({"phone": phone})
            if not user_doc:
                user_doc = {
                    "phone": phone,
                    "messages": [],
                    "last_activity": datetime.now().isoformat()
                }
                self.get_collection().insert_one(user_doc)
                user_doc = self.get_collection().find_one({"phone": phone})
            
            # Adiciona nova mensagem
            messages = user_doc.get("messages", [])
            messages.append(message.to_dict())
            
            # Atualiza documento
            self.get_collection().update_one(
                {"phone": phone},
                {
                    "$set": {
                        "messages": messages,
                        "last_activity": datetime.now().isoformat()
                    }
                }
            )
        except Exception as e:
            logger.error(f"Erro ao adicionar mensagem ao histórico: {e}")

    def get_recent_messages(self, phone: str, hours: int = 24) -> List[ConversationMessage]:
        """Recupera mensagens das últimas N horas"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            user_doc = self.get_collection().find_one({"phone": phone})
            if not user_doc:
                return []
            
            messages = []
            for msg_data in user_doc.get("messages", []):
                msg = ConversationMessage.from_dict(msg_data)
                if msg.timestamp >= cutoff_time:
                    messages.append(msg)
            
            return messages
        except Exception as e:
            logger.error(f"Erro ao recuperar histórico: {e}")
            return []

    def clear_old_messages(self, phone: str, hours: int = 24):
        """Remove mensagens mais antigas que N horas"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            user_doc = self.get_collection().find_one({"phone": phone})
            if not user_doc:
                return
            
            messages = []
            for msg_data in user_doc.get("messages", []):
                msg = ConversationMessage.from_dict(msg_data)
                if msg.timestamp >= cutoff_time:
                    messages.append(msg_data)
            
            self.get_collection().update_one(
                {"phone": phone},
                {"$set": {"messages": messages}}
            )
        except Exception as e:
            logger.error(f"Erro ao limpar histórico antigo: {e}")

    def get_conversation_context(self, phone: str, max_messages: int = 10) -> str:
        """Retorna contexto da conversa como string para LLM"""
        messages = self.get_recent_messages(phone, hours=24)
        if not messages:
            return ""
        
        # Pega as últimas N mensagens
        recent = messages[-max_messages:] if len(messages) > max_messages else messages
        
        context_lines = []
        for msg in recent:
            role_label = "Usuário" if msg.role == "user" else "Assistente"
            context_lines.append(f"{role_label}: {msg.content}")
        
        return "\n".join(context_lines)

reservation_repo = ReservationRepository()
state_repo = ConversationStateRepository()
history_repo = ConversationHistoryRepository()

# ===== NLU E HELPERS =====
HOURS_PATTERN = re.compile(r"(\d{1,2})(?:h|:\d{2})?", re.IGNORECASE)
DATE_PATTERN = re.compile(r"(hoje|amanh[aã]|\d{1,2}/\d{1,2}|\d{4}-\d{2}-\d{2})", re.IGNORECASE)
HOURS_QTY_PATTERN = re.compile(r"(\d{1,2})\s*(h|horas?)", re.IGNORECASE)

def parse_date(text: str) -> Optional[datetime]:
    text = text.lower()
    now = datetime.now()
    if "hoje" in text:
        return now
    if "amanh" in text:
        return now + timedelta(days=1)
    m = DATE_PATTERN.search(text)
    if m:
        token = m.group(1)
        try:
            if "/" in token:
                d, mth = token.split("/")
                year = now.year
                return datetime(year=int(year), month=int(mth), day=int(d))
            if "-" in token:
                return datetime.fromisoformat(token)
        except Exception:
            return None
    return None

def parse_time(text: str) -> Optional[int]:
    match = HOURS_PATTERN.search(text)
    if match:
        hour = int(match.group(1))
        if 0 <= hour <= 23:
            return hour
    return None

def parse_hours_qty(text: str) -> int:
    m = HOURS_QTY_PATTERN.search(text)
    if m:
        return max(1, min(6, int(m.group(1))))
    return 1

def find_court_by_hint(text: str) -> Optional[Court]:
    hint = text.lower()
    courts = court_repo.get_all()
    for c in courts:
        if c.nome.lower() in hint or c.tipo.lower() in hint:
            return c
    return courts[0] if courts else None

def get_consecutive_slots(base: datetime, hours: int) -> List[str]:
    slots = []
    for i in range(hours):
        slot_dt = base + timedelta(hours=i)
        slots.append(slot_dt.isoformat())
    return slots

def check_availability(court: Court, base: datetime, hours: int) -> bool:
    needed = set(get_consecutive_slots(base, hours))
    available = set([h if isinstance(h, str) else (h.isoformat() if isinstance(h, datetime) else str(h)) for h in court.horarios_disponiveis])
    return needed.issubset(available)

def block_slots(court: Court, base: datetime, hours: int):
    needed = set(get_consecutive_slots(base, hours))
    court.horarios_disponiveis = [h for h in [hh if isinstance(hh, str) else (hh.isoformat() if isinstance(hh, datetime) else str(hh)) for hh in court.horarios_disponiveis] if h not in needed]
    # persist change
    mongodb.get_collection("quadras").update_one({"_id": ObjectId(court._id)}, {"$set": {"horarios_disponiveis": court.horarios_disponiveis}})

def intent_from_text(text: str, pending_state: Optional[dict]) -> str:
    t = text.lower()
    # Saudações diretas
    if t.strip() in ["oi", "olá", "ola", "bom dia", "boa tarde", "boa noite"]:
        return "saudacao"
    if pending_state and pending_state.get("awaiting") == "confirmation":
        if any(w in t for w in ["confirmo", "confirmar", "sim", "ok"]):
            return "confirmar"
        if any(w in t for w in ["cancelar", "cancela", "não", "nao"]):
            return "cancelar"
    if any(w in t for w in ["ajuda", "menu", "opcoes", "opções", "help"]):
        return "ajuda"
    if any(w in t for w in ["minhas reservas", "minhas", "consultar", "minhas reservas", "ver reservas"]):
        return "consultar"
    if any(w in t for w in ["cancelar reserva", "cancelar", "cancelamento"]):
        return "cancelar"
    if any(w in t for w in ["reservar", "reserva", "agendar", "quero reservar"]):
        return "reservar"
    return "desconhecido"

def handle_help() -> str:
    return (
        "Posso ajudar com: reservar quadra, consultar reservas e cancelar.\n"
        "Exemplos: 'reservar amanhã 19h por 2 horas society' ou 'consultar minhas reservas'."
    )

def handle_consulta(phone: str) -> str:
    reservas = reservation_repo.get_by_user_phone(phone)
    if not reservas:
        return "Você não possui reservas."
    lines = []
    for r in reservas:
        dt = datetime.fromisoformat(r.get("data_reserva"))
        qid = r.get("quadra_id")
        court_doc = mongodb.get_collection("quadras").find_one({"_id": ObjectId(qid)})
        nome = court_doc.get("nome") if court_doc else "Quadra"
        horas = r.get("quantidade_horas", 1)
        lines.append(f"- {nome} em {dt.strftime('%d/%m %H:%M')} por {horas}h (status: {r.get('status')})")
    return "Suas reservas:\n" + "\n".join(lines)

def handle_reserva_flow(user: User, text: str, phone: str) -> str:
    date = parse_date(text)
    hour = parse_time(text)
    hours_qty = parse_hours_qty(text)
    court = find_court_by_hint(text)
    if not court:
        return "Não encontrei quadras cadastradas."
    if date is None or hour is None:
        return "Informe data e hora. Ex.: 'reservar amanhã 19h por 2 horas'."
    start_dt = date.replace(hour=hour, minute=0, second=0, microsecond=0)
    if not check_availability(court, start_dt, hours_qty):
        return "Não há disponibilidade para esse horário/intervalo. Tente outro horário."
    total = court.valor_hora * hours_qty
    # salva estado aguardando confirmação
    state_repo.set_state(phone, {
        "awaiting": "confirmation",
        "court_id": court._id,
        "court_nome": court.nome,
        "start_iso": start_dt.isoformat(),
        "hours_qty": hours_qty,
        "preco_hora": court.valor_hora,
        "total": total
    })
    return (f"{court.nome} disponível em {start_dt.strftime('%d/%m %H:%M')} por {hours_qty}h. "
            f"Preço R${court.valor_hora:.2f}/h, total R${total:.2f}. Confirmar?")

def handle_confirm(phone: str, user: User) -> str:
    state = state_repo.get_state(phone)
    if not state or state.get("awaiting") != "confirmation":
        return "Não há reserva pendente para confirmar."
    court_id = state["court_id"]
    start_dt = datetime.fromisoformat(state["start_iso"])
    hours_qty = int(state["hours_qty"])
    # verifica e grava
    court_doc = mongodb.get_collection("quadras").find_one({"_id": ObjectId(court_id)})
    if not court_doc:
        return "Quadra não encontrada."
    court = Court.from_dict(court_doc)
    if not check_availability(court, start_dt, hours_qty):
        state_repo.clear_state(phone)
        return "Infelizmente o horário ficou indisponível. Tente outro."
    # bloquear slots e salvar reserva
    block_slots(court, start_dt, hours_qty)
    reserva = Reservation(usuario=user, quadra_id=court_id, data_reserva=start_dt, quantidade_horas=hours_qty, status="confirmada")
    res_id = reservation_repo.create(reserva)
    state_repo.clear_state(phone)
    return (f"Reserva confirmada! Código {res_id}. {court.nome} em {start_dt.strftime('%d/%m %H:%M')} "
            f"por {hours_qty}h. Precisando, é só chamar!")

def handle_cancel(phone: str) -> str:
    state_repo.clear_state(phone)
    return "Ok, cancelado. Se quiser, posso buscar outro horário."

def process_message(phone: str, text: str) -> str:
    # Salva mensagem do usuário no histórico
    user_message = ConversationMessage(role="user", content=text)
    history_repo.add_message(phone, user_message)
    
    user = user_repo.find_or_create_by_phone(phone)
    pending = state_repo.get_state(phone)
    intent = intent_from_text(text, pending)
    
    # Processa com NLU tradicional primeiro
    if intent == "saudacao":
        response = (
            "Olá! Eu sou seu assistente de reservas. Posso reservar quadra, consultar e cancelar. "
            "Diga algo como: 'reservar amanhã 19h por 2 horas society'."
        )
    elif intent == "ajuda":
        response = handle_help()
    elif intent == "consultar":
        response = handle_consulta(phone)
    elif intent == "reservar":
        response = handle_reserva_flow(user, text, phone)
    elif intent == "confirmar":
        response = handle_confirm(phone, user)
    elif intent == "cancelar":
        # prioridade: cancelar fluxo pendente
        if pending and pending.get("awaiting") == "confirmation":
            response = handle_cancel(phone)
        else:
            response = "Para cancelar, informe o código ou responda durante uma confirmação."
    else:
        # Fallback: usar LLM com contexto da conversa
        response = generate_llm_response(phone, text)
    
    # Salva resposta do assistente no histórico
    assistant_message = ConversationMessage(role="assistant", content=response)
    history_repo.add_message(phone, assistant_message)
    
    # Limpa mensagens antigas (mais de 24h)
    history_repo.clear_old_messages(phone, hours=24)
    
    return response

def generate_llm_response(phone: str, text: str) -> str:
    """Gera resposta usando LLM com contexto da conversa"""
    if not groq_client:
        return "Não entendi. Envie 'ajuda' para ver exemplos."
    
    try:
        # Contexto das quadras
        courts = court_repo.get_all()
        courts_context = "\n".join([f"- {c.nome} ({c.tipo}) - R${c.valor_hora:.2f}/h" for c in courts][:10]) or "(sem quadras cadastradas)"
        
        # Contexto da conversa (últimas 10 mensagens)
        conversation_context = history_repo.get_conversation_context(phone, max_messages=10)
        
        # Estado atual (se houver)
        pending = state_repo.get_state(phone)
        state_context = ""
        if pending and pending.get("awaiting") == "confirmation":
            state_context = f"\nEstado atual: Aguardando confirmação de reserva - {pending.get('court_nome')} em {pending.get('start_iso')} por {pending.get('hours_qty')}h - Total: R${pending.get('total', 0):.2f}"
        
        # Monta prompt com contexto completo
        prompt = f"""Você é um assistente de reservas de quadras esportivas via WhatsApp. 
Aja de forma natural, amigável e objetiva em português do Brasil.

CONTEXTO DAS QUADRAS:
{courts_context}

HISTÓRICO DA CONVERSA (últimas mensagens):
{conversation_context if conversation_context else "Primeira mensagem da conversa"}

{state_context}

MENSAGEM ATUAL DO USUÁRIO: {text}

INSTRUÇÕES:
- Use o histórico para entender o contexto da conversa
- Se o usuário estiver perguntando sobre disponibilidade, liste as quadras e horários
- Se quiser reservar, peça data, hora e quantidade de horas
- Seja natural e mantenha o contexto da conversa
- Se não entender, peça esclarecimento de forma amigável
- Respostas devem ser curtas e diretas (máximo 200 caracteres)"""

        chat = groq_client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=[
                {"role": "system", "content": "Você é um assistente especializado em reservas de quadras esportivas."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=200,
        )
        
        return chat.choices[0].message.content.strip()
        
    except Exception as e:
        logger.error(f"LLM fallback falhou: {e}")
        return "Não entendi. Envie 'ajuda' para ver exemplos."

# ===== ROTAS =====
@app.route("/")
def root():
    """Endpoint raiz para verificar se a API está funcionando"""
    return jsonify({
        "message": "Genia Quadras - Agente WhatsApp",
        "status": "online",
        "version": "1.0.0",
        "database": "connected" if mongodb.db is not None else "disconnected"
    })

@app.route("/health")
def health_check():
    """Endpoint de health check"""
    return jsonify({
        "status": "healthy", 
        "service": "genia-quadras",
        "database": "connected" if mongodb.db is not None else "disconnected"
    })

@app.route("/webhook", methods=["POST"])
def whatsapp_webhook():
    """
    Webhook para receber mensagens do Twilio WhatsApp
    """
    try:
        # Extrai dados do formulário enviado pelo Twilio (x-www-form-urlencoded)
        form = request.form or {}
        from_number = form.get("From", "")
        message_body = form.get("Body", "")
        wa_id = form.get("WaId")  # apenas números, ex: 5511999999999
        profile_name = form.get("ProfileName")
        channel_metadata = form.get("ChannelMetadata")
        # Fallback: se não veio From, monta a partir do WaId
        if (not from_number) and wa_id:
            from_number = f"whatsapp:+{wa_id}"
        # Sanitiza mínimos
        from_number = (from_number or "").strip()
        message_body = (message_body or "").strip()
        
        logger.info(f"Mensagem recebida de {from_number}: {message_body}")
        logger.debug(f"Payload Twilio: form={dict(form)}")
        
        # Valida se tem dados necessários
        if not from_number or not message_body:
            logger.warning("Mensagem sem dados necessários")
            return "OK"
        
        # Processa a mensagem com a lógica do agente
        reply_text = process_message(from_number, message_body)
        resp = MessagingResponse()
        resp.message(reply_text)
        logger.info(f"Resposta enviada para {from_number}")
        return str(resp)
        
    except Exception as e:
        logger.error(f"Erro no webhook: {e}")
        return "ERROR", 500

@app.route("/test-message", methods=["POST"])
def test_message():
    """
    Endpoint para testar o agente sem Twilio
    """
    try:
        data = request.get_json()
        phone = data.get("phone", "whatsapp:+5511999999999")
        message = data.get("message", "Oi")
        
        logger.info(f"Teste - Mensagem de {phone}: {message}")
        
        # Usa a mesma lógica do webhook (NLU + fluxo de reserva)
        reply_text = process_message(phone, message)
        
        return jsonify({
            "phone": phone,
            "message": message,
            "reply": reply_text
        })
        
    except Exception as e:
        logger.error(f"Erro no teste: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/courts", methods=["GET"])
def list_courts():
    """Lista todas as quadras cadastradas"""
    try:
        courts = court_repo.get_all()
        courts_data = [court.to_dict() for court in courts]
        return jsonify({
            "courts": courts_data,
            "count": len(courts_data)
        })
    except Exception as e:
        logger.error(f"Erro ao listar quadras: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/populate", methods=["POST"])
def populate_database():
    """Popula o banco com dados de exemplo"""
    try:
        # Cria algumas quadras de exemplo
        courts_data = [
            {
                "nome": "Quadra 1 - Futebol Society",
                "tipo": "Futebol Society",
                "endereco": {
                    "logradouro": "Rua das Flores, 123",
                    "bairro": "Centro",
                    "cidade": "São Paulo"
                },
                "valor_hora": 80.0,
                "horarios_disponiveis": []
            },
            {
                "nome": "Quadra 2 - Futsal",
                "tipo": "Futsal",
                "endereco": {
                    "logradouro": "Av. Paulista, 456",
                    "bairro": "Bela Vista",
                    "cidade": "São Paulo"
                },
                "valor_hora": 60.0,
                "horarios_disponiveis": []
            }
        ]
        
        # Gera horários disponíveis para os próximos 7 dias
        base_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        available_hours = list(range(8, 22))  # Horários de 8h às 21h
        
        created_courts = []
        for court_data in courts_data:
            # Gera horários para os próximos 7 dias
            horarios = []
            for day in range(7):
                for hour in available_hours:
                    horario = base_date + timedelta(days=day, hours=hour)
                    horarios.append(horario)
            
            court_data["horarios_disponiveis"] = horarios
            
            # Cria a quadra
            court = Court(
                nome=court_data["nome"],
                tipo=court_data["tipo"],
                endereco=court_data["endereco"],
                valor_hora=court_data["valor_hora"],
                horarios_disponiveis=court_data["horarios_disponiveis"]
            )
            
            court_id = court_repo.create(court)
            court._id = court_id
            created_courts.append(court.to_dict())
        
        return jsonify({
            "message": "Banco populado com sucesso!",
            "courts_created": len(created_courts),
            "courts": created_courts
        })
        
    except Exception as e:
        logger.error(f"Erro ao popular banco: {e}")
        return jsonify({"error": str(e)}), 500

# ===== INICIALIZAÇÃO =====
# Inicializar MongoDB
try:
    mongodb.connect_sync()
    logger.info("MongoDB conectado com sucesso!")
except Exception as e:
    logger.error(f"Erro ao conectar MongoDB: {e}")

if __name__ == "__main__":
    # Execução direta da aplicação (para desenvolvimento)
    port = int(os.getenv("PORT", 8000))
    app.run(
        host="0.0.0.0",
        port=port,
        debug=settings.DEBUG
    )
