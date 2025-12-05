# TR4CTION Agent - Deployment Guide

## 🚀 Guia de Publicação

### Pré-requisitos
- Python 3.10+
- Conta Render.com (recomendado para backend)
- Conta Vercel/Netlify (recomendado para frontend)

---

## 📦 Backend (FastAPI)

### Opção 1: AWS EC2 Free Tier (Recomendado)

**Vantagens:**
- 12 meses completamente grátis
- Controle total do servidor
- Profissional e escalável

**Guia completo:** Veja `AWS-DEPLOY.md`

**Quick Start:**
```bash
# 1. Criar EC2 (t2.micro, Ubuntu 22.04)
# 2. Conectar via SSH
ssh -i "sua-chave.pem" ubuntu@seu-ip-ec2

# 3. Rodar script automático
curl -fsSL https://raw.githubusercontent.com/lucasptrolesi-ai/FCJ_Tr4action/main/setup-aws.sh | bash

# 4. Configurar .env
nano /home/ubuntu/FCJ_Tr4action/backend/.env
```

### Opção 2: Railway.app

1. **Criar projeto em [railway.app](https://railway.app)**
2. **Adicionar variáveis de ambiente**
3. **Deploy automático**

### Opção 3: Vercel (Backend + Frontend)

```bash
# Deploy tudo junto
vercel
```

---

## 🌐 Frontend (HTML/JS)

### Opção 1: Vercel

1. **Instalar Vercel CLI:**
   ```bash
   npm install -g vercel
   ```

2. **Deploy:**
   ```bash
   cd frontend
   vercel
   ```

3. **Atualizar BACKEND_URL:**
   - Edite `js/app.js` e `js/admin_auth.js`
   - Substitua `http://127.0.0.1:8000` pela URL da sua AWS EC2

### Opção 2: Netlify

1. **Arraste a pasta `frontend` para [app.netlify.com](https://app.netlify.com)**
2. **Configure redirects** (criar arquivo `frontend/_redirects`):
   ```
   /*    /index.html   200
   ```

### Opção 3: GitHub Pages

```bash
cd frontend
git init
git add .
git commit -m "Deploy frontend"
git branch -M gh-pages
git remote add origin seu-repositorio
git push -u origin gh-pages
```

---

## ⚙️ Configurações Importantes

### CORS no Backend

Atualize o `.env` na AWS EC2:

```bash
ssh -i "sua-chave.pem" ubuntu@seu-ip-ec2
nano /home/ubuntu/FCJ_Tr4action/backend/.env

# Adicione:
ALLOWED_ORIGINS=https://seu-dominio.vercel.app,http://localhost:5500

# Reinicie:
sudo systemctl restart tr4ction-backend
```

### Atualizar URLs no Frontend

Nos arquivos:
- `frontend/js/app.js`
- `frontend/js/admin_auth.js`
- `frontend/login.html`
- `frontend/login-admin.html`

Substitua:
```javascript
const BACKEND_URL = "http://127.0.0.1:8000";
```

Por:
```javascript
const BACKEND_URL = "http://seu-ip-ec2/api";
// ou com domínio:
const BACKEND_URL = "https://api.seu-dominio.com";
```

---

## 🔐 Segurança em Produção

1. **Gerar chave JWT segura:**
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

2. **Alterar credenciais admin:**
   - Não usar credenciais padrão em produção
   - Definir via variáveis de ambiente

3. **HTTPS obrigatório:**
   - Render e Vercel já fornecem SSL
   - Nunca usar HTTP em produção

---

## 📊 Monitoramento

- **Logs AWS:** `sudo journalctl -u tr4ction-backend -f`
- **Erros Frontend:** Console do navegador (F12)
- **Performance:** AWS CloudWatch (gratuito)

---

## 🆘 Troubleshooting

### Erro CORS
- Verifique `ALLOWED_ORIGINS` no `.env` da EC2
- Certifique-se que frontend usa HTTPS

### Erro 401/403
- Verifique se JWT_SECRET_KEY está no `.env`
- Token expira em 24h
- Limpe localStorage do navegador

### Erro 500
- Logs: `sudo journalctl -u tr4ction-backend -n 50`
- Confirme OPENAI_API_KEY válida no `.env`

---

## 📝 Checklist de Deploy

- [ ] EC2 criada e configurada
- [ ] Backend rodando como serviço systemd
- [ ] Nginx configurado corretamente
- [ ] Arquivo .env com credenciais
- [ ] Frontend deployado no Vercel
- [ ] URLs atualizadas no frontend
- [ ] CORS configurado (ALLOWED_ORIGINS)
- [ ] Testes de login (admin e founder)
- [ ] Teste de chat funcional
- [ ] Upload de PPTX testado
- [ ] Firewall configurado (UFW/Security Group)
