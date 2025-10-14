"""
Aplicação principal FastAPI para o Agente de Reservas de Quadras
Versão compatível com Pydantic v1
"""
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import PlainTextResponse
import logging
import uvicorn
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

# Criação da aplicação FastAPI
app = FastAPI(
    title="Genia Quadras - Agente WhatsApp",
    description="Sistema de reservas de quadras via WhatsApp usando Twilio",
    version="1.0.0"
)


@app.get("/")
async def root():
    """Endpoint raiz para verificar se a API está funcionando"""
    return {
        "message": "Genia Quadras - Agente WhatsApp",
        "status": "online",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Endpoint de health check"""
    return {
        "status": "healthy", 
        "service": "genia-quadras"
    }


@app.post("/webhook")
async def whatsapp_webhook(request: Request):
    """
    Webhook para receber mensagens do Twilio WhatsApp
    """
    try:
        # Extrai dados do formulário enviado pelo Twilio
        form_data = await request.form()
        
        # Extrai informações da mensagem
        from_number = form_data.get("From", "")
        message_body = form_data.get("Body", "")
        
        logger.info(f"Mensagem recebida de {from_number}: {message_body}")
        
        # Valida se tem dados necessários
        if not from_number or not message_body:
            logger.warning("Mensagem sem dados necessários")
            return PlainTextResponse("OK")
        
        # Resposta simples para teste
        reply_text = f"Olá! Recebi sua mensagem: '{message_body}'. Sistema em desenvolvimento."
        
        logger.info(f"Resposta enviada para {from_number}")
        
        return PlainTextResponse("OK")
        
    except Exception as e:
        logger.error(f"Erro no webhook: {e}")
        return PlainTextResponse("ERROR", status_code=500)


@app.post("/test-message")
async def test_message(request: Request):
    """
    Endpoint para testar o agente sem Twilio
    """
    try:
        data = await request.json()
        phone = data.get("phone", "whatsapp:+5511999999999")
        message = data.get("message", "Oi")
        
        logger.info(f"Teste - Mensagem de {phone}: {message}")
        
        # Resposta simples para teste
        reply_text = f"Olá! Recebi sua mensagem: '{message}'. Sistema funcionando!"
        
        return {
            "phone": phone,
            "message": message,
            "reply": reply_text
        }
        
    except Exception as e:
        logger.error(f"Erro no teste: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    # Execução direta da aplicação (para desenvolvimento)
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
