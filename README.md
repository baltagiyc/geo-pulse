---
title: GEO Pulse
emoji: 🚀
colorFrom: purple
colorTo: pink
sdk: docker
app_port: 8501
pinned: false
---

# GEO Pulse

## Objective

GEO Pulse is a brand audit application for **GEO (Generative Engine Optimization)**. It evaluates a brand's visibility in LLM responses (ChatGPT, Gemini, Perplexity, etc.) and generates strategic recommendations to improve this visibility.

### How It Works

1. **Brand Context Generation**: Generates factual context about the brand (especially useful for less-known brands to prevent hallucinations)
2. **Question Generation**: The system generates realistic questions that a user might ask about the brand
3. **Web Search**: Uses Tavily API to retrieve relevant search results
4. **LLM Simulation**: Simulates responses that LLMs (ChatGPT, Gemini, etc.) would give based on search results
5. **Analysis and Recommendations**: Analyzes responses to calculate a visibility score (0.0 to 1.0) and generate targeted GEO/SEO recommendations

## Architecture

- **Backend**: FastAPI REST API + LangGraph for workflow orchestration
- **Frontend**: Streamlit web interface
- **Workflow**: Linear LangGraph with 5 nodes (brand context → questions → search → LLM simulation → analysis)
- **Services**: Modular services with factory pattern (LLM factory, search factory)
- **Configuration**: Centralized config (magic numbers, API keys, defaults)
- **Validation**: Pydantic for strict data validation (API schemas, internal models)
- **State Management**: TypedDict for LangGraph state, Pydantic for services
- **Testing**: Unit tests (with mocks) and integration tests (with real APIs)
- **Observability**: LangSmith tracking for LLM calls, structured logging

## Tech Stack

- Python 3.12+
- LangGraph (orchestration)
- FastAPI (REST API)
- Pydantic (validation)
- Tavily API (web search)
- OpenAI API (LLM)
- Streamlit (frontend)
- Pytest (testing)
- Ruff (linting/formatting)
- GitHub Actions (CI/CD)

## Installation

### Option 1: Docker (Recommended - No local dependencies needed)

See [Usage > Run with Docker](#run-with-docker-recommended---no-pythonuv-needed) section below. Just Docker + your API keys!

### Option 2: Local Development (requires Python 3.12+ and uv)

```bash
# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone the repository
git clone https://github.com/baltagiyc/geo-pulse.git
cd geo-pulse

# Install dependencies
uv sync --dev

# Configure environment variables
cp .env.example .env
# Edit .env and add your API keys (OPENAI_API_KEY, TAVILY_API_KEY)
```

## Usage

### Run with Docker (Recommended)

**The easiest way to run GEO Pulse:** Just Docker + your API keys. Docker handles everything (Python, dependencies, tools).

```bash
# 1. Prepare your API keys
cp .env.example .env
# Edit .env and add your API keys

# 2. Build the image (includes everything: Python, uv, dependencies)
docker build -t geo-pulse .

# 3. Run the container (backend + frontend)
docker run -p 8000:8000 -p 8501:8501 --name geo-pulse-container --env-file .env geo-pulse
```

Then access:
- **Frontend**: http://localhost:8501
- **Backend API**: http://localhost:8000
- **Swagger Docs**: http://localhost:8000/docs

For more details and Docker options, see `docker.md`.

### Run locally (Development)

```bash
# Start FastAPI backend
uv run uvicorn src.api.main:app --reload

# In another terminal, start Streamlit frontend
uv run streamlit run src/frontend/app.py
```

### Tests

```bash
# Unit tests (with mocks, fast)
uv run pytest tests/unit/ -v


## Contributing

1. Create a feature branch
2. Make your changes
3. Tests must pass (pre-commit + CI/CD)
4. Create a Pull Request to main
5. CI/CD must pass before merge is authorized
