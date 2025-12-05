#!/bin/bash
# Script de setup automático para AWS EC2

set -e

echo "🚀 Iniciando configuração TR4CTION Agent na AWS EC2..."
echo ""

# Verificar se está rodando como ubuntu
if [ "$USER" != "ubuntu" ]; then
    echo "❌ Execute este script como usuário ubuntu"
    exit 1
fi

# Atualizar sistema
echo "📦 Atualizando sistema..."
sudo apt update && sudo apt upgrade -y

# Instalar dependências
echo "📦 Instalando dependências..."
sudo apt install -y python3-pip python3-venv nginx git

# Clonar repositório
echo "📥 Clonando repositório..."
cd /home/ubuntu
if [ -d "FCJ_Tr4action" ]; then
    cd FCJ_Tr4action
    git pull
else
    git clone https://github.com/lucasptrolesi-ai/FCJ_Tr4action.git
    cd FCJ_Tr4action
fi

# Configurar backend
echo "⚙️  Configurando backend..."
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Criar .env se não existir
if [ ! -f ".env" ]; then
    echo "📝 Criando arquivo .env..."
    cat > .env << 'EOF'
OPENAI_API_KEY=sua-chave-aqui
OPENAI_MODEL=gpt-4o-mini
JWT_SECRET_KEY=sua-chave-jwt-super-secreta
ADMIN_USERNAME=fcj_creator
ADMIN_PASSWORD=senha-forte
ENVIRONMENT=production
ALLOWED_ORIGINS=http://localhost
EOF
    echo "⚠️  EDITE O ARQUIVO .env COM SUAS CREDENCIAIS!"
    echo "   nano /home/ubuntu/FCJ_Tr4action/backend/.env"
fi

# Criar serviço systemd
echo "🔧 Configurando serviço systemd..."
sudo tee /etc/systemd/system/tr4ction-backend.service > /dev/null << EOF
[Unit]
Description=TR4CTION Agent Backend
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/FCJ_Tr4action/backend
Environment="PATH=/home/ubuntu/FCJ_Tr4action/backend/venv/bin"
ExecStart=/home/ubuntu/FCJ_Tr4action/backend/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Ativar serviço
sudo systemctl daemon-reload
sudo systemctl enable tr4ction-backend
sudo systemctl start tr4ction-backend

# Obter IP público
PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)

# Configurar Nginx
echo "🌐 Configurando Nginx..."
sudo tee /etc/nginx/sites-available/tr4ction > /dev/null << EOF
server {
    listen 80;
    server_name $PUBLIC_IP;

    location / {
        root /home/ubuntu/FCJ_Tr4action/frontend;
        index login.html index.html;
        try_files \$uri \$uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:8000/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

sudo ln -sf /etc/nginx/sites-available/tr4ction /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx

# Configurar firewall
echo "🔒 Configurando firewall..."
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443
echo "y" | sudo ufw enable

echo ""
echo "════════════════════════════════════════"
echo "✅ Configuração concluída!"
echo "════════════════════════════════════════"
echo ""
echo "📋 Próximos passos:"
echo ""
echo "1. Edite o arquivo .env:"
echo "   nano /home/ubuntu/FCJ_Tr4action/backend/.env"
echo ""
echo "2. Reinicie o backend:"
echo "   sudo systemctl restart tr4ction-backend"
echo ""
echo "3. Acesse o sistema:"
echo "   http://$PUBLIC_IP/login.html"
echo ""
echo "4. Ver logs:"
echo "   sudo journalctl -u tr4ction-backend -f"
echo ""
echo "════════════════════════════════════════"
