# Quick Start Guide

## 🚀 Installation (Linux)

### Option 1: Automated Install (Recommended)

```bash
# Clone the repository
git clone https://github.com/mtsbatalha/file-server.git
cd file-server

# Run the installer (requires root)
sudo bash scripts/install.sh
```

The script will:
- ✅ Install system dependencies
- ✅ Setup Python venv and install packages
- ✅ Install Node.js and build frontend
- ✅ Create database and admin user
- ✅ Configure systemd services
- ✅ Setup firewall rules
- ✅ **Prompt for protocol selection (FTP, SFTP, SMB, S3)**

You can select multiple protocols during installation!
### Default Credentials

- **Username:** `admin`
- **Password:** `admin123`

⚠️ **CHANGE IMMEDIATELY AFTER FIRST LOGIN!**

---

## 🌐 Access

After installation:

- **Web Interface:** `http://YOUR_SERVER_IP:3000`
- **API:** `http://YOUR_SERVER_IP:8000`
- **API Docs:** `http://YOUR_SERVER_IP:8000/docs`

---

## 📊 Service Management

```bash
# View status
sudo bash scripts/status.sh

# View status with logs
sudo bash scripts/status.sh --logs

# Manage services
sudo systemctl status fileserver-api
sudo systemctl status fileserver-web

sudo systemctl restart fileserver-api
sudo systemctl restart fileserver-web

# View logs
sudo journalctl -u fileserver-api -f
sudo journalctl -u fileserver-web -f
```

---

## 🐳 Docker Installation (Alternative)

```bash
# Clone repository
git clone https://github.com/mtsbatalha/file-server.git
cd file-server

# Start with Docker Compose
docker-compose up -d

# Access
# Web UI: http://localhost:3000
# API: http://localhost:8000
```

---

## 🔧 Troubleshooting

### API Not Starting

```bash
# Check logs
sudo journalctl -u fileserver-api -n 50

# Reinstall dependencies
cd /opt/file-server
source venv/bin/activate
pip install -r backend/requirements.txt
deactivate

# Restart
sudo systemctl restart fileserver-api
```

### Frontend Build Issues

```bash
cd /opt/file-server/frontend
npm install
npm run build
sudo systemctl restart fileserver-web
```

### Database Reset

```bash
cd /opt/file-server
source venv/bin/activate

# Backup if needed
cp fileserver.db fileserver.db.backup

# Reset
rm fileserver.db
python3 -c "from backend.core.database import Base, engine; from backend.api.models.user import *; Base.metadata.create_all(bind=engine)"
python3 -c "from backend.api.services.user_service import create_default_admin; create_default_admin()"

deactivate
sudo systemctl restart fileserver-api
```

---

## 📝 Configuration

### Backend (.env)

```bash
# Edit configuration
sudo nano /opt/file-server/.env

# Change settings like:
# - CORS_ORIGINS
# - SECRET_KEY
# - DATABASE_URL
# - ADMIN_PASSWORD

# Restart after changes
sudo systemctl restart fileserver-api
```

### Frontend (.env.local)

```bash
sudo nano /opt/file-server/frontend/.env.local

# Update:
# NEXT_PUBLIC_API_URL=http://YOUR_IP:8000

# Restart
sudo systemctl restart fileserver-web
```

---

## 🔐 Security Checklist

- [ ] Change default admin password
- [ ] Generate new SECRET_KEY in .env
- [ ] Configure specific CORS_ORIGINS
- [ ] Enable firewall (UFW/firewalld)
- [ ] Setup SSL/HTTPS (Let's Encrypt recommended)
- [ ] Regular backups of fileserver.db

---

## 📚 More Info

- [Full README](README.md)
- [API Documentation](http://YOUR_IP:8000/docs)
- [GitHub Issues](https://github.com/mtsbatalha/file-server/issues)
