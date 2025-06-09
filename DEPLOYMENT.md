# 🚀 Terrascan Deployment Guide

## **🌐 Hosting Recommendations 2024**

### **🥇 Recommended: Hetzner VPS (Best Value)**
**Perfect for Terrascan's geological timescale approach!**

**Why Hetzner?**
- 💰 **Predictable costs**: €4.15/month for 2GB RAM, 40GB SSD
- 🌍 **EU-based**: GDPR compliant, excellent for European users  
- 🚀 **Great performance**: NVMe SSDs, excellent network
- 📊 **No surprises**: Fixed monthly cost vs AWS's unpredictable bills
- 🛠️ **Simple**: No complex pricing tiers or hidden costs

**Recommended Plan:**
```
CX21: €4.15/month
- 2 vCPU, 4GB RAM, 40GB NVMe SSD
- 20TB traffic included
- Perfect for Terrascan with SQLite
```

### **🥈 Alternative Options**

| Provider | Plan | Price/Month | Best For |
|----------|------|-------------|----------|
| **Hetzner** | CX21 | €4.15 | Production (recommended) |
| **DigitalOcean** | Basic Droplet | $6/month | Easy setup, good docs |
| **Linode** | Nanode 1GB | $5/month | US-based, reliable |
| **Vultr** | Regular Performance | $6/month | Global locations |
| **Contabo** | VPS S | €4.99/month | Budget option |

### **❌ Avoid for Simple Apps:**
- **AWS EC2**: Billing complexity, overkill for this use case
- **Google Cloud**: Same complexity issues
- **Azure**: Enterprise-focused, expensive for simple deployments

---

## **🛠️ Deployment Methods**

### **Method 1: One-Click VPS Deployment (Recommended)**

```bash
# 1. Create VPS and SSH in
ssh root@your-server-ip

# 2. Create deployment user
adduser deploy
usermod -aG sudo deploy
su - deploy

# 3. Clone and deploy
git clone https://github.com/yourusername/terrascan.git
cd terrascan
chmod +x deploy.sh
./deploy.sh
```

**That's it!** 🎉 The script handles everything:
- ✅ System packages (Python, Nginx, etc.)
- ✅ User creation and permissions
- ✅ Python virtual environment
- ✅ Database initialization
- ✅ Systemd service setup
- ✅ Nginx reverse proxy
- ✅ Automatic startup on boot

### **Method 2: Docker Deployment (Advanced)**

```dockerfile
# Dockerfile (if you prefer containers)
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN python3 setup_configs.py

EXPOSE 5000
CMD ["python3", "run.py"]
```

### **Method 3: Manual Setup**

If you prefer to understand each step, see the `deploy.sh` script for the exact commands.

---

## **🔧 Environment Setup**

### **1. Copy Environment File**
```bash
cp .env.example .env
nano .env  # Edit with your API keys
```

### **2. Required API Keys**
```bash
# Get these API keys (all free tiers available):
NASA_FIRMS_API_KEY=...     # https://firms.modaps.eosdis.nasa.gov/api/
WORLD_AQI_API_KEY=...      # https://aqicn.org/api/
OPENWEATHER_API_KEY=...    # https://openweathermap.org/api
OPENAQ_API_KEY=...         # Optional (free API)
```

### **3. Production Configuration**
```bash
FLASK_ENV=production
FLASK_DEBUG=false
SIMULATION_MODE=false  # Use real API data
PORT=5000
```

---

## **🔒 Security Setup**

### **1. SSL Certificate (Let's Encrypt)**
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate (replace your-domain.com)
sudo certbot --nginx -d your-domain.com

# Auto-renewal test
sudo certbot renew --dry-run
```

### **2. Firewall Setup**
```bash
# Basic firewall
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw enable
```

### **3. Basic Security**
```bash
# Disable root SSH login
sudo nano /etc/ssh/sshd_config
# Set: PermitRootLogin no
sudo systemctl restart ssh

# Keep system updated
sudo apt update && sudo apt upgrade -y
```

---

## **📊 Monitoring & Management**

### **System Commands**
```bash
# Check service status
sudo systemctl status terrascan

# View logs
sudo journalctl -u terrascan -f

# Restart application
sudo systemctl restart terrascan

# Update application
cd /opt/terrascan
sudo -u terrascan git pull
sudo systemctl restart terrascan
```

### **Health Checks**
- 🌐 **Web Interface**: `http://your-domain.com`
- 📊 **API Status**: `http://your-domain.com/api/task_status`  
- 🔥 **Data Check**: `http://your-domain.com/api/data/fires`

---

## **🔄 CI/CD Pipeline (Optional)**

### **Simple Git-based Deployment**
```bash
#!/bin/bash
# deploy-update.sh
cd /opt/terrascan
sudo -u terrascan git pull
sudo -u terrascan ./venv/bin/pip install -r requirements.txt
sudo systemctl restart terrascan
echo "✅ Deployment updated!"
```

### **GitHub Actions (Advanced)**
```yaml
# .github/workflows/deploy.yml
name: Deploy to VPS
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to VPS
        uses: appleboy/ssh-action@v0.1.5
        with:
          host: ${{ secrets.HOST }}
          username: ${{ secrets.USERNAME }}
          key: ${{ secrets.PRIVATE_KEY }}
          script: |
            cd /opt/terrascan
            sudo -u terrascan git pull
            sudo systemctl restart terrascan
```

---

## **💰 Cost Estimation**

### **Monthly Costs (Hetzner CX21)**
- 🖥️ **VPS**: €4.15/month
- 🌐 **Domain**: ~€10/year (€0.83/month)
- 🔒 **SSL**: Free (Let's Encrypt)
- 📊 **APIs**: Free tier covers most usage

**Total: ~€5/month** for a production environmental data platform! 🎉

### **Comparison vs Serverless**
- **AWS Lambda + RDS**: $20-50+/month (unpredictable)
- **Vercel + Database**: $20-40/month  
- **Hetzner VPS**: €5/month (predictable)

**Winner: VPS for this use case!** 🏆

---

## **🚀 Quick Start Commands**

```bash
# Hetzner VPS Quick Deploy
curl -fsSL https://raw.githubusercontent.com/yourusername/terrascan/main/deploy.sh | bash

# Or manual:
git clone https://github.com/yourusername/terrascan.git
cd terrascan
./deploy.sh

# Then visit: http://your-server-ip
```

**That's it! You have a production-ready environmental data platform!** 🌍✨ 
