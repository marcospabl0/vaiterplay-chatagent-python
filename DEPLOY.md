# 🚀 Deploy no Render.com - Genia Quadras

## 📋 Pré-requisitos

1. **Conta no Render.com** - [Criar conta](https://render.com)
2. **Repositório Git** - GitHub, GitLab ou Bitbucket
3. **Variáveis de ambiente** configuradas

## 🔧 Configuração das Variáveis de Ambiente

Configure as seguintes variáveis no dashboard do Render:

### **MongoDB**

```
MONGODB_URI=mongodb+srv://genia-mongodb-dev1:0MZ1z0W1mmSpG1RI@genia-cluster1.hky0vg2.mongodb.net/?retryWrites=true&w=majority&appName=GenIA-Cluster1
MONGODB_DB=vaiterplay
```

### **Twilio WhatsApp**

```
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886
```

### **Groq LLM (Opcional)**

```
GROQ_API_KEY=gsk_your_api_key_here
GROQ_MODEL=llama-3.1-8b-instant
USE_LLM=true
```

### **Aplicação**

```
DEBUG=false
LOG_LEVEL=INFO
```

## 🚀 Passos para Deploy

### **1. Conectar Repositório**

1. Acesse [Render Dashboard](https://dashboard.render.com)
2. Clique em "New +" → "Web Service"
3. Conecte seu repositório Git

### **2. Configurar Serviço**

- **Name**: `genia-quadras`
- **Environment**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### **3. Configurar Variáveis**

1. Vá para a aba "Environment"
2. Adicione todas as variáveis listadas acima
3. Clique em "Save Changes"

### **4. Deploy**

1. Clique em "Create Web Service"
2. Aguarde o build e deploy
3. Anote a URL gerada (ex: `https://genia-quadras.onrender.com`)

## 🔗 Configurar Webhook Twilio

### **1. Atualizar Webhook URL**

No dashboard do Twilio:

1. Vá para WhatsApp Sandbox
2. Configure Webhook URL: `https://sua-app.onrender.com/webhook`
3. Salve as configurações

### **2. Testar Webhook**

```bash
curl -X POST https://sua-app.onrender.com/health
# Deve retornar: OK
```

## 📱 Testando o Sistema

### **1. Teste de Saúde**

```bash
curl https://sua-app.onrender.com/health
```

### **2. Teste de Mensagem**

```bash
curl -X POST https://sua-app.onrender.com/test-message \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "whatsapp:+5511999999999",
    "message": "Oi"
  }'
```

### **3. Teste via WhatsApp**

Envie mensagem para o número do WhatsApp Sandbox:

- "Oi"
- "Quero reservar uma quadra de futebol amanhã às 18h"
- "Quais são minhas reservas?"

## 🔍 Monitoramento

### **Logs**

- Acesse a aba "Logs" no Render Dashboard
- Monitore erros e performance

### **Métricas**

- CPU e Memory usage
- Response time
- Error rate

## 🛠️ Troubleshooting

### **Erro de Build**

- Verifique se todas as dependências estão no `requirements.txt`
- Confirme se o Python 3.8+ está sendo usado

### **Erro de Conexão MongoDB**

- Verifique se `MONGODB_URI` está correto
- Confirme se o IP do Render está na whitelist do MongoDB

### **Erro Twilio**

- Verifique `TWILIO_ACCOUNT_SID` e `TWILIO_AUTH_TOKEN`
- Confirme se o webhook URL está correto

### **Erro Groq**

- Verifique se `GROQ_API_KEY` está válida
- Confirme se o modelo está disponível

## 📊 URLs Importantes

- **App**: `https://sua-app.onrender.com`
- **Health Check**: `https://sua-app.onrender.com/health`
- **API Docs**: `https://sua-app.onrender.com/docs`
- **Webhook**: `https://sua-app.onrender.com/webhook`

## 🎉 Pronto!

Seu agente de reservas está online e funcionando! 🚀
