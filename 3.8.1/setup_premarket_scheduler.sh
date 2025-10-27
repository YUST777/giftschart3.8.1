#!/bin/bash
"""
Premarket Scheduler Setup Script
Sets up the premarket price scheduler as a systemd service
"""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project directory
PROJECT_DIR="/home/yousefmsm1/Desktop/last 3.4"
SERVICE_NAME="premarket-scheduler"
SERVICE_FILE="${SERVICE_NAME}.service"

echo -e "${BLUE}🚀 Premarket Gift Price Scheduler Setup${NC}"
echo "=" * 50

# Function to print status
print_status() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ $2${NC}"
    else
        echo -e "${RED}❌ $2${NC}"
        exit 1
    fi
}

# Check if running as root for service installation
check_sudo() {
    if [ "$EUID" -ne 0 ]; then
        echo -e "${YELLOW}⚠️ This script needs sudo access to install systemd service${NC}"
        echo "Please run: sudo ./setup_premarket_scheduler.sh"
        exit 1
    fi
}

# Test the premarket system first
test_system() {
    echo -e "${BLUE}🧪 Testing premarket price fetching system...${NC}"
    cd "$PROJECT_DIR"
    source venv/bin/activate
    python3 -c "import tonnel_api; print('✅ Tonnel API module loaded successfully')"
    if [ $? -eq 0 ]; then
        print_status 0 "Premarket system test completed"
    else
        print_status 1 "Premarket system test failed"
    fi
}

# Install the systemd service
install_service() {
    echo -e "${BLUE}📋 Installing systemd service...${NC}"
    
    # Copy service file to systemd directory
    cp "$PROJECT_DIR/$SERVICE_FILE" /etc/systemd/system/
    print_status $? "Service file copied to /etc/systemd/system/"
    
    # Reload systemd daemon
    systemctl daemon-reload
    print_status $? "Systemd daemon reloaded"
    
    # Enable the service
    systemctl enable $SERVICE_NAME
    print_status $? "Service enabled for auto-start"
}

# Start the service
start_service() {
    echo -e "${BLUE}▶️ Starting premarket scheduler service...${NC}"
    systemctl start $SERVICE_NAME
    print_status $? "Service started"
}

# Check service status
check_status() {
    echo -e "${BLUE}📊 Service status:${NC}"
    systemctl status $SERVICE_NAME --no-pager -l
}

# Show logs
show_logs() {
    echo -e "${BLUE}📋 Recent logs:${NC}"
    journalctl -u $SERVICE_NAME -n 20 --no-pager
}

# Main installation process
main() {
    case "${1:-install}" in
        "test")
            cd "$PROJECT_DIR"
            source venv/bin/activate
            test_system
            ;;
        "install")
            check_sudo
            test_system
            install_service
            start_service
            sleep 3
            check_status
            echo -e "\n${GREEN}🎉 Premarket scheduler installed and started!${NC}"
            echo -e "${YELLOW}📋 Management commands:${NC}"
            echo "  sudo systemctl start $SERVICE_NAME     # Start service"
            echo "  sudo systemctl stop $SERVICE_NAME      # Stop service"
            echo "  sudo systemctl restart $SERVICE_NAME   # Restart service"
            echo "  sudo systemctl status $SERVICE_NAME    # Check status"
            echo "  sudo journalctl -u $SERVICE_NAME -f    # Follow logs"
            echo "  tail -f '$PROJECT_DIR/premarket_scheduler.log'  # Application logs"
            ;;
        "status")
            check_status
            ;;
        "logs")
            show_logs
            ;;
        "stop")
            check_sudo
            systemctl stop $SERVICE_NAME
            print_status $? "Service stopped"
            ;;
        "start")
            check_sudo
            systemctl start $SERVICE_NAME
            print_status $? "Service started"
            ;;
        "restart")
            check_sudo
            systemctl restart $SERVICE_NAME
            print_status $? "Service restarted"
            ;;
        "uninstall")
            check_sudo
            systemctl stop $SERVICE_NAME 2>/dev/null
            systemctl disable $SERVICE_NAME 2>/dev/null
            rm -f /etc/systemd/system/$SERVICE_FILE
            systemctl daemon-reload
            print_status 0 "Service uninstalled"
            ;;
        *)
            echo -e "${YELLOW}Usage: $0 {install|test|start|stop|restart|status|logs|uninstall}${NC}"
            echo ""
            echo "Commands:"
            echo "  install    - Install and start the service (requires sudo)"
            echo "  test       - Test the premarket system without installing"
            echo "  start      - Start the service (requires sudo)"
            echo "  stop       - Stop the service (requires sudo)"
            echo "  restart    - Restart the service (requires sudo)"
            echo "  status     - Show service status"
            echo "  logs       - Show recent logs"
            echo "  uninstall  - Remove the service (requires sudo)"
            ;;
    esac
}

main "$@" 