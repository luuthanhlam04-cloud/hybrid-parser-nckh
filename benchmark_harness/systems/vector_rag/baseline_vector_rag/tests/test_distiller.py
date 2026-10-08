"""
Test Suite for Single-Page HTML Distiller

This test suite verifies the HTML distillation component:
1. HTML Distillation: Remove junk tags while preserving core content
2. Structural Integrity: Maintain semantic hierarchy for technical documentation
3. Integration: Output compatibility with existing RAG pipeline

Test Philosophy:
- TDD-first: Tests verify functionality before implementation
- Mock HTML responses for deterministic testing
- Technical documentation focus (code blocks, API docs, structured sections)
- Compatibility verification with existing chunker

Why These Tests Matter:
- HTML distillation prevents noise from diluting semantic vectors
- Structural integrity maintains document hierarchy for better retrieval
- Integration tests ensure clean feed to existing RAG pipeline
"""

import pytest
from typing import List
import os
import sys

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from book_distiller import HTMLDistiller, BookDistiller


class TestHTMLDistillation:
    """
    Test suite for HTML distillation and cleaning.
    
    HTML distillation removes noise (nav, script, style) while preserving
    semantic content (headers, paragraphs, code blocks, tables).
    
    Why This Matters:
    - Junk tags dilute semantic vectors with noise
    - Clean HTML preserves the author's semantic intent
    - Technical documentation requires special handling (code blocks, API tables)
    - High-quality input is the foundation of effective RAG systems
    """
    
    def test_remove_junk_tags(self):
        """
        Test removal of junk tags (nav, script, style).
        
        Scenario: HTML with navigation, scripts, and main content.
        Expected: Junk removed, main content preserved.
        """
        html = """
        <html>
        <body>
            <nav class="navigation">Skip this</nav>
            <script>alert('skip this');</script>
            <main>
                <h1>Chapter 1</h1>
                <p>Main content here.</p>
            </main>
        </body>
        </html>
        """
        
        distiller = HTMLDistiller()
        cleaned = distiller.distill(html)
        
        assert "Skip this" not in cleaned
        assert "alert" not in cleaned
        assert "Chapter 1" in cleaned
        assert "Main content here" in cleaned
    
    def test_preserve_code_blocks(self):
        """
        Test preservation of code blocks.
        
        Scenario: HTML with code blocks in <pre> tags.
        Expected: Code blocks preserved with indentation.
        """
        html = """
        <html>
        <body>
            <main>
                <pre><code>def hello():
    print("Hello, World!")</code></pre>
            </main>
        </body>
        </html>
        """
        
        distiller = HTMLDistiller()
        cleaned = distiller.distill(html)
        
        assert "def hello():" in cleaned
        assert 'print("Hello, World!")' in cleaned
    
    def test_preserve_tables(self):
        """
        Test preservation of table structure.
        
        Scenario: HTML with API parameter table.
        Expected: Table converted to readable text format.
        """
        html = """
        <html>
        <body>
            <main>
                <table>
                    <tr><th>Parameter</th><th>Type</th></tr>
                    <tr><td>name</td><td>string</td></tr>
                    <tr><td>age</td><td>integer</td></tr>
                </table>
            </main>
        </body>
        </html>
        """
        
        distiller = HTMLDistiller()
        cleaned = distiller.distill(html)
        
        assert "Parameter" in cleaned
        assert "Type" in cleaned
        assert "name" in cleaned
        assert "string" in cleaned
    
    def test_preserve_headers(self):
        """
        Test preservation of header hierarchy.
        
        Scenario: HTML with h1, h2, h3 headers.
        Expected: Headers converted to markdown style.
        """
        html = """
        <html>
        <body>
            <main>
                <h1>Main Title</h1>
                <h2>Section 1</h2>
                <h3>Subsection 1.1</h3>
                <p>Content here.</p>
            </main>
        </body>
        </html>
        """
        
        distiller = HTMLDistiller()
        cleaned = distiller.distill(html)
        
        assert "# Main Title" in cleaned
        assert "## Section 1" in cleaned
        assert "### Subsection 1.1" in cleaned
    
    def test_normalize_whitespace(self):
        """
        Test whitespace normalization.
        
        Scenario: HTML with excessive spaces and line breaks.
        Expected: Whitespace normalized for consistent chunking.
        """
        html = """
        <html>
        <body>
            <main>
                <p>Test   content    with    spaces</p>
                <p>Line



breaks</p>
            </main>
        </body>
        </html>
        """
        
        distiller = HTMLDistiller()
        cleaned = distiller.distill(html)
        
        # Should not have excessive spaces
        assert "Test   content" not in cleaned
        assert "Test content" in cleaned


class TestStructuralIntegrity:
    """
    Test suite for structural integrity of distilled content.
    
    Structural integrity ensures that the semantic hierarchy of the
    document is preserved, which is critical for retrieval quality.
    
    Why This Matters:
    - Semantic hierarchy provides context for chunking
    - Preserved structure improves retrieval relevance
    - Document organization aids understanding
    - Technical docs rely on structure (APIs, tutorials, reference)
    """
    
    def test_preserve_list_structure(self):
        """
        Test preservation of list structure.
        
        Scenario: HTML with ordered and unordered lists.
        Expected: Lists converted with bullet points or numbering.
        """
        html = """
        <html>
        <body>
            <main>
                <ul>
                    <li>Item 1</li>
                    <li>Item 2</li>
                </ul>
                <ol>
                    <li>Step 1</li>
                    <li>Step 2</li>
                </ol>
            </main>
        </body>
        </html>
        """
        
        distiller = HTMLDistiller()
        cleaned = distiller.distill(html)
        
        assert "• Item 1" in cleaned
        assert "• Item 2" in cleaned
        assert "1. Step 1" in cleaned
        assert "2. Step 2" in cleaned
    
    def test_preserve_blockquotes(self):
        """
        Test preservation of blockquotes.
        
        Scenario: HTML with blockquotes for notes/warnings.
        Expected: Blockquotes preserved with markdown notation.
        """
        html = """
        <html>
        <body>
            <main>
                <blockquote>This is an important note.</blockquote>
            </main>
        </body>
        </html>
        """
        
        distiller = HTMLDistiller()
        cleaned = distiller.distill(html)
        
        assert ">" in cleaned
        assert "important note" in cleaned
    
    def test_content_extraction(self):
        """
        Test extraction of main content area.
        
        Scenario: HTML with sidebar and main content.
        Expected: Only main content extracted, sidebar removed.
        """
        html = """
        <html>
        <body>
            <aside class="sidebar">Skip this sidebar</aside>
            <main>
                <h1>Main Content</h1>
                <p>Important content here.</p>
            </main>
        </body>
        </html>
        """
        
        distiller = HTMLDistiller()
        cleaned = distiller.distill(html)
        
        assert "Skip this sidebar" not in cleaned
        assert "Main Content" in cleaned
        assert "Important content here" in cleaned


class TestBookDistiller:
    """
    Test suite for single-page book distiller.
    
    BookDistiller provides a simple interface for converting web-based
    technical documentation (single HTML page) into clean text strings.
    
    Why This Matters:
    - Simple interface for common use cases
    - Flexible configuration for different documentation sites
    - Zero modifications to existing RAG components
    - Single-page approach is more reliable than multi-page crawling
    """
    
    def test_distill_single_page(self):
        """
        Test distillation of a single HTML page.
        
        Scenario: Single HTML page with content.
        Expected: Clean text string returned.
        """
        # This test would require mocking HTTP requests
        # For now, we test the structure is correct
        distiller = BookDistiller(url="https://example.com/page.html")
        assert distiller.url == "https://example.com/page.html"
        assert distiller.distiller is not None
    
    def test_custom_distiller(self):
        """
        Test using a custom HTMLDistiller instance.
        
        Scenario: Custom cleaning rules provided.
        Expected: Custom distiller used for cleaning.
        """
        custom_distiller = HTMLDistiller(
            junk_selectors=['nav', 'footer'],
            content_selectors=['article']
        )
        
        distiller = BookDistiller(
            url="https://example.com/page.html",
            custom_distiller=custom_distiller
        )
        
        assert distiller.distiller == custom_distiller


class TestIntegration:
    """
    Integration tests for compatibility with existing RAG pipeline.
    
    These tests verify that the distiller output is compatible with
    the existing RecursiveCharacterTextSplitter and RAG pipeline.
    
    Why This Matters:
    - Ensures clean feed to existing RAG pipeline
    - Verifies output format compatibility
    - Tests end-to-end data flow
    """
    
    def test_output_format_compatibility(self):
        """
        Test that output format is compatible with chunker.
        
        Scenario: Distill HTML and verify output format.
        Expected: String output compatible with RecursiveCharacterTextSplitter.
        """
        html = """
        <html>
        <body>
            <main>
                <h1>Test</h1>
                <p>Content for chunking.</p>
            </main>
        </body>
        </html>
        """
        
        distiller = HTMLDistiller()
        cleaned = distiller.distill(html)
        
        # Verify output is string
        assert isinstance(cleaned, str)
        
        # Verify output is not empty
        assert len(cleaned) > 0
    
    def test_empty_html_handling(self):
        """
        Test handling of empty or None HTML.
        
        Scenario: Empty or None HTML input.
        Expected: Returns empty string without errors.
        """
        distiller = HTMLDistiller()
        
        # Test None
        assert distiller.distill(None) == ""
        
        # Test empty string
        assert distiller.distill("") == ""
        
        # Test HTML with no content
        html = "<html><body></body></html>"
        assert distiller.distill(html) == ""


class TestProjectGutenbergCleaning:
    """
    Test suite for Project Gutenberg-specific cleaning rules.
    
    Project Gutenberg books contain specific noise patterns:
    - Boilerplate headers/footers with branding
    - Metadata sections (Title, Author, etc.)
    - Table of Contents (navigation, not content)
    - Translator/editor notes
    
    Why This Matters:
    - PG boilerplate dilutes semantic vectors with noise
    - Metadata sections don't add informational value
    - TOC is navigation, not content
    - Cleaner input improves retrieval quality
    """
    
    def test_pg_url_detection(self):
        """
        Test detection of Project Gutenberg URLs.
        
        Scenario: Various Project Gutenberg URL patterns.
        Expected: Correctly identified as project_gutenberg source type.
        """
        from book_distiller import HTMLDistiller
        
        # Test cache/epub pattern
        distiller1 = HTMLDistiller(url="https://www.gutenberg.org/cache/epub/16256/pg16256-images.html")
        assert distiller1.source_type == "project_gutenberg"
        
        # Test files pattern
        distiller2 = HTMLDistiller(url="https://www.gutenberg.org/files/16256/")
        assert distiller2.source_type == "project_gutenberg"
        
        # Test non-PG URL
        distiller3 = HTMLDistiller(url="https://example.com/book.html")
        assert distiller3.source_type == "generic"
        
        # Test no URL
        distiller4 = HTMLDistiller()
        assert distiller4.source_type == "generic"
    
    def test_pg_boilerplate_removal(self):
        """
        Test removal of Project Gutenberg boilerplate text.
        
        Scenario: HTML with PG branding and license text.
        Expected: Boilerplate removed, content preserved.
        """
        html = """
        <html>
        <body>
            <div class="pg-header">
                Project Gutenberg
                This eBook is for the use of anyone anywhere
            </div>
            <main>
                <h1>Chapter 1</h1>
                <p>This is the actual content.</p>
            </main>
            <div class="pg-footer">
                Project Gutenberg
            </div>
        </body>
        </html>
        """
        
        distiller = HTMLDistiller(url="https://www.gutenberg.org/cache/epub/16256/pg16256-images.html")
        cleaned = distiller.distill(html)
        
        # Verify boilerplate removed
        assert "Project Gutenberg" not in cleaned or cleaned.count("Project Gutenberg") < 2
        assert "This eBook is for the use of anyone anywhere" not in cleaned
        
        # Verify content preserved
        assert "Chapter 1" in cleaned
        assert "This is the actual content" in cleaned
    
    def test_pg_metadata_removal(self):
        """
        Test removal of Project Gutenberg metadata sections.
        
        Scenario: HTML with Title, Author, etc. metadata.
        Expected: Metadata removed, content preserved.
        """
        html = """
        <html>
        <body>
            <p>Title: The Psychology of Management</p>
            <p>Author: Lilli Gilbreth</p>
            <p>Release Date: 1914</p>
            <main>
                <h1>Chapter 1</h1>
                <p>Main content here.</p>
            </main>
        </body>
        </html>
        """
        
        distiller = HTMLDistiller(url="https://www.gutenberg.org/cache/epub/16256/pg16256-images.html")
        cleaned = distiller.distill(html)
        
        # Verify metadata removed
        assert "Title:" not in cleaned
        assert "Author:" not in cleaned
        assert "Release Date:" not in cleaned
        
        # Verify content preserved
        assert "Chapter 1" in cleaned
        assert "Main content here" in cleaned
    
    def test_pg_toc_removal(self):
        """
        Test removal of Table of Contents sections.
        
        Scenario: HTML with TOC section.
        Expected: TOC removed, content preserved.
        """
        html = """
        <html>
        <body>
            <h2>CONTENTS</h2>
            <ul>
                <li>Chapter 1</li>
                <li>Chapter 2</li>
            </ul>
            <h1>Chapter 1</h1>
            <p>Actual content starts here.</p>
        </body>
        </html>
        """
        
        distiller = HTMLDistiller(url="https://www.gutenberg.org/cache/epub/16256/pg16256-images.html")
        cleaned = distiller.distill(html)
        
        # Verify TOC removed
        assert "CONTENTS" not in cleaned
        assert "Chapter 1" not in cleaned or cleaned.count("Chapter 1") <= 1  # Should only appear once in content
        
        # Verify content preserved
        assert "Actual content starts here" in cleaned
    
    def test_generic_cleaning_unaffected(self):
        """
        Test that generic cleaning still works for non-PG URLs.
        
        Scenario: Non-PG URL with standard HTML.
        Expected: Standard cleaning applied, no PG-specific rules.
        """
        html = """
        <html>
        <body>
            <nav>Skip this</nav>
            <main>
                <h1>Chapter 1</h1>
                <p>Content here.</p>
            </main>
        </body>
        </html>
        """
        
        distiller = HTMLDistiller(url="https://example.com/book.html")
        cleaned = distiller.distill(html)
        
        # Verify nav removed (standard cleaning)
        assert "Skip this" not in cleaned
        
        # Verify content preserved
        assert "Chapter 1" in cleaned
        assert "Content here" in cleaned


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
