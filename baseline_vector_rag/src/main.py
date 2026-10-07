"""
Terminal CLI for Web-Book RAG Orchestration

This module implements a terminal-based interface that orchestrates the Web-Book
Distiller with the RAG pipeline, providing an interactive REPL to ask questions
about ingested technical documentation.

Orchestration Flow:
1. CLI receives URL via Click
2. BookDistiller fetches and distills single HTML page
3. RecursiveCharacterTextSplitter chunks the content
4. VectorStore embeds and indexes all chunks
5. Retriever and Generator are configured
6. Interactive REPL allows querying the indexed content

Data Handoff Documentation:
The critical "Data Handoff" points between components:
- Distiller → Chunker: str (single page text) → chunking
- Chunker → VectorStore: List[str] (chunks) → batch embedding
- VectorStore → Retriever: Embedded vectors → similarity search
- Retriever → Generator: Retrieved chunks → context injection

Why This Matters:
- Orchestration is the glue that makes the system work end-to-end
- Data loss during handoff would silently degrade RAG quality
- Single-page approach is more reliable and simpler
- Source attribution builds trust in the responses
"""

import os
import sys
from typing import List, Dict, Optional, Tuple
from dotenv import load_dotenv

# CLI and terminal formatting
import click
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

# RAG components
from book_distiller import BookDistiller
from chunker import RecursiveCharacterTextSplitter
from vector_store import VectorStore, EmbeddingModel
from retriever import Retriever
from generator import Generator


# Initialize Rich console for beautiful terminal output
console = Console()


class RAGOrchestrator:
    """
    Orchestrates the complete RAG pipeline from URL to interactive REPL.
    
    This class coordinates all components of the RAG system:
    1. Web ingestion via BookDistiller (single-page mode)
    2. Text chunking via RecursiveCharacterTextSplitter
    3. Vector embedding and indexing via VectorStore
    4. Retrieval and generation configuration
    
    Data Handoff Points:
    - BookDistiller.distill_book() returns str (single page text)
    - Single text is chunked into manageable pieces
    - All chunks are used for batch embedding
    - VectorStore.add_chunks_batch() embeds and indexes in one operation
    
    Why This Class:
    - Encapsulates complex orchestration logic
    - Provides clean interface for CLI
    - Makes data flow explicit and documented
    - Facilitates testing and maintenance
    
    Attributes:
        url: URL of the single HTML page
        chunker: Text splitter for chunking content
        vector_store: Vector store for embeddings and search
        retriever: Semantic retriever for queries
        generator: Grounded generator for responses
        content: Cleaned text content
        chunks: List of all text chunks
    """
    
    def __init__(
        self,
        url: str,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        content_selector: Optional[str] = None,
        use_reranking: bool = True,
        precision_threshold: float = 0.7,
        faithfulness_threshold: float = 0.8,
        guardrail_threshold: float = 0.3,
        use_evaluation: bool = True,
        use_guardrail: bool = True,
    ):
        """
        Initialize the RAG orchestrator.
        
        Args:
            url: URL of the single HTML page containing full text
            chunk_size: Maximum characters per chunk
            chunk_overlap: Characters to overlap between chunks
            content_selector: CSS selector for main content area
            use_reranking: Whether to use cross-encoder re-ranking (default: True)
            precision_threshold: Context precision threshold (default: 0.7)
            faithfulness_threshold: Faithfulness threshold (default: 0.8)
            guardrail_threshold: Guardrail confidence threshold (default: 0.3)
            use_evaluation: Whether to enable quality evaluation (default: True)
            use_guardrail: Whether to enable guardrail checks (default: True)
        """
        self.url = url
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.content_selector = content_selector
        self.use_reranking = use_reranking
        self.precision_threshold = precision_threshold
        self.faithfulness_threshold = faithfulness_threshold
        self.guardrail_threshold = guardrail_threshold
        self.use_evaluation = use_evaluation
        self.use_guardrail = use_guardrail
        
        # Lazy initialization of expensive components
        self.vector_store: Optional[VectorStore] = None
        self.retriever: Optional[Retriever] = None
        self.generator: Optional[Generator] = None
        self.evaluator: Optional = None
        self.guardrail: Optional = None
        
        # Data storage
        self.content: str = ""
        self.chunks: List[str] = []
        
        # Session statistics
        self.stats = {
            "pages_processed": 0,
            "chunks_indexed": 0,
            "queries_asked": 0,
            "reranking_enabled": self.use_reranking,
            "evaluation_enabled": self.use_evaluation,
            "guardrail_enabled": self.use_guardrail,
            "avg_context_precision": 0.0,
            "avg_faithfulness": 0.0,
            "guardrail_triggers": 0,
        }
        
        # Quality tracking
        self.quality_history: List[Dict] = []
        
        # Initialize components
        self.chunker = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
    
    def ingest_book(self) -> None:
        """
        Ingest single HTML page to indexed vector store.
        
        Orchestration Steps:
        1. Fetch and distill single HTML page
        2. Chunk the content into manageable pieces
        3. Initialize VectorStore and embed all chunks (batch operation)
        4. Initialize Retriever and Generator for REPL
        
        Data Handoff Validation:
        - Verify distiller returns str (single page text)
        - Verify chunker returns List[str] (chunks)
        - Verify vector store receives all chunks without loss
        
        Why This Method:
        - Encapsulates the complete ingestion pipeline
        - Provides clear error handling at each stage
        - Allows progress feedback to user
        - Makes data flow explicit and testable
        """
        console.print(f"[cyan]📚 Ingesting content from:[/cyan] {self.url}")
        
        # Stage 1: Fetch and distill single page
        console.print("[yellow]⏳ Fetching and distilling page...[/yellow]")
        
        try:
            # Create custom distiller with content selector if provided
            if self.content_selector:
                from book_distiller import HTMLDistiller
                custom_distiller = HTMLDistiller(
                    content_selectors=[self.content_selector]
                )
                distiller = BookDistiller(url=self.url, custom_distiller=custom_distiller)
            else:
                distiller = BookDistiller(url=self.url)
            
            # Get cleaned text
            # Data Handoff: BookDistiller → str (single page text)
            self.content = distiller.distill_book()
            
            if not self.content.strip():
                console.print("[red]❌ No content found. Check URL.[/red]")
                raise ValueError("No content found")
            
            self.stats["pages_processed"] = 1
            console.print(f"[green]✓[/green] Processed page ({len(self.content)} characters)")
            
        except Exception as e:
            console.print(f"[red]❌ Error during distillation:[/red] {e}")
            raise
    
        # Stage 2: Chunk content
        console.print("[yellow]⏳ Chunking content...[/yellow]")
        
        try:
            # Data Handoff: str (single page text) → List[str] (chunks)
            # Chunk the entire content at once since it's a single page
            self.chunks = self.chunker.split_text(self.content)
            
            self.stats["chunks_indexed"] = len(self.chunks)
            console.print(f"[green]✓[/green] Created {len(self.chunks)} chunks")
            
        except Exception as e:
            console.print(f"[red]❌ Error during chunking:[/red] {e}")
            raise
    
        # Stage 3: Embed and index chunks
        console.print("[yellow]⏳ Embedding and indexing chunks...[/yellow]")
        
        try:
            # Initialize vector store with embedding model
            embedding_model = EmbeddingModel()
            self.vector_store = VectorStore(embedding_model=embedding_model)
            
            # Data Handoff: List[str] (all chunks) → batch embedding
            # add_chunks_batch is efficient - embeds all chunks at once
            self.vector_store.add_chunks_batch(self.chunks)
            
            console.print(f"[green]✓[/green] Indexed {len(self.chunks)} chunks")
            
        except Exception as e:
            console.print(f"[red]❌ Error during embedding:[/red] {e}")
            raise
    
        # Stage 4: Configure retriever and generator
        console.print("[yellow]⏳ Configuring RAG components...[/yellow]")
        
        try:
            # Data Handoff: VectorStore → Retriever
            # Retriever uses the vector store for semantic search
            self.retriever = Retriever(
                vector_store=self.vector_store,
                use_reranking=self.use_reranking
            )
            
            # Configure generator (requires API key)
            self.generator = Generator()
            
            reranking_status = "enabled" if self.use_reranking else "disabled"
            console.print(f"[green]✓[/green] RAG components configured (re-ranking: {reranking_status})")
            
        except Exception as e:
            console.print(f"[red]❌ Error during configuration:[/red] {e}")
            raise
    
    def query(self, user_query: str) -> Tuple[str, List[Dict], Dict]:
        """
        Query the indexed book and return response with sources and quality metrics.
        
        Query Pipeline:
        1. Use Retriever to find relevant chunks
        2. Extract chunk texts for generation
        3. Use Generator to produce grounded response
        4. Evaluate context precision (if evaluation enabled)
        5. Evaluate faithfulness (if evaluation enabled)
        6. Check guardrail (if guardrail enabled)
        7. Store quality metrics
        8. Return response with sources and quality metrics
        
        Data Handoff:
        - Retriever.retrieve() returns List[Dict] with "chunk" and "similarity"
        - Extract "chunk" values to get List[str] for generator
        - Generator.generate() uses List[str] (retrieved chunks) and query
        - Return response, sources, and quality metrics
        
        Args:
            user_query: User's question about the book content
        
        Returns:
            Tuple of (response_text, source_chunks, quality_metrics)
        """
        if not self.retriever or not self.generator:
            raise RuntimeError("RAG components not initialized. Call ingest_book() first.")
        
        # Data Handoff: query → Retriever.retrieve() → List[Dict] (retrieved chunks)
        retrieved_results = self.retriever.retrieve(user_query, k=5)
        
        # Extract chunk texts for generation
        # Data Handoff: List[Dict] → List[str] (chunk texts)
        retrieved_chunks = [result["chunk"] for result in retrieved_results]
        
        # Data Handoff: List[str] (retrieved chunks) + query → Generator.generate()
        response = self.generator.generate(retrieved_chunks, user_query)
        
        # Initialize quality metrics
        quality_metrics = {}
        
        # Evaluation: Context Precision and Faithfulness (if enabled)
        if self.use_evaluation:
            # Initialize evaluator if needed
            if not self.evaluator:
                from eval_guard import Evaluator
                self.evaluator = Evaluator(
                    precision_threshold=self.precision_threshold,
                    faithfulness_threshold=self.faithfulness_threshold
                )
            
            # Evaluate context precision
            context = "\n\n".join(retrieved_chunks)
            precision_result = self.evaluator.evaluate_context_precision(
                user_query, retrieved_chunks
            )
            
            # Evaluate faithfulness
            faithfulness_result = self.evaluator.evaluate_faithfulness(
                context, response
            )
            
            quality_metrics = {
                "context_precision": precision_result.score,
                "precision_passed": precision_result.passed,
                "faithfulness": faithfulness_result.score,
                "faithfulness_passed": faithfulness_result.passed,
                "hallucinations": faithfulness_result.details.get("hallucinations", []),
            }
            
            # Update statistics
            self._update_quality_stats(precision_result.score, faithfulness_result.score)
        
        # Guardrail check (if enabled)
        if self.use_guardrail:
            if not self.guardrail:
                from eval_guard import Guardrail
                self.guardrail = Guardrail(
                    evaluator=self.evaluator,
                    default_threshold=self.guardrail_threshold
                )
            
            guardrail_result = self.guardrail.check_grounding(
                user_query, context, threshold=self.guardrail_threshold
            )
            
            quality_metrics["guardrail_confidence"] = guardrail_result.confidence
            quality_metrics["guardrail_triggered"] = guardrail_result.triggered
            
            if guardrail_result.triggered:
                self.stats["guardrail_triggers"] += 1
                # Warning only - don't block, just track
                quality_metrics["guardrail_warning"] = guardrail_result.reason
        
        # Store quality history for comparison
        import time
        self.quality_history.append({
            "query": user_query,
            "timestamp": time.time(),
            **quality_metrics
        })
        
        # Update statistics
        self._update_quality_stats(precision_result.score, faithfulness_result.score)
        
        return response, retrieved_results, quality_metrics
    
    def _update_quality_stats(self, precision: float, faithfulness: float) -> None:
        """
        Update running averages for quality metrics.
        
        Args:
            precision: Context precision score
            faithfulness: Faithfulness score
        """
        # Increment queries_asked first
        self.stats["queries_asked"] += 1
        
        queries = self.stats["queries_asked"]
        if queries == 1:
            self.stats["avg_context_precision"] = precision
            self.stats["avg_faithfulness"] = faithfulness
        else:
            # Update running average
            old_precision = self.stats["avg_context_precision"]
            old_faithfulness = self.stats["avg_faithfulness"]
            self.stats["avg_context_precision"] = (old_precision * (queries - 1) + precision) / queries
            self.stats["avg_faithfulness"] = (old_faithfulness * (queries - 1) + faithfulness) / queries


def run_repl(orchestrator: RAGOrchestrator) -> None:
    """
    Run interactive REPL for querying the indexed book.
    
    REPL Features:
    - Colored prompts and responses using Rich
    - Source attribution showing which chunks provided context
    - Session commands: /help, /stats, /quit
    - Session statistics tracking
    - Graceful exit handling
    
    Why REPL:
    - Provides interactive exploration of book content
    - Immediate feedback improves user experience
    - Session commands give user control
    - Source attribution builds trust
    
    Args:
        orchestrator: Configured RAGOrchestrator instance
    """
    # Display welcome message
    welcome_text = Text()
    welcome_text.append("📖 ", style="bold cyan")
    welcome_text.append("Web-Book RAG Chat", style="bold white")
    welcome_text.append("\n\n", style="white")
    welcome_text.append("Ask questions about the book content.", style="dim")
    welcome_text.append("\n", style="dim")
    welcome_text.append("Commands: /help, /stats, /quality, /quit", style="dim")
    
    console.print(Panel(welcome_text, border_style="cyan"))
    
    while True:
        try:
            # Get user input
            console.print("\n[cyan]You:[/cyan] ", end="")
            user_input = input().strip()
            
            # Handle empty input
            if not user_input:
                continue
            
            # Handle session commands
            if user_input.lower() in ['/quit', '/exit']:
                console.print("[yellow]👋 Goodbye![/yellow]")
                break
            
            elif user_input.lower() == '/help':
                display_help()
                continue
            
            elif user_input.lower() == '/stats':
                display_stats(orchestrator)
                continue
            
            elif user_input.lower() == '/quality':
                display_quality_comparison(orchestrator)
                continue
            
            # Process query
            console.print("[yellow]🤔 Processing...[/yellow]")
            
            try:
                response, sources, quality_metrics = orchestrator.query(user_input)
                
                # Display response
                console.print("\n[green]Assistant:[/green]")
                console.print(Panel(response, border_style="green"))
                
                # Display source attribution
                display_sources(sources)
                
                # Display quality feedback (always show)
                if quality_metrics:
                    display_quality_feedback(quality_metrics)
                
            except Exception as e:
                console.print(f"[red]❌ Error processing query:[/red] {e}")
                console.print("[dim]Try rephrasing your question or check if the content exists in the book.[/dim]")
        
        except KeyboardInterrupt:
            console.print("\n[yellow]👋 Goodbye![/yellow]")
            break
        except EOFError:
            console.print("\n[yellow]👋 Goodbye![/yellow]")
            break


def display_help() -> None:
    """Display help information for session commands."""
    help_text = Text()
    help_text.append("Session Commands:\n\n", style="bold cyan")
    help_text.append("/help      ", style="white")
    help_text.append("- Show this help message\n", style="dim")
    help_text.append("/stats     ", style="white")
    help_text.append("- Show session statistics\n", style="dim")
    help_text.append("/quality   ", style="white")
    help_text.append("- Show quality comparison and metrics\n", style="dim")
    help_text.append("/quit      ", style="white")
    help_text.append("- Exit the session\n", style="dim")
    
    console.print(Panel(help_text, title="Help", border_style="cyan"))


def display_stats(orchestrator: RAGOrchestrator) -> None:
    """Display session statistics."""
    stats_text = Text()
    stats_text.append(f"Pages processed: {orchestrator.stats['pages_processed']}\n", style="white")
    stats_text.append(f"Chunks indexed: {orchestrator.stats['chunks_indexed']}\n", style="white")
    stats_text.append(f"Queries asked: {orchestrator.stats['queries_asked']}\n", style="white")
    reranking_status = "enabled" if orchestrator.stats['reranking_enabled'] else "disabled"
    stats_text.append(f"Re-ranking: {reranking_status}\n", style="white")
    
    # Add quality metrics if evaluation enabled
    if orchestrator.stats.get("evaluation_enabled"):
        stats_text.append(f"Avg Context Precision: {orchestrator.stats['avg_context_precision']:.2f}\n", style="white")
        stats_text.append(f"Avg Faithfulness: {orchestrator.stats['avg_faithfulness']:.2f}\n", style="white")
        stats_text.append(f"Guardrail Triggers: {orchestrator.stats['guardrail_triggers']}\n", style="white")
    
    console.print(Panel(stats_text, title="Session Statistics", border_style="cyan"))


def display_sources(sources: List[Dict]) -> None:
    """
    Display source attribution for the response.
    
    Source Attribution:
    - Shows which chunks provided context for the response
    - Includes similarity scores for transparency
    - Helps users verify response grounding
    
    Why Source Attribution:
    - Builds trust in the system
    - Allows users to verify information
    - Provides transparency in AI responses
    - Helps debug incorrect responses
    
    Args:
        sources: List of retrieved chunk dictionaries with similarity scores
    """
    if not sources:
        return
    
    sources_text = Text()
    sources_text.append("Sources:\n", style="bold cyan")
    
    for i, source in enumerate(sources[:3], 1):  # Show top 3 sources
        similarity = source.get("similarity", 0.0)
        chunk_preview = source["chunk"][:100] + "..." if len(source["chunk"]) > 100 else source["chunk"]
        sources_text.append(f"{i}. Similarity: {similarity:.2f}\n", style="dim")
        sources_text.append(f"   {chunk_preview}\n\n", style="dim")
    
    console.print(Panel(sources_text, title="Sources", border_style="dim"))


def display_quality_feedback(quality_metrics: Dict) -> None:
    """
    Display quality metrics to user.
    
    Shows:
    - Context precision score and pass/fail status
    - Faithfulness score and pass/fail status
    - Guardrail confidence and trigger status
    - Warnings if thresholds not met
    - Hallucination warnings if detected
    
    Args:
        quality_metrics: Dictionary with quality evaluation results
    """
    quality_text = Text()
    quality_text.append("📊 Quality Metrics:\n\n", style="bold cyan")
    
    # Context precision
    precision = quality_metrics.get("context_precision", 0.0)
    precision_passed = quality_metrics.get("precision_passed", True)
    precision_color = "green" if precision_passed else "yellow"
    quality_text.append(f"Context Precision: {precision:.2f} ", style="white")
    quality_text.append("✓" if precision_passed else "⚠", style=precision_color)
    quality_text.append("\n", style="white")
    
    # Faithfulness
    faithfulness = quality_metrics.get("faithfulness", 0.0)
    faithfulness_passed = quality_metrics.get("faithfulness_passed", True)
    faithfulness_color = "green" if faithfulness_passed else "yellow"
    quality_text.append(f"Faithfulness: {faithfulness:.2f} ", style="white")
    quality_text.append("✓" if faithfulness_passed else "⚠", style=faithfulness_color)
    quality_text.append("\n", style="white")
    
    # Guardrail
    guardrail_confidence = quality_metrics.get("guardrail_confidence", 0.0)
    guardrail_triggered = quality_metrics.get("guardrail_triggered", False)
    guardrail_color = "green" if not guardrail_triggered else "yellow"
    quality_text.append(f"Guardrail Confidence: {guardrail_confidence:.2f} ", style="white")
    quality_text.append("✓" if not guardrail_triggered else "⚠", style=guardrail_color)
    quality_text.append("\n", style="white")
    
    # Warnings
    warnings = []
    if not precision_passed:
        warnings.append(f"Low context precision ({precision:.2f} < 0.7)")
    if not faithfulness_passed:
        warnings.append(f"Low faithfulness ({faithfulness:.2f} < 0.8)")
    if guardrail_triggered:
        warnings.append(f"Guardrail triggered (confidence: {guardrail_confidence:.2f} < 0.3)")
    
    hallucinations = quality_metrics.get("hallucinations", [])
    if hallucinations:
        warnings.append(f"Potential hallucinations: {len(hallucinations)} claims")
    
    if warnings:
        quality_text.append("\n⚠️ Warnings:\n", style="yellow")
        for warning in warnings:
            quality_text.append(f"  • {warning}\n", style="dim")
    
    console.print(Panel(quality_text, title="Quality Assessment", border_style="cyan"))


def display_quality_comparison(orchestrator: RAGOrchestrator) -> None:
    """
    Display quality comparison over session.
    
    Shows:
    - Average scores over session
    - Trend analysis (improving/degrading)
    - Individual query quality history
    - Comparison with thresholds
    
    Args:
        orchestrator: RAGOrchestrator instance with quality history
    """
    if not orchestrator.quality_history:
        console.print("[dim]No quality data available yet. Ask some questions first.[/dim]")
        return
    
    comparison_text = Text()
    comparison_text.append("📈 Quality Comparison:\n\n", style="bold cyan")
    
    # Calculate averages
    avg_precision = sum(m.get("context_precision", 0) for m in orchestrator.quality_history) / len(orchestrator.quality_history)
    avg_faithfulness = sum(m.get("faithfulness", 0) for m in orchestrator.quality_history) / len(orchestrator.quality_history)
    avg_guardrail = sum(m.get("guardrail_confidence", 0) for m in orchestrator.quality_history) / len(orchestrator.quality_history)
    
    # Display averages
    comparison_text.append(f"Average Context Precision: {avg_precision:.2f}\n", style="white")
    comparison_text.append(f"Average Faithfulness: {avg_faithfulness:.2f}\n", style="white")
    comparison_text.append(f"Average Guardrail Confidence: {avg_guardrail:.2f}\n", style="white")
    
    # Display trend
    if len(orchestrator.quality_history) >= 2:
        recent = orchestrator.quality_history[-3:]
        recent_avg = sum(m.get("faithfulness", 0) for m in recent) / len(recent)
        overall_avg = avg_faithfulness
        trend = "improving" if recent_avg > overall_avg else "stable"
        comparison_text.append(f"\nTrend: {trend}\n", style="green" if trend == "improving" else "dim")
    
    # Display individual query history
    comparison_text.append(f"\nQuery History ({len(orchestrator.quality_history)} queries):\n", style="bold white")
    for i, metrics in enumerate(orchestrator.quality_history[-5:], 1):  # Last 5 queries
        query_preview = metrics.get("query", "")[:30] + "..." if len(metrics.get("query", "")) > 30 else metrics.get("query", "")
        precision = metrics.get("context_precision", 0)
        faithfulness = metrics.get("faithfulness", 0)
        comparison_text.append(f"{i}. {query_preview}\n", style="dim")
        comparison_text.append(f"   Precision: {precision:.2f}, Faithfulness: {faithfulness:.2f}\n", style="white")
    
    console.print(Panel(comparison_text, title="Quality Comparison", border_style="cyan"))


@click.command()
@click.option('--url', required=True, help='URL of the HTML page containing full text')
@click.option('--chunk-size', type=int, default=1000, help='Maximum characters per chunk')
@click.option('--chunk-overlap', type=int, default=200, help='Characters to overlap between chunks')
@click.option('--content-selector', default=None, help='CSS selector for main content area')
@click.option('--no-reranking', is_flag=True, help='Disable cross-encoder re-ranking (enabled by default)')
@click.option('--precision-threshold', type=float, default=0.7, help='Context precision threshold (default: 0.7)')
@click.option('--faithfulness-threshold', type=float, default=0.8, help='Faithfulness threshold (default: 0.8)')
@click.option('--guardrail-threshold', type=float, default=0.3, help='Guardrail confidence threshold (default: 0.3)')
@click.option('--disable-evaluation', is_flag=True, help='Disable quality evaluation')
@click.option('--disable-guardrail', is_flag=True, help='Disable guardrail checks')
def main(url: str, chunk_size: int, chunk_overlap: int, content_selector: str, no_reranking: bool, precision_threshold: float, faithfulness_threshold: float, guardrail_threshold: float, disable_evaluation: bool, disable_guardrail: bool):
    """
    Web-Book RAG CLI - Interactive chat with technical documentation.
    
    This CLI orchestrates the complete RAG pipeline:
    1. Fetches and distills single HTML page
    2. Chunks, embeds, and indexes the content
    3. Launches interactive REPL for querying
    
    Example usage:
        python src/main.py --url https://docs.example.com/book/full-text.html
        python src/main.py --url https://docs.example.com/book/full-text.html --chunk-size 800
        python src/main.py --url https://docs.example.com/book/full-text.html --content-selector "div.book"
        python src/main.py --url https://docs.example.com/book/full-text.html --no-reranking
    """
    # Load environment variables (for API keys)
    load_dotenv()
    
    # Validate URL
    if not url.startswith(('http://', 'https://')):
        console.print("[red]❌ Invalid URL. Must start with http:// or https://[/red]")
        sys.exit(1)
    
    # Initialize orchestrator (re-ranking enabled by default)
    orchestrator = RAGOrchestrator(
        url=url,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        content_selector=content_selector,
        use_reranking=not no_reranking,  # Invert flag: --no-reranking means False
        precision_threshold=precision_threshold,
        faithfulness_threshold=faithfulness_threshold,
        guardrail_threshold=guardrail_threshold,
        use_evaluation=not disable_evaluation,
        use_guardrail=not disable_guardrail,
    )
    
    try:
        # Ingest the book
        orchestrator.ingest_book()
        
        # Run interactive REPL
        run_repl(orchestrator)
        
    except KeyboardInterrupt:
        console.print("\n[yellow]👋 Interrupted by user.[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"[red]❌ Fatal error:[/red] {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
