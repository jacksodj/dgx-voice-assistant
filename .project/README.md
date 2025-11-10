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

### Applications

The spec.yaml defines three applications accessible from the AI Workbench UI:

1. **Web UI** (port 3000) - Main user interface with voice support
2. **vLLM API** (port 8000) - OpenAI-compatible API endpoint
3. **Backend API** (port 8080) - Search and storage API

### Resource Requirements

- **GPU**: 1x NVIDIA GPU with 16GB+ VRAM
- **System RAM**: ~6GB
- **Disk Space**: ~32GB (model + data)
- **CUDA**: 12.2 or newer recommended

### Starting the Project

From AI Workbench:

1. Ensure the environment is built
2. Click "Start Environment"
3. Access applications from the Applications tab
4. The Web UI will auto-launch in your browser

From Command Line (within Workbench terminal):

```bash
# Start all services
./start-simple.sh

# Or use docker-compose directly
docker-compose -f docker-compose.complete.yml up -d
```

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
