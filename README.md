# GEO Pulse

## Objective

GEO Pulse is a brand audit application for **GEO (Generative Engine Optimization)**. It evaluates a brand's visibility in LLM responses (ChatGPT, Gemini, Perplexity, etc.) and generates strategic recommendations to improve this visibility.

To test the application, you can run `tests/integration/test_graph.py` and specify the brand name and LLM provider.

### How It Works

1. **Question Generation**: The system generates realistic questions that a user might ask about the brand
2. **Web Search**: Uses Tavily API to retrieve relevant search results
3. **LLM Simulation**: Simulates responses that LLMs (ChatGPT, Gemini, etc.) would give based on search results
4. **Analysis and Recommendations**: Analyzes responses to calculate a visibility score (0.0 to 1.0) and generate targeted GEO/SEO recommendations

## Architecture

- **Backend**: LangGraph for workflow orchestration
- **Services**: Modular services for question generation, web search, LLM simulation, and analysis
- **Validation**: Pydantic for strict data validation
- **Testing**: Unit tests (with mocks) and integration tests (with real APIs)

## Current Project Status

### Implemented

- **LangGraph Workflow**: 4 functional nodes (question generator, search executor, LLM simulator, response analyst)
- **Business Services**: Question generator, Tavily search, LLM simulator, Analyst service
- **Tests**: 17 passing unit and integration tests
- **Code Quality**: Pre-commit hooks (Ruff, Detect-secrets)
- **CI/CD**: GitHub Actions with automatic unit tests
- **Branch Protection**: Main branch protected with test verification before merge

### To Do

1. **FastAPI**: Expose the LangGraph workflow via a REST API
2. **Streamlit**: Create a user interface to interact with the API
3. **Docker**: Containerize the application for deployment
4. **Deployment**: Deploy to production 

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

### Run the graph directly

```python
from src.core.graph.graph import create_audit_graph, create_initial_state

graph = create_audit_graph()
initial_state = create_initial_state(brand="Nike", llm_provider="gpt-4")
result = graph.invoke(initial_state)

print(f"Score: {result['reputation_score']}")
print(f"Recommendations: {result['recommendations']}")
```

### Tests

```bash
# Unit tests (with mocks, fast)
uv run pytest tests/unit/ -v

```

## Project Structure

```
geo-pulse/
├── src/
│   ├── core/
│   │   ├── graph/          # LangGraph (state, nodes, graph)
│   │   └── services/        # Business services (search, llm, analysis)
│   └── api/                # FastAPI (coming soon)
├── tests/
│   ├── unit/               # Unit tests (mocks)
│   └── integration/        # Integration tests (real APIs)
├── .github/
│   └── workflows/           # GitHub Actions CI/CD
└── pyproject.toml          # Dependencies and configuration
```

## Contributing

1. Create a feature branch
2. Make your changes
3. Tests must pass (pre-commit + CI/CD)
4. Create a Pull Request to main
5. CI/CD must pass before merge is authorized
