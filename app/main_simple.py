"""
Aplicação principal FastAPI para o Agente de Reservas de Quadras
Versão simplificada para produção
"""
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import PlainTextResponse
from contextlib import asynccontextmanager
import logging
import uvicorn
import os

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Detecta ambiente de produção
try:
    if os.getenv("RENDER") or os.getenv("PRODUCTION"):
        from app.production_settings import production_settings as settings
    else:
        from app.settings import settings
except ImportError as e:
    logger.warning(f"Erro ao importar configurações: {e}")
    # Configurações de fallback
    class FallbackSettings:
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
    
    settings = FallbackSettings()

# Importações condicionais para evitar erros
try:
    from app.db import connect_to_mongo, close_mongo_connection
    DB_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Database não disponível: {e}")
    DB_AVAILABLE = False

try:
    from app.services.agent_logic import agent_logic
    from app.services.whatsapp_service import whatsapp_service
    SERVICES_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Serviços não disponíveis: {e}")
    SERVICES_AVAILABLE = False


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerenciador de ciclo de vida da aplicação"""
    # Startup
    logger.info("Iniciando aplicação Genia Quadras...")
    
    if DB_AVAILABLE:
        try:
            await connect_to_mongo()
            logger.info("Conectado ao MongoDB com sucesso!")
        except Exception as e:
            logger.error(f"Erro ao conectar ao MongoDB: {e}")
    
    logger.info("Aplicação iniciada com sucesso!")
    
    yield
    
    # Shutdown
    logger.info("Encerrando aplicação...")
    
    if DB_AVAILABLE:
        try:
            await close_mongo_connection()
            logger.info("Conexão com MongoDB fechada")
        except Exception as e:
            logger.error(f"Erro ao fechar conexão MongoDB: {e}")
    
    logger.info("Aplicação encerrada!")


# Criação da aplicação FastAPI
app = FastAPI(
    title="Genia Quadras - Agente WhatsApp",
    description="Sistema de reservas de quadras via WhatsApp usando Twilio",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/")
async def root():
    """Endpoint raiz para verificar se a API está funcionando"""
    return {
        "message": "Genia Quadras - Agente WhatsApp",
        "status": "online",
        "version": "1.0.0",
        "database": "connected" if DB_AVAILABLE else "unavailable",
        "services": "available" if SERVICES_AVAILABLE else "unavailable"
    }


@app.get("/health")
async def health_check():
    """Endpoint de health check"""
    return {
        "status": "healthy", 
        "service": "genia-quadras",
        "database": "connected" if DB_AVAILABLE else "unavailable",
        "services": "available" if SERVICES_AVAILABLE else "unavailable"
    }


@app.post("/webhook")
async def whatsapp_webhook(request: Request):
    """
    Webhook para receber mensagens do Twilio WhatsApp
    """
    if not SERVICES_AVAILABLE:
        logger.error("Serviços não disponíveis")
        return PlainTextResponse("SERVICE_UNAVAILABLE", status_code=503)
    
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
        
        # Processa a mensagem através do agente
        reply_text = await agent_logic.process_message(from_number, message_body)
        
        # Envia resposta via WhatsApp
        success = whatsapp_service.send_message(from_number, reply_text)
        
        if success:
            logger.info(f"Resposta enviada para {from_number}")
        else:
            logger.error(f"Falha ao enviar resposta para {from_number}")
        
        return PlainTextResponse("OK")
        
    except Exception as e:
        logger.error(f"Erro no webhook: {e}")
        return PlainTextResponse("ERROR", status_code=500)


@app.post("/test-message")
async def test_message(request: Request):
    """
    Endpoint para testar o agente sem Twilio
    """
    if not SERVICES_AVAILABLE:
        return {"error": "Serviços não disponíveis"}
    
    try:
        data = await request.json()
        phone = data.get("phone", "whatsapp:+5511999999999")
        message = data.get("message", "Oi")
        
        logger.info(f"Teste - Mensagem de {phone}: {message}")
        
        # Processa a mensagem
        reply_text = await agent_logic.process_message(phone, message)
        
        return {
            "phone": phone,
            "message": message,
            "reply": reply_text
        }
        
    except Exception as e:
        logger.error(f"Erro no teste: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/courts")
async def list_courts():
    """Lista todas as quadras cadastradas"""
    if not DB_AVAILABLE:
        raise HTTPException(status_code=503, detail="Database não disponível")
    
    try:
        from app.repositories.courts_repo import courts_repo
        courts = await courts_repo.get_all()
        return {"courts": courts}
    except Exception as e:
        logger.error(f"Erro ao listar quadras: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/reservations/{phone}")
async def list_user_reservations(phone: str):
    """Lista reservas de um usuário específico"""
    if not DB_AVAILABLE:
        raise HTTPException(status_code=503, detail="Database não disponível")
    
    try:
        from app.repositories.reservations_repo import reservations_repo
        reservations = await reservations_repo.get_by_user_phone(phone)
        return {"reservations": reservations}
    except Exception as e:
        logger.error(f"Erro ao listar reservas: {e}")
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
