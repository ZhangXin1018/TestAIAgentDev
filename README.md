# Fashion Sustainability Multi-Agent System

This project demonstrates a collaborative LangChain application composed of two
cooperating agents powered by OpenAI models:

- **Agent A – Fashion Material Analyzer**: inspects a garment photo, identifies
each distinct garment, and estimates a material breakdown with weight
information.
- **Agent B – Sustainability Estimator**: consumes Agent A's output, performs
supplementary web research, and forecasts the associated water usage, carbon
emissions, and energy consumption.

The orchestrator coordinates both agents so they can respond to user requests in
a single workflow.

## Project layout

```
.
├── pyproject.toml            # Python project configuration and dependencies
├── .env.example              # Sample environment variable configuration
├── src/
│   ├── agents/
│   │   ├── fashion_analyzer.py          # Agent A implementation
│   │   ├── sustainability_estimator.py  # Agent B implementation
│   │   └── orchestrator.py              # Coordinates agent collaboration
│   ├── tools/
│   │   ├── image_material_tool.py       # Helpers for image preprocessing
│   │   └── web_search.py                # Web search abstraction (Tavily enabled)
│   ├── config.py                        # Environment-driven settings
│   └── main.py                          # CLI entrypoint
└── README.md
```

## Prerequisites

1. **Python 3.10+**
2. **OpenAI API key** – required to run both agents.
3. **(Optional) Tavily API key** – enables high quality sustainability-focused web search.

Install the dependencies in a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

Copy the example environment file and populate your credentials:

```bash
cp .env.example .env
# edit .env with your OPENAI_API_KEY and, optionally, TAVILY_API_KEY
```

## Running the agents

Supply either an image URL or a local image path. Local files are converted into
data URIs automatically before being passed to OpenAI's multimodal models.

```bash
python -m src.main ./sample-garment.jpg --prompt "Focus on the denim jacket."
```

By default the orchestrator prints a JSON payload summarizing the material
analysis and sustainability estimates. Use `--output` to persist the response to
a file.

## Extending the system

- Swap the OpenAI models by adjusting `FASHION_ANALYZER_MODEL` and
  `SUSTAINABILITY_ANALYZER_MODEL` in your `.env` file.
- Replace Tavily with a different search provider by modifying
  `src/tools/web_search.py`.
- Integrate additional downstream agents (e.g., supply-chain optimizers) by
  extending `CollaborativeAgentOrchestrator`.

## Testing the workflow without credentials

If you want to inspect the system without valid API keys, instantiate the agents
with mock LLMs in a notebook or a unit test. Each agent class accepts an
optional LangChain `ChatOpenAI` instance, making it easy to plug in
`langchain_core.language_models.fake.FakeListLLM` for deterministic testing.
