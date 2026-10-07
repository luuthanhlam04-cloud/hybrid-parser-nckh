"""
TDD Test Suite for Recursive Character Text Splitter

These tests define the expected behavior of the chunker before implementation.
Following TDD principles: tests first, implementation second.
"""

import pytest
import sys
import os

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from chunker import RecursiveCharacterTextSplitter


class TestChunkCount:
    """Verify the chunker generates the correct number of chunks for sample text."""
    
    def test_simple_text_no_overlap(self):
        """With no overlap, chunks should be evenly divided by chunk_size."""
        text = "A" * 100  # 100 characters
        splitter = RecursiveCharacterTextSplitter(chunk_size=50, chunk_overlap=0)
        chunks = splitter.split_text(text)
        
        assert len(chunks) == 2, f"Expected 2 chunks, got {len(chunks)}"
        assert all(len(chunk) == 50 for chunk in chunks), "Each chunk should be exactly 50 characters"
    
    def test_simple_text_with_overlap(self):
        """With overlap, more chunks are needed to cover the full text."""
        text = "A" * 100  # 100 characters
        splitter = RecursiveCharacterTextSplitter(chunk_size=50, chunk_overlap=10)
        chunks = splitter.split_text(text)
        
        # With 50 char chunks and 10 char overlap:
        # Chunk 1: 0-50, Chunk 2: 40-90, Chunk 3: 80-100 (partial)
        assert len(chunks) == 3, f"Expected 3 chunks with overlap, got {len(chunks)}"
    
    def test_text_shorter_than_chunk_size(self):
        """Text shorter than chunk_size should return single chunk."""
        text = "Short text"
        splitter = RecursiveCharacterTextSplitter(chunk_size=100, chunk_overlap=0)
        chunks = splitter.split_text(text)
        
        assert len(chunks) == 1, f"Expected 1 chunk for short text, got {len(chunks)}"
        assert chunks[0] == text, "Single chunk should contain the full text"


class TestOverlapAccuracy:
    """Verify overlap is mathematically accurate between consecutive chunks."""
    
    def test_overlap_percentage_calculation(self):
        """Calculate overlap as percentage and verify it matches configuration."""
        text = "A" * 100
        chunk_size = 50
        chunk_overlap = 10  # 20% of chunk_size
        
        splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        chunks = splitter.split_text(text)
        
        # Check overlap between consecutive chunks
        for i in range(len(chunks) - 1):
            current_chunk = chunks[i]
            next_chunk = chunks[i + 1]
            
            # The overlap is the suffix of current_chunk that matches prefix of next_chunk
            overlap_length = len(current_chunk) - chunk_overlap  # Start position of overlap in current chunk
            overlap_text = current_chunk[overlap_length:]
            
            # Verify this overlap appears at the start of next chunk
            assert next_chunk.startswith(overlap_text), \
                f"Chunk {i+1} should start with overlap from chunk {i}"
            
            # Verify exact overlap length
            actual_overlap = len(overlap_text)
            assert actual_overlap == chunk_overlap, \
                f"Expected overlap of {chunk_overlap}, got {actual_overlap}"
    
    def test_zero_overlap(self):
        """Zero overlap means chunks should be adjacent with no shared text."""
        # Use unique characters to ensure no natural repetition
        text = "".join(chr(i) for i in range(65, 145))  # 80 unique characters
        splitter = RecursiveCharacterTextSplitter(chunk_size=40, chunk_overlap=0)
        chunks = splitter.split_text(text)
        
        for i in range(len(chunks) - 1):
            # Last character of current chunk should not appear in next chunk
            assert chunks[i][-1] not in chunks[i+1], \
                "Chunks should have no overlap when chunk_overlap=0"
    
    def test_large_overlap(self):
        """Large overlap (e.g., 50%) should still be mathematically accurate."""
        text = "A" * 100
        chunk_size = 40
        chunk_overlap = 20  # 50% overlap
        
        splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        chunks = splitter.split_text(text)
        
        # Verify overlap between first two chunks
        overlap_text = chunks[0][chunk_size - chunk_overlap:]  # Last 20 chars of first chunk
        assert chunks[1].startswith(overlap_text), \
            "Large overlap should still be accurate"


class TestRecursiveSplitting:
    """Verify the recursive nature of splitting at natural boundaries."""
    
    def test_splits_at_newlines_first(self):
        """Recursive splitter should prefer splitting at newlines over mid-sentence."""
        text = "First sentence.\nSecond sentence.\nThird sentence."
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=30, 
            chunk_overlap=0,
            separators=["\n", ".", " "]  # Newlines prioritized
        )
        chunks = splitter.split_text(text)
        
        # Should split at newline if possible, not mid-sentence
        assert "\n" not in chunks[0] or chunks[0].endswith("\n"), \
            "Should prefer splitting at newline boundaries"
    
    def test_fallback_to_space(self):
        """When no preferred separator found, fall back to space."""
        text = "No natural boundaries here just a long continuous string of text without breaks"
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=20,
            chunk_overlap=0,
            separators=["\n", ".", " "]
        )
        chunks = splitter.split_text(text)
        
        # Should eventually split at space when other separators unavailable
        assert len(chunks) > 1, "Should split text even without preferred separators"


class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_empty_text(self):
        """Empty text should return empty list or single empty chunk."""
        splitter = RecursiveCharacterTextSplitter(chunk_size=50, chunk_overlap=0)
        chunks = splitter.split_text("")
        
        assert len(chunks) == 0 or (len(chunks) == 1 and chunks[0] == ""), \
            "Empty text should return empty list or single empty chunk"
    
    def test_overlap_greater_than_chunk_size(self):
        """Overlap cannot exceed chunk size - should raise ValueError."""
        text = "A" * 50
        with pytest.raises(ValueError, match="chunk_overlap.*must be less than chunk_size"):
            splitter = RecursiveCharacterTextSplitter(chunk_size=30, chunk_overlap=40)
    
    def test_single_character_chunks(self):
        """Minimum chunk size of 1 character should work."""
        text = "ABC"
        splitter = RecursiveCharacterTextSplitter(chunk_size=1, chunk_overlap=0)
        chunks = splitter.split_text(text)
        
        assert len(chunks) == 3, "Should create 3 single-character chunks"
        assert chunks == ["A", "B", "C"], "Each chunk should be a single character"
