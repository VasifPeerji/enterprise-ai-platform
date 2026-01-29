# 🧠 Enterprise AI Platform

**Composable, Production-Grade, Multi-Tenant AI Assistant Platform**

A state-of-the-art AI platform built with strict architectural discipline, designed for enterprise scalability, multi-tenancy, and domain flexibility.

---

## 🎯 Core Principles

- **Layer-based Architecture**: 7 distinct layers with clear boundaries
- **Model Agnostic**: Support for OpenAI, Anthropic, Azure, and more via LiteLLM
- **Multi-Tenant**: Complete tenant isolation at every layer
- **Production-Ready**: Type-safe, tested, observable, and maintainable
- **Domain Flexible**: Easily extensible to Banking, Healthcare, Retail, etc.

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│  Layer 6: AI Ops & Evaluation (CI/CD for AI)              │
├─────────────────────────────────────────────────────────────┤
│  Layer 5: Governance, Observability & Learning            │
├─────────────────────────────────────────────────────────────┤
│  Layer 4: Platform Engine (Multi-Tenancy)                 │
├─────────────────────────────────────────────────────────────┤
│  Layer 3: Domain Engine (Banking, Healthcare, etc.)       │
├─────────────────────────────────────────────────────────────┤
│  Layer 2: Transaction & Agent Runtime (DOING)             │
├─────────────────────────────────────────────────────────────┤
│  Layer 1: Core Intelligence (THINKING)                    │
├─────────────────────────────────────────────────────────────┤
│  Layer 0: Model & Multimodal Infrastructure               │
└─────────────────────────────────────────────────────────────┘
```

### Layer Responsibilities

| Layer | Purpose | Can Import From | Side Effects |
|-------|---------|-----------------|--------------|
| **Layer 0** | Model abstraction, routing, fallback | None | No |
| **Layer 1** | NLU, RAG, reasoning, memory | Layer 0 | No |
| **Layer 2** | Transactions, workflows, agents | Layers 0-1 | **YES** |
| **Layer 3** | Domain-specific logic | Layers 0-2 | Via Layer 2 |
| **Layer 4** | Multi-tenancy, RBAC | Layers 0-3 | Via Layer 2 |
| **Layer 5** | Observability, audit | Layers 0-4 | Logging only |
| **Layer 6** | Evaluation, testing | Layers 0-5 | Testing only |

**Critical Rule**: Only Layer 2 can perform side effects (DB writes, API calls, transactions).

---

## 🛠️ Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Language** | Python 3.11+ | AI workload optimization |
| **API Framework** | FastAPI | Async-native, high performance |
| **Orchestration** | LangGraph | Stateful agent workflows |
| **Model Gateway** | LiteLLM | 100+ LLMs, unified interface |
| **Vector DB** | Qdrant | Multi-tenant vector search |
| **Database** | PostgreSQL | RBAC, transactions, logs |
| **Cache** | Redis | Session, memory, state |
| **ORM** | SQLModel | Pydantic + SQLAlchemy |
| **Validation** | Pydantic v2 | Rust-powered validation |
| **Migrations** | Alembic | Safe schema changes |
| **Observability** | Arize Phoenix | LLM tracing & evaluation |
| **Package Manager** | Poetry | Dependency management |
| **Frontend** | React + Vite + Tailwind | Admin & user interfaces |

---

## 🚀 Quick Start

### Prerequisites

- **Conda** or **Miniconda** installed
- **PostgreSQL** (local or Docker)
- **Redis** (local or Docker)
- **Qdrant** (local or Docker)
- API keys for LLM providers (OpenAI, Anthropic, etc.)

### 1. Clone & Setup Environment

```bash
# Clone the repository
git clone <repository-url>
cd enterprise-ai-platform

# Create conda environment
conda env create -f environment.yml

# Activate environment
conda activate enterprise-ai-platform

# Install dependencies via Poetry
poetry install
```

### 2. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your API keys and database credentials
nano .env  # or use your preferred editor
```

**Required Settings for Development:**
```env
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
POSTGRES_PASSWORD=your-password
REDIS_HOST=localhost
QDRANT_HOST=localhost
```

### 3. Start Infrastructure (Docker Compose)

```bash
# Start PostgreSQL, Redis, and Qdrant
docker-compose up -d

# Verify services are running
docker-compose ps
```

### 4. Run Database Migrations

```bash
# Create initial migrations
poetry run alembic upgrade head
```

### 5. Start the Application

```bash
# Development server with auto-reload
poetry run uvicorn src.interfaces.http.main:app --reload --host 0.0.0.0 --port 8000
```

Visit:
- **API Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

---

## 📁 Project Structure

```
enterprise-ai-platform/
├── src/
│   ├── layer0_model_infra/       # Model abstraction & routing
│   ├── layer1_intelligence/      # NLU, RAG, reasoning
│   ├── layer2_orchestrator/      # Transactions, workflows
│   ├── layer3_domain/            # Domain-specific logic
│   ├── layer4_platform/          # Multi-tenancy, RBAC
│   ├── layer5_governance/        # Observability, audit
│   ├── layer6_aiops/             # Evaluation, testing
│   ├── interfaces/
│   │   └── http/                 # FastAPI routes
│   └── shared/                   # Common utilities
│       ├── config.py             # Configuration
│       ├── errors.py             # Custom exceptions
│       └── logger.py             # Structured logging
├── tests/
│   ├── unit/                     # Unit tests
│   ├── integration/              # Integration tests
│   └── e2e/                      # End-to-end tests
├── config/                       # Configuration files
├── frontend/                     # React applications
├── docs/                         # Documentation
├── pyproject.toml               # Poetry dependencies
├── environment.yml              # Conda environment
├── .env.example                 # Environment template
├── docker-compose.yml           # Infrastructure
└── README.md                    # This file
```

---

## 🧪 Development Workflow

### Running Tests

```bash
# All tests
poetry run pytest

# Unit tests only
poetry run pytest tests/unit/

# With coverage
poetry run pytest --cov=src --cov-report=html
```

### Code Quality

```bash
# Format code
poetry run black src/ tests/

# Lint code
poetry run ruff src/ tests/

# Type checking
poetry run mypy src/
```

### Database Migrations

```bash
# Create a new migration
poetry run alembic revision --autogenerate -m "Description"

# Apply migrations
poetry run alembic upgrade head

# Rollback one migration
poetry run alembic downgrade -1
```

---

## 🏛️ Architectural Rules

### Dependency Rules

✅ **Allowed**:
- Layer 2 → Layer 1 → Layer 0
- Layer 3 → Layer 2 → Layer 1 → Layer 0
- Higher layers import from lower layers

❌ **Forbidden**:
- Layer 0 → Layer 1 (Lower cannot import from higher)
- Layer 1 → Layer 2 (Cognitive cannot depend on orchestrator)

### Side Effect Rules

✅ **Only Layer 2 can**:
- Write to databases
- Call external APIs
- Execute transactions
- Modify system state

❌ **Layers 0 & 1 must be pure**:
- No database writes
- No API calls
- No side effects
- Pure computation only

### Coding Standards

1. **Type Safety**: All functions must be fully typed
2. **Validation**: Use Pydantic for all data structures
3. **Async**: All I/O operations must be async
4. **Error Handling**: Use custom exceptions from `src/shared/errors.py`
5. **Logging**: Use structured logging from `src/shared/logger.py`
6. **Testing**: Write tests for all new code

---

## 📊 Observability

### Structured Logging

All logs are JSON-formatted with automatic context:

```python
from src.shared.logger import get_logger, bind_context

logger = get_logger(__name__)

# Bind context for entire request
bind_context(trace_id="abc-123", tenant_id="acme", user_id="user_456")

# All subsequent logs include context automatically
logger.info("processing_request", input_tokens=100)
```

### Tracing with Arize Phoenix

```bash
# Start Phoenix
docker run -p 6006:6006 arizephoenix/phoenix:latest

# View traces at http://localhost:6006
```

---

## 🔐 Security

- **Secrets**: Never commit `.env` or API keys
- **Validation**: All inputs validated via Pydantic
- **Authentication**: JWT-based with configurable expiration
- **Authorization**: RBAC at Layer 4
- **Tenant Isolation**: Enforced at every layer
- **PII Handling**: Automatic redaction in logs

---

## 📝 Configuration

All configuration is managed via environment variables and validated at startup.

See `.env.example` for all available settings.

**Key Configuration Groups**:
- Application (name, version, environment)
- API Server (host, port, workers)
- Security (JWT, CORS)
- Model Infrastructure (API keys, default models)
- Databases (PostgreSQL, Redis, Qdrant)
- Observability (logging, tracing)
- Feature Flags (web search, multimodal, etc.)
- Cost Management (budgets, limits)

---

## 🤝 Contributing

1. Follow the architectural rules strictly
2. Write tests for all new code
3. Use type hints everywhere
4. Run code quality checks before committing
5. Update documentation for new features

---

## 📚 Documentation

- **Architecture**: See `ARCHITECTURE.md` (in this project)
- **API Reference**: http://localhost:8000/docs
- **Development Guide**: `docs/development.md`
- **Deployment Guide**: `docs/deployment.md`

---

## 📄 License

[Add your license here]

---

## 🆘 Support

For issues, questions, or contributions:
- GitHub Issues: [link]
- Documentation: [link]
- Email: [email]

---

**Built with ❤️ for Enterprise AI**
