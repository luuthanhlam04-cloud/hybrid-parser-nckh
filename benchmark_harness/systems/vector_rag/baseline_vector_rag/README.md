# RAG Baseline

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-Pytest-yellow.svg)](tests/)

A minimum viable RAG (Retrieval-Augmented Generation) system implementing the complete pipeline: web ingestion and HTML distillation, document chunking, semantic embedding, intelligent retrieval with cross-encoder re-ranking, and grounded generation with context injection.

## Features

- **Terminal CLI**: Interactive REPL for querying technical documentation with source attribution
- **Pipeline Orchestration**: End-to-end automation from single HTML page to interactive chat
- **Single-Page HTML Distiller**: Simplified web ingestion for HTML pages containing full text
- **HTML Cleaner**: CSS selector-based noise removal with semantic structure preservation
- **Project Gutenberg Auto-Cleaning**: Auto-detects PG URLs and removes boilerplate, metadata, and TOC
- **Recursive Character Text Splitter**: Intelligently splits text at natural boundaries (paragraphs, sentences, words) before falling back to character-level splitting
- **Configurable Overlap**: Maintains context between chunks with adjustable overlap for better retrieval quality
- **Semantic Preservation**: Prioritizes natural language boundaries to create more meaningful chunks
- **Vector Embeddings**: Converts text chunks to dense vector representations using sentence-transformers
- **Semantic Search**: NumPy-based vector store with cosine similarity search
- **Cross-Encoder Re-ranking**: Enabled by default for improved precision (similarity scores: 0.15-0.38 → 0.75-1.00)
- **Grounded Generation**: Context-aware generation using Gemini Flash with instruction hierarchy to prevent hallucination
- **Model Fallback**: Automatic fallback to gemini-3.5-flash-lite on 429 rate limit errors
- **AI-as-a-Judge Evaluation**: Automated evaluation of Context Precision and Faithfulness metrics using LLMs
- **Grounding Guardrails**: Post-processing checks with confidence thresholds to prevent hallucinations
- **Security-First**: Environment variable management for API keys, prompt injection prevention
- **Containerized**: Docker support for reproducible deployments
- **Tested**: Comprehensive unit tests with pytest (TDD approach)

## Installation

### Prerequisites

- Python 3.11 or higher
- [uv](https://github.com/astral-sh/uv) for fast package management (optional but recommended)
- Google Gemini API key for generation features (free tier available)

### Local Setup

```bash
# Clone the repository
git clone https://github.com/gilbertoesp/rag_baseline.git
cd rag_baseline

# Install dependencies using uv (recommended)
uv sync

# Or using pip
pip install -e ".[dev]"

# Set up environment variables
# Create a .env file with your Gemini API key
echo "GEMINI_API_KEY=your_api_key_here" > .env
```

### Getting a Gemini API Key

1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Sign in with your Google account
3. Create a new API key
4. Add it to your `.env` file: `GEMINI_API_KEY=your_key_here`
5. Free tier allows 15 requests/day per model
6. The system automatically falls back to gemini-3.5-flash-lite on rate limit errors
7. Cross-encoder re-ranking is enabled by default for improved retrieval precision
```

## Usage

### Quick Start: Chat with a Book

```bash
# Chat with "Meditations" by Marcus Aurelius from Project Gutenberg
uv run python src/main.py --url "https://www.gutenberg.org/cache/epub/2680/pg2680-images.html"

# Chat with "Producing Open Source Software" (modern technical book)
uv run python src/main.py --url "https://producingoss.com/en/producingoss.html" --content-selector "div.book"

# Then ask questions interactively:
# "What is this book about?"
# "What are the key concepts?"
# "Describe the ideal Wise Man"
# /stats  # View session statistics
# /quit  # Exit the session
```

**Note**: Cross-encoder re-ranking is now enabled by default for improved retrieval precision. If you previously used `--use-reranking`, this flag has been replaced with `--no-reranking` (opt-out instead of opt-in).

### Web Book Distillation (Programmatic Use)

```python
from src.book_distiller import BookDistiller, HTMLDistiller

# Distill a single page from a URL
book_distiller = BookDistiller(
    url="https://www.gutenberg.org/cache/epub/2680/pg2680-images.html"
)

# Get clean text (compatible with existing chunker)
clean_text = book_distiller.distill_book()
print(f"Distilled {len(clean_text)} characters")

# Process with existing chunker
from src.chunker import RecursiveCharacterTextSplitter
chunker = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

chunks = chunker.split_text(clean_text)
print(f"Split into {len(chunks)} chunks")
```

**HTML Distillation Features:**
- **Junk Removal**: Automatically removes navigation, scripts, styles, and UI elements
- **Project Gutenberg Auto-Cleaning**: Auto-detects PG URLs and removes boilerplate, metadata, and TOC
- **Semantic Preservation**: Maintains headers, paragraphs, lists, and code blocks
- **Technical Doc Awareness**: Preserves code blocks, API tables, and structured data
- **Whitespace Normalization**: Ensures consistent chunking behavior
- **CSS Selector-Based**: Configurable cleaning rules for different documentation sites

**Why Web Distillation Matters:**
- High-quality context construction via data-centric AI
- Removes noise that would dilute semantic vectors
- Preserves semantic hierarchy for better retrieval
- Acts as a clean feed for the existing RAG pipeline

### Terminal CLI for Interactive Book Chat

The CLI reads a **single HTML page** containing the full text of a book and provides an interactive chat interface to ask questions about its content.

**How to Use in Your Terminal:**

```bash
# Navigate to the project directory
cd rag_baseline

# Run the CLI with a single HTML page URL
uv run python src/main.py --url https://producingoss.com/en/producingoss.html --content-selector "div.book"

# Or with Python directly
python src/main.py --url https://producingoss.com/en/producingoss.html --content-selector "div.book"
```

**Finding Books in Single-Page HTML Format:**

Many public domain books are available in single-page HTML format from **Project Gutenberg**:

```bash
# Example: "The Psychology of Management" from Project Gutenberg
uv run python src/main.py --url "https://www.gutenberg.org/cache/epub/16256/pg16256-images.html"

# Example: "Producing Open Source Software" (modern technical book)
uv run python src/main.py --url "https://producingoss.com/en/producingoss.html" --content-selector "div.book"
```

**More Project Gutenberg Examples:**
- Search Project Gutenberg (https://www.gutenberg.org) for books
- Look for the "HTML" format link on book pages (usually ends with `-images.html`)
- Copy the HTML URL and use it with the CLI
- Most Project Gutenberg books work without `--content-selector`

**CLI Flags Explained:**

- `--url` (required): URL of the single HTML page containing the full book text
  - Example: `--url "https://www.gutenberg.org/cache/epub/16256/pg16256-images.html"`
  
- `--content-selector` (optional): CSS selector to extract the main content area
  - Useful when the HTML page contains navigation, sidebars, or other UI elements
  - Example: `--content-selector "div.book"` for Project Gutenberg books
  - Example: `--content-selector "article"` for modern documentation
  - Default: Uses built-in content selectors (article, main, .content, .chapter, .book)
  - Note: Most Project Gutenberg books work without this flag. Modern technical docs may need it.
  
- `--chunk-size` (optional): Maximum characters per chunk for text splitting
  - Smaller chunks = more precise retrieval but more chunks to embed
  - Larger chunks = broader context but less precise retrieval
  - Default: 1000 characters
  - Example: `--chunk-size 800`
  
- `--chunk-overlap` (optional): Characters to overlap between chunks
  - Ensures context is preserved across chunk boundaries
  - Default: 200 characters
  - Example: `--chunk-overlap 100`
  
- `--no-reranking` (optional): Disable cross-encoder re-ranking
  - Re-ranking is enabled by default for improved precision
  - Use this flag to disable re-ranking for faster processing
  - Default: Re-ranking enabled
  
- `--precision-threshold` (optional): Context precision threshold for evaluation
  - Minimum fraction of retrieved chunks that must be relevant
  - Lower = more lenient, Higher = stricter quality control
  - Default: 0.7 (70% of chunks must be relevant)
  - Example: `--precision-threshold 0.8`
  
- `--faithfulness-threshold` (optional): Faithfulness threshold for evaluation
  - Minimum fraction of response claims that must be grounded in context
  - Lower = more lenient, Higher = stricter hallucination prevention
  - Default: 0.8 (80% of claims must be grounded)
  - Example: `--faithfulness-threshold 0.9`
  
- `--guardrail-threshold` (optional): Guardrail confidence threshold
  - Minimum confidence that context can answer the question
  - Lower = more permissive, Higher = more conservative
  - Default: 0.3 (conservative to prevent guessing)
  - Example: `--guardrail-threshold 0.5`
  
- `--disable-evaluation` (optional): Disable quality evaluation
  - Disables AI-as-a-Judge evaluation for faster processing
  - Evaluation is enabled by default
  - Example: `--disable-evaluation`
  
- `--disable-guardrail` (optional): Disable guardrail checks
  - Disables post-processing guardrail checks
  - Guardrail is enabled by default
  - Example: `--disable-guardrail`

**Complete Example with All Flags:**

```bash
uv run python src/main.py \
  --url "https://www.gutenberg.org/cache/epub/16256/pg16256-images.html" \
  --content-selector "div.book" \
  --chunk-size 800 \
  --chunk-overlap 150
```

**CLI Features:**
- **Interactive REPL**: Ask questions about the book content in real-time
- **Source Attribution**: See which chunks provided context for each answer with similarity scores
- **Session Commands**: `/help`, `/stats`, `/quit` for session control
- **Progress Feedback**: Status messages during distillation, chunking, and embedding
- **Rich Terminal Output**: Beautiful colored prompts and responses
- **Model Fallback**: Automatically switches to fallback model on rate limit errors
- **Project Gutenberg Cleaning**: Auto-detects and removes PG boilerplate, metadata, and TOC
- **Cross-Encoder Re-ranking**: Enabled by default for improved retrieval precision

**Orchestration Flow:**
1. Web ingestion: Fetches and distills single HTML page
2. Text chunking: Splits content into manageable chunks
3. Vector embedding: Embeds and indexes all chunks
4. Interactive REPL: Allows querying the indexed content

**Session Commands:**
- `/help` - Display available commands
- `/stats` - Show session statistics (pages processed, chunks indexed, queries asked, re-ranking status, quality metrics)
- `/quality` - Show quality comparison and metrics (average scores, trends, query history)
- `/quit` - Exit the session

**Why Single-Page HTML:**
- More reliable: No network failures during multi-page crawling
- Simpler architecture: Fewer components, less complexity
- Easier to use: Single URL instead of TOC + selector configuration
- Faster: No sequential page fetching with delays
- Project Gutenberg provides thousands of books in this format

**Quality Improvements:**
- **Project Gutenberg Auto-Cleaning**: Automatically detects Project Gutenberg URLs and removes boilerplate (headers, footers, license text), metadata (Title, Author, etc.), and Table of Contents sections. This significantly improves embedding quality by reducing noise. Verified with real PG books showing clean text starting with actual content.
- **Cross-Encoder Re-ranking**: Enabled by default for improved retrieval precision. Two-stage retrieval (bi-encoder + cross-encoder) improves similarity scores from 0.15-0.38 to 0.75-1.00, resulting in highly relevant chunks being retrieved. Real-world testing with "Meditations" shows scores like 0.97, 1.00, and 0.92 for precise queries, with the system correctly identifying the "ideal Wise Man" concept and Greek terms like "αὐταρκής" with high confidence.
- **AI-as-a-Judge Evaluation**: Automated quality assessment using LLMs to evaluate Context Precision and Faithfulness. Shows quality metrics after each response with warnings when thresholds are not met. Enables quality monitoring and comparison over time via `/quality` command.
- **Grounding Guardrails**: Post-processing checks with confidence thresholds to prevent hallucinations. Warns when responses may not be grounded in retrieved context, providing better "I don't know" behavior based on context relevance.

### Quality Evaluation System

The RAG system includes a comprehensive evaluation framework with two main components:

**1. Evaluator (AI-as-a-Judge) - Quality Assessment**
- **Purpose**: Measures and scores RAG output quality using LLMs
- **Context Precision**: Evaluates if retrieved chunks are relevant to the question (threshold: 0.7)
- **Faithfulness**: Evaluates if the response is grounded in the context (threshold: 0.8)
- **Behavior**: Does NOT block responses, only measures quality
- **Use Case**: Quality monitoring, A/B testing, user feedback

**2. Guardrail (Post-Processing) - Safety Enforcement**
- **Purpose**: Prevents ungrounded responses from reaching users
- **Grounding Check**: Evaluates if context can answer the question (threshold: 0.3)
- **Behavior**: Warns when confidence is low (warning-only, not blocking)
- **Use Case**: Safety guarantee, preventing hallucinations

**Quality Feedback Display:**
After each response, the system shows:
- Context Precision score with pass/fail status
- Faithfulness score with pass/fail status
- Guardrail confidence with trigger status
- Warnings if thresholds are not met
- Hallucination warnings if detected

**Quality Comparison Command:**
Use `/quality` to see:
- Average scores over the session
- Trend analysis (improving/degrading)
- Individual query quality history
- Comparison with thresholds

**Configuration:**
- Thresholds are configurable via CLI flags (`--precision-threshold`, `--faithfulness-threshold`, `--guardrail-threshold`)
- Evaluation can be disabled for faster processing (`--disable-evaluation`)
- Guardrail can be disabled if needed (`--disable-guardrail`)
- Default thresholds: Precision 0.7, Faithfulness 0.8, Guardrail 0.3

### Programmatic Usage (Advanced)

If you want to use the components programmatically in your own code:

#### HTML Distillation

```python
from src.book_distiller import HTMLDistiller

# Distill HTML content
distiller = HTMLDistiller()
html_content = """
<html>
<body>
    <nav class="navigation">Skip this</nav>
    <main>
        <h1>Chapter 1: Introduction</h1>
        <p>This is the main content.</p>
        <pre><code>def hello():
    print("Hello, World!")</code></pre>
    </main>
</body>
</html>
"""

clean_text = distiller.distill(html_content)
print(f"Cleaned text: {clean_text}")
```

#### Basic Chunking

```python
from src.chunker import RecursiveCharacterTextSplitter

# Initialize with default settings (1000 chars, 200 overlap)
splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)

# Split your text
text = "Your long document text here..."
chunks = splitter.split_text(text)

print(f"Created {len(chunks)} chunks")
```

#### Custom Separators

```python
# Customize the splitting strategy
splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=100,
    separators=["\n\n", "\n", ". ", " ", ""]
)
chunks = splitter.split_text(text)
```

#### Vector Embeddings and Storage

```python
from src.chunker import RecursiveCharacterTextSplitter
from src.vector_store import EmbeddingModel, VectorStore

# Chunk your document
text = "Your document text..."
chunker = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
chunks = chunker.split_text(text)

# Initialize embedding model and vector store
embedding_model = EmbeddingModel(model_name="all-MiniLM-L6-v2")
vector_store = VectorStore(embedding_model=embedding_model)

# Add chunks to vector store
vector_store.add_chunks_batch(chunks)

print(f"Stored {vector_store.size()} chunks in vector store")
```

#### Semantic Search

```python
from src.retriever import Retriever

# Initialize retriever (without re-ranking)
retriever = Retriever(vector_store=vector_store, use_reranking=False)

# Search for relevant chunks
query = "machine learning algorithms"
results = retriever.retrieve(query, k=5)

for i, result in enumerate(results, 1):
    print(f"{i}. Similarity: {result['similarity']:.4f}")
    print(f"   {result['chunk'][:100]}...")
```

#### Semantic Search with Re-ranking

```python
# Initialize retriever with cross-encoder re-ranking
retriever = Retriever(
    vector_store=vector_store,
    use_reranking=True,
    rerank_model="ms-marco-MiniLM-L-6-v2",
    top_k_for_rerank=20
)

# Search with re-ranking for improved precision
query = "neural networks in deep learning"
results = retriever.retrieve(query, k=5)

for i, result in enumerate(results, 1):
    print(f"{i}. Relevance Score: {result['similarity']:.4f}")
    print(f"   {result['chunk'][:100]}...")
```

#### Grounded Generation

```python
from src.generator import Generator

# Initialize generator with Gemini Flash
generator = Generator(
    model_name="gemini-2.5-flash",
    api_key_env="GEMINI_API_KEY",
    temperature=0.0  # Maximum factuality
)

# Generate response using retrieved context
retrieved_chunks = [result['chunk'] for result in results]
response = generator.generate(retrieved_chunks, user_query)

print(f"Response: {response}")
```

#### End-to-End Pipeline

```python
from src.chunker import RecursiveCharacterTextSplitter
from src.vector_store import EmbeddingModel, VectorStore
from src.retriever import Retriever
from src.generator import Generator

# Step 1: Chunk document
chunker = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
chunks = chunker.split_text(document_text)

# Step 2: Create vector store and embed chunks
embedding_model = EmbeddingModel(model_name="all-MiniLM-L6-v2")
vector_store = VectorStore(embedding_model=embedding_model)
vector_store.add_chunks_batch(chunks)

# Step 3: Retrieve with re-ranking
retriever = Retriever(vector_store=vector_store, use_reranking=True)
results = retriever.retrieve(user_query, k=5)

# Step 4: Generate grounded response
generator = Generator(temperature=0.0)
retrieved_chunks = [result['chunk'] for result in results]
response = generator.generate(retrieved_chunks, user_query)

print(f"Response: {response}")
```

#### Evaluation and Guardrails

```python
from src.eval_guard import Evaluator, Guardrail, evaluate_rag_pipeline

# Initialize evaluator with custom thresholds
evaluator = Evaluator(
    precision_threshold=0.7,    # 70% of retrieved chunks must be relevant
    faithfulness_threshold=0.8  # 80% of response claims must be grounded
)

# Evaluate context precision
question = "What is the capital of France?"
retrieved_chunks = [
    "France is a country in Western Europe.",
    "The capital of France is Paris.",
    "Paris is known for the Eiffel Tower."
]
precision_result = evaluator.evaluate_context_precision(question, retrieved_chunks)
print(f"Context Precision: {precision_result.score:.2f} (Passed: {precision_result.passed})")

# Evaluate faithfulness
context = "The capital of France is Paris. Paris has a population of 2.1 million."
response = "The capital of France is Paris, and it has a population of 2.1 million."
faithfulness_result = evaluator.evaluate_faithfulness(context, response)
print(f"Faithfulness: {faithfulness_result.score:.2f} (Passed: {faithfulness_result.passed})")

# Apply grounding guardrail
guardrail = Guardrail(
    fallback_message="I don't have enough information to answer this question.",
    default_threshold=0.3
)

# Check if response can be grounded
guardrail_result = guardrail.check_grounding(
    question=question,
    context=context,
    threshold=0.3
)

if guardrail_result.triggered:
    print(f"Guardrail triggered: {guardrail_result.fallback_response}")
else:
    print(f"Response allowed with confidence: {guardrail_result.confidence:.2f}")

# Complete pipeline evaluation
results = evaluate_rag_pipeline(
    question=question,
    retrieved_chunks=retrieved_chunks,
    context=context,
    response=response
)
print(f"Overall Passed: {results['overall_passed']}")
```

**Evaluation Metrics:**
- **Context Precision** (threshold: 0.7): Measures fraction of retrieved chunks relevant to the question
- **Faithfulness** (threshold: 0.8): Ensures responses are strictly grounded in provided context
- **Guardrail Confidence** (threshold: 0.3): Post-processing check to prevent hallucinations

**Grounding Principles:**
- Responses must be based ONLY on provided context (ground truth)
- Internal model knowledge is explicitly excluded from RAG responses
- When confidence is low, the system refuses to answer rather than guessing
- This ensures reliability and trustworthiness in production deployments

## Testing

Run the test suite:

```bash
# Using pytest directly
pytest tests/

# With coverage
pytest tests/ --cov=.

# Using uv
uv run pytest tests/

# Run specific test suite
uv run pytest tests/test_eval_guard.py -v
```

**Test Coverage:**
- Unit tests for chunker, vector store, retriever, generator, and distiller
- Evaluation and guardrail tests (context precision, faithfulness, guardrail triggers)
- Web distillation tests (link extraction, HTML cleaning, structural integrity)
- Integration tests for end-to-end pipeline
- TDD approach with comprehensive coverage reporting

## Docker

Build and run the container:

```bash
# Build the image
docker build -t rag_baseline .

# Run tests in container
docker run rag_baseline

# Run with custom command
docker run rag_baseline python -c "from src.chunker import RecursiveCharacterTextSplitter; print('Ready')"

# Run with API key for generation
docker run -e GEMINI_API_KEY=your_key rag_baseline python -c "from src.generator import Generator; print('Ready')"
```

**Docker Features:**
- Uses Python 3.11 slim image for minimal footprint
- Leverages uv for fast, deterministic dependency installation
- Caches sentence-transformer models to avoid repeated downloads
- Supports environment variable injection for API keys

## Project Structure

```
rag_baseline/
├── src/
│   ├── main.py             # Terminal CLI for interactive book chat
│   ├── book_distiller.py   # Single-page HTML distillation for technical docs
│   ├── chunker.py          # Recursive character text splitter implementation
│   ├── vector_store.py     # Embedding model and vector store for semantic search
│   ├── retriever.py        # Retrieval component with cross-encoder re-ranking
│   ├── generator.py        # Grounded generation with context injection
│   └── eval_guard.py      # AI-as-a-Judge evaluation and grounding guardrails
├── tests/
│   ├── test_main.py         # Unit tests for CLI and orchestration
│   ├── test_distiller.py   # Unit tests for HTML distillation
│   ├── test_chunker.py     # Unit tests for chunker
│   ├── test_vector_store.py # Unit tests for vector store
│   ├── test_retriever.py   # Unit tests for retriever
│   ├── test_generator.py   # Unit tests for generator
│   ├── test_eval_guard.py  # Unit tests for evaluation and guardrails
│   └── test_integration.py # End-to-end integration test
├── Dockerfile              # Container configuration
├── pyproject.toml          # Project dependencies and metadata
├── .env.example            # Example environment variables template
└── README.md              # This file
```

## How It Works

The RAG baseline implements a complete retrieval-augmented generation pipeline:

### 1. CLI Orchestration and Web Ingestion
The `main.py` CLI orchestrates the complete RAG pipeline with interactive chat:

**CLI Interface:**
- Accepts `--url` argument for single HTML page URL
- Optional parameters: `--chunk-size`, `--chunk-overlap`, `--use-reranking`
- Rich terminal formatting for beautiful user experience
- Progress feedback during long operations

**Orchestration Flow:**
1. BookDistiller fetches and distills single HTML page
2. RecursiveCharacterTextSplitter chunks the content
3. VectorStore embeds and indexes all chunks
4. Retriever and Generator configured for REPL
5. Interactive REPL allows querying the indexed content

**Data Handoff:**
- Distiller → Chunker: str (single page text) → chunking
- Chunker → VectorStore: List[str] (chunks) → batch embedding
- VectorStore → Retriever: Embedded vectors → similarity search
- Retriever → Generator: Retrieved chunks → context injection

**Interactive REPL:**
- Colored prompts and responses using Rich
- Source attribution showing which chunks provided context
- Session commands: `/help`, `/stats`, `/quit`
- Session statistics tracking

**Why Single-Page Approach:**
- More reliable: No network failures during multi-page crawling
- Simpler architecture: Fewer components, less complexity
- Easier to use: Single URL instead of TOC + selector configuration
- Faster: No sequential page fetching with delays
- Easier to maintain: Less code to debug and update

### 2. Web Ingestion and HTML Distillation
The `BookDistiller` and `HTMLDistiller` enable automated ingestion of technical documentation:

**Single-Page Fetching:**
- Fetches single HTML page containing full text
- HTTP retry logic for robustness
- Handles network errors gracefully

**HTML Distillation:**
- Removes junk tags (nav, script, style, footer) using CSS selectors
- Preserves semantic structure (headers, paragraphs, lists, code blocks)
- Technical documentation awareness (preserves code blocks, API tables)
- Normalizes whitespace for consistent chunking
- Outputs clean text strings compatible with existing chunker

**Why This Matters:**
- High-quality context construction via data-centric AI
- Removes noise that would dilute semantic vectors
- Preserves semantic hierarchy for better retrieval
- Acts as a clean feed for the existing RAG pipeline

### 3. Document Chunking
The `RecursiveCharacterTextSplitter` uses a hierarchical approach:

1. **Try natural boundaries first**: Attempts to split at paragraph boundaries (`\n\n`)
2. **Fallback to line breaks**: If paragraphs are too large, tries line breaks (`\n`)
3. **Word-level splitting**: Falls back to spaces (` `) for sentence boundaries
4. **Character-level splitting**: Final fallback to ensure no chunk exceeds `chunk_size`

This recursive strategy ensures chunks are semantically coherent, which improves retrieval quality.

### 4. Vector Embeddings
- Text chunks are converted to dense vector representations using sentence-transformers
- The default model (`all-MiniLM-L6-v2`) produces 384-dimensional embeddings
- Vectors are L2-normalized for efficient cosine similarity computation
- Normalization allows using dot product as a proxy for cosine similarity (faster computation)

### 5. Vector Storage
- Chunks and their embeddings are stored in a NumPy-based vector store
- Supports both single and batch chunk addition
- Provides brute-force k-NN search using cosine similarity
- Time complexity: O(n × d) where n is number of vectors, d is embedding dimension

### 6. Semantic Retrieval
- User queries are encoded using the same model as document chunks (critical for compatibility)
- Vector similarity search retrieves top-k candidate chunks
- Optional cross-encoder re-ranking refines results for improved precision

### 7. Cross-Encoder Re-ranking
**Why re-ranking is necessary:**
Bi-encoder models compress documents into fixed-dimensional vectors, leading to "dilution" - loss of fine-grained semantic information. Cross-encoders solve this by:
- Scoring query-document pairs directly without compression loss
- Using attention mechanisms to model full query-document interactions
- Providing more accurate relevance scores

**Two-stage approach:**
1. Fast bi-encoder retrieval narrows candidates from millions to hundreds
2. Accurate cross-encoder refines top candidates for final ranking
This balances speed (vector search) with precision (cross-encoder)

### 8. Grounded Generation
The `Generator` component completes the RAG pipeline with context-aware generation:

**Instruction Hierarchy:**
Prompts are structured as System → Context → User Query to prevent prompt injection:
- System instructions (highest priority): Define role and constraints
- Context (marked as ground truth): Retrieved chunks in `<context>` tags
- User query (lowest priority): The actual question to answer

**Why Instruction Hierarchy Matters:**
Without proper hierarchy, user input can override system instructions through prompt injection attacks. The strict hierarchy ensures:
- System instructions cannot be bypassed
- Context is clearly marked as ground truth, not user input
- User queries cannot manipulate the model's behavior

**Context Markers and Hallucination Prevention:**
XML tags like `<context>` and `</context>` create unambiguous boundaries that:
- Signal to the model: "This is factual ground truth"
- Prevent the model from treating context as conversational input
- Reduce "self-delusion" where the model convinces itself of false facts

**Temperature Control:**
- Temperature is set to 0.0 for maximum factuality
- Lower values = more deterministic, factual responses
- Higher values = more creative, but more prone to hallucination
- For RAG, factual accuracy is prioritized over creativity

### 9. Evaluation and Guardrails
The evaluation and guardrail system ensures RAG quality and prevents hallucinations:

**AI-as-a-Judge Evaluation:**
- Uses LLMs to evaluate Context Precision and Faithfulness metrics
- Context Precision: Measures fraction of retrieved chunks relevant to the question (threshold: 0.7)
- Faithfulness: Ensures responses are strictly grounded in provided context (threshold: 0.8)
- Provides consistent, scalable evaluation for production systems

**Grounding Guardrails:**
- Post-processing checks that validate response grounding before reaching users
- Confidence-based thresholds determine when to refuse vs. answer (default: 0.3)
- Overrides LLM output with fallback message when confidence is low
- Prevents guessing when context is irrelevant or insufficient

**Grounding Principles:**
- Ground Truth: Information explicitly present in retrieved context chunks
- Internal Knowledge: Information from model's training data (must be excluded)
- The system must refuse to answer if the answer isn't in the context
- This enforces the RAG contract: answers come from documents, not the model

**Why This Matters:**
- Hallucinations can spread misinformation
- Users trust RAG systems to be factual, not creative
- External knowledge may be outdated or incorrect
- Faithfulness is the core value proposition of RAG over raw LLMs

## License

This project is released under the MIT License. See LICENSE file for details.

## Dependencies

### Core Dependencies
- `sentence-transformers>=2.2.0`: Text embedding models for semantic search
- `numpy>=1.24.0`: Numerical computing for vector operations
- `google-genai>=1.0.0`: Gemini API for generation and evaluation
- `python-dotenv>=1.0.0`: Environment variable management
- `ragas>=0.1.0`: RAG evaluation framework
- `tenacity>=8.0.0`: Retry logic for robust API calls
- `beautifulsoup4>=4.12.0`: HTML parsing and cleaning for web distillation
- `httpx>=0.25.0`: Modern HTTP client for fetching single HTML pages
- `lxml>=4.9.0`: Fast HTML/XML parser for BeautifulSoup
- `rich>=13.0.0`: Terminal formatting and colored output for CLI
- `click>=8.0.0`: Command-line argument parsing and interface

### Development Dependencies
- `pytest>=8.0.0`: Testing framework
- `pytest-cov>=4.0.0`: Code coverage reporting

## Architecture Decisions

### Minimum Viable Architecture (AMV)
This project follows AMV principles:
- **TDD-first**: Tests verify functionality before implementation
- **Container-ready**: Docker support for reproducible deployments
- **Production-grade**: Error handling, retry logic, and fallback mechanisms
- **Well-documented**: Extensive comments explaining design decisions

### Why These Choices?
- **CLI Orchestration**: End-to-end automation from single HTML page to interactive chat with Rich + Click
- **Single-Page HTML Distiller**: Simplified, reliable web ingestion without multi-page crawling complexity
- **CSS Selector-Based Cleaning**: Robust HTML parsing with semantic preservation
- **Recursive Character Text Splitter**: Balances semantic coherence with fixed-size chunks
- **Cross-Encoder Re-ranking**: Improves retrieval precision without sacrificing speed
- **Instruction Hierarchy**: Prevents prompt injection and ensures grounding
- **AI-as-a-Judge Evaluation**: Scalable, consistent evaluation for production systems
- **Post-Processing Guardrails**: Hard safety checks regardless of model behavior

## Contributing

Contributions are welcome! Please ensure:
- All tests pass (`pytest tests/`)
- Code follows existing style and patterns
- New features include tests and documentation
- Commits follow semantic versioning (feat:, fix:, docs:, etc.)

## Environment Variables

The following environment variables are used:

- `GEMINI_API_KEY`: Required for generation functionality. Get your API key from [Google AI Studio](https://makersuite.google.com/app/apikey)

## Performance Considerations

- **Chunk Size**: Larger chunks (1000-2000 chars) provide more context but may reduce precision
- **Overlap**: 10-20% overlap helps maintain context across chunk boundaries
- **Embedding Model**: `all-MiniLM-L6-v2` is fast (80MB) but consider larger models for complex domains
- **Re-ranking**: Adds ~50-100ms per query but significantly improves precision
- **Vector Store**: NumPy-based approach is suitable for <100K chunks. Consider FAISS for larger datasets

## Future Enhancements

- [ ] Add support for FAISS or other vector databases for scalability
- [ ] Implement streaming generation for real-time responses
- [ ] Add support for multiple embedding models
- [ ] Implement document metadata filtering
- [ ] Add citation and source tracking
- [ ] Support for hybrid search (semantic + keyword)
- [ ] Add evaluation metrics and benchmarking suite

## Contributing

Contributions are welcome! Please follow these guidelines:

1. **Fork the repository** and create a feature branch
2. **Write tests** for new functionality following TDD principles
3. **Ensure all tests pass**: `pytest tests/ --cov=.`
4. **Maintain code style** consistent with existing codebase
5. **Update documentation** for any new features or changes
6. **Submit a pull request** with a clear description of changes

### Development Workflow

```bash
# Create a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies in development mode
pip install -e ".[dev]"

# Run tests with coverage
pytest tests/ --cov=. --cov-report=term-missing

# Run specific test file
pytest tests/test_chunker.py -v
```
