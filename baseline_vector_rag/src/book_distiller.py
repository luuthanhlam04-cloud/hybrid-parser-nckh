"""
Single-Page HTML Distiller for RAG Ingestion

This module implements simplified web ingestion for RAG systems:
1. Fetches a single HTML page containing full text
2. HTML cleaning to remove noise while preserving semantic content
3. Source-type detection for site-specific cleaning rules
4. Output of clean text strings compatible with existing RAG pipeline

Data-Centric AI Philosophy:
This component focuses on high-quality context construction as a form of
feature engineering. Clean, well-structured input leads to better embeddings,
retrieval, and generation in RAG systems.

Why Single-Page Approach:
- More reliable: No network failures during multi-page crawling
- Simpler architecture: Fewer components, less complexity
- Easier to use: Single URL instead of TOC + selector configuration
- Faster: No sequential page fetching with delays
- Easier to maintain: Less code to debug and update

Why HTML Distillation Matters:
- Junk tags (nav, script, style) dilute semantic vectors with noise
- Clean HTML preserves the author's semantic intent
- Technical documentation requires special handling (code blocks, API tables)
- High-quality input is the foundation of effective RAG systems

Why Source-Type Detection:
- Different sites have different noise patterns (PG, technical docs, etc.)
- Site-specific cleaning rules improve embedding quality
- Project Gutenberg books contain boilerplate that dilutes semantic vectors
- Auto-detection allows optimal cleaning without user configuration

CSS Selector Strategy:
We use CSS selectors rather than regex for HTML parsing because:
- CSS selectors are more robust for hierarchical structures
- They handle malformed HTML better than regex
- They're more maintainable and readable
- They can target specific semantic elements (article, main, .content)
"""

import re
from typing import List, Optional
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential


class HTMLDistiller:
    """
    HTML distiller that removes noise while preserving semantic content.
    
    This class implements intelligent HTML cleaning optimized for technical
    documentation. It removes navigation, scripts, styles, and other noise
    while preserving the semantic structure that matters for RAG systems.
    
    Key Features:
    - CSS selector-based junk removal (nav, footer, script, style)
    - Semantic structure preservation (headers, paragraphs, lists)
    - Technical documentation awareness (code blocks, API tables)
    - Source-type detection for site-specific cleaning (Project Gutenberg, etc.)
    - Whitespace normalization for consistent chunking
    
    Why CSS Selectors:
    CSS selectors are more robust than regex for HTML parsing because:
    - They understand HTML structure and hierarchy
    - They handle malformed HTML gracefully (via BeautifulSoup)
    - They're more maintainable and easier to understand
    - They can target specific classes and IDs common in technical docs
    
    Junk Tag Rationale:
    - <nav>, <footer>: Navigation elements don't add informational value
    - <script>, <style>: Implementation details, not content
    - .sidebar, .advertisement: UI elements, not documentation
    - These tags dilute semantic vectors if included in embeddings
    
    Technical Documentation Awareness:
    - Code blocks (<pre>, <code>) must be preserved for technical accuracy
    - API tables contain critical structured information
    - Syntax highlighting classes should be removed but content preserved
    
    Project Gutenberg Awareness:
    - PG books contain boilerplate headers/footers that dilute embeddings
    - Metadata sections (Title, Author, etc.) should be removed
    - Table of Contents is navigation, not content
    - Translator/editor notes should be removed unless clearly part of content
    
    Args:
        junk_selectors: CSS selectors for elements to remove
                      Default: Common navigation and UI elements
        content_selectors: CSS selectors for main content areas
                          Default: Common documentation container selectors
        preserve_selectors: CSS selectors for elements to always preserve
                          Default: Code blocks and technical content
        url: Optional URL for source-type detection
            If provided, enables site-specific cleaning rules
    """
    
    def __init__(
        self,
        junk_selectors: Optional[List[str]] = None,
        content_selectors: Optional[List[str]] = None,
        preserve_selectors: Optional[List[str]] = None,
        url: Optional[str] = None,
    ):
        """
        Initialize the HTML distiller with configurable cleaning rules.
        
        Args:
            junk_selectors: CSS selectors for elements to remove
            content_selectors: CSS selectors for main content areas
            preserve_selectors: CSS selectors for elements to always preserve
            url: Optional URL for source-type detection
        """
        self.url = url
        self.source_type = self._detect_source_type(url) if url else "generic"
        
        # Default junk selectors: navigation, scripts, styles, UI elements
        # These don't add informational value and dilute semantic vectors
        self.junk_selectors = junk_selectors or [
            'nav', 'footer', 'header', 'aside',
            'script', 'style', 'noscript',
            '.sidebar', '.advertisement', '.banner',
            '.navigation', '.breadcrumbs', '.menu',
            'iframe', 'svg', 'img'  # Images handled separately if needed
        ]
        
        # Add Project Gutenberg-specific junk selectors if detected
        if self.source_type == "project_gutenberg":
            self.junk_selectors.extend([
                '.pg-header', '.pg-footer',
                '.metadata', '.pg-metadata',
                '.toc', 'div.toc', '.contents',
                '.translator-note', '.editor-note',
                'div.pg-boilerplate'
            ])
        
        # Default content selectors: main documentation containers
        # This helps identify the primary content area
        self.content_selectors = content_selectors or [
            'article', 'main', '.content', '.chapter', '.book',
            '#main-content', '#content', '.documentation',
            '.post-content', '.entry-content', 'div.book'
        ]
        
        # Default preserve selectors: technical documentation elements
        # These must be preserved for technical accuracy
        self.preserve_selectors = preserve_selectors or [
            'pre', 'code', '.highlight', '.codehilite',
            'table', '.parameters', '.api-table',
            'blockquote', '.note', '.warning', '.tip'
        ]
    
    def _detect_source_type(self, url: Optional[str]) -> str:
        """
        Detect the source type from URL for site-specific cleaning rules.
        
        Supported source types:
        - "project_gutenberg": Project Gutenberg books (gutenberg.org)
        - "generic": Standard technical documentation
        
        Args:
            url: URL to analyze
        
        Returns:
            Source type identifier string
        """
        if not url:
            return "generic"
        
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            path = parsed.path.lower()
            
            # Project Gutenberg detection
            if "gutenberg.org" in domain:
                # Match patterns like:
                # https://www.gutenberg.org/cache/epub/16256/pg16256-images.html
                # https://www.gutenberg.org/files/16256/
                if "/cache/epub/" in path or "/files/" in path:
                    return "project_gutenberg"
            
            return "generic"
        except Exception:
            return "generic"
    
    def distill(self, html: Optional[str]) -> str:
        """
        Distill HTML to clean text by removing noise and preserving structure.
        
        Distillation Process:
        1. Parse HTML with BeautifulSoup (handles malformed HTML gracefully)
        2. Apply source-type specific cleaning (PG vs generic)
        3. Remove junk elements using CSS selectors
        4. Extract main content area if content selectors provided
        5. Convert HTML structure to clean text format
        6. Normalize whitespace for consistent chunking
        
        Why This Process:
        - Step 1: BeautifulSoup's lenient parsing handles real-world HTML
        - Step 2: Source-type cleaning removes site-specific noise (PG boilerplate)
        - Step 3: Junk removal prevents noise in semantic vectors
        - Step 4: Content extraction focuses on documentation vs UI
        - Step 5: Structure conversion maintains semantic hierarchy
        - Step 6: Whitespace normalization ensures consistent chunking
        
        Args:
            html: Raw HTML string to distill
        
        Returns:
            Cleaned text string ready for RAG ingestion
        """
        if not html:
            return ""
        
        # Parse HTML with lxml parser (faster than html.parser)
        soup = BeautifulSoup(html, 'lxml')
        
        # Apply source-type specific cleaning
        if self.source_type == "project_gutenberg":
            self._apply_pg_cleaning(soup)
        
        # Remove junk elements
        self._remove_junk(soup)
        
        # Extract main content area if possible
        content = self._extract_content(soup)
        
        # Convert to clean text with structure preservation
        text = self._html_to_text(content)
        
        # Normalize whitespace
        text = self._normalize_whitespace(text)
        
        return text
    
    def _remove_junk(self, soup: BeautifulSoup) -> None:
        """
        Remove junk elements using CSS selectors.
        
        Junk elements are those that don't add informational value:
        - Navigation elements (nav, footer, header)
        - Scripts and styles (implementation details)
        - UI elements (sidebar, advertisement, banner)
        
        Why Remove These:
        - They dilute semantic vectors with noise
        - They don't contribute to the document's informational content
        - They can confuse the chunker and retrieval systems
        
        Args:
            soup: BeautifulSoup object to clean
        """
        for selector in self.junk_selectors:
            for element in soup.select(selector):
                # Check if element should be preserved
                if not self._should_preserve(element):
                    element.decompose()
    
    def _should_preserve(self, element) -> bool:
        """
        Check if an element should be preserved despite junk selectors.
        
        Some elements might match junk selectors but contain important content.
        For example, a <nav> might contain a table of contents we want to preserve.
        
        Args:
            element: BeautifulSoup element to check
        
        Returns:
            True if element should be preserved, False otherwise
        """
        # Check if element or its parents match preserve selectors
        for selector in self.preserve_selectors:
            if element.select_one(selector) or element.parent and element.parent.select_one(selector):
                return True
        return False
    
    def _apply_pg_cleaning(self, soup: BeautifulSoup) -> None:
        """
        Apply Project Gutenberg-specific cleaning rules.
        
        Project Gutenberg books contain specific noise patterns:
        - Boilerplate headers/footers with branding
        - Metadata sections (Title, Author, etc.)
        - Table of Contents (navigation, not content)
        - Translator/editor notes
        
        This method removes these elements before generic cleaning.
        
        Args:
            soup: BeautifulSoup object to clean
        """
        # Remove Project Gutenberg boilerplate text
        # Look for common PG patterns in text content
        for element in soup.find_all(string=True):
            if "Project Gutenberg" in element and len(element) < 200:
                # Remove short PG branding text
                if element.parent:
                    element.parent.decompose()
            elif "This eBook is for the use of anyone anywhere" in element:
                # Remove license boilerplate
                if element.parent:
                    element.parent.decompose()
        
        # Remove metadata sections (Title:, Author:, etc.)
        for pattern in ['Title:', 'Author:', 'Translator:', 'Release Date:', 'Language:', 'Produced by:']:
            for element in soup.find_all(string=re.compile(pattern)):
                # Find the parent paragraph/section and remove it
                parent = element.parent
                if parent and parent.name in ['p', 'div', 'span']:
                    parent.decompose()
        
        # Remove Table of Contents sections
        for element in soup.find_all(['h1', 'h2', 'h3']):
            if element.get_text(strip=True).upper() in ['CONTENTS', 'TABLE OF CONTENTS', 'CONTENTS\n']:
                # Remove the TOC section (assume it continues until next major header)
                next_element = element.find_next(['h1', 'h2', 'h3'])
                if next_element:
                    # Remove everything between current header and next header
                    current = element.next_sibling
                    while current and current != next_element:
                        to_remove = current
                        current = current.next_sibling
                        to_remove.decompose()
                element.decompose()
    
    def _extract_content(self, soup: BeautifulSoup) -> BeautifulSoup:
        """
        Extract main content area using content selectors.
        
        Many documentation sites have navigation, sidebars, and other UI
        elements surrounding the main content. This step isolates the
        actual documentation content.
        
        Why Content Extraction:
        - Focuses distillation on documentation vs UI
        - Removes boilerplate that doesn't add value
        - Improves signal-to-noise ratio for embeddings
        
        Args:
            soup: BeautifulSoup object to extract content from
        
        Returns:
            BeautifulSoup object containing main content or original if not found
        """
        for selector in self.content_selectors:
            content = soup.select_one(selector)
            if content:
                # Create a new soup with just the content
                new_soup = BeautifulSoup('<div></div>', 'lxml')
                new_soup.div.replace_with(content.extract())
                return new_soup
        
        # If no content selector matches, return original
        return soup
    
    def _html_to_text(self, soup: BeautifulSoup) -> str:
        """
        Convert HTML structure to clean text preserving semantic hierarchy.
        
        Conversion Strategy:
        - Headers (h1-h6) converted to markdown-style (# Header)
        - Paragraphs preserved with line breaks
        - Lists converted with bullet points or numbering
        - Code blocks preserved with indentation
        - Tables converted to readable text format
        
        Why This Conversion:
        - Maintains semantic hierarchy for better chunking
        - Preserves document structure for retrieval
        - Makes text human-readable while maintaining structure
        - Compatible with existing RecursiveCharacterTextSplitter
        
        Args:
            soup: BeautifulSoup object to convert
        
        Returns:
            Text string with preserved structure
        """
        lines = []
        
        for element in soup.find_all(True):
            if element.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                # Convert headers to markdown style
                level = int(element.name[1])
                prefix = '#' * level
                text = element.get_text(strip=True)
                if text:
                    lines.append(f"{prefix} {text}")
                    lines.append("")  # Empty line after header
            
            elif element.name == 'p':
                text = element.get_text(strip=True)
                if text:
                    lines.append(text)
                    lines.append("")  # Empty line after paragraph
            
            elif element.name == 'ul':
                for li in element.find_all('li', recursive=False):
                    text = li.get_text(strip=True)
                    if text:
                        lines.append(f"• {text}")
                lines.append("")  # Empty line after list
            
            elif element.name == 'ol':
                for i, li in enumerate(element.find_all('li', recursive=False), 1):
                    text = li.get_text(strip=True)
                    if text:
                        lines.append(f"{i}. {text}")
                lines.append("")  # Empty line after list
            
            elif element.name == 'pre':
                # Preserve code blocks with indentation
                text = element.get_text()
                if text.strip():
                    lines.append("```")
                    for line in text.split('\n'):
                        lines.append(f"    {line}")
                    lines.append("```")
                    lines.append("")
            
            elif element.name == 'code' and element.parent.name != 'pre':
                # Inline code
                text = element.get_text(strip=True)
                if text:
                    lines.append(f"`{text}`")
            
            elif element.name == 'table':
                # Convert table to readable text
                self._convert_table(element, lines)
                lines.append("")
        
            elif element.name == 'blockquote':
                text = element.get_text(strip=True)
                if text:
                    lines.append(f"> {text}")
                    lines.append("")
        
        return '\n'.join(lines)
    
    def _convert_table(self, table, lines: List[str]) -> None:
        """
        Convert HTML table to readable text format.
        
        Tables are common in technical documentation for API parameters,
        configuration options, and other structured data. We preserve
        this structure in a readable text format.
        
        Why Table Preservation:
        - API documentation often uses tables for parameters
        - Configuration options are typically presented in tables
        - Structured data aids understanding and retrieval
        
        Args:
            table: BeautifulSoup table element
            lines: List to append converted table content to
        """
        rows = table.find_all('tr')
        if not rows:
            return
        
        for row in rows:
            cells = row.find_all(['th', 'td'])
            if cells:
                text = ' | '.join(cell.get_text(strip=True) for cell in cells)
                lines.append(text)
        
        # Add separator line after header row
        if rows and rows[0].find_all('th'):
            separator = ' | '.join(['---'] * len(rows[0].find_all(['th', 'td'])))
            lines.append(separator)
    
    def _normalize_whitespace(self, text: str) -> str:
        """
        Normalize whitespace for consistent chunking behavior.
        
        Normalization Steps:
        1. Collapse multiple spaces to single spaces
        2. Normalize line endings to \n
        3. Remove excessive blank lines (more than 2 consecutive)
        4. Trim leading/trailing whitespace
        
        Why Whitespace Normalization:
        - Ensures consistent chunking behavior
        - Prevents inconsistent chunk boundaries
        - Improves embedding quality by reducing noise
        - Makes text more predictable for the chunker
        
        Args:
            text: Text to normalize
        
        Returns:
            Normalized text string
        """
        # Collapse multiple spaces
        text = re.sub(r' +', ' ', text)
        
        # Normalize line endings
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        
        # Remove excessive blank lines (more than 2 consecutive)
        text = re.sub(r'\n\n\n+', '\n\n', text)
        
        # Trim leading/trailing whitespace
        text = text.strip()
        
        return text


class BookDistiller:
    """
    Single-page HTML distiller for RAG ingestion.
    
    This class provides a simple interface for converting web-based technical
    documentation (single HTML page) into clean text strings ready for RAG ingestion.
    
    Key Features:
    - Fetches single HTML page containing full text
    - Cleans HTML to remove noise while preserving semantic content
    - Outputs clean text strings compatible with existing chunker
    - Configurable cleaning rules for different documentation sites
    
    Output Format:
    - Returns str - single clean text string
    - Compatible with RecursiveCharacterTextSplitter
    - Ready for direct ingestion into existing RAG pipeline
    
    Why Single-Page Approach:
    - More reliable: No network failures during multi-page crawling
    - Simpler architecture: Fewer components, less complexity
    - Easier to use: Single URL instead of TOC + selector configuration
    - Faster: No sequential page fetching with delays
    - Easier to maintain: Less code to debug and update
    
    Args:
        url: URL of the HTML page containing full text
        custom_distiller: Custom HTMLDistiller instance (optional)
    """
    
    def __init__(
        self,
        url: str,
        custom_distiller: Optional[HTMLDistiller] = None,
    ):
        """
        Initialize the single-page book distiller.
        
        Args:
            url: URL of the HTML page containing full text
            custom_distiller: Custom HTMLDistiller instance
        """
        self.url = url
        # Pass URL to HTMLDistiller for source-type detection
        self.distiller = custom_distiller or HTMLDistiller(url=url)
    
    def distill_book(self) -> str:
        """
        Distill single HTML page to clean text string.
        
        Process:
        1. Fetch HTML page
        2. Distill HTML to clean text
        3. Return clean text string
        
        Args:
            None
        
        Returns:
            Clean text string
        """
        # Fetch HTML page
        html = self._fetch_page(self.url)
        
        # Distill HTML to clean text
        clean_text = self.distiller.distill(html)
        
        return clean_text
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def _fetch_page(self, url: str) -> str:
        """
        Fetch HTML content from URL with retry logic.
        
        Args:
            url: URL to fetch
        
        Returns:
            HTML content as string
        
        Raises:
            httpx.HTTPError: If request fails after retries
        """
        response = httpx.get(url)
        response.raise_for_status()
        return response.text


if __name__ == "__main__":
    # Example usage
    print("Single-Page HTML Distiller for RAG Ingestion")
    print("=" * 50)
    
    # Example: Distill a single page
    distiller = HTMLDistiller()
    
    sample_html = """
    <html>
    <body>
        <nav class="navigation">Skip this</nav>
        <script>alert('skip this');</script>
        <main>
            <h1>Chapter 1: Introduction</h1>
            <p>This is the main content.</p>
            <pre><code>def hello():
    print("Hello, World!")</code></pre>
        </main>
    </body>
    </html>
    """
    
    cleaned = distiller.distill(sample_html)
    print("Cleaned text:")
    print(cleaned)
