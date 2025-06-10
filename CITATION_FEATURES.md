# Deep Research Agent - Source Citation Features

## Overview

The Deep Research Agent has been enhanced with comprehensive source citation capabilities. Every answer now includes properly formatted footnotes that link back to the original documents and sources used to generate the response.

## Key Features

### 1. Automatic Footnote Citations
- All information in responses includes numbered footnote citations: [1], [2], [3], etc.
- Citations appear inline with the relevant information
- Comprehensive "Sources" section automatically appended to all responses

### 2. Clickable Source Links
- Web sources include clickable URLs for immediate access
- Google Drive files link directly to the document (when file ID is available)
- **Enhanced Google Drive Support**: Multiple methods to extract file IDs and generate direct links
- Makes it easy to verify information and dive deeper into sources

### 3. Source Tracking
- Tracks all sources consulted during research
- Eliminates duplicate sources in citation lists
- Maintains chronological order of source discovery

## Citation Format Examples

### Web Sources
```
According to recent AI safety research [1], there have been significant developments in alignment techniques [2].

## Sources
[1] [AI Safety Report 2024](https://example.com/ai-safety-report)
[2] [Alignment Research Updates](https://arxiv.org/paper/alignment-2024)
```

### Google Drive Sources
```
The company's financial data shows growth [1], as outlined in the strategic plan [2].

## Sources
[1] [Q3 Financial Report - Google Drive](https://drive.google.com/file/d/abc123/view)
[2] [2024 Strategic Plan - Google Drive](https://drive.google.com/file/d/def456/view)
```

### Mixed Sources
```
Market research indicates trends [1], supported by internal analysis [2] and external reports [3].

## Sources
[1] Search results for 'market trends 2024' - Web
[2] [Internal Market Analysis - Google Drive](https://drive.google.com/file/d/ghi789/view)
[3] [Industry Report on Market Trends](https://example.com/market-report)
```

## Programmatic Access

### ResearchReport Object
The `ResearchReport` class now includes:

```python
@dataclass
class ResearchReport:
    query: str
    findings: List[Finding]
    synthesis: str
    sources_consulted: Dict[str, List[str]]
    timestamp: datetime
    citation_map: Dict[int, str]         # Maps citation numbers to sources
    clickable_sources: Dict[int, str]    # Maps citation numbers to URLs
```

### Useful Methods

```python
# Get formatted citations
report.get_formatted_citations()

# Get source for specific citation
report.get_source_by_citation(1)

# Get clickable URL for citation
report.get_clickable_url(1)

# Get all clickable sources
agent.get_clickable_sources()
```

## Usage Example

```python
from src.agents.deep_research import DeepResearchAgent

agent = DeepResearchAgent(verbose=True)
report = await agent.conduct_research("What are the latest AI developments?")

# Response automatically includes citations
print(report.synthesis)  # Includes [1], [2], etc. and Sources section

# Access individual sources
for num, url in report.clickable_sources.items():
    print(f"Citation {num}: {url}")
```

## Benefits

1. **Transparency**: Every claim is traceable to its source
2. **Verification**: Easy access to original documents for fact-checking
3. **Research Continuity**: Users can seamlessly continue research using provided links
4. **Academic Standards**: Follows proper citation conventions
5. **Legal Compliance**: Enables verification of information for sensitive use cases

## Implementation Details

- Citations are automatically generated during the research process
- Sources are deduplicated to avoid redundant entries
- Both in-text citations and source lists are formatted consistently
- The system handles both web sources and Google Drive documents
- Fallback handling for sources without direct links

### Google Drive Link Generation

The system uses multiple methods to ensure Google Drive documents are always linked when possible:

1. **Direct URL extraction**: From `google_drive_extract` tool calls
2. **Metadata file ID**: From tool call parameters
3. **Title parsing**: Extracting file IDs from source titles
4. **Content parsing**: Finding file IDs in search result content using regex patterns

This multi-layered approach ensures maximum coverage for Google Drive document linking.

This enhancement ensures that all research conducted by the Deep Research Agent meets high standards for source attribution and enables users to easily verify and extend the research. 