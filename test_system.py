"""
Script de teste para demonstrar o funcionamento do agente
"""
import asyncio
import requests
import json
from datetime import datetime

# URL da API (ajuste conforme necessário)
API_URL = "http://localhost:8000"

def test_api_endpoints():
    """Testa os endpoints básicos da API"""
    print("🧪 Testando endpoints da API...")
    
    try:
        # Teste health check
        response = requests.get(f"{API_URL}/health")
        print(f"✅ Health check: {response.status_code} - {response.json()}")
        
        # Teste endpoint raiz
        response = requests.get(f"{API_URL}/")
        print(f"✅ Endpoint raiz: {response.status_code} - {response.json()}")
        
    except requests.exceptions.ConnectionError:
        print("❌ API não está rodando. Execute: ./run.sh run")
        return False
    
    return True

def test_agent_messages():
    """Testa mensagens do agente"""
    print("\n🤖 Testando mensagens do agente...")
    
    test_cases = [
        {
            "phone": "whatsapp:+5511999999999",
            "message": "Oi",
            "description": "Saudação"
        },
        {
            "phone": "whatsapp:+5511999999999", 
            "message": "ajuda",
            "description": "Pedido de ajuda"
        },
        {
            "phone": "whatsapp:+5511999999999",
            "message": "Quero reservar uma quadra de futebol amanhã às 18h",
            "description": "Reserva de quadra"
        },
        {
            "phone": "whatsapp:+5511999999999",
            "message": "Quais são minhas reservas?",
            "description": "Consulta de reservas"
        },
        {
            "phone": "whatsapp:+5511999999999",
            "message": "Que horários estão livres hoje?",
            "description": "Consulta de disponibilidade"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 Teste {i}: {test_case['description']}")
        print(f"   Mensagem: '{test_case['message']}'")
        
        try:
            response = requests.post(
                f"{API_URL}/test-message",
                json={
                    "phone": test_case["phone"],
                    "message": test_case["message"]
                },
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Resposta: {data['reply'][:100]}...")
            else:
                print(f"   ❌ Erro: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Erro: {e}")

def test_courts_endpoint():
    """Testa endpoint de quadras"""
    print("\n🏟️ Testando endpoint de quadras...")
    
    try:
        response = requests.get(f"{API_URL}/courts")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ {len(data['courts'])} quadras encontradas")
            for court in data['courts'][:2]:  # Mostra apenas as 2 primeiras
                print(f"   🏟️ {court['nome']} - {court['tipo']} - R$ {court['valor_hora']}/h")
        else:
            print(f"❌ Erro: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro: {e}")

def main():
    """Função principal de teste"""
    print("🏟️ Genia Quadras - Teste do Sistema")
    print("=" * 50)
    
    # Testa endpoints básicos
    if not test_api_endpoints():
        return
    
    # Testa mensagens do agente
    test_agent_messages()
    
    # Testa endpoint de quadras
    test_courts_endpoint()
    
    print("\n" + "=" * 50)
    print("✅ Testes concluídos!")
    print("\n💡 Para testar com WhatsApp real:")
    print("   1. Configure suas credenciais no arquivo .env")
    print("   2. Execute: ./run.sh run")
    print("   3. Use ngrok para expor a API")
    print("   4. Configure o webhook no Twilio")

if __name__ == "__main__":
    main()
