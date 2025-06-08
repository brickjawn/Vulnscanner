#!/bin/bash

# Professional Docker build script for VulnScanner
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
IMAGE_NAME="vulnscanner"
GUI_IMAGE_NAME="vulnscanner-gui"
VERSION="2.0"
REGISTRY=""  # Add your registry here if pushing to one

echo -e "${BLUE}╔══════════════════════════════════════════════════════════════════╗"
echo -e "║                    VulnScanner Docker Builder                   ║"
echo -e "╚══════════════════════════════════════════════════════════════════╝${NC}"

# Function to print status
print_status() {
    echo -e "${GREEN}[✓] $1${NC}"
}

print_info() {
    echo -e "${BLUE}[*] $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}[!] $1${NC}"
}

print_error() {
    echo -e "${RED}[✗] $1${NC}"
}

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker and try again."
    exit 1
fi

print_status "Docker is running"

# Build CLI version
print_info "Building CLI version..."
docker build \
    --target production \
    --tag ${IMAGE_NAME}:${VERSION} \
    --tag ${IMAGE_NAME}:latest \
    --file Dockerfile \
    --build-arg BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ') \
    --build-arg VERSION=${VERSION} \
    .

if [ $? -eq 0 ]; then
    print_status "CLI image built successfully"
else
    print_error "Failed to build CLI image"
    exit 1
fi

# Build GUI version
print_info "Building GUI version..."
docker build \
    --target gui \
    --tag ${GUI_IMAGE_NAME}:${VERSION} \
    --tag ${GUI_IMAGE_NAME}:latest \
    --file Dockerfile.gui \
    --build-arg BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ') \
    --build-arg VERSION=${VERSION} \
    .

if [ $? -eq 0 ]; then
    print_status "GUI image built successfully"
else
    print_error "Failed to build GUI image"
    exit 1
fi

# Show image sizes
print_info "Image sizes:"
docker images | grep -E "(vulnscanner|vulnscanner-gui)" | head -4

# Test the images
print_info "Testing CLI image..."
if docker run --rm ${IMAGE_NAME}:latest --help >/dev/null; then
    print_status "CLI image test passed"
else
    print_warning "CLI image test failed"
fi

# Security scan (if available)
if command -v trivy >/dev/null 2>&1; then
    print_info "Running security scan with Trivy..."
    trivy image ${IMAGE_NAME}:latest
else
    print_warning "Trivy not found. Consider installing it for security scanning."
fi

# Optional: Push to registry
if [ ! -z "$REGISTRY" ]; then
    read -p "Push images to registry? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_info "Pushing to registry..."
        
        # Tag for registry
        docker tag ${IMAGE_NAME}:latest ${REGISTRY}/${IMAGE_NAME}:${VERSION}
        docker tag ${IMAGE_NAME}:latest ${REGISTRY}/${IMAGE_NAME}:latest
        docker tag ${GUI_IMAGE_NAME}:latest ${REGISTRY}/${GUI_IMAGE_NAME}:${VERSION}
        docker tag ${GUI_IMAGE_NAME}:latest ${REGISTRY}/${GUI_IMAGE_NAME}:latest
        
        # Push
        docker push ${REGISTRY}/${IMAGE_NAME}:${VERSION}
        docker push ${REGISTRY}/${IMAGE_NAME}:latest
        docker push ${REGISTRY}/${GUI_IMAGE_NAME}:${VERSION}
        docker push ${REGISTRY}/${GUI_IMAGE_NAME}:latest
        
        print_status "Images pushed to registry"
    fi
fi

echo ""
print_status "Build completed successfully!"
echo ""
echo -e "${BLUE}Usage:${NC}"
echo -e "  CLI:  ${GREEN}docker run --rm vulnscanner:latest --url https://example.com${NC}"
echo -e "  GUI:  ${GREEN}docker-compose up vulnscanner-gui${NC}"
echo -e "  Compose: ${GREEN}docker-compose up${NC}"
echo "" 