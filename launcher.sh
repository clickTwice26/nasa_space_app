#!/bin/bash
# NASA Space App Quick Launcher
# Simple wrapper script for common operations

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MANAGE_SCRIPT="$SCRIPT_DIR/manage.py"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_header() {
    echo -e "${BLUE}🚀 NASA Space App Launcher${NC}"
    echo -e "${BLUE}=============================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ️  $1${NC}"
}

# Check if Python is available
check_python() {
    if command -v python3 &> /dev/null; then
        return 0
    elif command -v python &> /dev/null; then
        return 0
    else
        print_error "Python is not installed or not in PATH"
        return 1
    fi
}

# Get Python command
get_python_cmd() {
    if command -v python3 &> /dev/null; then
        echo "python3"
    else
        echo "python"
    fi
}

# Main menu
show_menu() {
    print_header
    echo "Select an option:"
    echo "1) 📊 Check Project Status"
    echo "2) 🏗️  Complete Project Setup"
    echo "3) 🌐 Start Flask Web Server"
    echo "4) 🧪 Initialize Flask Database"
    echo "5) 📓 Start Jupyter Notebook (ML)"
    echo "6) 📂 Validate Dataset Structure"
    echo "7) 🧹 Clean Project Files"
    echo "8) 📖 Show Help"
    echo "9) 🚪 Exit"
    echo ""
    read -p "Enter your choice [1-9]: " choice
}

# Execute commands
execute_command() {
    local python_cmd=$(get_python_cmd)
    
    case $choice in
        1)
            print_info "Checking project status..."
            $python_cmd "$MANAGE_SCRIPT" status
            ;;
        2)
            print_info "Setting up complete project..."
            $python_cmd "$MANAGE_SCRIPT" setup
            ;;
        3)
            print_info "Starting Flask web server..."
            print_info "Server will start on http://localhost:6767"
            print_info "Press Ctrl+C to stop the server"
            $python_cmd "$MANAGE_SCRIPT" flask run
            ;;
        4)
            print_info "Initializing Flask database..."
            $python_cmd "$MANAGE_SCRIPT" flask init-db
            ;;
        5)
            print_info "Starting Jupyter Notebook..."
            $python_cmd "$MANAGE_SCRIPT" ml jupyter
            ;;
        6)
            print_info "Validating dataset structure..."
            $python_cmd "$MANAGE_SCRIPT" dataset validate
            $python_cmd "$MANAGE_SCRIPT" dataset catalog
            ;;
        7)
            print_info "Cleaning project files..."
            $python_cmd "$MANAGE_SCRIPT" clean
            ;;
        8)
            print_info "Available commands:"
            $python_cmd "$MANAGE_SCRIPT" --help
            echo ""
            print_info "Flask commands:"
            $python_cmd "$MANAGE_SCRIPT" flask --help
            echo ""
            print_info "ML commands:"
            $python_cmd "$MANAGE_SCRIPT" ml --help
            echo ""
            print_info "Dataset commands:"
            $python_cmd "$MANAGE_SCRIPT" dataset --help
            ;;
        9)
            print_success "Goodbye! 🚀"
            exit 0
            ;;
        *)
            print_error "Invalid option. Please try again."
            ;;
    esac
}

# Main execution
main() {
    # Check if manage.py exists
    if [[ ! -f "$MANAGE_SCRIPT" ]]; then
        print_error "Management script not found: $MANAGE_SCRIPT"
        exit 1
    fi
    
    # Check Python availability
    if ! check_python; then
        exit 1
    fi
    
    # Run interactive menu
    while true; do
        show_menu
        execute_command
        echo ""
        read -p "Press Enter to continue..."
        clear
    done
}

# Handle command line arguments
if [[ $# -eq 0 ]]; then
    # No arguments, show interactive menu
    clear
    main
else
    # Arguments provided, run management script directly
    python_cmd=$(get_python_cmd)
    $python_cmd "$MANAGE_SCRIPT" "$@"
fi