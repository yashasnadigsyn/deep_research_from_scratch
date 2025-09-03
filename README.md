# 🧱 Deep Research From Scratch 

Deep research has broken out as one of the most popular agent applications. [OpenAI](https://openai.com/index/introducing-deep-research/), [Anthropic](https://www.anthropic.com/engineering/built-multi-agent-research-system), [Perplexity](https://www.perplexity.ai/hub/blog/introducing-perplexity-deep-research), and [Google](https://gemini.google/overview/deep-research/?hl=en) all have deep research products that produce comprehensive reports using [various sources](https://www.anthropic.com/news/research) of context. There are also many [open](https://huggingface.co/blog/open-deep-research) [source](https://github.com/google-gemini/gemini-fullstack-langgraph-quickstart) implementations. We built an [open deep researcher](https://github.com/langchain-ai/open_deep_research) that is simple and configurable, allowing users to bring their own models, search tools, and MCP servers. In this repo, we'll build a deep researcher from scratch! Here is a map of the major pieces that we will build:

![overview](https://github.com/user-attachments/assets/b71727bd-0094-40c4-af5e-87cdb02123b4)

## 🚀 Quickstart 

### Prerequisites

- **Node.js and npx** (required for MCP server in notebook 3):
```bash
# Install Node.js (includes npx)
# On macOS with Homebrew:
brew install node

# On Ubuntu/Debian:
curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
sudo apt-get install -y nodejs

# Verify installation:
node --version
npx --version
```

- Ensure you're using Python 3.11 or later.
- This version is required for optimal compatibility with LangGraph.
```bash
python3 --version
```
- [uv](https://docs.astral.sh/uv/) package manager
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
# Update PATH to use the new uv version
export PATH="/Users/$USER/.local/bin:$PATH"
```

### Installation

1. Clone the repository:
```bash
git clone https://github.com/langchain-ai/deep_research_from_scratch
cd deep_research_from_scratch
```

2. Install the package and dependencies (this automatically creates and manages the virtual environment):
```bash
uv sync
```

3. Set up Ollama (required for local AI processing):
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull the required model
ollama pull qwen3:0.6b-q8_0
```

4. Create a `.env` file in the project root (optional for tracing):
```bash
# Create .env file
touch .env
```

Add your API keys to the `.env` file (optional):
```env
# Optional: For evaluation and tracing
LANGSMITH_API_KEY=your_langsmith_api_key_here
LANGSMITH_TRACING=true
LANGSMITH_PROJECT=deep_research_from_scratch
```

5. Run the deep research agent:
```bash
# Interactive mode
uv run python main.py

# Command line mode
uv run python main.py "What are the best coffee shops in San Francisco?"

# Or activate the virtual environment if preferred
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

## 📊 Logging

The system includes comprehensive logging for debugging and monitoring:

- **Log Files**: Automatically created in `logs/` directory with timestamps
- **Console Output**: Real-time logging to console during execution
- **Module-Specific Loggers**: Separate loggers for different components
- **Configurable Levels**: DEBUG, INFO, WARNING, ERROR levels available

### Log Files

Log files are automatically created in the `logs/` directory with timestamps:
```
logs/
├── deep_research_20250101_120000.log
├── deep_research_20250101_130000.log
└── ...
```

### Log Levels

- **INFO**: General information about research progress
- **DEBUG**: Detailed debugging information (tool calls, state transitions)
- **WARNING**: Non-critical issues
- **ERROR**: Errors and exceptions with full stack traces

### Example Log Output

```
2025-01-01 12:00:00 - deep_research - INFO - Starting research session for query: What are the best coffee shops in San Francisco?
2025-01-01 12:00:01 - deep_research.scope - INFO - Starting user clarification process
2025-01-01 12:00:02 - deep_research.scope - INFO - Sufficient information provided - proceeding to research brief generation
2025-01-01 12:00:03 - deep_research.supervisor - INFO - Supervisor node executing - iteration 1
2025-01-01 12:00:04 - deep_research.utils - INFO - DDGS search tool called with query: 'best coffee shops San Francisco', max_results: 3
2025-01-01 12:00:05 - deep_research.research_agent - INFO - LLM made 2 tool calls: ['ddgs_search', 'think_tool']
```

## 🚀 Quick Start with main.py

The easiest way to use the deep research agent is through the `main.py` script:

```bash
# Interactive mode - ask multiple questions
uv run python main.py

# Command line mode - single question
uv run python main.py "What are the best coffee shops in San Francisco?"
uv run python main.py "Compare OpenAI vs Anthropic AI approaches"
uv run python main.py "What are the latest developments in quantum computing?"
```

The agent will:
1. **Clarify** your question if needed
2. **Research** using web search and multi-agent coordination
3. **Generate** a comprehensive report with sources

## 🔧 Key Features

- **Local AI Processing**: Uses Ollama with Qwen3 model for all AI operations
- **DDGS Search**: Uses Dux Distributed Global Search for web research
- **Multi-Agent Coordination**: Intelligent task delegation for complex research
- **No External APIs**: Runs completely locally (except for web search)
- **Rich Output**: Beautiful formatted reports with proper citations
- **Comprehensive Logging**: Detailed logging for debugging and monitoring

## Background 

Research is an open‑ended task; the best strategy to answer a user request can't be easily known in advance. Requests can require different research strategies and varying levels of search depth. Consider this request. 

[Agents](https://langchain-ai.github.io/langgraph/tutorials/workflows/#agent) are well suited to research because they can flexibly apply different strategies, using intermediate results to guide their exploration. Open deep research uses an agent to conduct research as part of a three step process:

1. **Scope** – clarify research scope
2. **Research** – perform research
3. **Write** – produce the final report

## 📝 Architecture

This project implements a complete deep research system with the following components:

### 🏗️ System Components

- **Research Agent Scope** (`src/deep_research_from_scratch/research_agent_scope.py`): User clarification and research brief generation
- **Research Agent** (`src/deep_research_from_scratch/research_agent.py`): Individual research agent with web search capabilities
- **Multi-Agent Supervisor** (`src/deep_research_from_scratch/multi_agent_supervisor.py`): Coordinates multiple research agents for complex tasks
- **Full Research System** (`src/deep_research_from_scratch/research_agent_full.py`): Complete end-to-end research workflow

### 🎯 Key Features

- **Structured Output**: Using Pydantic schemas for reliable AI decision making
- **Async Orchestration**: Strategic use of async patterns for parallel coordination
- **Agent Patterns**: ReAct loops, supervisor patterns, multi-agent coordination
- **Search Integration**: DDGS (Dux Distributed Global Search) for web research
- **Workflow Design**: LangGraph patterns for complex multi-step processes
- **State Management**: Complex state flows across subgraphs and nodes

The system implements a three-phase architecture: **Scope** → **Research** → **Write**, providing comprehensive research capabilities with intelligent scoping and coordinated execution. 
