# Script rápido para atualizar URLs após deploy

# Substitua estas URLs pelas suas URLs de produção
$BACKEND_URL = "https://seu-backend.onrender.com"
$FRONTEND_URL = "https://seu-frontend.vercel.app"

Write-Host "🔄 Atualizando URLs para produção..." -ForegroundColor Cyan
Write-Host ""

# Arquivos para atualizar
$files = @(
    "frontend\js\app.js",
    "frontend\js\admin_auth.js",
    "frontend\login.html",
    "frontend\login-admin.html"
)

foreach ($file in $files) {
    if (Test-Path $file) {
        Write-Host "Atualizando $file..." -ForegroundColor Yellow
        
        # Ler conteúdo
        $content = Get-Content $file -Raw
        
        # Substituir URL
        $content = $content -replace 'http://127\.0\.0\.1:8000', $BACKEND_URL
        $content = $content -replace 'http://localhost:8000', $BACKEND_URL
        
        # Salvar
        Set-Content $file -Value $content
        
        Write-Host "✅ $file atualizado" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "✨ URLs atualizadas para:" -ForegroundColor Green
Write-Host "   Backend: $BACKEND_URL"
Write-Host "   Frontend: $FRONTEND_URL"
Write-Host ""
Write-Host "⚠️  Lembre-se de:" -ForegroundColor Yellow
Write-Host "   1. Adicionar $FRONTEND_URL em ALLOWED_ORIGINS no Render"
Write-Host "   2. Fazer commit e push das alterações"
Write-Host "   3. Redesployer o frontend"
