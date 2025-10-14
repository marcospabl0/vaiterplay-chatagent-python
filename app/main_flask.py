"""
Aplicação Flask simples para o Agente de Reservas de Quadras
Versão com MongoDB integrado
"""
from flask import Flask, request, jsonify
import logging
import os
from datetime import datetime
from app.db_flask import mongodb
from app.repositories_flask import user_repo, court_repo, reservation_repo
from app.models_flask import User, Court, Reservation

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

# Inicializar MongoDB
try:
    mongodb.connect_sync()
    logger.info("MongoDB conectado com sucesso!")
except Exception as e:
    logger.error(f"Erro ao conectar MongoDB: {e}")


@app.route("/")
def root():
    """Endpoint raiz para verificar se a API está funcionando"""
    return jsonify({
        "message": "Genia Quadras - Agente WhatsApp",
        "status": "online",
        "version": "1.0.0",
        "database": "connected" if mongodb.db else "disconnected"
    })


@app.route("/health")
def health_check():
    """Endpoint de health check"""
    return jsonify({
        "status": "healthy", 
        "service": "genia-quadras",
        "database": "connected" if mongodb.db else "disconnected"
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


@app.route("/reservations/<phone>", methods=["GET"])
def list_user_reservations(phone: str):
    """Lista reservas de um usuário específico"""
    try:
        reservations = reservation_repo.get_by_user_phone(phone)
        return jsonify({
            "reservations": reservations,
            "count": len(reservations)
        })
    except Exception as e:
        logger.error(f"Erro ao listar reservas: {e}")
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
        from datetime import timedelta
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


if __name__ == "__main__":
    # Execução direta da aplicação (para desenvolvimento)
    port = int(os.getenv("PORT", 8000))
    app.run(
        host="0.0.0.0",
        port=port,
        debug=settings.DEBUG
    )
