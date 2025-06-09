#!/bin/bash
# 🚀 Terrascan VPS Deployment Script

set -e  # Exit on any error

echo "🌍 Deploying Terrascan to VPS..."

# Configuration
APP_NAME="terrascan"
APP_USER="terrascan"
APP_DIR="/opt/terrascan"
SERVICE_NAME="terrascan"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "This script should not be run as root for security reasons"
   exit 1
fi

# Update system packages
print_status "Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
print_status "Installing Python and system dependencies..."
sudo apt install -y python3 python3-pip python3-venv nginx supervisor git curl

# Create application user if doesn't exist
if ! id "$APP_USER" &>/dev/null; then
    print_status "Creating application user: $APP_USER"
    sudo useradd --system --shell /bin/bash --home-dir $APP_DIR --create-home $APP_USER
fi

# Create application directory
print_status "Setting up application directory..."
sudo mkdir -p $APP_DIR
sudo chown $APP_USER:$APP_USER $APP_DIR

# Copy application files
print_status "Copying application files..."
sudo -u $APP_USER cp -r . $APP_DIR/
cd $APP_DIR

# Create Python virtual environment
print_status "Creating Python virtual environment..."
sudo -u $APP_USER python3 -m venv venv
sudo -u $APP_USER ./venv/bin/pip install --upgrade pip

# Install Python dependencies
print_status "Installing Python dependencies..."
sudo -u $APP_USER ./venv/bin/pip install -r requirements.txt

# Copy environment file
if [ -f ".env" ]; then
    print_status "Environment file found, copying..."
    sudo -u $APP_USER cp .env $APP_DIR/
else
    print_warning "No .env file found, creating from example..."
    sudo -u $APP_USER cp .env.example $APP_DIR/.env
    print_warning "⚠️ Please edit $APP_DIR/.env with your API keys!"
fi

# Initialize database
print_status "Initializing database..."
sudo -u $APP_USER ./venv/bin/python3 -c "
from database.db import init_database
init_database()
print('Database initialized successfully!')
"

# Setup configurations
print_status "Setting up system configurations..."
sudo -u $APP_USER ./venv/bin/python3 setup_configs.py

# Create systemd service
print_status "Creating systemd service..."
sudo tee /etc/systemd/system/$SERVICE_NAME.service > /dev/null <<EOF
[Unit]
Description=Terrascan Environmental Data Platform
After=network.target

[Service]
Type=simple
User=$APP_USER
WorkingDirectory=$APP_DIR
Environment=PATH=$APP_DIR/venv/bin
ExecStart=$APP_DIR/venv/bin/python3 run.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Create Nginx configuration
print_status "Creating Nginx configuration..."
sudo tee /etc/nginx/sites-available/$APP_NAME > /dev/null <<EOF
server {
    listen 80;
    server_name _;  # Replace with your domain

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # Serve static files directly
    location /static/ {
        alias $APP_DIR/web/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
EOF

# Enable Nginx site
sudo ln -sf /etc/nginx/sites-available/$APP_NAME /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Test Nginx configuration
sudo nginx -t

# Start and enable services
print_status "Starting services..."
sudo systemctl daemon-reload
sudo systemctl enable $SERVICE_NAME
sudo systemctl start $SERVICE_NAME
sudo systemctl enable nginx
sudo systemctl restart nginx

# Check service status
print_status "Checking service status..."
sudo systemctl status $SERVICE_NAME --no-pager

print_status "🎉 Deployment completed successfully!"
print_status "🌐 Terrascan should now be available at http://your-server-ip"
print_status "📊 Check logs with: sudo journalctl -u $SERVICE_NAME -f"
print_status "🔧 Manage service with: sudo systemctl {start|stop|restart|status} $SERVICE_NAME"

# Display next steps
print_warning "📋 Next Steps:"
echo "1. 🔑 Edit $APP_DIR/.env with your actual API keys"
echo "2. 🌐 Configure your domain name in /etc/nginx/sites-available/$APP_NAME"
echo "3. 🔒 Set up SSL certificate (Let's Encrypt recommended)"
echo "4. 🔄 Restart services: sudo systemctl restart $SERVICE_NAME nginx" 
