#!/bin/bash

# Professional Docker run script for VulnScanner
set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

IMAGE_NAME="vulnscanner:latest"
CONTAINER_NAME="vulnscanner-run"

print_usage() {
    echo "VulnScanner Docker Runner"
    echo ""
    echo "Usage: $0 [OPTIONS] COMMAND"
    echo ""
    echo "Commands:"
    echo "  scan      Run a vulnerability scan"
    echo "  gui       Start GUI with VNC access"
    echo "  shell     Interactive shell in container"
    echo "  build     Build Docker images"
    echo "  clean     Clean up containers and images"
    echo "  logs      Show container logs"
    echo ""
    echo "Options:"
    echo "  -u, --url URL          Target URL to scan"
    echo "  -t, --threads N        Number of threads (default: 5)"
    echo "  -p, --pages N          Max pages to crawl (default: 10)"
    echo "  -o, --output FORMAT    Output format (cli/json/csv)"
    echo "  --enable-portscan      Enable port scanning"
    echo "  -h, --help            Show this help"
    echo ""
    echo "Examples:"
    echo "  $0 scan -u https://example.com"
    echo "  $0 scan -u https://target.com -t 10 --enable-portscan -o json"
    echo "  $0 gui"
    echo "  $0 shell"
}

print_info() {
    echo -e "${BLUE}[*] $1${NC}"
}

print_success() {
    echo -e "${GREEN}[✓] $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}[!] $1${NC}"
}

print_error() {
    echo -e "${RED}[✗] $1${NC}"
}

# Ensure reports directory exists
mkdir -p reports logs

case "$1" in
    scan)
        shift
        SCAN_ARGS=""
        
        # Parse arguments
        while [[ $# -gt 0 ]]; do
            case $1 in
                -u|--url)
                    URL="$2"
                    SCAN_ARGS="$SCAN_ARGS --url $2"
                    shift 2
                    ;;
                -t|--threads)
                    SCAN_ARGS="$SCAN_ARGS --threads $2"
                    shift 2
                    ;;
                -p|--pages)
                    SCAN_ARGS="$SCAN_ARGS --max-pages $2"
                    shift 2
                    ;;
                -o|--output)
                    SCAN_ARGS="$SCAN_ARGS --output $2"
                    shift 2
                    ;;
                --enable-portscan)
                    SCAN_ARGS="$SCAN_ARGS --enable-portscan"
                    shift
                    ;;
                *)
                    SCAN_ARGS="$SCAN_ARGS $1"
                    shift
                    ;;
            esac
        done
        
        if [ -z "$URL" ]; then
            print_error "URL is required for scanning"
            print_usage
            exit 1
        fi
        
        print_info "Starting vulnerability scan..."
        print_info "Target: $URL"
        
        docker run --rm \
            --name "$CONTAINER_NAME" \
            -v "$(pwd)/reports:/app/reports" \
            -v "$(pwd)/logs:/app/logs" \
            --network host \
            "$IMAGE_NAME" $SCAN_ARGS
        
        print_success "Scan completed! Check reports/ directory for results."
        ;;
        
    gui)
        print_info "Starting GUI with VNC access..."
        docker-compose up -d vulnscanner-gui
        
        sleep 3
        print_success "GUI is running!"
        echo ""
        echo -e "${BLUE}Access methods:${NC}"
        echo -e "  VNC Client: ${GREEN}localhost:5900${NC} (password: vulnscan123)"
        echo -e "  Web Browser: ${GREEN}http://localhost:6080/vnc.html${NC}"
        echo ""
        echo -e "To stop: ${YELLOW}docker-compose down${NC}"
        ;;
        
    shell)
        print_info "Starting interactive shell..."
        docker run --rm -it \
            --name "$CONTAINER_NAME-shell" \
            -v "$(pwd)/reports:/app/reports" \
            -v "$(pwd)/logs:/app/logs" \
            --network host \
            --entrypoint /bin/sh \
            "$IMAGE_NAME"
        ;;
        
    build)
        print_info "Building Docker images..."
        chmod +x docker/build.sh
        ./docker/build.sh
        ;;
        
    clean)
        print_info "Cleaning up Docker containers and images..."
        
        # Stop and remove containers
        docker-compose down 2>/dev/null || true
        docker container prune -f
        
        # Remove images
        docker rmi vulnscanner:latest vulnscanner-gui:latest 2>/dev/null || true
        docker image prune -f
        
        print_success "Cleanup completed"
        ;;
        
    logs)
        SERVICE=${2:-vulnscanner}
        print_info "Showing logs for $SERVICE..."
        docker-compose logs -f "$SERVICE"
        ;;
        
    -h|--help|help)
        print_usage
        ;;
        
    *)
        print_error "Unknown command: $1"
        print_usage
        exit 1
        ;;
esac 