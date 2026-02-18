#!/bin/bash

# n8n SEO Writer Workflow - Initialization Script
# This script sets up the development environment for the n8n workflow automation

set -e

echo "============================================"
echo "n8n SEO Writer Workflow - Environment Setup"
echo "============================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check for required tools
check_requirement() {
    if command -v $1 &> /dev/null; then
        echo -e "${GREEN}[OK]${NC} $1 is installed"
        return 0
    else
        echo -e "${RED}[MISSING]${NC} $1 is not installed"
        return 1
    fi
}

echo "Checking prerequisites..."
echo ""

MISSING_DEPS=0

# Check Docker
check_requirement "docker" || MISSING_DEPS=1

# Check Docker Compose
if command -v "docker-compose" &> /dev/null || docker compose version &> /dev/null; then
    echo -e "${GREEN}[OK]${NC} docker-compose is available"
else
    echo -e "${RED}[MISSING]${NC} docker-compose is not available"
    MISSING_DEPS=1
fi

# Check Ollama
check_requirement "ollama" || {
    echo -e "${YELLOW}[WARNING]${NC} Ollama not found. Install from https://ollama.ai"
    MISSING_DEPS=1
}

echo ""

if [ $MISSING_DEPS -eq 1 ]; then
    echo -e "${YELLOW}Some dependencies are missing. Please install them before proceeding.${NC}"
    echo ""
fi

# Create necessary directories
echo "Creating project directories..."
mkdir -p n8n-data
mkdir -p comfyui-output
mkdir -p workflow-exports

# Create docker-compose.yml for n8n if it doesn't exist
if [ ! -f "docker-compose.yml" ]; then
    echo "Creating docker-compose.yml..."
    cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  n8n:
    image: n8nio/n8n:latest
    container_name: n8n-seo-writer
    restart: unless-stopped
    ports:
      - "5680:5678"
    environment:
      - N8N_HOST=localhost
      - N8N_PORT=5678
      - N8N_PROTOCOL=http
      - WEBHOOK_URL=http://localhost:5680/
      - GENERIC_TIMEZONE=Europe/Berlin
      - TZ=Europe/Berlin
      # Enable execution data pruning for performance
      - EXECUTIONS_DATA_PRUNE=true
      - EXECUTIONS_DATA_MAX_AGE=168
    volumes:
      - ./n8n-data:/home/node/.n8n
    networks:
      - seo-writer-network

networks:
  seo-writer-network:
    driver: bridge
EOF
    echo -e "${GREEN}[OK]${NC} docker-compose.yml created"
else
    echo -e "${GREEN}[OK]${NC} docker-compose.yml already exists"
fi

# Create environment template if it doesn't exist
if [ ! -f ".env.example" ]; then
    echo "Creating .env.example..."
    cat > .env.example << 'EOF'
# n8n Configuration
N8N_HOST=localhost
N8N_PORT=5678
N8N_PROTOCOL=http

# Ollama Configuration
OLLAMA_HOST=http://host.docker.internal:11434
OLLAMA_MODEL=llama3

# ComfyUI / Flux Configuration
COMFYUI_HOST=http://host.docker.internal:8188

# Google Sheets Configuration (OAuth2 or Service Account)
GOOGLE_CLIENT_ID=your-client-id
GOOGLE_CLIENT_SECRET=your-client-secret
GOOGLE_SHEET_ID=your-sheet-id

# WordPress Configuration
WORDPRESS_URL=https://your-wordpress-site.com
WORDPRESS_USERNAME=your-username
WORDPRESS_APP_PASSWORD=your-app-password

# SMTP Configuration (for failure notifications)
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=your-email@example.com
SMTP_PASSWORD=your-password
SMTP_FROM=notifications@example.com
SMTP_TO=admin@example.com
EOF
    echo -e "${GREEN}[OK]${NC} .env.example created"
else
    echo -e "${GREEN}[OK]${NC} .env.example already exists"
fi

# Copy .env.example to .env if .env doesn't exist
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo -e "${YELLOW}[INFO]${NC} Created .env from .env.example - please update with your credentials"
fi

echo ""
echo "Starting n8n Docker container..."

# Start n8n container
docker compose up -d

# Wait for n8n to be ready
echo "Waiting for n8n to start..."
max_attempts=30
attempt=0
while [ $attempt -lt $max_attempts ]; do
    if curl -s http://localhost:5680/healthz > /dev/null 2>&1; then
        echo -e "${GREEN}[OK]${NC} n8n is running"
        break
    fi
    attempt=$((attempt + 1))
    sleep 2
done

if [ $attempt -eq $max_attempts ]; then
    echo -e "${YELLOW}[WARNING]${NC} n8n may not be fully ready yet. Check logs with: docker compose logs -f"
fi

# Check Ollama status
echo ""
echo "Checking Ollama status..."
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo -e "${GREEN}[OK]${NC} Ollama is running"

    # List available models
    echo ""
    echo "Available Ollama models:"
    ollama list 2>/dev/null || curl -s http://localhost:11434/api/tags | grep -o '"name":"[^"]*"' | cut -d'"' -f4
else
    echo -e "${YELLOW}[WARNING]${NC} Ollama is not running. Start it with: ollama serve"
    echo "Recommended models: llama3, mistral"
    echo "Install a model with: ollama pull llama3"
fi

echo ""
echo "============================================"
echo "Environment Setup Complete!"
echo "============================================"
echo ""
echo "Access Points:"
echo "  - n8n:     http://localhost:5680"
echo "  - Ollama:  http://localhost:11434 (if running)"
echo "  - ComfyUI: http://localhost:8188 (if running)"
echo ""
echo "Next Steps:"
echo "  1. Update .env with your credentials"
echo "  2. Open n8n at http://localhost:5680"
echo "  3. Import the workflow from workflow-exports/"
echo "  4. Configure credentials in n8n for:"
echo "     - Google Sheets (OAuth2 or Service Account)"
echo "     - WordPress (Application Password)"
echo "     - SMTP (for notifications)"
echo "  5. Create Google Sheet with required columns"
echo "  6. Set up Google Apps Script for Approve button"
echo ""
echo "For troubleshooting:"
echo "  - View n8n logs: docker compose logs -f n8n"
echo "  - Stop n8n: docker compose down"
echo "  - Restart n8n: docker compose restart"
echo ""
