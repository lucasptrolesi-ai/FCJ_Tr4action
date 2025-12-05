# TR4CTION Agent - Script de Deploy (Windows)

Write-Host "🚀 TR4CTION Agent - Script de Deploy" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""

# Verificar diretório
if (-not (Test-Path "backend\main.py")) {
    Write-Host "❌ Erro: Execute este script da raiz do projeto" -ForegroundColor Red
    exit 1
}

Write-Host "📋 Checklist pré-deploy:" -ForegroundColor Yellow
Write-Host ""

# 1. Verificar .env
if (-not (Test-Path "backend\.env")) {
    Write-Host "❌ Arquivo .env não encontrado" -ForegroundColor Red
    Write-Host "Crie backend\.env com as variáveis necessárias"
    exit 1
} else {
    Write-Host "✅ Arquivo .env encontrado" -ForegroundColor Green
}

# 2. Verificar OPENAI_API_KEY
$envContent = Get-Content "backend\.env" -Raw
if ($envContent -match "OPENAI_API_KEY=sk-") {
    Write-Host "✅ OPENAI_API_KEY configurada" -ForegroundColor Green
} else {
    Write-Host "⚠️  OPENAI_API_KEY pode estar incorreta" -ForegroundColor Yellow
}

# 3. Verificar dependências
Write-Host ""
Write-Host "📦 Verificando dependências..." -ForegroundColor Yellow

try {
    pip list | Select-String "fastapi" | Out-Null
    Write-Host "✅ Dependências Python instaladas" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Instalando dependências..." -ForegroundColor Yellow
    Set-Location backend
    pip install -r requirements.txt
    Set-Location ..
}

# 4. Git
Write-Host ""
Write-Host "📝 Preparando Git..." -ForegroundColor Yellow

if (-not (Test-Path ".git")) {
    Write-Host "Inicializando repositório Git..."
    git init
    git add .
    git commit -m "Initial commit - TR4CTION Agent"
    Write-Host "✅ Repositório Git criado" -ForegroundColor Green
} else {
    Write-Host "✅ Repositório Git já existe" -ForegroundColor Green
}

# 5. Instruções finais
Write-Host ""
Write-Host "================================" -ForegroundColor Green
Write-Host "✅ Projeto pronto para deploy!" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Green
Write-Host ""
Write-Host "📌 Próximos passos:" -ForegroundColor Yellow
Write-Host ""
Write-Host "🔹 BACKEND (Render.com):" -ForegroundColor Cyan
Write-Host "   1. Acesse https://render.com"
Write-Host "   2. New > Web Service"
Write-Host "   3. Conecte este repositório"
Write-Host "   4. Root Directory: backend"
Write-Host "   5. Build Command: pip install -r requirements.txt"
Write-Host "   6. Start Command: uvicorn main:app --host 0.0.0.0 --port `$PORT"
Write-Host "   7. Adicione variáveis de ambiente:"
Write-Host "      - OPENAI_API_KEY"
Write-Host "      - OPENAI_MODEL=gpt-4o-mini"
Write-Host "      - JWT_SECRET_KEY (gere uma chave segura)"
Write-Host "      - ADMIN_USERNAME=fcj_creator"
Write-Host "      - ADMIN_PASSWORD=(defina senha forte)"
Write-Host "      - ENVIRONMENT=production"
Write-Host "      - ALLOWED_ORIGINS=https://seu-frontend.vercel.app"
Write-Host ""
Write-Host "🔹 FRONTEND (Vercel):" -ForegroundColor Cyan
Write-Host "   1. Instale Vercel CLI: npm install -g vercel"
Write-Host "   2. cd frontend"
Write-Host "   3. vercel"
Write-Host "   4. Após deploy, copie a URL"
Write-Host "   5. Atualize BACKEND_URL nos arquivos JS"
Write-Host "   6. Adicione URL no ALLOWED_ORIGINS do Render"
Write-Host ""
Write-Host "🔹 Documentação completa: DEPLOY.md" -ForegroundColor Cyan
Write-Host ""

# Perguntar se quer criar repositório no GitHub
Write-Host "Deseja criar repositório no GitHub agora? (S/N)" -ForegroundColor Yellow
$response = Read-Host

if ($response -eq "S" -or $response -eq "s") {
    Write-Host ""
    Write-Host "Para criar repositório no GitHub:" -ForegroundColor Cyan
    Write-Host "1. Acesse https://github.com/new"
    Write-Host "2. Nome: tr4ction-agent"
    Write-Host "3. Privado: Sim"
    Write-Host "4. Não inicialize com README"
    Write-Host ""
    Write-Host "Depois execute:" -ForegroundColor Yellow
    Write-Host "  git remote add origin https://github.com/seu-usuario/tr4ction-agent.git"
    Write-Host "  git branch -M main"
    Write-Host "  git push -u origin main"
}

Write-Host ""
Write-Host "✨ Script finalizado!" -ForegroundColor Green
