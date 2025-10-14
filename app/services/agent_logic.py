"""
Lógica principal do agente de reservas
"""
from datetime import datetime, timedelta
from typing import Optional
import logging

from app.utils.nlu import nlu_processor
from app.services.whatsapp_service import whatsapp_service
from app.services.groq_llm_service import groq_llm_service
from app.repositories.users_repo import users_repo
from app.repositories.courts_repo import courts_repo
from app.repositories.reservations_repo import reservations_repo
from app.models.user import UserCreate
from app.models.reservation import ReservationCreate

logger = logging.getLogger(__name__)


class AgentLogic:
    """Lógica principal do agente de reservas"""
    
    def __init__(self):
        self.nlu = nlu_processor
        self.whatsapp = whatsapp_service
        self.llm = groq_llm_service
    
    async def process_message(self, phone: str, message: str) -> str:
        """
        Processa mensagem do usuário usando abordagem híbrida (NLU + LLM)
        
        Args:
            phone: Número do telefone do usuário
            message: Mensagem recebida
            
        Returns:
            str: Resposta do agente
        """
        try:
            # Busca ou cria usuário primeiro
            user = await users_repo.find_or_create_by_phone(phone, "Usuário")
            
            # 1. Tenta processar com NLU tradicional primeiro
            nlu_data = self.nlu.process_message(message)
            intent = nlu_data["intent"]
            
            logger.info(f"NLU identificou intenção: {intent}")
            
            # 2. Se NLU conseguiu identificar uma intenção clara, usa lógica tradicional
            if intent != "indefinida" and intent in ["saudacao", "ajuda", "reservar", "consultar", "cancelar"]:
                logger.info("Usando lógica tradicional NLU")
                return await self._handle_with_traditional_logic(user, nlu_data)
            
            # 3. Se NLU não conseguiu identificar, tenta LLM ou usa fallback
            if intent == "indefinida":
                if self.llm.is_available():
                    logger.info("Usando LLM para processar mensagem indefinida")
                    return await self._handle_with_llm(user, message, nlu_data)
                else:
                    # Fallback para lógica tradicional se LLM não disponível
                    logger.info("LLM não disponível, usando lógica tradicional para mensagem indefinida")
                    return await self._handle_unknown_intent(user, message)
            else:
                # Se NLU identificou uma intenção válida, usa lógica tradicional
                logger.info("Usando lógica tradicional para intenção identificada")
                return await self._handle_with_traditional_logic(user, nlu_data)
                
        except Exception as e:
            logger.error(f"Erro ao processar mensagem: {e}")
            return "❌ Ops! Algo deu errado. Tente novamente ou digite 'ajuda' para ver as opções disponíveis."
    
    async def _handle_with_traditional_logic(self, user, nlu_data: dict) -> str:
        """Processa mensagem usando lógica tradicional NLU"""
        intent = nlu_data["intent"]
        
        if intent == "saudacao":
            return await self._handle_greeting(user)
        elif intent == "ajuda":
            return await self._handle_help(user)
        elif intent == "reservar":
            return await self._handle_reservation(user, nlu_data)
        elif intent == "confirmar":
            return await self._handle_confirmation(user, nlu_data)
        elif intent == "consultar":
            return await self._handle_list_reservations(user)
        elif intent == "cancelar":
            return await self._handle_cancel_reservation(user, nlu_data)
        elif intent == "disponibilidade":
            return await self._handle_availability(nlu_data)
        else:
            return await self._handle_unknown_intent(user, nlu_data["original_message"])
    
    async def _handle_with_llm(self, user, message: str, nlu_data: dict) -> str:
        """Processa mensagem usando LLM"""
        try:
            # Prepara contexto adicional
            context = {
                "user_name": user.nome,
                "user_phone": user.telefone,
                "nlu_data": nlu_data
            }
            
            # Usa LLM para processar a mensagem
            llm_response = await self.llm.process_with_llm(message, user.telefone, context)
            
            # Se o LLM sugerir uma ação específica (como reservar), executa a lógica tradicional
            if self._should_execute_action(llm_response, nlu_data):
                logger.info("LLM sugeriu ação específica, executando lógica tradicional")
                return await self._handle_with_traditional_logic(user, nlu_data)
            
            return llm_response
            
        except Exception as e:
            logger.error(f"Erro ao processar com LLM: {e}")
            # Fallback para lógica tradicional
            return await self._handle_with_traditional_logic(user, nlu_data)
    
    def _should_execute_action(self, llm_response: str, nlu_data: dict) -> bool:
        """Verifica se o LLM sugeriu uma ação que deve ser executada pela lógica tradicional"""
        # Se NLU já identificou uma intenção clara de ação, executa
        if nlu_data["intent"] in ["reservar", "consultar", "cancelar"]:
            return True
        
        # Para mensagens indefinidas, não executa ação tradicional
        # Deixa o LLM responder diretamente
        return False
    
    async def _handle_greeting(self, user) -> str:
        """Processa saudações"""
        return f"""Olá {user.nome}! 👋

Bem-vindo ao sistema de reservas de quadras! 

Posso te ajudar com:
🏟️ Reservar uma quadra
📋 Consultar suas reservas  
❌ Cancelar uma reserva
📅 Ver horários disponíveis

Como posso te ajudar hoje?"""
    
    async def _handle_help(self, user) -> str:
        """Processa pedidos de ajuda"""
        return """📋 *Como usar o sistema:*

🏟️ *Para reservar:*
"Quero reservar uma quadra de futebol amanhã às 18h"

📅 *Para consultar:*
"Quais são minhas reservas?"

❌ *Para cancelar:*
"Quero cancelar minha reserva de amanhã às 18h"

📋 *Para ver disponibilidade:*
"Que horários estão livres hoje?"

Digite sua solicitação em linguagem natural! 😊"""
    
    async def _handle_reservation(self, user, data: dict) -> str:
        """Processa solicitações de reserva"""
        try:
            # Verifica se tem dados suficientes
            if not data.get("datetime"):
                return """❌ Preciso saber quando você quer reservar!

Por favor, especifique:
- Tipo de quadra (futebol, futsal, vôlei, etc.)
- Data (hoje, amanhã, ou data específica)
- Horário (ex: 18h, 19:30)

Exemplo: "Quero reservar uma quadra de futebol amanhã às 18h" """
            
            reservation_datetime = data["datetime"]
            court_type = data.get("court_type", "futebol")
            hours_quantity = data.get("hours_quantity", 1)
            
            # Busca quadras disponíveis
            available_courts = await courts_repo.get_available_at_time(reservation_datetime)
            
            if not available_courts:
                return f"❌ Nenhuma quadra disponível em {reservation_datetime.strftime('%d/%m às %H:%M')}.\n\nTente outro horário ou digite 'disponibilidade' para ver horários livres."
            
            # Filtra por tipo se especificado
            if court_type:
                available_courts = [court for court in available_courts 
                                 if court_type.lower() in court.tipo.lower()]
            
            if not available_courts:
                return f"❌ Nenhuma quadra de {court_type} disponível em {reservation_datetime.strftime('%d/%m às %H:%M')}.\n\nTente outro tipo de quadra ou horário."
            
            # Pega a primeira quadra disponível
            selected_court = available_courts[0]
            
            # Calcula valores
            valor_hora = selected_court.valor_hora
            valor_total = valor_hora * hours_quantity
            
            # Verifica se já existe reserva para este usuário no mesmo horário
            existing_reservation = await reservations_repo.get_by_court_and_time(
                selected_court.id, reservation_datetime
            )
            
            if existing_reservation and existing_reservation.usuario.telefone == user.telefone:
                return f"✅ Você já tem uma reserva confirmada para {reservation_datetime.strftime('%d/%m às %H:%M')} na {selected_court.nome}!"
            
            # Mostra confirmação de preço antes de criar a reserva
            return f"""💰 *Confirmação de Reserva*

🏟️ Quadra: {selected_court.nome}
⚽ Tipo: {selected_court.tipo}
📅 Data: {reservation_datetime.strftime('%d/%m/%Y')}
🕐 Horário: {reservation_datetime.strftime('%H:%M')}
⏰ Duração: {hours_quantity} hora{'s' if hours_quantity > 1 else ''}
💰 Valor/hora: R$ {valor_hora:.2f}
💵 Valor total: R$ {valor_total:.2f}

Para confirmar, digite: 'confirmar reserva'
Para cancelar, digite: 'cancelar'"""
            
        except Exception as e:
            logger.error(f"Erro ao processar reserva: {e}")
            return "❌ Erro ao processar sua reserva. Tente novamente."
    
    async def _handle_confirmation(self, user, data: dict) -> str:
        """Processa confirmação de reserva"""
        try:
            # Por enquanto, vamos implementar uma versão simples
            # Em uma versão mais avançada, poderíamos armazenar dados temporários
            return """❌ Confirmação não implementada ainda.

Por favor, faça uma nova solicitação de reserva com todos os detalhes:
"Quero reservar uma quadra de futebol amanhã às 18h por 2 horas"

Em breve implementaremos o sistema de confirmação! 🚀"""
            
        except Exception as e:
            logger.error(f"Erro ao processar confirmação: {e}")
            return "❌ Erro ao processar confirmação. Tente novamente."
    
    async def _handle_list_reservations(self, user) -> str:
        """Lista reservas do usuário"""
        try:
            reservations = await reservations_repo.get_by_user_phone(user.telefone)
            
            if not reservations:
                return "📋 Você não tem nenhuma reserva confirmada no momento.\n\nPara fazer uma reserva, digite algo como: 'Quero reservar uma quadra de futebol amanhã às 18h'"
            
            response = f"📋 *Suas reservas:*\n\n"
            
            for i, reservation in enumerate(reservations, 1):
                response += f"{i}. 🏟️ {reservation.quadra_nome}\n"
                response += f"   ⚽ {reservation.quadra_tipo}\n"
                response += f"   📅 {reservation.data_reserva.strftime('%d/%m/%Y às %H:%M')}\n"
                response += f"   💰 R$ {reservation.valor_hora:.2f}/hora\n"
                response += f"   📊 Status: {reservation.status.title()}\n\n"
            
            response += "Para cancelar uma reserva, digite: 'Quero cancelar minha reserva de [data] às [hora]'"
            
            return response
            
        except Exception as e:
            logger.error(f"Erro ao listar reservas: {e}")
            return "❌ Erro ao consultar suas reservas. Tente novamente."
    
    async def _handle_cancel_reservation(self, user, data: dict) -> str:
        """Processa cancelamento de reserva"""
        try:
            if not data.get("datetime"):
                return """❌ Para cancelar uma reserva, preciso saber qual!

Por favor, especifique a data e horário da reserva que deseja cancelar.

Exemplo: "Quero cancelar minha reserva de amanhã às 18h" """
            
            reservation_datetime = data["datetime"]
            
            # Cancela a reserva
            success = await reservations_repo.cancel_by_user_and_time(
                user.telefone, reservation_datetime
            )
            
            if success:
                return f"✅ Reserva cancelada com sucesso!\n\n📅 Data cancelada: {reservation_datetime.strftime('%d/%m às %H:%M')}\n\nPara fazer uma nova reserva, é só me avisar! 😊"
            else:
                return f"❌ Não encontrei nenhuma reserva sua para {reservation_datetime.strftime('%d/%m às %H:%M')}.\n\nVerifique os dados e tente novamente."
            
        except Exception as e:
            logger.error(f"Erro ao cancelar reserva: {e}")
            return "❌ Erro ao cancelar reserva. Tente novamente."
    
    async def _handle_availability(self, data: dict) -> str:
        """Mostra horários disponíveis"""
        try:
            # Busca todas as quadras
            all_courts = await courts_repo.get_all()
            
            if not all_courts:
                return "❌ Nenhuma quadra cadastrada no sistema."
            
            response = "📅 *Horários disponíveis:*\n\n"
            
            # Agrupa por tipo de quadra
            courts_by_type = {}
            for court in all_courts:
                court_type = court.tipo
                if court_type not in courts_by_type:
                    courts_by_type[court_type] = []
                courts_by_type[court_type].append(court)
            
            for court_type, courts in courts_by_type.items():
                response += f"⚽ *{court_type.upper()}*\n"
                
                for court in courts:
                    if court.horarios_disponiveis:
                        response += f"  🏟️ {court.nome}:\n"
                        for horario in sorted(court.horarios_disponiveis):
                            response += f"    • {horario.strftime('%d/%m às %H:%M')}\n"
                        response += f"    💰 R$ {court.valor_hora:.2f}/hora\n\n"
                    else:
                        response += f"  🏟️ {court.nome}: Sem horários disponíveis\n"
                        response += f"    💰 R$ {court.valor_hora:.2f}/hora\n\n"
            
            response += "Para reservar, digite: 'Quero reservar uma quadra de [tipo] [data] às [hora]'"
            
            return response
            
        except Exception as e:
            logger.error(f"Erro ao consultar disponibilidade: {e}")
            return "❌ Erro ao consultar disponibilidade. Tente novamente."
    
    async def _handle_unknown_intent(self, user, message: str) -> str:
        """Processa intenções não reconhecidas"""
        return f"""🤔 Não entendi sua solicitação: "{message}"

Posso te ajudar com:
🏟️ Reservar uma quadra
📋 Consultar suas reservas
❌ Cancelar uma reserva  
📅 Ver horários disponíveis

Digite 'ajuda' para ver exemplos de como usar o sistema! 😊"""


# Instância global da lógica do agente
agent_logic = AgentLogic()
