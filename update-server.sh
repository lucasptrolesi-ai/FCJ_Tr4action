# 🚀 SCRIPT DE ATUALIZAÇÃO - TR4CTION AGENT
# Execute no servidor AWS EC2 após fazer push das alterações

echo "=================================================="
echo "🔄 Atualizando TR4CTION Agent no Servidor"
echo "=================================================="

# Navegar para o diretório do projeto
cd /home/ubuntu/FCJ_Tr4action || exit

# Backup do .env atual
echo "📋 Fazendo backup do .env..."
cp backend/.env backend/.env.backup

# Puxar últimas alterações do Git
echo "📥 Puxando alterações do GitHub..."
git pull origin main

# Ativar ambiente virtual
echo "🐍 Ativando ambiente virtual..."
source backend/.venv/bin/activate

# Instalar novas dependências
echo "📦 Instalando novas dependências..."
pip install -r backend/requirements.txt

# Atualizar variáveis de ambiente
echo "⚙️  Verificando configurações do .env..."
if ! grep -q "JWT_SECRET_KEY" backend/.env || grep -q "tr4ction-secret-key-change-in-production" backend/.env; then
    echo "⚠️  ATENÇÃO: JWT_SECRET_KEY precisa ser atualizada!"
    echo "Execute: python3 -c 'import secrets; print(secrets.token_hex(32))'"
    echo "E adicione ao arquivo backend/.env"
fi

if ! grep -q "ALLOWED_ORIGINS" backend/.env; then
    echo "⚠️  ATENÇÃO: ALLOWED_ORIGINS não configurada!"
    echo "Adicione ao backend/.env:"
    echo "ALLOWED_ORIGINS=https://fcj-tr4action-b44i-obqzrkf34-lpwebedatas-projects.vercel.app"
fi

# Reiniciar o serviço
echo "🔄 Reiniciando serviço..."
sudo systemctl restart tr4ction-backend

# Verificar status
echo "✅ Verificando status do serviço..."
sudo systemctl status tr4ction-backend --no-pager

echo "=================================================="
echo "✅ Atualização concluída!"
echo "=================================================="
echo ""
echo "📝 Próximos passos manuais:"
echo "1. Verifique o arquivo backend/.env"
echo "2. Atualize JWT_SECRET_KEY se necessário"
echo "3. Configure ALLOWED_ORIGINS corretamente"
echo "4. Execute: sudo systemctl restart tr4ction-backend"
echo ""
