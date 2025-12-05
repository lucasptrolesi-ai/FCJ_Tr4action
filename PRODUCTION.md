# 🎯 Otimizações para Produção

## 🔒 Segurança

### 1. Gerar JWT Secret Seguro
```python
python -c "import secrets; print(secrets.token_urlsafe(32))"
```
Use essa chave no `JWT_SECRET_KEY`

### 2. Credenciais Fortes
```env
ADMIN_USERNAME=admin_fcj_$(date +%s)
ADMIN_PASSWORD=Use_senha_com_16+_caracteres_!@#$
```

### 3. HTTPS Obrigatório
```python
# backend/main.py - adicionar:
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

if os.getenv("ENVIRONMENT") == "production":
    app.add_middleware(HTTPSRedirectMiddleware)
```

### 4. Rate Limiting
```bash
pip install slowapi

# backend/main.py
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@limiter.limit("10/minute")
@router.post("/agent/ask")
async def ask_agent(...):
    ...
```

## ⚡ Performance

### 1. Caching de Embeddings
```python
# core/rag_engine.py
from functools import lru_cache

@lru_cache(maxsize=128)
def get_embedding(text: str):
    return self.model.encode([text])[0]
```

### 2. Compressão Frontend
```bash
# Instalar minificador
npm install -g minify

# Minificar CSS/JS
minify frontend/css/style.css > frontend/css/style.min.css
minify frontend/js/app.js > frontend/js/app.min.js
```

### 3. CDN para Assets
Usar CDN para bibliotecas (já está implementado para favicon)

### 4. Lazy Loading
```html
<!-- index.html -->
<script src="js/app.js" defer></script>
```

## 📊 Monitoramento

### 1. Logging Estruturado
```python
# backend/main.py
import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = datetime.now()
    response = await call_next(request)
    duration = (datetime.now() - start).total_seconds()
    
    logging.info(f"{request.method} {request.url.path} - {response.status_code} - {duration}s")
    return response
```

### 2. Error Tracking (Sentry)
```bash
pip install sentry-sdk[fastapi]

# backend/main.py
import sentry_sdk

sentry_sdk.init(
    dsn="seu-sentry-dsn",
    environment="production"
)
```

### 3. Analytics Frontend
```html
<!-- index.html -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXX"></script>
```

## 💾 Banco de Dados (Upgrade Futuro)

### Para escalar além de arquivos JSON:

```python
# Opção 1: PostgreSQL (Render)
pip install psycopg2-binary sqlalchemy

# Opção 2: MongoDB (MongoDB Atlas)
pip install motor pymongo

# Opção 3: Supabase
pip install supabase
```

## 🔄 CI/CD

### GitHub Actions
```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Deploy Backend
        run: |
          # Render auto-deploys on push
          
      - name: Deploy Frontend
        run: |
          cd frontend
          npm install -g vercel
          vercel --prod --token=${{ secrets.VERCEL_TOKEN }}
```

## 📈 Métricas

### Adicionar Health Check
```python
# backend/main.py
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }
```

### Monitorar OpenAI Usage
```python
# Adicionar tracking de tokens
import tiktoken

def count_tokens(text: str, model: str = "gpt-4"):
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))
```

## 🌐 Domínio Customizado

### Render
```
Settings > Custom Domain > Add Domain
```

### Vercel
```bash
vercel domains add seu-dominio.com
```

### SSL
Ambos provêm SSL automaticamente via Let's Encrypt

## 🔧 Variáveis de Ambiente

### Render (adicionar)
```env
# Limites
MAX_TOKENS=1000
MAX_HISTORY_LENGTH=10
REQUEST_TIMEOUT=30

# Features
ENABLE_ANALYTICS=true
ENABLE_RATE_LIMITING=true
```

## ✅ Checklist Pré-Produção

- [ ] JWT_SECRET_KEY gerado com secrets
- [ ] Credenciais admin alteradas
- [ ] CORS configurado com URLs exatas
- [ ] HTTPS ativo
- [ ] Rate limiting implementado
- [ ] Logs configurados
- [ ] Health check funcionando
- [ ] Backup da base de conhecimento
- [ ] Testes end-to-end realizados
- [ ] Documentação atualizada
- [ ] Monitoring configurado

## 🆘 Rollback Plan

### Se algo der errado:

**Render:**
1. Dashboard > Deploy > Rollback to Previous

**Vercel:**
```bash
vercel rollback
```

**Git:**
```bash
git revert HEAD
git push
```

---

**Lembre-se:** Sempre teste em staging antes de produção! 🚀
