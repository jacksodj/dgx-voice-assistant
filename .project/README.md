# NVIDIA AI Workbench Configuration

This directory contains the NVIDIA AI Workbench project configuration for the DGX Voice Assistant.

## Files

- **spec.yaml** - Main project specification file defining the environment, applications, and resources
- **postBuild.bash** - Post-build script that runs after environment setup
- **README.md** - This file

## Using with AI Workbench

### Initial Setup

1. Open NVIDIA AI Workbench
2. Click "Clone Project" or "Import Project"
3. Enter the repository URL or select the local directory
4. AI Workbench will automatically detect the `.project/spec.yaml` file
5. Click "Build" to set up the environment

### Configuration

The project is configured to run as a multi-container application using Docker Compose. The following services are defined:

- **vllm** - vLLM inference server running Qwen3-Omni-30B
- **backend** - Enhanced backend with search and storage
- **webui** - Open WebUI for user interaction

### Environment Variables

You can configure environment variables in AI Workbench through:

1. The UI: Settings → Environment → Variables
2. Or by editing the `.env` file directly

Required/Optional variables:

- `HF_TOKEN` (optional) - For accessing gated models
- `BRAVE_API_KEY` (optional) - For internet search
- `GPU_MEMORY_UTILIZATION` - Adjust GPU memory usage (default: 0.85)

### Multi-Container Application

This project uses docker-compose to run multiple services:

1. **vLLM** - Qwen3-Omni model inference server (port 8000)
2. **Backend** - Enhanced API with search and storage (port 8080)
3. **Web UI** - Open WebUI for chat interface (port 3000)

Start/stop these services through: **Environment → Compose** in AI Workbench.

### Applications (Endpoints)

The Applications tab shows endpoints to access the running services:

1. **Voice Assistant Web UI** (port 3000) - Main user interface with voice support
2. **vLLM API Server** (port 8000) - OpenAI-compatible API endpoint
3. **Backend API** (port 8080) - Search and storage API

These are just endpoint links - you must start the services via Environment → Compose first.

### Resource Requirements

- **GPU**: 1x NVIDIA GPU with 16GB+ VRAM
- **System RAM**: ~6GB
- **Disk Space**: ~32GB (model + data)
- **CUDA**: 12.2 or newer recommended

### Starting the Project

**Using AI Workbench (Recommended):**

1. Ensure the environment is built
2. Go to **Environment → Compose**
3. Click **Start** to launch all services (vLLM, Backend, Web UI)
4. Go to **Applications** tab to access the service endpoints
5. Click on "Voice Assistant Web UI" to open the interface

**From Command Line:**

```bash
# From Workbench terminal or local machine
cd /project
docker-compose -f docker-compose.complete.yml up -d

# Or use the start script
./start-simple.sh
```

**Important:** The multi-container application is managed through AI Workbench's Compose feature. The Applications tab shows endpoints to the running services, but you must start/stop the services through Environment → Compose.

### Customization

#### Changing Models

Edit `docker-compose.complete.yml` to use a different model:

```yaml
services:
  vllm:
    command: >
      --model your/custom-model
      --quantization awq
      --trust-remote-code
```

#### Adjusting GPU Memory

Edit the `.env` file or environment variable:

```bash
GPU_MEMORY_UTILIZATION=0.75  # Use 75% instead of 85%
```

#### Adding Custom Services

Edit `docker-compose.complete.yml` and add your service, then update `spec.yaml`:

```yaml
environment:
  compose:
    services:
      - vllm
      - backend
      - webui
      - your-custom-service
```

### Troubleshooting

#### Environment Won't Build

- Check Docker daemon is running
- Ensure NVIDIA Container Runtime is installed
- Check GPU drivers are up to date

#### Services Won't Start

```bash
# Check service logs
docker-compose logs vllm
docker-compose logs backend
docker-compose logs webui

# Restart services
docker-compose restart
```

#### Out of GPU Memory

Reduce GPU memory utilization:

```bash
# In .env file
GPU_MEMORY_UTILIZATION=0.70
```

Or use a smaller quantization in the vLLM command.

### Data Persistence

Data is persisted in the `data/` directory:

- Conversation history
- Notes and context
- SQLite database

This directory is mapped to `gitignore` storage in the spec, so it won't be committed to version control but will persist between environment restarts.

## Support

For issues specific to AI Workbench:
- [NVIDIA AI Workbench Documentation](https://docs.nvidia.com/ai-workbench/)
- [AI Workbench Forums](https://forums.developer.nvidia.com/c/ai-workbench/)

For project-specific issues:
- See main [README.md](../README.md)
- Check [QUICK-START.md](../QUICK-START.md)
