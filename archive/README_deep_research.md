# DeepResearchAgent with ReAct Framework

A powerful AI research agent that uses the ReAct (Reasoning + Acting) framework to conduct intelligent multi-source research. The agent can search the web and Google Drive, automatically reasoning about what information to look for and reflecting on findings to guide its research strategy.

## Features

- **ReAct Framework**: Implements a Think-Act-Observe-Reflect loop for intelligent research
- **Multi-Source Integration**: Currently supports web search (Brave/fallback) and Google Drive
- **Automatic Content Extraction**: Extracts and analyzes content from web pages and documents
- **Self-Reflection**: Evaluates research progress and adjusts strategy dynamically
- **Confidence Tracking**: Monitors research completeness and quality
- **Research Synthesis**: Provides comprehensive reports with source attribution

## Architecture

The agent follows this research loop:
1. **THINK**: Analyze what information is needed and which sources to consult
2. **ACT**: Execute searches and extract content from selected sources
3. **OBSERVE**: Process and store findings
4. **REFLECT**: Evaluate quality of findings and determine next steps
5. **SYNTHESIZE**: Create a comprehensive report when confidence threshold is reached

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure API Keys

Create a `.env` file in the project root:

```env
# Required
ANTHROPIC_API_KEY=your_anthropic_api_key

# Optional (for enhanced web search)
BRAVE_SEARCH_API_KEY=your_brave_api_key
FIRECRAWL_API_KEY=your_firecrawl_api_key

# For Google Drive (see authentication section below)
GOOGLE_SERVICE_ACCOUNT_FILE=path/to/service_account.json
```

### 3. Google Drive Authentication

The agent supports three authentication methods for Google Drive:

#### Option 1: OAuth2 (Interactive - Recommended for personal use)
```python
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
import pickle

SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

def authenticate_google_drive():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Download credentials.json from Google Cloud Console
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    
    return creds
```

#### Option 2: Service Account (Recommended for server applications)
1. Create a service account in Google Cloud Console
2. Download the JSON key file
3. Set the path in `.env`: `GOOGLE_SERVICE_ACCOUNT_FILE=path/to/key.json`
4. Share Google Drive files/folders with the service account email

#### Option 3: Application Default Credentials
If running on Google Cloud Platform, the agent will automatically use default credentials.

## Usage

### Basic Usage

```python
from deep_research_agent import DeepResearchAgent, DeepResearchConfig

# Initialize the agent
config = DeepResearchConfig(
    enable_sources=["web", "google_drive"],
    research_depth="balanced",
    verbose=True
)

agent = DeepResearchAgent(config=config)

# Conduct research
report = agent.run("What are the latest developments in quantum computing?")

# Access results
print(f"Confidence: {report.confidence_level:.2%}")
print(f"Sources consulted: {report.sources_consulted}")
print(f"\nSynthesis:\n{report.synthesis}")
```

### Advanced Configuration

```python
config = DeepResearchConfig(
    # Model settings
    model="claude-3-sonnet-20240229",
    max_tokens=4096,
    temperature=0.7,
    
    # Research settings
    enable_sources=["web", "google_drive"],
    research_depth="deep",  # 'shallow', 'balanced', 'deep'
    max_iterations=10,      # Maximum research iterations
    
    # Performance settings
    enable_caching=True,
    cache_duration=3600,    # 1 hour
    
    # Output settings
    verbose=True            # Show detailed progress
)
```

### Async Usage

```python
import asyncio

async def research_async():
    agent = DeepResearchAgent()
    report = await agent.conduct_research("Your research query")
    return report

# Run async
report = asyncio.run(research_async())
```

## Research Process Example

Here's what happens when you run a research query:

```
🔍 Starting Deep Research for: What are the latest developments in quantum computing?
============================================================

📍 Iteration 1/10
----------------------------------------
🤔 THINKING about next steps...
💭 Analysis: Need to search for recent quantum computing developments
📊 Confidence: 0.00
🎯 Recommended sources: ['web']

🔧 ACTING on web with 2 queries
[DeepResearchAgent] Executing brave_search(query='quantum computing breakthroughs 2024')
[DeepResearchAgent] Extracting content from: https://example.com/quantum-news

👀 OBSERVING: Found 3 new pieces of information

🔍 REFLECTING on findings...
📈 Quality: high
🎯 New confidence: 0.35
❓ Remaining questions: 2
➡️  Continue: True

📍 Iteration 2/10
----------------------------------------
🤔 THINKING about next steps...
💭 Analysis: Found public information, checking for internal documents
📊 Confidence: 0.35
🎯 Recommended sources: ['google_drive']

🔧 ACTING on google_drive with 1 queries
[DeepResearchAgent] Executing google_drive_search(query='quantum computing project')
[DeepResearchAgent] Extracting content from file: 1234567890

👀 OBSERVING: Found 2 new pieces of information

🔍 REFLECTING on findings...
📈 Quality: high
🎯 New confidence: 0.85
❓ Remaining questions: 0
➡️  Continue: False

✅ Research complete based on reflection

📝 SYNTHESIZING final research report...

✨ Research completed!
📊 Final confidence: 0.85
🔄 Iterations performed: 2
📚 Sources consulted: ['web', 'google_drive']
```

## Extending the Agent

### Adding New Data Sources

1. Create a new tool class inheriting from `Tool`:

```python
class CustomSourceTool(Tool):
    def __init__(self):
        super().__init__(
            name="custom_source",
            description="Search custom data source",
            input_schema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"}
                },
                "required": ["query"]
            }
        )
    
    async def execute(self, query: str) -> str:
        # Implement your custom search logic
        results = await search_custom_source(query)
        return format_results(results)
```

2. Add to the agent's tool initialization:

```python
def _initialize_tools(self) -> List[Tool]:
    tools = []
    if "custom" in self.config.enable_sources:
        tools.append(CustomSourceTool())
    return tools
```

### Customizing Research Strategy

Modify the reasoning prompts in `ReActReasoningEngine` to adjust how the agent thinks about research:

```python
def _get_reasoning_prompt(self) -> str:
    return """Your custom reasoning instructions..."""
```

## Troubleshooting

### Google Drive Authentication Issues
- Ensure credentials are properly set up (see Authentication section)
- Check that the service account has access to the files
- Verify the Google Drive API is enabled in your Google Cloud project

### Web Search Fallbacks
- If Brave Search API is not available, the agent falls back to DuckDuckGo
- If Firecrawl is not available, basic BeautifulSoup extraction is used

### Performance Optimization
- Reduce `max_iterations` for faster but potentially less thorough research
- Adjust `research_depth` to 'shallow' for quicker results
- Enable caching to avoid repeated searches

## API Reference

### DeepResearchConfig

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `enable_sources` | List[str] | ["web", "google_drive"] | Data sources to enable |
| `research_depth` | str | "balanced" | Research thoroughness: 'shallow', 'balanced', 'deep' |
| `max_iterations` | int | 10 | Maximum ReAct loop iterations |
| `verbose` | bool | True | Show detailed progress |
| `enable_caching` | bool | True | Cache search results |

### ResearchReport

| Attribute | Type | Description |
|-----------|------|-------------|
| `query` | str | Original research query |
| `objective` | str | Extracted research objective |
| `findings` | List[Finding] | All findings from research |
| `synthesis` | str | Synthesized research summary |
| `confidence_level` | float | Research confidence (0-1) |
| `sources_consulted` | Dict | Sources and queries used |
| `iterations_performed` | int | Number of ReAct iterations |

## License

This project is provided as-is for demonstration purposes. 