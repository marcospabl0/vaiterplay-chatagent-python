"""
Serviço para envio de mensagens via Twilio WhatsApp
"""
from twilio.rest import Client
from twilio.base.exceptions import TwilioException
import logging

from app.settings import settings

logger = logging.getLogger(__name__)


class WhatsAppService:
    """Serviço para envio de mensagens WhatsApp via Twilio"""
    
    def __init__(self):
        self.client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        self.from_number = settings.TWILIO_WHATSAPP_FROM
    
    def send_message(self, to_number: str, text: str) -> bool:
        """
        Envia mensagem WhatsApp
        
        Args:
            to_number: Número de destino (formato whatsapp:+5511999999999)
            text: Texto da mensagem
            
        Returns:
            bool: True se enviado com sucesso, False caso contrário
        """
        try:
            # Garante que o número está no formato correto
            if not to_number.startswith("whatsapp:"):
                to_number = f"whatsapp:{to_number}"
            
            message = self.client.messages.create(
                from_=self.from_number,
                to=to_number,
                body=text
            )
            
            logger.info(f"Mensagem enviada para {to_number}: {message.sid}")
            return True
            
        except TwilioException as e:
            logger.error(f"Erro Twilio ao enviar mensagem: {e}")
            return False
        except Exception as e:
            logger.error(f"Erro geral ao enviar mensagem: {e}")
            return False
    
    def send_welcome_message(self, to_number: str, user_name: str = None) -> bool:
        """Envia mensagem de boas-vindas"""
        name = user_name or "usuário"
        message = f"""Olá {name}! 👋

Bem-vindo ao sistema de reservas de quadras! 

Posso te ajudar com:
🏟️ Reservar uma quadra
📋 Consultar suas reservas
❌ Cancelar uma reserva
📅 Ver horários disponíveis

Como posso te ajudar hoje?"""
        
        return self.send_message(to_number, message)
    
    def send_help_message(self, to_number: str) -> bool:
        """Envia mensagem de ajuda"""
        message = """📋 *Como usar o sistema:*

🏟️ *Para reservar:*
"Quero reservar uma quadra de futebol amanhã às 18h"

📅 *Para consultar:*
"Quais são minhas reservas?"

❌ *Para cancelar:*
"Quero cancelar minha reserva de amanhã às 18h"

📋 *Para ver disponibilidade:*
"Que horários estão livres hoje?"

Digite sua solicitação em linguagem natural! 😊"""
        
        return self.send_message(to_number, message)
    
    def send_error_message(self, to_number: str, error_type: str = "geral") -> bool:
        """Envia mensagem de erro"""
        if error_type == "reserva_nao_encontrada":
            message = "❌ Não encontrei nenhuma reserva com essas informações. Verifique os dados e tente novamente."
        elif error_type == "horario_indisponivel":
            message = "❌ Este horário não está disponível. Tente outro horário."
        elif error_type == "dados_incompletos":
            message = "❌ Preciso de mais informações. Por favor, especifique o tipo de quadra e horário desejado."
        else:
            message = "❌ Ops! Algo deu errado. Tente novamente ou digite 'ajuda' para ver as opções disponíveis."
        
        return self.send_message(to_number, message)


# Instância global do serviço
whatsapp_service = WhatsAppService()
