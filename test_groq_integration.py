"""
Script de teste para demonstrar a integração com Groq LLM
"""
import asyncio
import logging
import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# Configuração de logging
logging.basicConfig(level=logging.INFO)

from app.db import connect_to_mongo, close_mongo_connection
from app.services.agent_logic import agent_logic
from app.services.groq_llm_service import groq_llm_service

async def test_groq_integration():
    """Testa a integração com Groq LLM"""
    
    print("🧠 Testando integração com Groq LLM...")
    print("=" * 50)
    
    # Conecta ao banco
    await connect_to_mongo()
    
    try:
        # Verifica se o serviço LLM está disponível
        if groq_llm_service.is_available():
            print("✅ Serviço Groq LLM disponível!")
            print(f"📋 Modelo: {groq_llm_service.model}")
        else:
            print("❌ Serviço Groq LLM não disponível")
            print("💡 Configure GROQ_API_KEY no arquivo .env")
            return
        
        # Casos de teste
        test_cases = [
            {
                "message": "Oi",
                "description": "Saudação simples (deve usar NLU tradicional)"
            },
            {
                "message": "Quero reservar uma quadra de futebol amanhã às 18h",
                "description": "Reserva específica (deve usar NLU tradicional)"
            },
            {
                "message": "Me fale sobre as quadras disponíveis",
                "description": "Pergunta geral (deve usar LLM)"
            },
            {
                "message": "Qual é o melhor horário para jogar futebol?",
                "description": "Pergunta de opinião (deve usar LLM)"
            },
            {
                "message": "Preciso de ajuda para entender como funciona o sistema",
                "description": "Solicitação de ajuda (deve usar LLM)"
            },
            {
                "message": "Que tipos de esportes vocês oferecem?",
                "description": "Pergunta sobre serviços (deve usar LLM)"
            }
        ]
        
        phone = "whatsapp:+5511999999999"
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n📝 Teste {i}: {test_case['description']}")
            print(f"   Mensagem: '{test_case['message']}'")
            print("   " + "-" * 40)
            
            try:
                result = await agent_logic.process_message(phone, test_case['message'])
                print(f"   ✅ Resposta: {result[:100]}...")
                
                # Pequena pausa entre testes
                await asyncio.sleep(1)
                
            except Exception as e:
                print(f"   ❌ Erro: {e}")
        
        print("\n" + "=" * 50)
        print("🎉 Testes concluídos!")
        
    except Exception as e:
        print(f"❌ Erro geral: {e}")
    
    finally:
        await close_mongo_connection()

async def test_llm_only():
    """Testa apenas o serviço LLM"""
    
    print("\n🤖 Testando apenas o serviço LLM...")
    print("=" * 30)
    
    if not groq_llm_service.is_available():
        print("❌ Serviço LLM não disponível")
        return
    
    test_messages = [
        "Me explique como funciona o sistema de reservas",
        "Quais são os benefícios de praticar esportes?",
        "Você pode me dar dicas de saúde?",
        "Como posso melhorar meu jogo de futebol?"
    ]
    
    phone = "whatsapp:+5511999999999"
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n📝 Teste LLM {i}: '{message}'")
        print("-" * 30)
        
        try:
            result = await groq_llm_service.process_with_llm(message, phone)
            print(f"✅ Resposta: {result}")
            
        except Exception as e:
            print(f"❌ Erro: {e}")
        
        await asyncio.sleep(1)

def main():
    """Função principal"""
    print("🏟️ Genia Quadras - Teste de Integração Groq LLM")
    print("=" * 60)
    
    # Verifica se a API key está configurada
    api_key = os.getenv('GROQ_API_KEY', '')
    if not api_key or api_key == 'gsk_your_api_key_here':
        print("⚠️  GROQ_API_KEY não configurada!")
        print("💡 Configure sua API key do Groq no arquivo .env")
        print("🔗 Obtenha sua API key em: https://console.groq.com/")
        return
    
    # Executa os testes
    asyncio.run(test_groq_integration())
    asyncio.run(test_llm_only())

if __name__ == "__main__":
    main()
