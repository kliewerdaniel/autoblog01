# Comprehensive Prompt for CLIne: Agentic Blog Post Generation System

Build a complete Python-based agentic workflow system that generates high-quality, SEO-optimized blog posts for a Next.js site by leveraging semantic search across existing blog posts stored as the knowledge base. The system should use Ollama with the gpt-oss:20b model and implement a multi-stage agentic process with RAG (Retrieval-Augmented Generation).

## Project Overview

Create a sophisticated blog post generation system with the following capabilities:
- Ingest existing .md blog posts from `content/blog/` into a vector database
- Perform semantic/agentic search across the knowledge base
- Generate new, polished blog posts based on user-specified topics and requirements
- Ensure output matches the existing Next.js site format and SEO standards
- Support detailed specification inputs for customized article generation

## Technical Stack & Dependencies

### Core Dependencies
- **ollama**: Python client for local LLM interaction (gpt-oss:20b model)
- **chromadb** or **qdrant-client**: Vector database for semantic search
- **sentence-transformers**: For generating embeddings (use 'all-MiniLM-L6-v2' or similar lightweight model)
- **python-frontmatter**: Parse and create YAML frontmatter
- **PyYAML**: YAML manipulation
- **python-slugify**: URL-safe slug generation
- **langchain** or **llama-index**: Optional, for advanced RAG patterns
- **rich**: CLI progress indicators and beautiful output
- **click** or **argparse**: CLI argument parsing
- **pydantic**: Data validation and settings management

### Project Structure

```
your-account/rez04/
├── content/
│   └── blog/
│       └── *.md (existing blog posts)
├── agent/
│   ├── __init__.py
│   ├── config.py                 # Configuration and constants
│   ├── cli.py                    # Main CLI entrypoint
│   ├── ingest.py                 # Knowledge base ingestion
│   ├── vector_store.py           # Vector DB operations
│   ├── retrieval.py              # Semantic search & retrieval
│   ├── llm_client.py             # Ollama LLM interface
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── researcher.py         # Research agent for context gathering
│   │   ├── outliner.py           # Outline generation agent
│   │   ├── writer.py             # Main writing agent
│   │   ├── editor.py             # Editing & polishing agent
│   │   └── seo_optimizer.py     # SEO enhancement agent
│   ├── prompts/
│   │   ├── __init__.py
│   │   ├── system_prompts.py    # System prompts for each agent
│   │   └── templates.py         # Prompt templates
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── parser.py            # Markdown & frontmatter parsing
│   │   ├── validator.py         # Content validation
│   │   └── file_utils.py        # File I/O operations
│   └── models.py                # Pydantic models for data structures
├── .agent_data/
│   ├── vector_db/               # ChromaDB/Qdrant storage
│   └── cache/                   # Optional caching
├── requirements.txt
├── pyproject.toml
└── README.md
```

## Detailed Implementation Requirements

### 1. Configuration (agent/config.py)

Create a comprehensive configuration system using Pydantic:

```python
from pydantic_settings import BaseSettings
from pathlib import Path

class AgentConfig(BaseSettings):
    # Paths
    project_root: Path = Path(__file__).parent.parent
    blog_dir: Path = project_root / "content" / "blog"
    vector_db_dir: Path = project_root / ".agent_data" / "vector_db"
    
    # Ollama settings
    ollama_model: str = "gpt-oss:20b"
    ollama_base_url: str = "http://localhost:11434"
    
    # Embedding settings
    embedding_model: str = "all-MiniLM-L6-v2"
    chunk_size: int = 500
    chunk_overlap: int = 50
    
    # Vector DB settings
    collection_name: str = "blog_knowledge_base"
    top_k_retrieval: int = 5
    
    # Generation settings
    min_word_count: int = 800
    max_word_count: int = 2000
    temperature: float = 0.7
    
    # SEO requirements
    min_headings: int = 3
    max_headings: int = 7
    require_meta_description: bool = True
    target_keyword_density: float = 0.02  # 2%
```

### 2. Knowledge Base Ingestion (agent/ingest.py)

Implement a robust ingestion pipeline:

**Requirements:**
- Scan `content/blog/` for all .md files
- Parse frontmatter and extract: title, date, categories, tags, content
- Split content into semantically meaningful chunks (consider paragraphs, sections)
- Generate embeddings for each chunk using sentence-transformers
- Store in vector database with metadata:
  - source_file
  - title
  - date
  - categories
  - tags
  - chunk_index
  - full_content (for context)
- Implement incremental updates (only process new/modified files)
- Create an index manifest (JSON) tracking ingested files and their timestamps

**Key Functions:**
```python
def scan_blog_posts(blog_dir: Path) -> List[Path]
def parse_blog_post(file_path: Path) -> BlogPost  # Pydantic model
def chunk_content(content: str, chunk_size: int, overlap: int) -> List[str]
def generate_embeddings(texts: List[str]) -> np.ndarray
def ingest_to_vector_db(posts: List[BlogPost], vector_store: VectorStore)
def build_index_manifest(posts: List[BlogPost]) -> dict
```

### 3. Vector Store Operations (agent/vector_store.py)

Implement vector database abstraction (support ChromaDB as primary, with interface for easy switching):

**Requirements:**
- Initialize/connect to vector database
- Add documents with embeddings and metadata
- Perform similarity search with filters (by date, category, tags)
- Hybrid search (combine semantic + keyword matching)
- Return top-k results with relevance scores
- Support metadata filtering for more precise retrieval

**Key Functions:**
```python
class VectorStore:
    def __init__(self, config: AgentConfig)
    def add_documents(self, texts: List[str], embeddings: np.ndarray, metadata: List[dict])
    def similarity_search(self, query: str, top_k: int, filters: dict = None) -> List[Document]
    def hybrid_search(self, query: str, keywords: List[str], top_k: int) -> List[Document]
    def get_collection_stats(self) -> dict
```

### 4. Semantic Retrieval System (agent/retrieval.py)

Build an intelligent retrieval layer:

**Requirements:**
- Query expansion (generate related search terms from user topic)
- Multi-query retrieval (search with multiple formulations)
- Re-ranking results by relevance
- Context assembly (combine retrieved chunks into coherent context)
- Deduplicate results from same source
- Score and rank by recency, relevance, and topic match

**Key Functions:**
```python
def expand_query(query: str, llm_client: LLMClient) -> List[str]
def retrieve_relevant_context(query: str, vector_store: VectorStore, top_k: int) -> List[Document]
def rerank_results(query: str, results: List[Document]) -> List[Document]
def assemble_context_window(results: List[Document], max_tokens: int) -> str
```

### 5. LLM Client (agent/llm_client.py)

Create a clean interface to Ollama:

**Requirements:**
- Support for chat and completion modes
- Streaming support with progress indicators
- Retry logic with exponential backoff
- Token counting and context window management
- Error handling for connection issues, timeouts, model not found
- Support for system prompts and multi-turn conversations

**Key Functions:**
```python
class LLMClient:
    def __init__(self, config: AgentConfig)
    def chat(self, messages: List[dict], temperature: float = 0.7, stream: bool = False) -> str
    def generate(self, prompt: str, system_prompt: str = None, temperature: float = 0.7) -> str
    def count_tokens(self, text: str) -> int
    def is_model_available(self) -> bool
```

### 6. Multi-Agent System

Implement a pipeline of specialized agents, each with specific responsibilities:

#### 6.1 Research Agent (agent/agents/researcher.py)

**Purpose:** Gather and synthesize relevant context from the knowledge base

**Process:**
1. Receive user topic/specification
2. Generate multiple search queries using query expansion
3. Retrieve top-k relevant documents from vector store
4. Synthesize findings into a structured research brief
5. Identify key themes, facts, and relevant existing content

**Output:** Research brief with:
- Key themes and concepts
- Relevant facts and statistics from knowledge base
- Related topics covered in existing posts
- Gaps in current knowledge base
- Recommended focus areas

#### 6.2 Outliner Agent (agent/agents/outliner.py)

**Purpose:** Create a detailed, SEO-optimized outline

**Process:**
1. Receive research brief and user specifications
2. Generate outline with:
   - Compelling headline (H1) with target keyword
   - 3-7 main sections (H2s)
   - 2-4 subsections per main section (H3s)
   - Key points to cover in each section
   - Suggested word count per section
   - SEO recommendations (keywords, internal linking opportunities)

**Output:** Structured outline in markdown format

#### 6.3 Writer Agent (agent/agents/writer.py)

**Purpose:** Generate the main blog post content

**Process:**
1. Receive outline and research brief
2. Write each section following the outline
3. Incorporate facts and insights from knowledge base naturally
4. Maintain consistent tone and style (analyze existing posts for style matching)
5. Include transitions between sections
6. Write introduction (hook + overview) and conclusion (summary + CTA)
7. Ensure target word count is met (800-2000 words)

**Output:** Complete draft blog post in markdown

#### 6.4 Editor Agent (agent/agents/editor.py)

**Purpose:** Polish and refine the content

**Process:**
1. Review draft for:
   - Clarity and readability
   - Grammar and spelling
   - Consistency in tone
   - Logical flow
   - Redundancy removal
   - Sentence variety
2. Enhance with:
   - Better transitions
   - More engaging language
   - Concrete examples
   - Active voice preference
3. Format properly:
   - Markdown headings
   - Lists and bullets where appropriate
   - Code blocks if technical content
   - Bold/italic emphasis sparingly

**Output:** Polished draft

#### 6.5 SEO Optimizer Agent (agent/agents/seo_optimizer.py)

**Purpose:** Ensure SEO best practices

**Process:**
1. Analyze content for:
   - Keyword density (target: 2%)
   - Heading structure (H1 > H2 > H3 hierarchy)
   - Meta description (155-160 characters)
   - Internal linking opportunities (reference other posts from knowledge base)
   - Image alt text suggestions (if images mentioned)
   - URL slug optimization
2. Generate:
   - Optimized title (50-60 characters)
   - Meta description
   - Suggested tags and categories
   - Related posts for internal linking
   - Featured excerpt (150-200 characters)

**Output:** SEO metadata and recommendations

### 7. Prompt Engineering (agent/prompts/)

Create sophisticated, role-specific prompts for each agent:

**System Prompts Requirements:**
- Clear role definition for each agent
- Specific instructions on input/output format
- Examples of desired output
- Constraints and guidelines
- Context about the existing blog's style and audience

**Template Variables:**
- User topic/specification
- Retrieved context
- Existing post style examples
- SEO requirements
- Word count targets
- Tone/style preferences

### 8. CLI Interface (agent/cli.py)

Build a comprehensive command-line interface:

**Commands:**

```bash
# Ingest knowledge base (first-time setup or update)
python agent/cli.py ingest [--force] [--verbose]

# Generate a blog post
python agent/cli.py generate \
  --topic "Your Topic Here" \
  --style "technical|casual|professional" \
  --length "short|medium|long" \
  --categories "Category1,Category2" \
  --tags "tag1,tag2,tag3" \
  --keywords "primary keyword, secondary keyword" \
  --tone "informative|persuasive|educational" \
  --output "path/to/output.md" \
  --dry-run

# Interactive mode
python agent/cli.py generate --interactive

# Search knowledge base
python agent/cli.py search "query" [--top-k 10]

# View statistics
python agent/cli.py stats
```

**Interactive Mode Requirements:**
- Step-by-step wizard asking for:
  - Topic/title
  - Target audience
  - Desired length
  - Key points to cover
  - Categories and tags
  - SEO keywords
  - Special requirements
- Show progress for each agent phase
- Display preview before saving
- Option to regenerate specific sections
- Ability to provide feedback and iterate

### 9. Output Generation & Validation (agent/utils/)

#### 9.1 Frontmatter Generation

**Required Format:**
```yaml
---
layout: post
title: "Generated Title Here"
date: 2025-10-07 10:30:00 -0500
categories: ["Category1", "Category2"]
tags: ["tag1", "tag2", "tag3"]
excerpt: "150-200 character excerpt for SEO"
slug: "url-safe-slug"
---
```

**Requirements:**
- Auto-generate date in exact format shown (with timezone)
- Ensure title is properly quoted if contains special characters
- Validate categories and tags are lists
- Generate URL-safe slug from title
- Create compelling excerpt if not provided
- Preserve layout: post

#### 9.2 Content Validation

Implement comprehensive validation:

**Checks:**
- Frontmatter is valid YAML
- Required fields present: layout, title, date, categories, tags
- Date format is correct
- Slug is URL-safe (lowercase, hyphens, no special chars)
- Content meets minimum word count
- Proper markdown heading hierarchy (no skipped levels)
- No broken internal links
- Code blocks properly formatted
- Lists properly formatted
- No excessive capitalization or punctuation

**Validation Function:**
```python
def validate_blog_post(content: str) -> Tuple[bool, List[str]]:
    """Returns (is_valid, list_of_errors)"""
```

#### 9.3 File Writing

**Requirements:**
- Compute filename: `YYYY-MM-DD-slug.md`
- Check for collisions (add suffix -1, -2, etc. if needed)
- Write to `content/blog/` with UTF-8 encoding
- Preserve line endings (LF for consistency)
- Create backup of existing file if overwriting
- Log file path and metadata

### 10. Error Handling & Logging

**Comprehensive Error Handling:**
- Ollama connection failures (check if service running, model available)
- Vector DB initialization failures
- Parsing errors (malformed markdown, invalid YAML)
- LLM output format errors (retry with corrected prompt)
- File I/O errors (permissions, disk space)
- Timeout errors (long-running operations)

**Logging:**
- Use Python logging module with multiple levels
- Log file: `.agent_data/logs/agent.log`
- Console output: INFO and above
- File output: DEBUG and above
- Include timestamps, component names, and context

### 11. Advanced Features

#### 11.1 Style Matching

Analyze existing posts to match writing style:
- Average sentence length
- Common phrases and transitions
- Technical depth level
- Use of examples/metaphors
- Formatting patterns

#### 11.2 Topic Planning & Memory

Maintain state across runs:
- Track generated topics (avoid duplicates)
- Maintain topic queue
- Store feedback on generated posts
- Learn from user edits (what gets changed often)

#### 11.3 Iterative Refinement

Support user feedback loop:
- Save draft versions
- Allow section-by-section regeneration
- Accept natural language feedback
- Re-run specific agents (e.g., just SEO pass)

#### 11.4 Content Analysis

Before generation, analyze knowledge base:
- Topic coverage gaps
- Trending themes
- Most referenced posts
- Underutilized categories
- Suggest topics based on gaps

### 12. Testing & Quality Assurance

**Unit Tests:**
- Test each agent independently
- Mock LLM responses for deterministic testing
- Test parsing and validation functions
- Test vector store operations

**Integration Tests:**
- Full pipeline test with sample topic
- Test retrieval quality
- Test output format compliance
- Test error recovery

**Quality Metrics:**
- Content coherence (manual review)
- SEO score (use ahrefs/semrush standards)
- Readability score (Flesch-Kincaid)
- Style consistency (compare to existing posts)

### 13. Documentation

Create comprehensive documentation:

**README.md:**
- Quick start guide
- Installation instructions
- Usage examples
- Configuration options
- Troubleshooting

**Code Documentation:**
- Docstrings for all functions and classes
- Type hints throughout
- Inline comments for complex logic

**User Guide:**
- How to ingest knowledge base
- How to generate posts
- How to customize prompts
- How to interpret agent outputs
- Best practices

### 14. Example Workflow

```bash
# First time setup
cd your-project-directory
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Check Ollama is running
ollama list | grep gpt-oss:20b

# Ingest existing blog posts
python agent/cli.py ingest --verbose

# Generate a blog post
python agent/cli.py generate \
  --topic "Building Agentic Workflows with Python and Ollama" \
  --style "technical" \
  --length "long" \
  --categories "AI & ML,Development" \
  --tags "Python,Ollama,Agents,Workflow" \
  --keywords "agentic workflows, Python automation" \
  --interactive

# Review generated post in content/blog/
# Edit if needed
# Commit to git when satisfied
```

## Success Criteria

The system is successful when:
1. It can ingest 50+ existing blog posts into vector DB in < 5 minutes
2. Semantic search returns relevant context with > 80% relevance
3. Generated posts are 800-2000 words and coherent
4. Output matches exact frontmatter format without manual editing
5. SEO metadata is comprehensive and optimized
6. Generated content naturally incorporates knowledge base insights
7. Writing style matches existing posts
8. CLI is intuitive and provides clear feedback
9. Error handling prevents crashes and provides actionable messages
10. Posts require minimal manual editing (< 5 minutes)

## Implementation Priority

1. **Phase 1 - Foundation (Week 1):**
   - Project structure
   - Configuration system
   - LLM client
   - Basic ingestion pipeline
   - Vector store integration

2. **Phase 2 - Core Agents (Week 2):**
   - Research agent
   - Outliner agent
   - Writer agent
   - Basic CLI

3. **Phase 3 - Polish (Week 3):**
   - Editor agent
   - SEO optimizer
   - Validation system
   - Advanced CLI features

4. **Phase 4 - Enhancement (Week 4):**
   - Style matching
   - Iterative refinement
   - Testing suite
   - Documentation

Build this system with production-quality code: proper error handling, type hints, docstrings, logging, and tests. Make it extensible so new agents can be easily added. Optimize for both development speed and runtime performance. The code should be clean, maintainable, and well-documented.
