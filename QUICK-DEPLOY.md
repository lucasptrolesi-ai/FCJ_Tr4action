# TR4CTION Agent - Guia Rápido de Deploy

## ⚡ Deploy Rápido

### 1️⃣ Preparar Backend (AWS EC2 - 12 meses grátis)

**Passo 1: Criar instância EC2**
1. Acesse https://aws.amazon.com/free
2. Login no Console → EC2 → Launch Instance
3. Configurar:
   - **Name:** tr4ction-agent
   - **AMI:** Ubuntu Server 22.04 LTS
   - **Instance type:** t2.micro (Free tier)
   - **Key pair:** Criar novo (.pem)
   - **Security Group:** Allow SSH, HTTP, HTTPS

**Passo 2: Conectar e instalar**
```bash
# Conectar via SSH
ssh -i "sua-chave.pem" ubuntu@seu-ip-ec2

# Rodar script automático
curl -fsSL https://raw.githubusercontent.com/lucasptrolesi-ai/FCJ_Tr4action/main/setup-aws.sh | bash

# Editar credenciais
nano /home/ubuntu/FCJ_Tr4action/backend/.env
```

**Passo 3: Reiniciar e testar**
```bash
sudo systemctl restart tr4ction-backend
```

Acesse: `http://seu-ip-ec2/login.html`

📖 **Guia completo:** `AWS-DEPLOY.md`

---

### 2️⃣ Preparar Frontend (Vercel - Grátis)

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
$BACKEND_URL = "http://seu-ip-ec2/api"
$FRONTEND_URL = "https://tr4ction-agent.vercel.app"
```

**Executar:**
```bash
.\update-urls.ps1
```

**Atualizar ALLOWED_ORIGINS na AWS:**
```bash
# Editar .env na EC2
ssh -i "sua-chave.pem" ubuntu@seu-ip-ec2
nano /home/ubuntu/FCJ_Tr4action/backend/.env
# ALLOWED_ORIGINS=https://seu-frontend.vercel.app
sudo systemctl restart tr4ction-backend
```

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
- Verifique ALLOWED_ORIGINS no .env da EC2
- Certifique-se que frontend usa HTTPS

**401/403 Error:**
- Verifique JWT_SECRET_KEY no .env
- Limpe localStorage do navegador

**500 Error:**
- Veja logs: `sudo journalctl -u tr4ction-backend -f`
- Confirme OPENAI_API_KEY válida

**Backend não inicia:**
```bash
sudo systemctl status tr4ction-backend
sudo journalctl -u tr4ction-backend -n 50
```

## 📊 Monitoramento

**Logs Backend (AWS):**
```bash
sudo journalctl -u tr4ction-backend -f
```

**Logs Nginx:**
```bash
sudo tail -f /var/log/nginx/error.log
```

**Frontend Errors:**
```
F12 → Console
```

---

**Tempo total:** ~20-30 minutos
**Custo:** Grátis por 12 meses (AWS Free Tier)
