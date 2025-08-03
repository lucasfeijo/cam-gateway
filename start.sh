#!/bin/bash

# CAM Gateway Startup Script
# This script helps deploy and manage the CAM Gateway application

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
COMPOSE_FILE="docker-compose.yml"
DATA_DIR="data"

# Functions
print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}    CAM Gateway Manager${NC}"
    echo -e "${BLUE}================================${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    print_success "Docker and Docker Compose are available"
}

create_data_dir() {
    if [ ! -d "$DATA_DIR" ]; then
        print_info "Creating data directory..."
        mkdir -p "$DATA_DIR"
        print_success "Data directory created"
    else
        print_info "Data directory already exists"
    fi
}

build_and_start() {
    print_info "Building and starting CAM Gateway..."
    docker-compose -f "$COMPOSE_FILE" up -d --build
    print_success "CAM Gateway started successfully"
}

stop_service() {
    print_info "Stopping CAM Gateway..."
    docker-compose -f "$COMPOSE_FILE" down
    print_success "CAM Gateway stopped"
}

restart_service() {
    print_info "Restarting CAM Gateway..."
    docker-compose -f "$COMPOSE_FILE" restart
    print_success "CAM Gateway restarted"
}

show_logs() {
    print_info "Showing CAM Gateway logs..."
    docker-compose -f "$COMPOSE_FILE" logs -f cam-gateway
}

show_status() {
    print_info "CAM Gateway Status:"
    docker-compose -f "$COMPOSE_FILE" ps
    
    echo ""
    print_info "Container logs (last 10 lines):"
    docker-compose -f "$COMPOSE_FILE" logs --tail=10 cam-gateway
}

test_application() {
    print_info "Testing CAM Gateway application..."
    
    # Wait for application to start
    sleep 5
    
    # Test health endpoint
    if curl -s http://localhost:8000/health > /dev/null; then
        print_success "Health check passed"
    else
        print_error "Health check failed"
        return 1
    fi
    
    # Test API docs
    if curl -s http://localhost:8000/api/docs > /dev/null; then
        print_success "API documentation accessible"
    else
        print_error "API documentation not accessible"
        return 1
    fi
    
    print_success "Application tests passed"
}

show_help() {
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  start     - Build and start CAM Gateway"
    echo "  stop      - Stop CAM Gateway"
    echo "  restart   - Restart CAM Gateway"
    echo "  logs      - Show application logs"
    echo "  status    - Show application status"
    echo "  test      - Test application functionality"
    echo "  help      - Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 start    # Start the application"
    echo "  $0 logs     # View logs"
    echo "  $0 status   # Check status"
}

# Main script
main() {
    print_header
    
    # Check if command is provided
    if [ $# -eq 0 ]; then
        show_help
        exit 1
    fi
    
    # Check Docker availability
    check_docker
    
    # Create data directory
    create_data_dir
    
    # Handle commands
    case "$1" in
        start)
            build_and_start
            test_application
            print_info "CAM Gateway is now running at http://localhost:8000"
            ;;
        stop)
            stop_service
            ;;
        restart)
            restart_service
            test_application
            ;;
        logs)
            show_logs
            ;;
        status)
            show_status
            ;;
        test)
            test_application
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            print_error "Unknown command: $1"
            show_help
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@" 