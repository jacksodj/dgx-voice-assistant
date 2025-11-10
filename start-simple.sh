#!/bin/bash
# Simplified Qwen3-Omni Startup for DGX Spark

set -e

echo "🚀 Starting Qwen3-Omni Voice Assistant"
echo ""

# Check GPU
if ! nvidia-smi &> /dev/null; then
    echo "❌ NVIDIA GPU not detected!"
    exit 1
fi
echo "✓ GPU detected: $(nvidia-smi --query-gpu=name --format=csv,noheader)"

# Check Docker
if ! docker --version &> /dev/null; then
    echo "❌ Docker not installed!"
    exit 1
fi
echo "✓ Docker installed"

# Setup NVIDIA Container Toolkit if needed
if ! docker run --rm --gpus all nvidia/cuda:12.3.0-base-ubuntu22.04 nvidia-smi &> /dev/null 2>&1; then
    echo "⚙️  Installing NVIDIA Container Toolkit..."
    
    distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
    curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
    curl -s -L https://nvidia.github.io/libnvidia-container/$distribution/libnvidia-container.list | \
        sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
        sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
    
    sudo apt-get update
    sudo apt-get install -y nvidia-container-toolkit
    sudo nvidia-ctk runtime configure --runtime=docker
    sudo systemctl restart docker
    
    echo "✓ NVIDIA Container Toolkit installed"
fi

# Create .env if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cat > .env <<EOF
# Hugging Face token (optional, for private models)
HF_TOKEN=

# Brave Search API key (optional, for internet search)
# Get free key at: https://brave.com/search/api
BRAVE_API_KEY=

# Session secret
SESSION_SECRET=$(openssl rand -hex 32)
EOF
    echo "✓ Created .env file (edit it to add API keys)"
fi

# Create data directory
mkdir -p data

# Pull images in parallel
echo "📦 Pulling Docker images (first time may take a few minutes)..."
docker-compose -f docker-compose.complete.yml pull &
wait

# Start services
echo "🚀 Starting services..."
docker-compose -f docker-compose.complete.yml up -d

# Wait for vLLM
echo "⏳ Waiting for model to load (2-3 minutes)..."
until curl -sf http://localhost:8000/health &> /dev/null; do
    echo -n "."
    sleep 5
done
echo ""
echo "✓ Model loaded!"

# Get IP
LOCAL_IP=$(hostname -I | awk '{print $1}')

echo ""
echo "╔════════════════════════════════════════════════════════╗"
echo "║           🎉 ALL SYSTEMS OPERATIONAL! 🎉              ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""
echo "Access your assistant:"
echo "  🌐 Web UI (Local):    http://localhost:3000"
echo "  🌐 Web UI (Network):  http://${LOCAL_IP}:3000"
echo "  🔧 API Endpoint:      http://${LOCAL_IP}:8000"
echo "  📚 API Docs:          http://${LOCAL_IP}:8000/docs"
echo ""
echo "Features:"
echo "  ✓ Voice input/output"
echo "  ✓ Document upload"
echo "  ✓ Image/video understanding"
echo "  ✓ Mobile responsive"
echo "  ✓ Chat history (persistent)"
if [ -n "$BRAVE_API_KEY" ]; then
    echo "  ✓ Internet search (enabled)"
else
    echo "  ⚠ Internet search (add BRAVE_API_KEY to .env to enable)"
fi
echo ""
echo "Useful commands:"
echo "  View logs:    docker-compose logs -f"
echo "  Stop:         docker-compose down"
echo "  Restart:      docker-compose restart"
echo ""
