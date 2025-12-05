# TR4CTION Agent - Guia Rápido de Deploy

## ⚡ Deploy Rápido (5 minutos)

### 1️⃣ Preparar Backend (Render.com)

```bash
# Execute o script de preparação
.\deploy.ps1
```

**Render.com:**
1. Criar conta em https://render.com
2. New → Web Service
3. Conectar GitHub repo
4. Configurar:
   - **Name:** tr4ction-agent-backend
   - **Root Directory:** `backend`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Instance Type:** Free

5. **Environment Variables:**
   ```
   OPENAI_API_KEY=sk-proj-...
   OPENAI_MODEL=gpt-4o-mini
   JWT_SECRET_KEY=gere-chave-segura
   ADMIN_USERNAME=fcj_creator
   ADMIN_PASSWORD=senha-forte
   ENVIRONMENT=production
   ALLOWED_ORIGINS=https://seu-frontend.vercel.app
   ```

6. Deploy → Copiar URL (ex: `https://tr4ction-agent.onrender.com`)

### 2️⃣ Preparar Frontend (Vercel)

```bash
# Instalar Vercel CLI
npm install -g vercel

# Deploy
cd frontend
vercel
```

**Seguir prompts:**
- Set up and deploy? **Y**
- Which scope? (sua conta)
- Link to existing project? **N**
- Project name? **tr4ction-agent**
- Directory? **./** (enter)
- Override settings? **N**

Copiar URL de produção (ex: `https://tr4ction-agent.vercel.app`)

### 3️⃣ Conectar Backend e Frontend

**Editar `update-urls.ps1`:**
```powershell
$BACKEND_URL = "https://tr4ction-agent.onrender.com"
$FRONTEND_URL = "https://tr4ction-agent.vercel.app"
```

**Executar:**
```bash
.\update-urls.ps1
```

**Atualizar ALLOWED_ORIGINS no Render:**
- Ir no dashboard do Render
- Environment → Edit
- ALLOWED_ORIGINS = URL do Vercel

### 4️⃣ Redesployer

```bash
# Commit alterações
git add .
git commit -m "Update production URLs"
git push

# Redesploy frontend
cd frontend
vercel --prod
```

## ✅ Teste

1. Acesse `https://seu-frontend.vercel.app/login.html`
2. Faça login como founder
3. Teste o chat
4. Acesse `/login-admin.html` com credenciais admin
5. Teste upload de PPTX

## 🆘 Problemas Comuns

**CORS Error:**
- Verifique ALLOWED_ORIGINS no Render
- Certifique-se que frontend usa HTTPS

**401/403 Error:**
- Verifique JWT_SECRET_KEY
- Limpe localStorage do navegador

**500 Error:**
- Veja logs no Render Dashboard
- Confirme OPENAI_API_KEY válida

## 📊 Monitoramento

**Render Logs:**
```
Dashboard → Logs → Real-time
```

**Frontend Errors:**
```
F12 → Console
```

---

**Tempo total:** ~5-10 minutos ⚡
