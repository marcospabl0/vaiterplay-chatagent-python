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
from typing import Optional, List
import re

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
        # Extrai dados do formulário enviado pelo Twilio
        from_number = request.form.get("From", "")
        message_body = request.form.get("Body", "")
        
        logger.info(f"Mensagem recebida de {from_number}: {message_body}")
        
        # Valida se tem dados necessários
        if not from_number or not message_body:
            logger.warning("Mensagem sem dados necessários")
            return "OK"
        
        # Busca ou cria usuário
        try:
            user = user_repo.find_or_create_by_phone(from_number)
            logger.info(f"Usuário encontrado/criado: {user.nome}")
        except Exception as e:
            logger.error(f"Erro ao buscar/criar usuário: {e}")
            user = User(nome="Usuário", telefone=from_number)
        
        # Resposta simples para teste
        reply_text = f"Olá {user.nome}! Recebi sua mensagem: '{message_body}'. Sistema com MongoDB funcionando!"
        
        logger.info(f"Resposta enviada para {from_number}")
        
        return "OK"
        
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
        
        # Busca ou cria usuário
        try:
            user = user_repo.find_or_create_by_phone(phone)
            logger.info(f"Usuário encontrado/criado: {user.nome}")
        except Exception as e:
            logger.error(f"Erro ao buscar/criar usuário: {e}")
            user = User(nome="Usuário", telefone=phone)
        
        # Resposta simples para teste
        reply_text = f"Olá {user.nome}! Recebi sua mensagem: '{message}'. Sistema com MongoDB funcionando!"
        
        return jsonify({
            "phone": phone,
            "message": message,
            "reply": reply_text,
            "user": user.to_dict()
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
