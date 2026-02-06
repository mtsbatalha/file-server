#!/bin/bash

###############################################################################
# File Server Management System - Linux Installer
# Automated installation script for Ubuntu/Debian/RHEL/CentOS/Rocky/Fedora
###############################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
INSTALL_DIR="/opt/file-server"
PYTHON_VERSION="3.10"
NODE_VERSION="18"

# Print functions
print_header() {
    echo -e "${BLUE}"
    echo "╔════════════════════════════════════════════════════════════════════╗"
    echo "║                                                                    ║"
    echo "║     📦 FILE SERVER MANAGEMENT SYSTEM - INSTALLER                   ║"
    echo "║                                                                    ║"
    echo "╚════════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if running as root
check_root() {
    if [[ $EUID -ne 0 ]]; then
        print_error "This script must be run as root (use sudo)"
        exit 1
    fi
    print_success "Running as root"
}

# Detect OS and distribution
detect_os() {
    print_info "Detecting operating system..."
    
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS=$ID
        OS_VERSION=$VERSION_ID
        print_success "Detected: $NAME $VERSION"
    else
        print_error "Cannot detect OS. /etc/os-release not found."
        exit 1
    fi
}

# Install system dependencies
install_dependencies() {
    print_info "Installing system dependencies..."
    
    case "$OS" in
        ubuntu|debian)
            apt-get update
            apt-get install -y \
                python3 python3-pip python3-venv \
                git curl wget \
                build-essential \
                sqlite3 \
                nginx \
                certbot python3-certbot-nginx
            ;;
        rhel|centos|rocky|fedora)
            if command -v dnf &> /dev/null; then
                PKG_MGR="dnf"
            else
                PKG_MGR="yum"
            fi
            
            $PKG_MGR install -y \
                python3 python3-pip \
                git curl wget \
                gcc gcc-c++ make \
                sqlite \
                nginx \
                certbot python3-certbot-nginx
            ;;
        *)
            print_error "Unsupported distribution: $OS"
            exit 1
            ;;
    esac
    
    print_success "System dependencies installed"
}

# Check Python version
check_python() {
    print_info "Checking Python version..."
    
    PYTHON_CMD=$(which python3)
    PYTHON_VER=$($PYTHON_CMD --version | cut -d' ' -f2 | cut -d'.' -f1,2)
    
    if [ "$(printf '%s\n' "$PYTHON_VERSION" "$PYTHON_VER" | sort -V | head -n1)" = "$PYTHON_VERSION" ]; then
        print_success "Python $PYTHON_VER is installed"
    else
        print_error "Python $PYTHON_VERSION or higher is required (found $PYTHON_VER)"
        exit 1
    fi
}

# Install Node.js
install_nodejs() {
    print_info "Installing Node.js..."
    
    if command -v node &> /dev/null; then
        NODE_VER=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
        if [ "$NODE_VER" -ge "$NODE_VERSION" ]; then
            print_success "Node.js $NODE_VER is already installed"
            return
        fi
    fi
    
    # Install via NodeSource
    curl -fsSL https://deb.nodesource.com/setup_${NODE_VERSION}.x | bash -
    
    case "$OS" in
        ubuntu|debian)
            apt-get install -y nodejs
            ;;
        rhel|centos|rocky|fedora)
            $PKG_MGR install -y nodejs
            ;;
    esac
    
    print_success "Node.js installed"
}

# Create installation directory
create_install_dir() {
    print_info "Creating installation directory..."
    
    mkdir -p "$INSTALL_DIR"
    cd "$INSTALL_DIR"
    
    print_success "Installation directory created: $INSTALL_DIR"
}

# Copy application files
install_application() {
    print_info "Installing application files..."
    
    # Assuming the script is run from the project directory
    SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
    PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
    
    # Get absolute paths for comparison
    PROJECT_ABS="$(cd "$PROJECT_DIR" && pwd)"
    INSTALL_ABS="$(cd "$INSTALL_DIR" && pwd)"
    
    # Check if source and destination are the same
    if [ "$PROJECT_ABS" = "$INSTALL_ABS" ]; then
        print_success "Already in installation directory, skipping file copy"
        return 0
    fi
    
    # Copy files (exclude .git and node_modules)
    rsync -av --exclude='.git' --exclude='node_modules' --exclude='frontend/.next' --exclude='venv' \
        "$PROJECT_DIR/" "$INSTALL_DIR/" 2>/dev/null || \
        cp -r "$PROJECT_DIR"/* "$INSTALL_DIR/"
    
    print_success "Application files copied"
}

# Setup Python virtual environment
setup_venv() {
    print_info "Setting up Python virtual environment..."
    
    cd "$INSTALL_DIR"
    python3 -m venv venv
    source venv/bin/activate
    
    pip install --upgrade pip
    pip install -r backend/requirements.txt
    
    deactivate
    
    print_success "Python virtual environment configured"
}

# Install frontend dependencies
install_frontend() {
    print_info "Installing frontend dependencies (this may take a while)..."
    
    cd "$INSTALL_DIR/frontend"
    
    # Create .env.local if doesn't exist
    if [ ! -f .env.local ]; then
        cp .env.local.example .env.local
        
        # Get server IP
        SERVER_IP=$(hostname -I | awk '{print $1}')
        
        # Update API URL
        sed -i "s|http://localhost:8000|http://${SERVER_IP}:8000|" .env.local
        
        print_success "Frontend environment file created"
    fi
    
    # Install dependencies
    npm install
    
    # Build frontend for production
    print_info "Building frontend for production..."
    npm run build
    
    print_success "Frontend dependencies installed and built"
}

# Initialize database
init_database() {
    print_info "Initializing database..."
    
    cd "$INSTALL_DIR"
    source venv/bin/activate
    
    # Create .env file if doesn't exist
    if [ ! -f .env ]; then
        cp .env.example .env
        
        # Generate secret key
        SECRET_KEY=$(openssl rand -hex 32)
        sed -i "s/change-this-secret-key-use-openssl-rand-hex-32/$SECRET_KEY/" .env
        
        print_success "Environment file created with secure secret key"
    fi
    
    # Remove old database if exists (for clean install)
    if [ -f "$INSTALL_DIR/fileserver.db" ]; then
        print_warning "Existing database found, removing for fresh install..."
        rm -f "$INSTALL_DIR/fileserver.db"
    fi
    
    # Create database tables
    print_info "Creating database tables..."
    python3 << 'PYEOF'
from backend.core.database import Base, engine
from backend.api.models.user import User, Protocol, SharedPath, UserProtocolAccess, AccessLog

try:
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully")
except Exception as e:
    print(f"Error creating tables: {e}")
    exit(1)
PYEOF
    
    if [ $? -ne 0 ]; then
        print_error "Failed to create database tables"
        deactivate
        exit 1
    fi
    
    # Create default admin user
    print_info "Creating default admin user..."
    python3 -c "from backend.api.services.user_service import create_default_admin; create_default_admin()" 2>&1 | grep -v "error reading bcrypt version" | grep -v "AttributeError"
    
    if [ $? -eq 0 ]; then
        print_success "Default admin user created (username: admin, password: admin123)"
        print_warning "⚠️  CHANGE THE DEFAULT PASSWORD IMMEDIATELY!"
    else
        print_warning "Admin user creation had warnings but may have succeeded"
    fi
    
    # Initialize default protocols
    print_info "Initializing default protocols..."
    python3 -c "from backend.api.services.protocol_service import initialize_protocols; initialize_protocols()" 2>&1 || true
    
    deactivate
    
    print_success "Database initialized"
}

# Create systemd services
create_systemd_services() {
    print_info "Creating systemd services..."
    
    # Backend API service
    cat > /etc/systemd/system/fileserver-api.service << EOF
[Unit]
Description=File Server Management API
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$INSTALL_DIR
Environment="PATH=$INSTALL_DIR/venv/bin"
ExecStart=$INSTALL_DIR/venv/bin/python3 -m uvicorn backend.api.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

    # Frontend service (Next.js)
    cat > /etc/systemd/system/fileserver-web.service << EOF
[Unit]
Description=File Server Management Web Interface
After=network.target fileserver-api.service

[Service]
Type=simple
User=root
WorkingDirectory=$INSTALL_DIR/frontend
Environment="NODE_ENV=production"
ExecStart=/usr/bin/npm start
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

    # Reload systemd
    systemctl daemon-reload
    
    print_success "Systemd services created"
}

# Configure firewall
configure_firewall() {
    print_info "Configuring firewall..."
    
    if command -v ufw &> /dev/null; then
        # UFW (Ubuntu/Debian)
        ufw allow 8000/tcp comment 'File Server API'
        ufw allow 3000/tcp comment 'File Server Web'
        ufw allow 80/tcp comment 'HTTP'
        ufw allow 443/tcp comment 'HTTPS'
        
        print_success "UFW firewall configured"
    elif command -v firewall-cmd &> /dev/null; then
        # firewalld (RHEL/CentOS/Fedora)
        firewall-cmd --permanent --add-port=8000/tcp
        firewall-cmd --permanent --add-port=3000/tcp
        firewall-cmd --permanent --add-service=http
        firewall-cmd --permanent --add-service=https
        firewall-cmd --reload
        
        print_success "firewalld configured"
    else
        print_warning "No firewall detected. Please configure manually."
    fi
}

# Start services
start_services() {
    print_info "Starting services..."
    
    systemctl enable fileserver-api
    systemctl start fileserver-api
    
    systemctl enable fileserver-web
    systemctl start fileserver-web
    
    # Wait for services to be ready
    sleep 5
    
    print_success "Services started"
    
    # Show status
    systemctl status fileserver-api --no-pager
    echo ""
    systemctl status fileserver-web --no-pager
}

# Print completion message
print_completion() {
    echo ""
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                                                                    ║${NC}"
    echo -e "${GREEN}║     ✅ INSTALLATION COMPLETE!                                       ║${NC}"
    echo -e "${GREEN}║                                                                    ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    print_info "File Server Management System has been installed successfully!"
    echo ""
    print_info "📍 Installation directory: $INSTALL_DIR"
    print_info "🔐 Default admin credentials:"
    echo "     Username: admin"
    echo "     Password: admin123"
    echo -e "${RED}     ⚠️  CHANGE THIS PASSWORD IMMEDIATELY!${NC}"
    echo ""
    print_info "🌐 Web Interface: http://$(hostname -I | awk '{print $1}'):3000"
    print_info "🔗 API: http://$(hostname -I | awk '{print $1}'):8000"
    print_info "📚 API Docs: http://$(hostname -I | awk '{print $1}'):8000/docs"
    echo ""
    print_info "🎯 To start the CLI menu: cd $INSTALL_DIR && source venv/bin/activate && python3 cli/main.py"
    echo ""
    print_info "📊 Service management:"
    echo "     • View API status: systemctl status fileserver-api"
    echo "     • View Web status: systemctl status fileserver-web"
    echo "     • View API logs: journalctl -u fileserver-api -f"
    echo "     • View Web logs: journalctl -u fileserver-web -f"
    echo "     • Restart API: systemctl restart fileserver-api"
    echo "     • Restart Web: systemctl restart fileserver-web"
    echo ""
}

# Main installation flow
main() {
    print_header
    
    check_root
    detect_os
    install_dependencies
    check_python
    install_nodejs
    create_install_dir
    install_application
    setup_venv
    install_frontend
    init_database
    create_systemd_services
    configure_firewall
    start_services
    print_completion
}

# Run installation
main
