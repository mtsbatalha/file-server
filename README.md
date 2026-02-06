# File Server Management System

🚀 Sistema completo de gerenciamento de servidor de arquivos multi-protocolo com instalação automatizada, interface web moderna e gestão centralizada.

## 📦 Protocolos Suportados

- **FTP/FTPS** - File Transfer Protocol com SSL/TLS
- **SFTP** - SSH File Transfer Protocol
- **NFS** - Network File System
- **SMB/CIFS** - Server Message Block (Windows Shares)
- **WebDAV** - Web Distributed Authoring and Versioning
- **S3** - Object Storage (MinIO)
- **NextCloud** - Plataforma de colaboração completa

## ✨ Features

- ✅ Instalação automatizada para Linux e Windows
- ✅ Interface web moderna e responsiva
- ✅ Menu CLI interativo
- ✅ Gerenciamento centralizado de usuários
- ✅ Sistema de quotas de disco
- ✅ Logs e auditoria em tempo real
- ✅ SSL/TLS automático (Let's Encrypt)
- ✅ Configuração automática de firewall
- ✅ Suporte multi-plataforma

## 🛠️ Stack Tecnológico

- **Backend**: Python 3.10+ / FastAPI / SQLAlchemy
- **Frontend**: Next.js 14 / React 18 / Tailwind CSS
- **Database**: SQLite (default) / PostgreSQL (optional)
- **CLI**: Rich + Typer

## 📋 Requisitos de Sistema

### Mínimo
- 4 CPU cores
- 8 GB RAM
- 50 GB disco livre
- Python 3.10+
- Node.js 18+

### Recomendado (Todos os Protocolos)
- 8 CPU cores
- 16 GB RAM  
- 100 GB disco livre
- IP público fixo (para SSL automático)

## 🚀 Instalação Rápida

### Linux
```bash
curl -fsSL https://raw.githubusercontent.com/user/file-server/main/scripts/install.sh | sudo bash
```

### Windows (PowerShell Admin)
```powershell
irm https://raw.githubusercontent.com/user/file-server/main/scripts/install.ps1 | iex
```

### Docker
```bash
git clone https://github.com/user/file-server
cd file-server
docker-compose up -d
```

## 📖 Uso

### CLI Menu Interativo
```bash
file-server-cli
```

### Iniciar Web Interface
```bash
file-server-web
```
Acesse: `http://localhost:8000`

### API Documentation
Acesse: `http://localhost:8000/docs` (Swagger UI)

## 🔐 Segurança

- Senhas hasheadas com bcrypt/argon2
- JWT authentication
- Rate limiting
- Fail2ban integration
- SSL/TLS enforced
- Input validation e sanitization
- Audit logging completo

## 📊 Arquitetura

```
┌─────────────┐     ┌─────────────┐
│  Web UI     │────▶│  REST API   │
│  (Next.js)  │     │  (FastAPI)  │
└─────────────┘     └──────┬──────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
   ┌────▼────┐       ┌─────▼─────┐     ┌─────▼─────┐
   │ Protocol│       │   User    │     │   Quota   │
   │Installers│       │  Manager  │     │  Monitor  │
   └────┬────┘       └───────────┘     └───────────┘
        │
   ┌────▼────────────────────────────────┐
   │  FTP │ SFTP │ NFS │ SMB │ WebDAV   │
   │  S3  │ NextCloud                   │
   └─────────────────────────────────────┘
```

## 🗺️ Roadmap

- [x] Core architecture
- [x] Installation scripts
- [ ] Backend API
- [ ] Protocol installers
- [ ] Web interface
- [ ] CLI menu
- [ ] SSL automation
- [ ] Quota system
- [ ] Logging & audit
- [ ] Testing suite
- [ ] Documentation

## 📝 Licença

MIT License

## 🤝 Contribuindo

Contributions are welcome! Please read our contributing guidelines.

## 📧 Suporte

- Issues: [GitHub Issues](https://github.com/user/file-server/issues)
- Docs: [Documentation](https://docs.file-server.example.com)
