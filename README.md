# TR4CTION Agent 🚀

Sistema de mentoria inteligente para a trilha TR4CTION da FCJ Venture Builder, com RAG (Retrieval-Augmented Generation) e OpenAI.

## 🎯 Funcionalidades

### Para Founders
- ✅ Chat inteligente com contexto da trilha TR4CTION
- ✅ Respostas profissionais e consultivas
- ✅ Busca semântica em documentos (RAG)
- ✅ Histórico de conversação

### Para Criadores de Conteúdo FCJ
- ✅ Upload de materiais PPTX
- ✅ Gestão da base de conhecimento
- ✅ Controle por etapas da trilha

## 🔐 Autenticação

**Founders:** Login simples (nome + startup)  
**Admin FCJ:** Credenciais protegidas

## 🛠️ Tecnologias

**Backend:**
- FastAPI
- OpenAI API (gpt-4o-mini)
- Sentence Transformers (RAG)
- JWT Authentication
- Python-PPTX

**Frontend:**
- HTML5, CSS3, JavaScript
- Design responsivo
- Interface profissional

## 📦 Instalação Local

### Backend

```bash
cd backend
pip install -r requirements.txt

# Criar arquivo .env
echo "OPENAI_API_KEY=sua_chave_aqui" > .env
echo "OPENAI_MODEL=gpt-4o-mini" >> .env

# Iniciar servidor
uvicorn main:app --reload
```

### Frontend

```bash
cd frontend
# Abrir index.html ou usar Live Server
```

## 🚀 Deploy

Veja o arquivo [DEPLOY.md](DEPLOY.md) para instruções completas de publicação.

**Recomendado:**
- Backend: Render.com (gratuito)
- Frontend: Vercel (gratuito)

## 📂 Estrutura do Projeto

```
Tr4ction_Agente/
├── backend/
│   ├── main.py              # FastAPI app
│   ├── api/
│   │   ├── agent.py         # Chat endpoint
│   │   ├── admin.py         # Gestão de conteúdo
│   │   └── auth.py          # Autenticação
│   ├── core/
│   │   ├── auth.py          # Sistema JWT
│   │   ├── config.py        # Configurações
│   │   └── rag_engine.py    # Motor RAG
│   ├── services/
│   │   └── openai_client.py # Cliente OpenAI
│   └── data/                # Base de conhecimento
├── frontend/
│   ├── index.html           # Chat (founders)
│   ├── admin.html           # Painel admin
│   ├── login.html           # Login founders
│   ├── login-admin.html     # Login admin
│   ├── css/
│   │   └── style.css
│   └── js/
│       ├── app.js           # Chat com auth
│       └── admin_auth.js    # Admin com auth
└── DEPLOY.md                # Guia de publicação
```

## 🔧 Configuração

### Variáveis de Ambiente

```env
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
JWT_SECRET_KEY=chave_segura_aqui
ADMIN_USERNAME=fcj_creator
ADMIN_PASSWORD=senha_forte
```

## 📝 Uso

### Founders
1. Acesse `/login.html`
2. Informe nome e startup
3. Faça perguntas sobre a trilha

### Criadores FCJ
1. Acesse `/login-admin.html`
2. Login com credenciais admin
3. Upload de materiais PPTX
4. Gerencie base de conhecimento

## 🤝 Contribuindo

Este é um projeto interno da FCJ Venture Builder.

## 📄 Licença

Uso interno FCJ Venture Builder - Todos os direitos reservados.

## 🆘 Suporte

Para dúvidas ou problemas, contate a equipe FCJ.

---

**Desenvolvido para FCJ Venture Builder** 🚀
