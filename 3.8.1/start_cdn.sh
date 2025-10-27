#!/bin/bash

# CDN Server Management Script
# Usage: ./start_cdn.sh [start|stop|restart|status|install]

CDN_DIR="/home/yousefmsm1/Desktop/3.6.3.1"
SERVICE_NAME="cdn-server"
PYTHON_VENV="$CDN_DIR/venv/bin/python"
CDN_SCRIPT="$CDN_DIR/cdn_server.py"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}=== Telegram Bot Assets CDN Server ===${NC}"
}

# Check if running as root
check_root() {
    if [[ $EUID -eq 0 ]]; then
        print_error "This script should not be run as root"
        exit 1
    fi
}

# Check if virtual environment exists
check_venv() {
    if [[ ! -f "$PYTHON_VENV" ]]; then
        print_error "Virtual environment not found at $PYTHON_VENV"
        print_warning "Please create virtual environment first:"
        echo "cd $CDN_DIR"
        echo "python3 -m venv venv"
        echo "source venv/bin/activate"
        echo "pip install -r cdn_requirements.txt"
        exit 1
    fi
}

# Check if CDN script exists
check_script() {
    if [[ ! -f "$CDN_SCRIPT" ]]; then
        print_error "CDN script not found at $CDN_SCRIPT"
        exit 1
    fi
}

# Install systemd service
install_service() {
    print_header
    print_status "Installing systemd service..."
    
    # Copy service file to systemd directory
    sudo cp "$CDN_DIR/cdn-server.service" /etc/systemd/system/
    
    # Reload systemd
    sudo systemctl daemon-reload
    
    # Enable service
    sudo systemctl enable $SERVICE_NAME
    
    print_status "Service installed and enabled successfully!"
    print_status "Use 'sudo systemctl start $SERVICE_NAME' to start the service"
}

# Start CDN server
start_cdn() {
    print_header
    print_status "Starting CDN server..."
    
    # Check if already running
    if pgrep -f "cdn_server.py" > /dev/null; then
        print_warning "CDN server is already running"
        return
    fi
    
    # Start the server
    cd "$CDN_DIR"
    nohup $PYTHON_VENV $CDN_SCRIPT > cdn.log 2>&1 &
    
    sleep 2
    
    # Check if started successfully
    if pgrep -f "cdn_server.py" > /dev/null; then
        print_status "CDN server started successfully!"
        print_status "Logs: $CDN_DIR/cdn.log"
        print_status "API: https://asadffastest.store"
    else
        print_error "Failed to start CDN server"
        print_status "Check logs: $CDN_DIR/cdn.log"
    fi
}

# Stop CDN server
stop_cdn() {
    print_header
    print_status "Stopping CDN server..."
    
    # Kill the process
    pkill -f "cdn_server.py"
    
    sleep 2
    
    if pgrep -f "cdn_server.py" > /dev/null; then
        print_warning "CDN server is still running, force killing..."
        pkill -9 -f "cdn_server.py"
    fi
    
    print_status "CDN server stopped"
}

# Restart CDN server
restart_cdn() {
    print_header
    print_status "Restarting CDN server..."
    stop_cdn
    sleep 2
    start_cdn
}

# Show status
show_status() {
    print_header
    
    # Check if process is running
    if pgrep -f "cdn_server.py" > /dev/null; then
        print_status "CDN server is RUNNING"
        PID=$(pgrep -f "cdn_server.py")
        print_status "Process ID: $PID"
        
        # Check port
        if netstat -tlnp 2>/dev/null | grep :8080 > /dev/null; then
            print_status "Port 8080 is listening"
        else
            print_warning "Port 8080 is not listening"
        fi
        
        # Show recent logs
        if [[ -f "$CDN_DIR/cdn.log" ]]; then
            print_status "Recent logs:"
            tail -5 "$CDN_DIR/cdn.log"
        fi
    else
        print_error "CDN server is NOT RUNNING"
    fi
    
    # Check systemd service status
    if systemctl is-active --quiet $SERVICE_NAME 2>/dev/null; then
        print_status "Systemd service is ACTIVE"
    else
        print_warning "Systemd service is not active"
    fi
}

# Test CDN endpoints
test_cdn() {
    print_header
    print_status "Testing CDN endpoints..."
    
    # Test main endpoint
    if curl -s https://asadffastest.store/ > /dev/null; then
        print_status "✓ Main endpoint (/) is working"
    else
        print_error "✗ Main endpoint (/) is not working"
    fi
    
    # Test health endpoint
    if curl -s https://asadffastest.store/health > /dev/null; then
        print_status "✓ Health endpoint (/health) is working"
    else
        print_error "✗ Health endpoint (/health) is not working"
    fi
    
    # Test folder listing
    if curl -s https://asadffastest.store/api/new_gift_cards > /dev/null; then
        print_status "✓ Folder listing endpoint is working"
    else
        print_error "✗ Folder listing endpoint is not working"
    fi
}

# Main script logic
main() {
    check_root
    check_venv
    check_script
    
    case "$1" in
        "start")
            start_cdn
            ;;
        "stop")
            stop_cdn
            ;;
        "restart")
            restart_cdn
            ;;
        "status")
            show_status
            ;;
        "install")
            install_service
            ;;
        "test")
            test_cdn
            ;;
        *)
            echo "Usage: $0 {start|stop|restart|status|install|test}"
            echo ""
            echo "Commands:"
            echo "  start   - Start the CDN server"
            echo "  stop    - Stop the CDN server"
            echo "  restart - Restart the CDN server"
            echo "  status  - Show server status"
            echo "  install - Install systemd service"
            echo "  test    - Test CDN endpoints"
            exit 1
            ;;
    esac
}

# Run main function
main "$@" 