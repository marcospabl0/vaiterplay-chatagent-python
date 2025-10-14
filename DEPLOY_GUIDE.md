# 🚀 Guia Completo de Deploy - Genia Quadras

## ✅ Arquivos Criados para Deploy

### **Configuração do Render**

- ✅ `render.yaml` - Configuração automática do Render
- ✅ `render.config` - Configurações manuais
- ✅ `start.sh` - Script de inicialização
- ✅ `app/production_settings.py` - Configurações de produção

### **Documentação**

- ✅ `DEPLOY.md` - Guia completo de deploy
- ✅ `README.md` - Atualizado com instruções
- ✅ `.gitignore` - Atualizado para produção

## 🎯 Próximos Passos

### **1. Preparar Repositório Git**

```bash
# Inicializar git (se não existir)
git init

# Adicionar arquivos
git add .

# Commit inicial
git commit -m "feat: sistema completo de reservas com LLM"

# Conectar ao GitHub/GitLab
git remote add origin https://github.com/seu-usuario/genia-quadras.git
git push -u origin main
```

### **2. Configurar Render.com**

#### **A. Criar Conta e Conectar Repositório**

1. Acesse [render.com](https://render.com)
2. Clique em "Get Started for Free"
3. Conecte sua conta GitHub/GitLab
4. Clique em "New +" → "Web Service"
5. Selecione seu repositório `genia-quadras`

#### **B. Configurar Serviço**

- **Name**: `genia-quadras`
- **Environment**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

#### **C. Configurar Variáveis de Ambiente**

Na aba "Environment", adicione:

```env
# MongoDB (já configurado)
MONGODB_URI=mongodb+srv://genia-mongodb-dev1:0MZ1z0W1mmSpG1RI@genia-cluster1.hky0vg2.mongodb.net/?retryWrites=true&w=majority&appName=GenIA-Cluster1
MONGODB_DB=vaiterplay

# Twilio WhatsApp (configure suas credenciais)
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886

# Groq LLM (opcional - configure sua API key)
GROQ_API_KEY=gsk_your_api_key_here
GROQ_MODEL=llama-3.1-8b-instant
USE_LLM=true

# Aplicação
DEBUG=false
LOG_LEVEL=INFO
```

### **3. Deploy**

1. Clique em "Create Web Service"
2. Aguarde o build (2-3 minutos)
3. Anote a URL gerada: `https://genia-quadras.onrender.com`

### **4. Configurar Webhook Twilio**

1. Acesse [Twilio Console](https://console.twilio.com)
2. Vá para WhatsApp Sandbox
3. Configure Webhook URL: `https://sua-app.onrender.com/webhook`
4. Salve as configurações

### **5. Testar Sistema**

#### **A. Teste de Saúde**

```bash
curl https://sua-app.onrender.com/health
# Deve retornar: OK
```

#### **B. Teste de API**

```bash
curl -X POST https://sua-app.onrender.com/test-message \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "whatsapp:+5511999999999",
    "message": "Oi"
  }'
```

#### **C. Teste via WhatsApp**

Envie mensagem para o número do WhatsApp Sandbox:

- "Oi"
- "Quero reservar uma quadra de futebol amanhã às 18h por 2 horas"
- "Quais são minhas reservas?"

## 🔧 Troubleshooting

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

### **Funcionalidades Disponíveis:**

- ✅ Reservas com confirmação de preço
- ✅ Múltiplas horas por reserva
- ✅ Horários de hora em hora
- ✅ Integração com LLM Groq/Llama
- ✅ Processamento de linguagem natural
- ✅ Webhook WhatsApp funcional

### **Próximas Melhorias:**

- 🔄 Sistema de confirmação de reservas
- 📧 Notificações por email
- 📊 Dashboard administrativo
- 💳 Integração com pagamentos
- 📱 App mobile
