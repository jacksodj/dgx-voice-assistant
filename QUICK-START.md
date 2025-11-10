# Quick Start Guide

## Choose Your Deployment:

### 1. Ultra-Minimal (Just the model)
```bash
docker-compose -f docker-compose.minimal.yml up -d
```
Access: http://localhost:8000

### 2. Complete (Model + UI + Search + Storage)
```bash
chmod +x start-simple.sh
./start-simple.sh
```
Access: http://localhost:3000

### 3. Simple (Model + Basic Backend)
```bash
docker-compose -f docker-compose.simple.yml up -d
```

## Comparison:

| Feature | Minimal | Simple | Complete |
|---------|---------|--------|----------|
| Setup Time | 2 min | 5 min | 5 min |
| Services | 1 | 2-3 | 3-4 |
| UI | None | Basic | Full |
| Internet Search | ❌ | ❌ | ✅ |
| Storage | ❌ | ❌ | ✅ |
| Voice Support | ❌ | ❌ | ✅ |

## Recommendation:

**Start with Complete** - Has everything you need!

Read README-COMPLETE.md for full details.
