# 🔧 SOLUÇÃO PARA CONFLITOS DE DEPENDÊNCIAS

## ❌ Erro Identificado

```
ERROR: Cannot install -r requirements.txt (line 1) and pydantic==2.0.0 because these package versions have conflicting dependencies.
```

## ✅ SOLUÇÃO IMPLEMENTADA

### **1. Requirements Minimal Criado**

```
fastapi==0.95.0
uvicorn==0.22.0
motor==3.2.0
pymongo==4.3.0
twilio==8.5.0
python-dotenv==0.21.0
pydantic==1.10.0
python-dateutil==2.8.2
```

### **2. Removido Groq Temporariamente**

- ❌ `groq==0.15.0` (pode causar conflitos)
- ✅ Funcionalidade LLM será adicionada depois

### **3. render.yaml Atualizado**

- ✅ Usa `requirements-minimal.txt`
- ✅ Start command: `uvicorn app.main_minimal:app`

## 🚀 DEPLOY IMEDIATO

### **Opção 1: Deploy Manual (Recomendado)**

No dashboard do Render:

- **Build Command**: `pip install --upgrade pip && pip install -r requirements-minimal.txt`
- **Start Command**: `uvicorn app.main_minimal:app --host 0.0.0.0 --port $PORT`

### **Opção 2: Deploy Automático**

1. **Commit e push** das alterações
2. **Deploy automático** via Git

## 📋 Variáveis de Ambiente

```env
MONGODB_URI=mongodb+srv://genia-mongodb-dev1:0MZ1z0W1mmSpG1RI@genia-cluster1.hky0vg2.mongodb.net/?retryWrites=true&w=majority&appName=GenIA-Cluster1
MONGODB_DB=vaiterplay
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886
DEBUG=false
LOG_LEVEL=INFO
```

## 🔄 EVOLUÇÃO GRADUAL

### **Fase 1: Deploy Básico** ✅

- Aplicação funcionando
- Endpoints básicos
- Webhook Twilio

### **Fase 2: MongoDB** (Próximo)

- Adicionar conexão MongoDB
- Implementar modelos básicos

### **Fase 3: LLM** (Futuro)

- Adicionar Groq quando estável
- Implementar processamento de linguagem natural

## ✅ CHECKLIST

- [x] `requirements-minimal.txt` criado
- [x] `render.yaml` atualizado
- [x] Conflitos de dependências resolvidos
- [ ] Deploy no Render
- [ ] Teste dos endpoints
- [ ] Configurar webhook Twilio

## 🎯 RESULTADO ESPERADO

**Deploy deve funcionar sem conflitos de dependências!**

Aplicação básica funcionando, pronta para evolução gradual.
