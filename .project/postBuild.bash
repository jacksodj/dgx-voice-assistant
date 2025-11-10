#!/bin/bash
# NVIDIA AI Workbench Post-Build Script
# This script runs after the environment is built

set -e

echo "===== Post-Build Setup for DGX Voice Assistant ====="

# Create necessary directories
echo "Creating data directories..."
mkdir -p data
chmod 755 data

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cat > .env << 'EOF'
# Hugging Face token (optional, for gated models)
HF_TOKEN=

# Brave Search API key (optional, for internet search)
# Get free key at: https://brave.com/search/api
BRAVE_API_KEY=

# vLLM Configuration
VLLM_API_URL=http://vllm:8000
ENABLE_SEARCH=true
GPU_MEMORY_UTILIZATION=0.85

# Auto-generated session secret
SESSION_SECRET=$(openssl rand -hex 32)
EOF
    echo ".env file created. Please edit it to add your API keys."
else
    echo ".env file already exists, skipping..."
fi

# Set executable permissions on start script
if [ -f start-simple.sh ]; then
    chmod +x start-simple.sh
    echo "Made start-simple.sh executable"
fi

# Pull Docker images in advance to speed up first run
echo "Pre-pulling Docker images (this may take a while)..."
docker pull vllm/vllm-openai:latest || echo "Warning: Could not pull vLLM image"
docker pull ghcr.io/open-webui/open-webui:main || echo "Warning: Could not pull Open WebUI image"

echo "===== Post-Build Setup Complete ====="
echo ""
echo "Next steps:"
echo "1. Edit .env file to add your API keys (optional)"
echo "2. Run: ./start-simple.sh"
echo "3. Access Web UI at: http://localhost:3000"
echo ""
