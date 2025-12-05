#!/bin/bash

echo "🚀 TR4CTION Agent - Script de Deploy"
echo "===================================="
echo ""

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Verificar se está no diretório correto
if [ ! -f "backend/main.py" ]; then
    echo -e "${RED}❌ Erro: Execute este script da raiz do projeto${NC}"
    exit 1
fi

echo -e "${YELLOW}📋 Checklist pré-deploy:${NC}"
echo ""

# 1. Verificar .env
if [ ! -f "backend/.env" ]; then
    echo -e "${RED}❌ Arquivo .env não encontrado${NC}"
    echo "Crie backend/.env com as variáveis necessárias"
    exit 1
else
    echo -e "${GREEN}✅ Arquivo .env encontrado${NC}"
fi

# 2. Verificar OPENAI_API_KEY
if ! grep -q "OPENAI_API_KEY=sk-" backend/.env 2>/dev/null; then
    echo -e "${YELLOW}⚠️  OPENAI_API_KEY pode estar incorreta${NC}"
else
    echo -e "${GREEN}✅ OPENAI_API_KEY configurada${NC}"
fi

# 3. Verificar dependências
echo ""
echo -e "${YELLOW}📦 Verificando dependências...${NC}"
cd backend
if pip list | grep -q "fastapi"; then
    echo -e "${GREEN}✅ Dependências Python instaladas${NC}"
else
    echo -e "${YELLOW}⚠️  Instalando dependências...${NC}"
    pip install -r requirements.txt
fi
cd ..

# 4. Git
echo ""
echo -e "${YELLOW}📝 Preparando Git...${NC}"

if [ ! -d ".git" ]; then
    echo "Inicializando repositório Git..."
    git init
    git add .
    git commit -m "Initial commit - TR4CTION Agent"
    echo -e "${GREEN}✅ Repositório Git criado${NC}"
else
    echo -e "${GREEN}✅ Repositório Git já existe${NC}"
fi

# 5. Instruções finais
echo ""
echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}✅ Projeto pronto para deploy!${NC}"
echo -e "${GREEN}================================${NC}"
echo ""
echo -e "${YELLOW}📌 Próximos passos:${NC}"
echo ""
echo "🔹 BACKEND (Render.com):"
echo "   1. Acesse https://render.com"
echo "   2. New > Web Service"
echo "   3. Conecte este repositório"
echo "   4. Build Command: pip install -r backend/requirements.txt"
echo "   5. Start Command: uvicorn backend.main:app --host 0.0.0.0 --port \$PORT"
echo "   6. Adicione variáveis de ambiente:"
echo "      - OPENAI_API_KEY"
echo "      - OPENAI_MODEL=gpt-4o-mini"
echo "      - JWT_SECRET_KEY (gere uma chave segura)"
echo "      - ADMIN_USERNAME=fcj_creator"
echo "      - ADMIN_PASSWORD=(defina senha forte)"
echo "      - ENVIRONMENT=production"
echo "      - ALLOWED_ORIGINS=https://seu-frontend.vercel.app"
echo ""
echo "🔹 FRONTEND (Vercel):"
echo "   1. Instale Vercel CLI: npm install -g vercel"
echo "   2. cd frontend"
echo "   3. vercel"
echo "   4. Após deploy, copie a URL"
echo "   5. Atualize BACKEND_URL nos arquivos JS"
echo "   6. Adicione URL no ALLOWED_ORIGINS do Render"
echo ""
echo "🔹 Documentação completa: DEPLOY.md"
echo ""
