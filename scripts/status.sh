#!/bin/bash

###############################################################################
# File Server Management System - Status Script
# Shows service status, recent logs, and listening ports
###############################################################################

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color
BOLD='\033[1m'

# Configuration
LOG_LINES=20
INSTALL_DIR="/opt/file-server"

# Print functions
print_header() {
    echo -e "${BLUE}${BOLD}"
    echo "╔════════════════════════════════════════════════════════════════════╗"
    echo "║                                                                    ║"
    echo "║     📊 FILE SERVER MANAGEMENT - STATUS DASHBOARD                   ║"
    echo "║                                                                    ║"
    echo "╚════════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

print_section() {
    echo -e "\n${CYAN}${BOLD}═══ $1 ═══${NC}\n"
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

# Function to get service status
get_service_status() {
    local service=$1
    if systemctl is-active --quiet "$service"; then
        echo -e "${GREEN}●${NC} Running"
    elif systemctl is-enabled --quiet "$service" 2>/dev/null; then
        echo -e "${RED}●${NC} Stopped (enabled)"
    else
        echo -e "${YELLOW}●${NC} Not installed"
    fi
}

# Function to get service uptime
get_service_uptime() {
    local service=$1
    if systemctl is-active --quiet "$service"; then
        systemctl show "$service" --property=ActiveEnterTimestamp --value | \
            xargs -I {} date -d "{}" "+%Y-%m-%d %H:%M:%S" 2>/dev/null || echo "N/A"
    else
        echo "N/A"
    fi
}

# Function to display service table
show_services_table() {
    print_section "SERVICE STATUS"
    
    printf "%-25s %-20s %-25s\n" "Service" "Status" "Started At"
    printf "%-25s %-20s %-25s\n" "-------" "------" "----------"
    
    # Main services
    local services=("fileserver-api" "fileserver-web")
    
    for service in "${services[@]}"; do
        local status=$(get_service_status "$service")
        local uptime=$(get_service_uptime "$service")
        printf "%-25s %-30s %-25s\n" "$service" "$status" "$uptime"
    done
    
    echo ""
    
    # Check for protocol services if they exist
    if systemctl list-units --all --type=service | grep -q "vsftpd\|smbd\|nmbd\|sshd\|minio"; then
        printf "\n%-25s %-20s %-25s\n" "Protocol Services" "Status" "Started At"
        printf "%-25s %-20s %-25s\n" "-----------------" "------" "----------"
        
        for proto_service in vsftpd smbd nmbd sshd minio; do
            if systemctl list-units --all --type=service | grep -q "$proto_service"; then
                local status=$(get_service_status "$proto_service")
                local uptime=$(get_service_uptime "$proto_service")
                printf "%-25s %-30s %-25s\n" "$proto_service" "$status" "$uptime"
            fi
        done
    fi
}

# Function to show listening ports
show_listening_ports() {
    print_section "LISTENING PORTS"
    
    echo "Checking active network ports..."
    echo ""
    
    printf "%-10s %-25s %-15s\n" "Port" "Service" "Process"
    printf "%-10s %-25s %-15s\n" "----" "-------" "-------"
    
    # Check common ports
    local ports=(
        "8000:API Backend"
        "3000:Web Interface"
        "21:FTP"
        "22:SSH/SFTP"
        "139:SMB"
        "445:SMB"
        "9000:MinIO S3"
        "9001:MinIO Console"
        "2049:NFS"
    )
    
    for port_info in "${ports[@]}"; do
        IFS=':' read -r port service <<< "$port_info"
        
        # Check if port is listening
        if ss -ltn 2>/dev/null | grep -q ":$port "; then
            # Try to get process name
            local process=$(ss -ltnp 2>/dev/null | grep ":$port " | awk -F'users:' '{print $2}' | sed 's/[()]//g' | awk -F',' '{print $1}' | sed 's/"//g' | head -n1)
            [ -z "$process" ] && process="unknown"
            printf "${GREEN}%-10s${NC} %-25s %-15s\n" "$port" "$service" "$process"
        else
            printf "${YELLOW}%-10s${NC} %-25s %-15s\n" "$port" "$service" "Not listening"
        fi
    done
}

# Function to show recent logs
show_recent_logs() {
    print_section "RECENT LOGS (Last $LOG_LINES lines)"
    
    # API Logs
    echo -e "${BOLD}${MAGENTA}▶ File Server API (fileserver-api)${NC}"
    if systemctl is-active --quiet fileserver-api; then
        journalctl -u fileserver-api -n "$LOG_LINES" --no-pager 2>/dev/null || echo "No logs available"
    else
        echo -e "${YELLOW}Service not running${NC}"
    fi
    
    echo ""
    echo "─────────────────────────────────────────────────────────────────"
    echo ""
    
    # Web Logs
    echo -e "${BOLD}${MAGENTA}▶ Web Interface (fileserver-web)${NC}"
    if systemctl is-active --quiet fileserver-web; then
        journalctl -u fileserver-web -n "$LOG_LINES" --no-pager 2>/dev/null || echo "No logs available"
    else
        echo -e "${YELLOW}Service not running${NC}"
    fi
}

# Function to show system resources
show_system_resources() {
    print_section "SYSTEM RESOURCES"
    
    echo -e "${BOLD}CPU Usage:${NC}"
    top -bn1 | grep "Cpu(s)" | sed "s/.*, *\([0-9.]*\)%* id.*/\1/" | awk '{print "  Idle: " $1 "% | Used: " 100-$1 "%"}'
    
    echo ""
    echo -e "${BOLD}Memory Usage:${NC}"
    free -h | awk 'NR==2{printf "  Total: %s | Used: %s (%.2f%%) | Free: %s\n", $2, $3, $3*100/$2, $4}'
    
    echo ""
    echo -e "${BOLD}Disk Usage (/)${NC}"
    df -h / | awk 'NR==2{printf "  Total: %s | Used: %s (%s) | Available: %s\n", $2, $3, $5, $4}'
}

# Function to show quick actions
show_quick_actions() {
    print_section "QUICK ACTIONS"
    
    echo "Service Management:"
    echo "  • Restart API:        sudo systemctl restart fileserver-api"
    echo "  • Restart Web:        sudo systemctl restart fileserver-web"
    echo "  • View API logs:      sudo journalctl -u fileserver-api -f"
    echo "  • View Web logs:      sudo journalctl -u fileserver-web -f"
    echo ""
    echo "Protocol Management:"
    echo "  • CLI Menu:           cd $INSTALL_DIR && source venv/bin/activate && python3 cli/main.py"
    echo "  • Web Interface:      http://$(hostname -I | awk '{print $1}'):3000"
    echo "  • API Docs:           http://$(hostname -I | awk '{print $1}'):8000/docs"
}

# Function to show network info
show_network_info() {
    print_section "NETWORK INFORMATION"
    
    local ip=$(hostname -I | awk '{print $1}')
    local hostname=$(hostname)
    
    echo "Hostname:         $hostname"
    echo "Primary IP:       $ip"
    echo ""
    echo "Access URLs:"
    echo "  • Web Interface:  http://$ip:3000"
    echo "  • API Endpoint:   http://$ip:8000"
    echo "  • API Docs:       http://$ip:8000/docs"
}

# Main execution
main() {
    clear
    print_header
    
    # Check if running as root for full info
    if [[ $EUID -ne 0 ]]; then
        print_warning "Running without root privileges. Some information may be limited."
        echo "  Run with: sudo $0"
        echo ""
    fi
    
    show_network_info
    show_services_table
    show_listening_ports
    show_system_resources
    
    # Only show logs if explicitly requested with --logs flag
    if [[ "$1" == "--logs" ]]; then
        show_recent_logs
    else
        echo ""
        print_info "To view recent logs, run: $0 --logs"
    fi
    
    show_quick_actions
    
    echo ""
    print_success "Status check completed at $(date '+%Y-%m-%d %H:%M:%S')"
    echo ""
}

# Run main function
main "$@"
