# 🦙 Ollama Setup Guide

This guide shows you how to set up Ollama for local, cost-free AI inference.

---

## Why Ollama?

**Cost Savings:**
- ✅ **$0 per request** (runs locally)
- ✅ No API rate limits
- ✅ No internet required
- ✅ Data stays on your machine

**When to Use:**
- Simple queries (greetings, FAQs)
- Development/testing
- Privacy-sensitive data
- High-volume, low-complexity workloads

**When NOT to Use:**
- Complex reasoning tasks
- Coding/debugging
- Vision/multimodal tasks
- Require latest knowledge

---

## Installation

### Windows

1. Download from: https://ollama.ai/download
2. Run installer
3. Ollama runs automatically on `http://localhost:11434`

### Mac

```bash
brew install ollama
ollama serve
```

### Linux

```bash
curl -fsSL https://ollama.ai/install.sh | sh
ollama serve
```

---

## Pull Models

Download the models configured in the platform:

```bash
# Fast model for simple queries (recommended)
ollama pull phi3:mini

# Balanced model
ollama pull llama3.1:8b

# Better reasoning
ollama pull mistral:7b
```

**Verify models:**
```bash
ollama list
```

---

## Test Ollama

```bash
# Test locally
ollama run phi3:mini "Hello, how are you?"
```

If this works, you're ready!

---

## Configure Platform

1. Edit `.env`:
```env
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_ENABLED=true
```

2. Restart the platform:
```bash
./run.bat  # Windows
./run.sh   # Linux/Mac
```

---

## Usage in Platform

The platform will **automatically** use Ollama for:
- Simple greetings ("Hello", "Hi", "Thanks")
- Basic FAQs
- Short informational queries
- Development testing

**You don't need to do anything** - the router handles it!

---

## Testing the Router

### Example 1: Simple Query (Uses Ollama - FREE)

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello! How are you?"
  }'
```

**Expected:** Uses `ollama-phi3-mini` (cost: $0.00)

---

### Example 2: Complex Query (Uses GPT-4)

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Explain the architectural tradeoffs between microservices and monoliths, considering scalability, maintainability, and operational complexity."
  }'
```

**Expected:** Uses `gpt-4-turbo` (cost: ~$0.01)

---

### Example 3: Analyze Without Generating

```bash
curl -X POST "http://localhost:8000/chat/analyze?message=Hello"
```

**Response shows:** Which model would be selected and why

---

## Troubleshooting

### "Connection refused" error

**Solution:** Make sure Ollama is running:
```bash
ollama serve
```

### "Model not found" error

**Solution:** Pull the model:
```bash
ollama pull phi3:mini
```

### Slow responses

**Cause:** First run downloads model (one-time)  
**Solution:** Wait for download to complete

---

## Cost Comparison

| Query Type | Without Ollama | With Ollama | Savings |
|------------|---------------|-------------|---------|
| 1,000 simple queries | ~$0.50 | **$0.00** | 100% |
| 10,000 simple queries | ~$5.00 | **$0.00** | 100% |
| 100,000 simple queries | ~$50.00 | **$0.00** | 100% |

**Complex queries still use premium models** - you only save on simple ones.

---

## Monitoring

View routing decisions in real-time:

```bash
# Start server with debug logging
LOG_LEVEL=DEBUG ./run.bat
```

Look for logs like:
```
routing_decision_made: selected_model=ollama-phi3-mini, reasoning="Query is simple, using cost-effective model"
```

---

## Hardware Requirements

**Minimum:**
- 8GB RAM
- 10GB disk space

**Recommended:**
- 16GB+ RAM
- GPU (optional, speeds up inference)

---

## Next Steps

✅ Ollama installed and running  
✅ Models pulled  
✅ Platform configured  
✅ Ready to save costs!

**Try the `/chat` endpoint and watch it intelligently route queries!**
