"""
Configurações específicas para produção
"""
import os
from app.settings import Settings

class ProductionSettings(Settings):
    """Configurações para ambiente de produção"""
    
    # MongoDB
    MONGODB_URI: str = os.getenv("MONGODB_URI", "")
    MONGODB_DB: str = os.getenv("MONGODB_DB", "vaiterplay")
    
    # Twilio
    TWILIO_ACCOUNT_SID: str = os.getenv("TWILIO_ACCOUNT_SID", "")
    TWILIO_AUTH_TOKEN: str = os.getenv("TWILIO_AUTH_TOKEN", "")
    TWILIO_WHATSAPP_FROM: str = os.getenv("TWILIO_WHATSAPP_FROM", "")
    
    # Groq LLM
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
    USE_LLM: bool = os.getenv("USE_LLM", "true").lower() == "true"
    
    # Aplicação
    DEBUG: bool = False
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

# Instância para produção
production_settings = ProductionSettings()
