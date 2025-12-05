# Deploy TR4CTION Agent - AWS EC2 Free Tier

## 🚀 Guia Completo AWS EC2

### Passo 1: Criar Conta AWS
1. Acesse https://aws.amazon.com/free
2. Criar conta (cartão necessário, mas não será cobrado no free tier)
3. 12 meses gratuitos de EC2 t2.micro

### Passo 2: Criar Instância EC2

1. **Acessar Console EC2:**
   - Login no AWS Console
   - Services → EC2 → Launch Instance

2. **Configurar Instância:**
   ```
   Nome: tr4ction-agent
   AMI: Ubuntu Server 22.04 LTS (Free tier eligible)
   Instance type: t2.micro (Free tier eligible)
   Key pair: Criar novo (download .pem)
   Network: Allow SSH, HTTP, HTTPS from 0.0.0.0/0
   Storage: 8 GB (Free tier)
   ```

3. **Launch Instance**

### Passo 3: Conectar à Instância

#### Windows (PowerShell):
```powershell
# Converter .pem para uso no Windows
# Baixe o arquivo .pem e salve como tr4ction-key.pem

# Ajustar permissões
icacls "tr4ction-key.pem" /inheritance:r
icacls "tr4ction-key.pem" /grant:r "$($env:USERNAME):(R)"

# Conectar via SSH
ssh -i "tr4ction-key.pem" ubuntu@seu-ip-publico-ec2
```

### Passo 4: Configurar Servidor

```bash
# Atualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Python e dependências
sudo apt install python3-pip python3-venv nginx git -y

# Clonar repositório
cd /home/ubuntu
git clone https://github.com/lucasptrolesi-ai/FCJ_Tr4action.git
cd FCJ_Tr4action

# Configurar backend
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Criar arquivo .env
nano .env
```

**Conteúdo do .env:**
```env
OPENAI_API_KEY=sk-proj-sua-chave
OPENAI_MODEL=gpt-4o-mini
JWT_SECRET_KEY=sua-chave-jwt-super-secreta
ADMIN_USERNAME=fcj_creator
ADMIN_PASSWORD=senha-forte
ENVIRONMENT=production
ALLOWED_ORIGINS=http://seu-ip-ec2,https://seu-dominio.com
```

### Passo 5: Configurar Systemd (Backend sempre ativo)

```bash
sudo nano /etc/systemd/system/tr4ction-backend.service
```

**Conteúdo:**
```ini
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
```

**Ativar serviço:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable tr4ction-backend
sudo systemctl start tr4ction-backend
sudo systemctl status tr4ction-backend
```

### Passo 6: Configurar Nginx (Frontend + Proxy)

```bash
sudo nano /etc/nginx/sites-available/tr4ction
```

**Conteúdo:**
```nginx
server {
    listen 80;
    server_name seu-ip-ec2;

    # Frontend
    location / {
        root /home/ubuntu/FCJ_Tr4action/frontend;
        index login.html index.html;
        try_files $uri $uri/ /index.html;
    }

    # Backend API
    location /api/ {
        proxy_pass http://127.0.0.1:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket support
    location /ws {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

**Ativar configuração:**
```bash
sudo ln -s /etc/nginx/sites-available/tr4ction /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Passo 7: Atualizar URLs no Frontend

```bash
cd /home/ubuntu/FCJ_Tr4action/frontend

# Editar arquivos JS
sudo nano js/app.js
# Alterar: const BACKEND_URL = "http://seu-ip-ec2/api";

sudo nano js/admin_auth.js
# Alterar: const BACKEND_URL = "http://seu-ip-ec2/api";

sudo nano login.html
# Alterar: const BACKEND_URL = "http://seu-ip-ec2/api";

sudo nano login-admin.html
# Alterar: const BACKEND_URL = "http://seu-ip-ec2/api";
```

### Passo 8: Configurar Firewall EC2

**Security Group Rules:**
```
Type        Protocol    Port    Source
SSH         TCP         22      0.0.0.0/0
HTTP        TCP         80      0.0.0.0/0
HTTPS       TCP         443     0.0.0.0/0
Custom      TCP         8000    127.0.0.1/32 (apenas local)
```

### Passo 9: (Opcional) Configurar HTTPS com Let's Encrypt

```bash
# Instalar Certbot
sudo apt install certbot python3-certbot-nginx -y

# Obter certificado (requer domínio)
sudo certbot --nginx -d seu-dominio.com

# Auto-renovação
sudo systemctl enable certbot.timer
```

### Passo 10: Testar

1. Acesse `http://seu-ip-ec2/login.html`
2. Teste login founder
3. Teste chat
4. Acesse `/login-admin.html`
5. Teste upload de PPTX

---

## 🔧 Comandos Úteis

**Ver logs do backend:**
```bash
sudo journalctl -u tr4ction-backend -f
```

**Reiniciar backend:**
```bash
sudo systemctl restart tr4ction-backend
```

**Reiniciar Nginx:**
```bash
sudo systemctl restart nginx
```

**Atualizar código:**
```bash
cd /home/ubuntu/FCJ_Tr4action
git pull
sudo systemctl restart tr4ction-backend
```

**Ver uso de recursos:**
```bash
htop
df -h
free -h
```

---

## 💰 Custos (Free Tier)

**Incluído grátis por 12 meses:**
- 750 horas/mês de EC2 t2.micro
- 30 GB de storage EBS
- 15 GB de bandwidth de saída

**Após 12 meses:**
- ~$8-10/mês (t2.micro)
- Considerar migrar para Railway/Vercel

---

## 🔐 Segurança Adicional

```bash
# Configurar firewall UFW
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable

# Desabilitar login root
sudo nano /etc/ssh/sshd_config
# PermitRootLogin no
sudo systemctl restart ssh

# Instalar fail2ban
sudo apt install fail2ban -y
sudo systemctl enable fail2ban
```

---

## 📊 Monitoramento

**CloudWatch (AWS):**
- Métricas de CPU, RAM, Network
- Alarmes gratuitos
- Logs centralizados

**Alternativa - Instalar Netdata:**
```bash
bash <(curl -Ss https://get.netdata.cloud/kickstart.sh)
# Acesse: http://seu-ip-ec2:19999
```

---

## 🆘 Troubleshooting

**Backend não inicia:**
```bash
sudo journalctl -u tr4ction-backend -n 50
```

**Nginx erro 502:**
```bash
sudo tail -f /var/log/nginx/error.log
curl http://127.0.0.1:8000
```

**Sem conexão:**
- Verificar Security Group no AWS Console
- Verificar firewall UFW

---

## 📝 Script de Deploy Automático

Salve como `deploy-aws.sh`:
```bash
#!/bin/bash
cd /home/ubuntu/FCJ_Tr4action
git pull
cd backend
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart tr4ction-backend
sudo systemctl restart nginx
echo "✅ Deploy concluído!"
```

Executar:
```bash
chmod +x deploy-aws.sh
./deploy-aws.sh
```

---

**Tempo estimado de setup:** 20-30 minutos
**Custo:** Gratuito por 12 meses, depois ~$10/mês
