"""
Aplicação Flask simples para o Agente de Reservas de Quadras
Versão sem dependências de compilação Rust
"""
from flask import Flask, request, jsonify
import logging
import os

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


@app.route("/")
def root():
    """Endpoint raiz para verificar se a API está funcionando"""
    return jsonify({
        "message": "Genia Quadras - Agente WhatsApp",
        "status": "online",
        "version": "1.0.0"
    })


@app.route("/health")
def health_check():
    """Endpoint de health check"""
    return jsonify({
        "status": "healthy", 
        "service": "genia-quadras"
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
        
        # Resposta simples para teste
        reply_text = f"Olá! Recebi sua mensagem: '{message_body}'. Sistema em desenvolvimento."
        
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
        
        # Resposta simples para teste
        reply_text = f"Olá! Recebi sua mensagem: '{message}'. Sistema funcionando!"
        
        return jsonify({
            "phone": phone,
            "message": message,
            "reply": reply_text
        })
        
    except Exception as e:
        logger.error(f"Erro no teste: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    # Execução direta da aplicação (para desenvolvimento)
    port = int(os.getenv("PORT", 8000))
    app.run(
        host="0.0.0.0",
        port=port,
        debug=settings.DEBUG
    )
