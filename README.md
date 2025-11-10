# Qwen3-Omni Voice Assistant

A production-ready voice assistant powered by Qwen3-Omni-30B, optimized for NVIDIA DGX systems and AI Workbench. Features include web-based UI, internet search capabilities, and persistent storage.

## Features

- **Voice Interaction**: Full voice input/output support through Open WebUI
- **Internet Search**: Real-time web search via Brave API
- **Website Browsing**: Fetch and parse web content
- **Persistent Storage**: SQLite-based conversation history and notes
- **Mobile Responsive**: Access from any device
- **GPU Optimized**: AWQ 4-bit quantization for efficient memory usage (~15-18GB)
- **Easy Deployment**: Pre-built containers, one-command setup
- **Model**: Qwen3-Omni-30B (AWQ quantized) - multimodal LLM with vision and audio

## Quick Start

### Prerequisites

- NVIDIA GPU with 16GB+ VRAM
- Docker with NVIDIA Container Runtime
- 30GB+ disk space for model

### Basic Setup

```bash
# Clone repository
git clone <repository-url>
cd dgx-voice-assistant

# (Optional) Configure environment
cp .env.example .env
# Edit .env to add API keys if needed

# Start all services
chmod +x start-simple.sh
./start-simple.sh
```

### Access Points

- **Web UI**: http://localhost:3000
- **vLLM API**: http://localhost:8000
- **Backend API**: http://localhost:8080

## Deployment Options

### Complete Setup (Recommended)

All features including UI, search, and storage:

```bash
docker-compose -f docker-compose.complete.yml up -d
```

### Simple Setup

Model and basic backend only:

```bash
docker-compose -f docker-compose.simple.yml up -d
```

### Minimal Setup

Just the vLLM model server:

```bash
docker-compose -f docker-compose.minimal.yml up -d
```

## Configuration

### Environment Variables

Create a `.env` file:

```bash
# Optional: For gated Hugging Face models
HF_TOKEN=your_huggingface_token

# Optional: For internet search (get free at brave.com/search/api)
BRAVE_API_KEY=your_brave_api_key

# Auto-generated
SESSION_SECRET=random_secret_here
```

### Resource Requirements

| Component | GPU Memory | System RAM | Disk Space |
|-----------|-----------|-----------|------------|
| vLLM Model | 15-18GB | 4-6GB | ~30GB |
| Backend | - | 512MB | Minimal |
| Web UI | - | 512MB | ~1GB |
| **Total** | **15-18GB** | **~6GB** | **~32GB** |

## Architecture

```
┌─────────────┐
│   Web UI    │ :3000
│ (Open WebUI)│
└──────┬──────┘
       │
┌──────▼──────┐     ┌──────────────┐
│   Backend   │────▶│ Internet/Web │
│   :8080     │     │   Search     │
└──────┬──────┘     └──────────────┘
       │
┌──────▼──────┐     ┌──────────────┐
│    vLLM     │────▶│   SQLite     │
│   :8000     │     │   Database   │
└─────────────┘     └──────────────┘
```

## API Usage

### Chat Completion

```python
import openai

client = openai.OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="sk-dummy"
)

response = client.chat.completions.create(
    model="Qwen/Qwen3-Omni-30B-A3B-Instruct",
    messages=[
        {"role": "user", "content": "Hello!"}
    ]
)

print(response.choices[0].message.content)
```

### Search & Browse (via Backend)

```bash
# Search the internet
curl -X POST http://localhost:8080/api/v1/search \
  -H "Content-Type: application/json" \
  -d '{"query": "latest AI news"}'

# Fetch web content
curl -X POST http://localhost:8080/api/v1/fetch \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
```

### Notes & Context

```bash
# Save a note
curl -X POST http://localhost:8080/api/v1/notes \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Important Info",
    "content": "Remember this...",
    "tags": "work,project"
  }'

# Search notes
curl "http://localhost:8080/api/v1/notes/search?q=project"
```

## Project Structure

```
dgx-voice-assistant/
├── .project/                     # AI Workbench configuration
│   └── spec.yaml
├── backend/                      # Enhanced backend service
│   ├── Dockerfile
│   └── main.py
├── data/                         # Persistent storage
│   └── qwen_context.db
├── docker-compose.complete.yml   # Full deployment
├── docker-compose.simple.yml     # Basic deployment
├── docker-compose.minimal.yml    # Model only
├── start-simple.sh              # Quick start script
└── README.md
```

## Troubleshooting

### Model Download Issues

```bash
# Check vLLM logs
docker-compose logs vllm

# For gated models, ensure HF_TOKEN is set in .env
```

### Out of Memory

```bash
# Reduce GPU memory utilization in docker-compose.yml
# Change from 0.85 to 0.75 or lower
--gpu-memory-utilization 0.75
```

### Search Not Working

```bash
# Verify Brave API key in .env
BRAVE_API_KEY=your_key

# Restart backend
docker-compose restart backend
```

### UI Not Accessible

```bash
# Check service status
docker-compose ps

# View logs
docker-compose logs webui
```

## NVIDIA AI Workbench

This project is configured as an NVIDIA AI Workbench project. To use with Workbench:

1. Open NVIDIA AI Workbench
2. Clone this repository
3. Workbench will automatically detect the `.project/spec.yaml` configuration
4. Start the environment from the Workbench UI

## Development

### Adding Custom Features

1. Modify `backend/main.py` for backend changes
2. Edit `docker-compose.complete.yml` for service configuration
3. Rebuild and restart:

```bash
docker-compose down
docker-compose up --build -d
```

### Using Different Models

Edit the vLLM command in `docker-compose.complete.yml`:

**For AWQ-quantized models (current setup):**
```yaml
command: >
  --model cpatonn/Qwen3-Omni-30B-A3B-Instruct-AWQ-4bit
  --quantization awq
  --trust-remote-code
```

**For full-precision models (requires more VRAM ~60GB):**
```yaml
command: >
  --model Qwen/Qwen3-Omni-30B-A3B-Instruct
  --dtype auto
  --trust-remote-code
  # Remove --quantization flag for full precision
```

**For other quantized models:**
- Find AWQ models on HuggingFace: search "Qwen3 AWQ" or "model-name AWQ"
- Use FP8 models from Qwen: `Qwen/Qwen3-30B-A3B-FP8`

## License

See [LICENSE](LICENSE) file for details.

## Support

For issues and questions:
- Review [QUICK-START.md](QUICK-START.md) for common scenarios
- Check Docker logs: `docker-compose logs [service-name]`
- Ensure GPU drivers and NVIDIA Container Runtime are properly installed

## Contributing

Contributions are welcome! Please ensure:
- Code follows existing style
- Docker images build successfully
- All services start without errors
- Documentation is updated
