#!/bin/bash

# Telegram Gift & Sticker Bot Deployment Script
# This script automates the setup and deployment process

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$PROJECT_DIR/venv"
PYTHON_VERSION="3.8"

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
    exit 1
}

info() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] INFO: $1${NC}"
}

# Check if running as root
check_root() {
    if [[ $EUID -eq 0 ]]; then
        error "This script should not be run as root. Please run as a regular user."
    fi
}

# Check Python version
check_python() {
    log "Checking Python version..."
    
    if ! command -v python3 &> /dev/null; then
        error "Python 3 is not installed. Please install Python 3.8 or higher."
    fi
    
    PYTHON_VERSION_ACTUAL=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    PYTHON_VERSION_MAJOR=$(echo $PYTHON_VERSION_ACTUAL | cut -d. -f1)
    PYTHON_VERSION_MINOR=$(echo $PYTHON_VERSION_ACTUAL | cut -d. -f2)
    
    if [[ $PYTHON_VERSION_MAJOR -lt 3 ]] || [[ $PYTHON_VERSION_MINOR -lt 8 ]]; then
        error "Python 3.8 or higher is required. Current version: $PYTHON_VERSION_ACTUAL"
    fi
    
    log "Python version $PYTHON_VERSION_ACTUAL is compatible"
}

# Create virtual environment
create_venv() {
    log "Creating virtual environment..."
    
    if [[ -d "$VENV_DIR" ]]; then
        warn "Virtual environment already exists. Removing old one..."
        rm -rf "$VENV_DIR"
    fi
    
    python3 -m venv "$VENV_DIR"
    log "Virtual environment created at $VENV_DIR"
}

# Activate virtual environment
activate_venv() {
    log "Activating virtual environment..."
    source "$VENV_DIR/bin/activate"
    
    if [[ "$VIRTUAL_ENV" != "$VENV_DIR" ]]; then
        error "Failed to activate virtual environment"
    fi
    
    log "Virtual environment activated"
}

# Install dependencies
install_dependencies() {
    log "Installing Python dependencies..."
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install requirements
    if [[ -f "$PROJECT_DIR/requirements.txt" ]]; then
        pip install -r "$PROJECT_DIR/requirements.txt"
        log "Dependencies installed successfully"
    else
        error "requirements.txt not found"
    fi
}

# Set up bot configuration
setup_config() {
    log "Setting up bot configuration..."
    
    # Check if bot_config.py exists
    if [[ ! -f "$PROJECT_DIR/bot_config.py" ]]; then
        error "bot_config.py not found. Please ensure the file exists."
    fi
    
    # Check if bot token is set
    if [[ -z "$TELEGRAM_BOT_TOKEN" ]]; then
        warn "TELEGRAM_BOT_TOKEN environment variable not set"
        info "Please set your bot token:"
        info "export TELEGRAM_BOT_TOKEN='your_bot_token_here'"
    else
        log "Bot token is configured"
    fi
}

# Make scripts executable
make_executable() {
    log "Making scripts executable..."
    
    chmod +x "$PROJECT_DIR/telegram_bot.py"
    chmod +x "$PROJECT_DIR/start_bot.py"
    chmod +x "$PROJECT_DIR/deploy.sh"
    
    log "Scripts made executable"
}

# Test installation
test_installation() {
    log "Testing installation..."
    
    # Test Python imports
    python3 -c "
import telegram
import PIL
import matplotlib
import numpy
import requests
import httpx
print('All required packages imported successfully')
" || error "Failed to import required packages"
    
    log "Installation test passed"
}

# Set up systemd service (optional)
setup_systemd() {
    if [[ "$1" == "--systemd" ]]; then
        log "Setting up systemd service..."
        
        # Check if running as root for systemd setup
        if [[ $EUID -ne 0 ]]; then
            warn "Systemd service setup requires root privileges"
            info "To set up systemd service, run: sudo $0 --systemd"
            return
        fi
        
        # Copy service file
        cp "$PROJECT_DIR/telegram-bot.service" /etc/systemd/system/
        
        # Reload systemd
        systemctl daemon-reload
        
        # Enable service
        systemctl enable telegram-bot.service
        
        log "Systemd service installed and enabled"
        info "To start the service: sudo systemctl start telegram-bot"
        info "To check status: sudo systemctl status telegram-bot"
    fi
}

# Create startup script
create_startup_script() {
    log "Creating startup script..."
    
    cat > "$PROJECT_DIR/run_bot.sh" << 'EOF'
#!/bin/bash

# Telegram Bot Startup Script
cd "$(dirname "$0")"

# Activate virtual environment
source venv/bin/activate

# Start the bot
python start_bot.py
EOF
    
    chmod +x "$PROJECT_DIR/run_bot.sh"
    log "Startup script created: run_bot.sh"
}

# Main deployment function
main() {
    log "Starting Telegram Gift & Sticker Bot deployment..."
    
    # Check prerequisites
    check_root
    check_python
    
    # Create and activate virtual environment
    create_venv
    activate_venv
    
    # Install dependencies
    install_dependencies
    
    # Setup configuration
    setup_config
    
    # Make scripts executable
    make_executable
    
    # Test installation
    test_installation
    
    # Create startup script
    create_startup_script
    
    # Setup systemd if requested
    setup_systemd "$1"
    
    log "Deployment completed successfully!"
    echo
    info "Next steps:"
    info "1. Set your bot token: export TELEGRAM_BOT_TOKEN='your_token'"
    info "2. Start the bot: ./run_bot.sh"
    info "3. Or use the startup script: python start_bot.py"
    echo
    info "For systemd service setup, run: sudo $0 --systemd"
}

# Show help
show_help() {
    echo "Telegram Gift & Sticker Bot Deployment Script"
    echo
    echo "Usage: $0 [OPTIONS]"
    echo
    echo "Options:"
    echo "  --systemd    Set up systemd service (requires root)"
    echo "  --help       Show this help message"
    echo
    echo "Examples:"
    echo "  $0                    # Basic deployment"
    echo "  sudo $0 --systemd     # Deploy with systemd service"
}

# Parse command line arguments
case "${1:-}" in
    --help|-h)
        show_help
        exit 0
        ;;
    --systemd)
        main "$1"
        ;;
    "")
        main
        ;;
    *)
        error "Unknown option: $1"
        show_help
        exit 1
        ;;
esac 