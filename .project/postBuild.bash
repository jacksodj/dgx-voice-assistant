#!/bin/bash
# NVIDIA AI Workbench Post-Build Script
# This script runs after the environment is built

set -e

echo "===== DGX Voice Assistant Post-Build Setup ====="

# Ensure docker and docker-compose are available
echo "Checking Docker installation..."
if ! command -v docker &> /dev/null; then
    echo "Installing Docker..."
    sudo apt-get update
    sudo apt-get install -y docker.io docker-compose
else
    echo "✓ Docker is installed"
fi

if ! command -v docker-compose &> /dev/null; then
    echo "Installing docker-compose..."
    sudo apt-get install -y docker-compose
else
    echo "✓ docker-compose is installed"
fi

# Ensure user can run docker without sudo
echo "Configuring Docker permissions..."
sudo usermod -aG docker $USER || true

# Create necessary directories
echo "Creating project directories..."
mkdir -p /project/data
mkdir -p /project/code
chmod 755 /project/data /project/code

# Create .env file if it doesn't exist
if [ ! -f /project/.env ]; then
    echo "Creating .env file from template..."
    cat > /project/.env << 'EOF'
# Hugging Face token (optional, for gated models)
# Get token at: https://huggingface.co/settings/tokens
HF_TOKEN=

# Brave Search API key (optional, for internet search)
# Get free key at: https://brave.com/search/api
BRAVE_API_KEY=

# vLLM Configuration
VLLM_API_URL=http://vllm:8000
ENABLE_SEARCH=true
GPU_MEMORY_UTILIZATION=0.85

# Auto-generated session secret
SESSION_SECRET=$(openssl rand -hex 32 2>/dev/null || echo "change-this-to-a-random-secret")
EOF
    echo "✓ .env file created"
    echo "  Edit /project/.env to add your API keys"
else
    echo "✓ .env file already exists"
fi

# Set executable permissions on start script
if [ -f /project/start-simple.sh ]; then
    chmod +x /project/start-simple.sh
    echo "✓ Made start-simple.sh executable"
fi

# Pre-pull Docker images to speed up first run
echo ""
echo "Pre-pulling Docker images (this may take several minutes)..."
echo "You can skip this by pressing Ctrl+C"
sleep 2

docker pull vllm/vllm-openai:latest 2>/dev/null || echo "⚠ Could not pull vLLM image (will pull on first run)"
docker pull ghcr.io/open-webui/open-webui:main 2>/dev/null || echo "⚠ Could not pull Open WebUI image (will pull on first run)"

echo ""
echo "===== Post-Build Setup Complete ====="
echo ""
echo "Next steps:"
echo "1. Configure API keys in /project/.env (optional)"
echo "2. Start the Voice Assistant from the Applications tab in AI Workbench"
echo "   - 'Voice Assistant Web UI' will auto-launch on port 3000"
echo "   - 'vLLM API Server' provides OpenAI-compatible API on port 8000"
echo "   - 'Backend API' provides search/storage on port 8080"
echo ""
echo "Or run manually:"
echo "  cd /project && docker-compose -f docker-compose.complete.yml up -d"
echo ""
