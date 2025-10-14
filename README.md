# 🏟️ Genia Quadras - Agente WhatsApp

Sistema inteligente de reservas de quadras via WhatsApp usando **FastAPI**, **MongoDB** e **Twilio**.

## 🎯 Sobre o Projeto

O **Genia Quadras** é um agente conversacional que permite aos usuários reservar, consultar e cancelar reservas de quadras esportivas através do WhatsApp, utilizando processamento de linguagem natural para entender comandos em português.

### ✨ Funcionalidades

- 🏟️ **Reservar quadras** - Sistema inteligente que entende comandos naturais
- 📋 **Consultar reservas** - Lista todas as reservas do usuário
- ❌ **Cancelar reservas** - Cancela reservas existentes
- 📅 **Ver disponibilidade** - Mostra horários livres
- 🤖 **Processamento Híbrido** - NLU tradicional + LLM Groq/Llama
- 💬 **Respostas inteligentes** - Conversas naturais e contextuais
- 🧠 **IA Avançada** - Entende perguntas complexas e fornece respostas personalizadas

## 🛠️ Tecnologias

- **FastAPI** - Framework web moderno e rápido
- **MongoDB** - Banco de dados NoSQL com Motor (async driver)
- **Twilio** - API WhatsApp para envio/recebimento de mensagens
- **Groq + Llama** - LLM para processamento de linguagem natural avançado
- **Pydantic** - Validação de dados e modelos
- **Python 3.8+** - Linguagem de programação

## 📁 Estrutura do Projeto

```
genia-quadras/
├── app/
│   ├── main.py                 # Aplicação principal FastAPI
│   ├── settings.py             # Configurações e variáveis de ambiente
│   ├── db.py                   # Conexão MongoDB
│   ├── models/                 # Modelos Pydantic
│   │   ├── court.py           # Modelo de quadras
│   │   ├── reservation.py     # Modelo de reservas
│   │   └── user.py            # Modelo de usuários
│   ├── repositories/          # Camada de acesso a dados
│   │   ├── courts_repo.py     # CRUD quadras
│   │   ├── reservations_repo.py # CRUD reservas
│   │   └── users_repo.py      # CRUD usuários
│   ├── services/              # Lógica de negócio
│   │   ├── whatsapp_service.py # Serviço Twilio WhatsApp
│   │   └── agent_logic.py     # Lógica principal do agente
│   └── utils/
│       └── nlu.py             # Processamento de linguagem natural
├── env.example                # Exemplo de variáveis de ambiente
├── requirements.txt           # Dependências Python
├── run.sh                     # Script de execução
└── README.md                  # Esta documentação
```

## 🚀 Instalação e Configuração

### 1. Pré-requisitos

- Python 3.8 ou superior
- Conta no MongoDB Atlas
- Conta no Twilio com WhatsApp Sandbox ativado

### 2. Clone e Instale

```bash
# Clone o repositório
git clone <url-do-repositorio>
cd genia-quadras

# Instale as dependências
./run.sh install
```

### 3. Configuração das Variáveis de Ambiente

```bash
# Copie o arquivo de exemplo
cp env.example .env

# Edite o arquivo .env com suas credenciais
nano .env
```

**Exemplo de configuração (.env):**

```env
# MongoDB Configuration
MONGODB_URI=mongodb+srv://usuario:senha@cluster.mongodb.net/genia_courts
MONGODB_DB=genia_courts

# Twilio Configuration
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886

# Application Configuration
DEBUG=true
LOG_LEVEL=INFO
```

### 4. Configuração do MongoDB Atlas

1. Crie um cluster no [MongoDB Atlas](https://cloud.mongodb.com)
2. Configure o usuário e senha
3. Adicione seu IP à whitelist
4. Copie a string de conexão para `MONGODB_URI`

### 5. Configuração do Twilio WhatsApp

1. Acesse o [Console Twilio](https://console.twilio.com)
2. Ative o WhatsApp Sandbox
3. Copie o Account SID e Auth Token
4. Configure o número do WhatsApp Sandbox

### 6. Configuração do Groq LLM (Opcional)

1. Acesse o [Console Groq](https://console.groq.com)
2. Crie uma conta gratuita
3. Gere uma API Key
4. Configure no arquivo `.env`:
   ```env
   GROQ_API_KEY=gsk_sua_api_key_aqui
   GROQ_MODEL=llama-3.1-8b-instant
   USE_LLM=true
   ```

**Modelos disponíveis no Groq:**

- `llama-3.1-8b-instant` (recomendado - rápido)
- `llama-3.1-70b-versatile` (mais poderoso)
- `mixtral-8x7b-32768` (multimodal)

## 🏃‍♂️ Executando o Projeto

### Desenvolvimento Local

```bash
# Execute a aplicação
./run.sh run
```

A aplicação estará disponível em:

- **API**: http://localhost:8000
- **Documentação**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

### Testando com ngrok

Para testar com o Twilio WhatsApp Sandbox:

```bash
# Instale o ngrok
# https://ngrok.com/download

# Execute a aplicação
./run.sh run

# Em outro terminal, exponha via HTTPS
ngrok http 8000
```

Configure o webhook no Twilio:

```
https://<seu-id>.ngrok.io/webhook
```

## 💬 Como Usar o Agente

### Exemplos de Comandos

**Reservar uma quadra:**

```
"Quero reservar uma quadra de futebol amanhã às 18h"
"Reservar quadra de futsal hoje às 19:30"
"Quero uma quadra de vôlei para depois de amanhã às 20h"
```

**Consultar reservas:**

```
"Quais são minhas reservas?"
"Mostrar minhas reservas"
"Consultar reservas"
```

**Cancelar reserva:**

```
"Quero cancelar minha reserva de amanhã às 18h"
"Cancelar reserva de hoje às 19h"
```

**Ver disponibilidade:**

```
"Que horários estão livres hoje?"
"Mostrar disponibilidade"
"Horários disponíveis"
```

**Ajuda:**

```
"ajuda"
"Como usar?"
"O que posso fazer?"
```

## 🗄️ Estrutura do Banco de Dados

### Coleção: `quadras`

```json
{
  "_id": ObjectId(),
  "nome": "Quadra 1",
  "tipo": "Futebol Society",
  "endereco": {
    "logradouro": "Av. das Flores, 100",
    "bairro": "Centro",
    "cidade": "Porto Alegre"
  },
  "valor_hora": 120.0,
  "horarios_disponiveis": [
    "2025-01-15T18:00:00",
    "2025-01-15T19:00:00"
  ]
}
```

### Coleção: `reservas`

```json
{
  "_id": ObjectId(),
  "usuario": {
    "nome": "Marcos Paulo",
    "telefone": "+5511999999999"
  },
  "quadra_id": ObjectId(),
  "data_reserva": "2025-01-15T18:00:00",
  "status": "confirmada",
  "criado_em": "2025-01-14T17:00:00"
}
```

### Coleção: `usuarios`

```json
{
  "_id": ObjectId(),
  "nome": "Marcos Paulo",
  "telefone": "+5511999999999",
  "criado_em": "2025-01-14T17:00:00"
}
```

## 🧪 Testando a API

### Endpoints Disponíveis

- `GET /` - Informações da API
- `GET /health` - Health check
- `POST /webhook` - Webhook Twilio WhatsApp
- `POST /test-message` - Teste sem Twilio
- `GET /courts` - Lista quadras
- `GET /reservations/{phone}` - Lista reservas do usuário

### Teste Manual

```bash
# Teste básico
curl http://localhost:8000/health

# Teste de mensagem
curl -X POST http://localhost:8000/test-message \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "whatsapp:+5511999999999",
    "message": "Oi"
  }'
```

### Teste da Integração Groq LLM

```bash
# Teste completo da integração
python3 test_groq_integration.py

# Teste de mensagens que usam LLM
curl -X POST http://localhost:8000/test-message \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "whatsapp:+5511999999999",
    "message": "Me fale sobre as quadras disponíveis"
  }'
```

## 🚀 Deploy

### Render.com (Recomendado)

📋 **Instruções completas**: Veja [DEPLOY.md](DEPLOY.md)

**Passos rápidos:**

1. Conecte seu repositório ao [Render.com](https://render.com)
2. Configure as variáveis de ambiente
3. Deploy automático a cada push

### Variáveis de Ambiente Necessárias

```env
# MongoDB
MONGODB_URI=mongodb+srv://genia-mongodb-dev1:0MZ1z0W1mmSpG1RI@genia-cluster1.hky0vg2.mongodb.net/?retryWrites=true&w=majority&appName=GenIA-Cluster1
MONGODB_DB=vaiterplay

# Twilio WhatsApp
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886

# Groq LLM (Opcional)
GROQ_API_KEY=gsk_your_api_key_here
GROQ_MODEL=llama-3.1-8b-instant
USE_LLM=true

# Aplicação
DEBUG=false
LOG_LEVEL=INFO
```

### Outras Plataformas

- **Heroku**: Use `Procfile` com `web: uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- **Railway**: Configure `PORT` environment variable
- **DigitalOcean App Platform**: Use Python buildpack

## 🔧 Desenvolvimento

### Adicionando Novas Funcionalidades

1. **Novos tipos de quadra**: Edite `app/utils/nlu.py`
2. **Novas intenções**: Adicione padrões em `nlu_processor.intent_patterns`
3. **Novos endpoints**: Adicione em `app/main.py`
4. **Novos modelos**: Crie em `app/models/`

### Logs

Os logs são exibidos no console com diferentes níveis:

- `INFO`: Operações normais
- `WARNING`: Avisos
- `ERROR`: Erros que não impedem execução
- `DEBUG`: Informações detalhadas (apenas em modo DEBUG)

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 📞 Suporte

Para dúvidas ou problemas:

1. Abra uma issue no GitHub
2. Verifique os logs da aplicação
3. Teste com o endpoint `/test-message`
4. Verifique as configurações do `.env`

---

**Desenvolvido com ❤️ para facilitar reservas de quadras via WhatsApp**
