# Blue - LangGraph Workflow

A LangGraph-based workflow application with LLM integration using ChatOpenAI and Ollama embeddings.

## Features

- LangGraph state management
- ChatOpenAI integration with custom endpoint
- Ollama embeddings support
- Simple question-answering workflow

## Installation

1. Clone the repository:
```bash
git clone https://github.com/amirhosseinzolfi/blue.git
cd blue
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

```python
from graph import app

# Run the workflow
result = app.invoke({"question": "Your question here"})
print(result["answer"])
```

## Configuration

The application uses:
- OpenAI-compatible API endpoint: `http://141.98.210.15:15203/v1`
- Model: `gpt-4o`
- Embeddings: `nomic-embed-text` via Ollama

## License

MIT License
