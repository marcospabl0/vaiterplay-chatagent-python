"""
Serviço de integração com Groq LLM
"""
from groq import Groq
import logging
from typing import Optional, Dict, Any
import json

from app.settings import settings
from app.repositories.courts_repo import courts_repo
from app.repositories.reservations_repo import reservations_repo

logger = logging.getLogger(__name__)


class GroqLLMService:
    """Serviço para integração com Groq LLM"""
    
    def __init__(self):
        self.client = None
        self.model = settings.GROQ_MODEL
        self.use_llm = settings.USE_LLM
        
        if settings.GROQ_API_KEY and self.use_llm:
            try:
                self.client = Groq(api_key=settings.GROQ_API_KEY)
                logger.info(f"Groq LLM inicializado com modelo: {self.model}")
            except Exception as e:
                logger.error(f"Erro ao inicializar Groq: {e}")
                self.client = None
        else:
            logger.warning("Groq LLM desabilitado - GROQ_API_KEY não configurada ou USE_LLM=False")
    
    async def process_with_llm(self, message: str, user_phone: str, context: Dict[str, Any] = None) -> str:
        """
        Processa mensagem usando Groq LLM
        
        Args:
            message: Mensagem do usuário
            user_phone: Telefone do usuário
            context: Contexto adicional (reservas, quadras, etc.)
            
        Returns:
            str: Resposta do LLM
        """
        if not self.client:
            return "❌ Serviço de IA temporariamente indisponível. Tente novamente."
        
        try:
            # Busca contexto do banco de dados
            courts = await courts_repo.get_all()
            user_reservations = await reservations_repo.get_by_user_phone(user_phone)
            
            # Prepara contexto das quadras
            courts_info = []
            for court in courts:
                courts_info.append(f"- {court.nome}: {court.tipo} (R$ {court.valor_hora}/hora)")
            
            # Prepara contexto das reservas
            reservations_info = []
            for reservation in user_reservations:
                reservations_info.append(
                    f"- {reservation.quadra_nome} ({reservation.quadra_tipo}) em "
                    f"{reservation.data_reserva.strftime('%d/%m às %H:%M')} - {reservation.status}"
                )
            
            # Monta o prompt
            prompt = self._build_prompt(message, courts_info, reservations_info, context)
            
            # Chama o LLM
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": self._get_system_prompt()
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=500,
                top_p=1,
                stream=False
            )
            
            llm_response = response.choices[0].message.content.strip()
            logger.info(f"LLM respondeu: {llm_response[:100]}...")
            
            return llm_response
            
        except Exception as e:
            logger.error(f"Erro ao processar com LLM: {e}")
            return "❌ Erro ao processar sua mensagem. Tente novamente."
    
    def _get_system_prompt(self) -> str:
        """Retorna o prompt do sistema para o LLM"""
        return """Você é um assistente especializado em reservas de quadras esportivas via WhatsApp.

INSTRUÇÕES IMPORTANTES:
1. Seja sempre amigável e prestativo
2. Use emojis para tornar as respostas mais atrativas
3. Responda em português brasileiro
4. Seja conciso mas informativo
5. Para reservas, sempre confirme os detalhes
6. Para consultas, liste as informações de forma clara
7. Se não souber algo específico, seja honesto

FUNCIONALIDADES:
- Reservar quadras esportivas
- Consultar reservas existentes
- Cancelar reservas
- Informar sobre disponibilidade
- Responder dúvidas gerais

TONE: Profissional mas descontraído, como um atendente de academia."""
    
    def _build_prompt(self, message: str, courts_info: list, reservations_info: list, context: Dict[str, Any] = None) -> str:
        """Constrói o prompt para o LLM"""
        
        prompt = f"""CONTEXTO DO SISTEMA DE QUADRAS:

QUADRAS DISPONÍVEIS:
{chr(10).join(courts_info) if courts_info else "Nenhuma quadra cadastrada"}

RESERVAS DO USUÁRIO:
{chr(10).join(reservations_info) if reservations_info else "Nenhuma reserva encontrada"}

MENSAGEM DO USUÁRIO: "{message}"

INSTRUÇÕES:
- Se o usuário quer RESERVAR uma quadra, confirme os detalhes e oriente sobre como proceder
- Se o usuário quer CONSULTAR reservas, liste as informações de forma clara
- Se o usuário quer CANCELAR uma reserva, confirme e oriente sobre o processo
- Se o usuário quer saber DISPONIBILIDADE, liste os horários disponíveis
- Se for uma SAUDAÇÃO, seja caloroso e ofereça ajuda
- Se for uma DÚVIDA geral, responda de forma útil
- Se não entender a solicitação, peça esclarecimentos de forma educada

Responda de forma natural e útil:"""
        
        return prompt
    
    async def extract_intent_with_llm(self, message: str) -> Dict[str, Any]:
        """
        Usa LLM para extrair intenção e dados da mensagem
        
        Args:
            message: Mensagem do usuário
            
        Returns:
            Dict com intenção e dados extraídos
        """
        if not self.client:
            return {"intent": "indefinida", "confidence": 0.0}
        
        try:
            prompt = f"""Analise a seguinte mensagem e identifique a intenção do usuário:

MENSAGEM: "{message}"

INTENÇÕES POSSÍVEIS:
- saudacao: Cumprimentos, oi, olá, bom dia, etc.
- reservar: Quer fazer uma reserva de quadra
- consultar: Quer ver suas reservas
- cancelar: Quer cancelar uma reserva
- disponibilidade: Quer saber horários disponíveis
- ajuda: Pedido de ajuda ou instruções
- indefinida: Não consegue identificar a intenção

Responda APENAS com um JSON válido no formato:
{{
    "intent": "nome_da_intenção",
    "confidence": 0.95,
    "court_type": "tipo_de_quadra_se_identificado",
    "datetime": "data_hora_se_identificado",
    "extracted_data": {{
        "additional_info": "outras informações relevantes"
    }}
}}"""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "Você é um especialista em análise de intenções. Responda APENAS com JSON válido."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=200
            )
            
            llm_response = response.choices[0].message.content.strip()
            
            # Tenta fazer parse do JSON
            try:
                result = json.loads(llm_response)
                logger.info(f"LLM extraiu intenção: {result.get('intent', 'indefinida')}")
                return result
            except json.JSONDecodeError:
                logger.warning(f"LLM retornou JSON inválido: {llm_response}")
                return {"intent": "indefinida", "confidence": 0.0}
                
        except Exception as e:
            logger.error(f"Erro ao extrair intenção com LLM: {e}")
            return {"intent": "indefinida", "confidence": 0.0}
    
    def is_available(self) -> bool:
        """Verifica se o serviço LLM está disponível"""
        return self.client is not None and self.use_llm


# Instância global do serviço LLM
groq_llm_service = GroqLLMService()
