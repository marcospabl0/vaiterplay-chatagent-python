# 🚨 Troubleshooting Render.com - Genia Quadras

## ❌ Erros Comuns e Soluções

### **1. Erro de Build**

```
Error: Failed to build
```

**Soluções:**

- ✅ Verificar se `requirements.txt` está correto
- ✅ Usar Python 3.11+ (especificado em `runtime.txt`)
- ✅ Verificar se todas as dependências estão listadas

### **2. Erro de Importação**

```
ModuleNotFoundError: No module named 'app'
```

**Soluções:**

- ✅ Verificar se todos os arquivos `__init__.py` existem
- ✅ Verificar estrutura de diretórios
- ✅ Usar importações relativas corretas

### **3. Erro de Variáveis de Ambiente**

```
KeyError: 'MONGODB_URI'
```

**Soluções:**

- ✅ Configurar todas as variáveis no dashboard do Render
- ✅ Usar valores padrão nas configurações
- ✅ Verificar se as variáveis estão marcadas como "Secret"

### **4. Erro de Porta**

```
Error: Port already in use
```

**Soluções:**

- ✅ Usar `$PORT` (variável do Render)
- ✅ Não hardcodar porta específica
- ✅ Verificar comando de start

### **5. Erro de MongoDB**

```
ConnectionError: MongoDB connection failed
```

**Soluções:**

- ✅ Verificar URI do MongoDB
- ✅ Adicionar IP do Render na whitelist do MongoDB
- ✅ Usar connection string correta

## 🔧 Configuração Manual no Render

### **Passo 1: Criar Web Service**

1. Acesse [Render Dashboard](https://dashboard.render.com)
2. Clique em "New +" → "Web Service"
3. Conecte seu repositório GitHub

### **Passo 2: Configurações Básicas**

- **Name**: `genia-quadras`
- **Environment**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### **Passo 3: Variáveis de Ambiente**

Configure no dashboard do Render:

```env
MONGODB_URI=mongodb+srv://genia-mongodb-dev1:0MZ1z0W1mmSpG1RI@genia-cluster1.hky0vg2.mongodb.net/?retryWrites=true&w=majority&appName=GenIA-Cluster1
MONGODB_DB=vaiterplay
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886
GROQ_API_KEY=gsk_your_api_key_here
GROQ_MODEL=llama-3.1-8b-instant
USE_LLM=true
DEBUG=false
LOG_LEVEL=INFO
```

### **Passo 4: Deploy**

1. Clique em "Create Web Service"
2. Aguarde o build (2-3 minutos)
3. Verifique os logs se houver erro

## 🐛 Debugging

### **Verificar Logs**

1. Acesse o dashboard do Render
2. Vá para a aba "Logs"
3. Procure por erros específicos

### **Testar Localmente**

```bash
# Instalar dependências
pip install -r requirements.txt

# Executar localmente
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Testar endpoints
curl http://localhost:8000/health
```

### **Verificar Estrutura**

```bash
# Verificar se todos os arquivos estão presentes
ls -la app/
ls -la app/models/
ls -la app/repositories/
ls -la app/services/
ls -la app/utils/
```

## 📞 Suporte

Se ainda houver problemas:

1. Verifique os logs detalhados no Render
2. Teste localmente primeiro
3. Verifique se todas as variáveis estão configuradas
4. Consulte a documentação do Render

## ✅ Checklist de Deploy

- [ ] Repositório conectado ao Render
- [ ] Build Command configurado
- [ ] Start Command configurado
- [ ] Todas as variáveis de ambiente configuradas
- [ ] MongoDB URI correto
- [ ] Twilio credenciais configuradas
- [ ] Groq API key configurada (se usando LLM)
- [ ] Logs sem erros
- [ ] Health check funcionando
