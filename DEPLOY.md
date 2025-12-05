# TR4CTION Agent - Deployment Guide

## 🚀 Guia de Publicação

### Pré-requisitos
- Python 3.10+
- Conta Render.com (recomendado para backend)
- Conta Vercel/Netlify (recomendado para frontend)

---

## 📦 Backend (FastAPI)

### Opção 1: Render.com (Recomendado - Gratuito)

1. **Criar conta em [render.com](https://render.com)**

2. **Criar novo Web Service:**
   - Repository: Conecte seu GitHub
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

3. **Configurar variáveis de ambiente:**
   ```
   OPENAI_API_KEY=sua_chave_aqui
   OPENAI_MODEL=gpt-4o-mini
   JWT_SECRET_KEY=gere_uma_chave_segura_aqui
   ADMIN_USERNAME=fcj_creator
   ADMIN_PASSWORD=fcj2025@tr4ction
   ```

4. **Deploy automático após cada commit**

### Opção 2: Railway.app

1. **Criar projeto em [railway.app](https://railway.app)**
2. **Adicionar variáveis de ambiente**
3. **Deploy automático**

### Opção 3: Heroku

```bash
heroku create tr4ction-agent-backend
heroku config:set OPENAI_API_KEY=sua_chave
heroku config:set OPENAI_MODEL=gpt-4o-mini
git push heroku main
```

---

## 🌐 Frontend (HTML/JS)

### Opção 1: Vercel (Recomendado)

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
   - Substitua `http://127.0.0.1:8000` pela URL do Render

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

Atualize `main.py` com a URL do frontend em produção:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://seu-dominio.vercel.app",
        "http://localhost:5500"  # apenas desenvolvimento
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
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
const BACKEND_URL = "https://seu-backend.onrender.com";
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

- **Logs Render:** Dashboard > Logs
- **Erros Frontend:** Console do navegador
- **Performance:** Render fornece métricas

---

## 🆘 Troubleshooting

### Erro CORS
- Verifique `allow_origins` no `main.py`
- Certifique-se que frontend usa HTTPS

### Erro 401/403
- Verifique se JWT_SECRET_KEY está configurado
- Token expira em 24h

### Erro 500
- Verifique logs do Render
- Confirme OPENAI_API_KEY válida

---

## 📝 Checklist de Deploy

- [ ] Backend deployado no Render
- [ ] Variáveis de ambiente configuradas
- [ ] Frontend deployado no Vercel
- [ ] URLs atualizadas no frontend
- [ ] CORS configurado corretamente
- [ ] Credenciais de produção definidas
- [ ] Testes de login (admin e founder)
- [ ] Teste de chat funcional
- [ ] Upload de PPTX testado
