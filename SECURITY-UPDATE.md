# 🔒 GUIA DE ATUALIZAÇÃO DE SEGURANÇA - TR4CTION AGENT

## ✅ Melhorias Implementadas

### 🛡️ Segurança
- ✅ **CORS Configurável**: Agora usa `ALLOWED_ORIGINS` do arquivo `.env`
- ✅ **JWT Secret Obrigatório**: Removidos valores padrão inseguros
- ✅ **Credenciais Protegidas**: Admin username/password obrigatórios no `.env`
- ✅ **Rate Limiting**: 20 requisições por minuto por IP no endpoint `/agent/ask`
- ✅ **Logging Estruturado**: Todas as operações críticas agora são logadas

### 🧹 Código
- ✅ **Exception Handling**: Tratamento específico de erros OpenAI
- ✅ **Console.logs Protegidos**: Não expõe informações em produção
- ✅ **Código Limpo**: Removidos arquivos `.bak` e endpoints não implementados

---

## 🚀 PASSOS PARA ATUALIZAR O SERVIDOR AWS

### 1️⃣ **Conectar ao Servidor**
```powershell
ssh -i "C:\Users\Micro\Downloads\tr4ction-key.pem" ubuntu@3.235.65.249
```

### 2️⃣ **Gerar Nova JWT Secret**
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```
**Copie o resultado** (64 caracteres)

### 3️⃣ **Atualizar Arquivo .env**
```bash
cd /home/ubuntu/FCJ_Tr4action/backend
nano .env
```

Adicione/atualize as seguintes linhas:
```env
# JWT Secret (cole a chave gerada no passo 2)
JWT_SECRET_KEY=COLE_AQUI_A_CHAVE_GERADA_64_CARACTERES

# CORS - Adicione o domínio Vercel
ALLOWED_ORIGINS=https://fcj-tr4action-b44i-obqzrkf34-lpwebedatas-projects.vercel.app,http://localhost:5500

# Credenciais Admin (opcional: altere a senha)
ADMIN_USERNAME=fcj_creator
ADMIN_PASSWORD=FCJ@Tr4ction2025!SecurePassword
```

**Salvar**: `Ctrl+O` → `Enter` → `Ctrl+X`

### 4️⃣ **Executar Script de Atualização**
```bash
cd /home/ubuntu/FCJ_Tr4action
chmod +x update-server.sh
./update-server.sh
```

### 5️⃣ **Verificar Logs**
```bash
sudo journalctl -u tr4ction-backend -f
```

**Procure por**:
- ✅ `CORS configurado para origens: ['https://fcj-tr4action-...']`
- ✅ `INFO: Application startup complete`
- ❌ Erros de `JWT_SECRET_KEY` ou `ADMIN_PASSWORD`

---

## ⚠️ IMPORTANTE: O QUE MUDOU

### ❌ **O que NÃO funciona mais:**
1. **Backend sem `.env`**: Aplicação não iniciará
2. **CORS aberto (`*`)**: Removido por segurança
3. **Credenciais padrão**: Não há mais valores fallback

### ✅ **O que agora é OBRIGATÓRIO:**
1. Arquivo `.env` com:
   - `JWT_SECRET_KEY` (64 caracteres)
   - `ADMIN_USERNAME` e `ADMIN_PASSWORD`
   - `ALLOWED_ORIGINS` (domínios permitidos)
2. Domínio Vercel adicionado ao CORS

---

## 🧪 TESTAR APÓS ATUALIZAÇÃO

### 1. **Testar Autenticação**
```bash
curl -X POST http://3.235.65.249/api/auth/admin/login \
  -H "Content-Type: application/json" \
  -d '{"username":"fcj_creator","password":"FCJ@Tr4ction2025!SecurePassword"}'
```
**Esperado**: `{"access_token":"...","role":"admin"}`

### 2. **Testar CORS**
Acesse: https://fcj-tr4action-b44i-obqzrkf34-lpwebedatas-projects.vercel.app

- Faça login como founder
- Envie uma pergunta no chat
- **Esperado**: Resposta normal do agente

### 3. **Testar Rate Limit**
Execute 25 requisições seguidas ao `/agent/ask`
**Esperado**: Erro 429 (Too Many Requests) após a 20ª

---

## 🔧 TROUBLESHOOTING

### ❌ Erro: "JWT_SECRET_KEY não configurada"
**Solução**: Adicione `JWT_SECRET_KEY` ao `.env` (veja passo 2 e 3)

### ❌ Erro: "CORS policy blocked"
**Solução**: Verifique se `ALLOWED_ORIGINS` contém a URL Vercel exata:
```bash
grep ALLOWED_ORIGINS /home/ubuntu/FCJ_Tr4action/backend/.env
```

### ❌ Erro: "Credenciais inválidas" (admin)
**Solução**: Verifique username/password no `.env`:
```bash
grep -E "ADMIN_USERNAME|ADMIN_PASSWORD" /home/ubuntu/FCJ_Tr4action/backend/.env
```

### ❌ Backend não inicia
**Ver logs completos**:
```bash
sudo journalctl -u tr4ction-backend -n 100 --no-pager
```

---

## 📊 ARQUIVOS ALTERADOS

**Backend:**
- `main.py` - CORS + rate limiting + logging
- `core/auth.py` - Validação obrigatória de credenciais
- `services/openai_client.py` - Exception handling melhorado
- `api/agent.py` - Rate limit + logging
- `api/admin.py` - Logging de operações
- `api/auth.py` - Logging de tentativas de login
- `requirements.txt` - Adicionado `slowapi==0.1.9`

**Frontend:**
- `js/app.js` - Removido endpoint templates, console.logs protegidos
- `js/admin.js` - Console.logs protegidos
- `js/admin_auth.js` - Console.logs protegidos

**Infraestrutura:**
- `.gitignore` - Adicionado `*.bak`, `logs.txt`
- `.env.example` - Documentação completa
- `update-server.sh` - Script de deploy automático

---

## 📞 SUPORTE

Se encontrar problemas após a atualização:

1. **Revisar logs**: `sudo journalctl -u tr4ction-backend -f`
2. **Verificar .env**: Todas as variáveis obrigatórias preenchidas?
3. **Testar local**: Execute `uvicorn main:app --reload` no backend local

**Commit:** d011b43  
**Data:** 5 de dezembro de 2025
