"""
Recursive Character Text Splitter for RAG Ingestion

This module implements a robust text chunking strategy that:
1. Recursively tries to split text at natural boundaries (newlines, sentences, words)
2. Maintains configurable overlap between chunks for context preservation
3. Falls back to character-level splitting when no natural boundaries exist

The recursive approach ensures chunks are more semantically meaningful than
arbitrary character splits, which improves retrieval quality in RAG systems.
"""

from typing import List, Optional


class RecursiveCharacterTextSplitter:
    """
    Splits text into chunks by trying to split at natural boundaries first.
    
    The splitter works recursively: it tries to split text using the first separator,
    and if the resulting chunks are still too large, it tries the next separator,
    and so on. This preserves sentence and word boundaries when possible.
    
    Args:
        chunk_size: Maximum number of characters per chunk
        chunk_overlap: Number of characters to overlap between consecutive chunks
        separators: List of separators to try, in order of preference.
                   Default: ["\n\n", "\n", " ", ""]
                   - "\n\n" splits at paragraph boundaries first
                   - "\n" splits at line boundaries second  
                   - " " splits at word boundaries third
                   - "" (empty string) is the fallback for character-level splitting
        length_function: Function to measure chunk length (default: len)
    
    Attributes:
        chunk_size: Maximum characters per chunk
        chunk_overlap: Characters to overlap between chunks
        separators: Ordered list of splitting preferences
    """
    
    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        separators: Optional[List[str]] = None,
        length_function: callable = len,
    ):
        # Validate overlap doesn't exceed chunk size
        if chunk_overlap >= chunk_size:
            raise ValueError(
                f"chunk_overlap ({chunk_overlap}) must be less than chunk_size ({chunk_size})"
            )
        
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.length_function = length_function
        
        # Default separators prioritize natural language boundaries
        # This makes chunks more semantically coherent for RAG retrieval
        if separators is None:
            self.separators = ["\n\n", "\n", " ", ""]
        else:
            self.separators = separators
    
    def split_text(self, text: str) -> List[str]:
        """
        Split input text into chunks using recursive boundary detection.
        
        The algorithm:
        1. Try to split text using the highest-priority separator
        2. If chunks are still too large, recursively try next separator
        3. Once chunks are small enough, apply overlap between consecutive chunks
        4. Return final list of chunks with proper overlap
        
        Args:
            text: Input text to be chunked
            
        Returns:
            List of text chunks with overlap between consecutive chunks
        """
        if not text:
            return []
        
        # Step 1: Recursively split text until chunks fit within chunk_size
        # This tries to preserve natural boundaries (paragraphs, sentences, words)
        final_chunks = self._split_text_recursive(text, self.separators)
        
        # Step 2: Apply overlap between consecutive chunks
        # Overlap ensures context continuity between chunks for better retrieval
        chunks_with_overlap = self._add_overlap(final_chunks)
        
        return chunks_with_overlap
    
    def _split_text_recursive(self, text: str, separators: List[str]) -> List[str]:
        """
        Recursively split text using separators in priority order.
        
        This is the core recursive logic:
        - Try splitting with the first (highest priority) separator
        - If any resulting chunk is still too large, try the next separator
        - Continue until all chunks fit within chunk_size
        - Empty string separator is the fallback for character-level splitting
        
        Args:
            text: Text to split
            separators: Remaining separators to try (ordered by priority)
            
        Returns:
            List of chunks that fit within chunk_size
        """
        # Base case: no separators left, do character-level splitting
        if not separators:
            return self._split_by_character(text)
        
        # Try splitting with the current separator
        separator = separators[0]
        
        # Handle empty string separator as special case for character-level splitting
        # Python's str.split() raises ValueError for empty separator
        if separator == "":
            return self._split_by_character(text)
        
        separator_splits = text.split(separator)
        
        # Check if any split exceeds chunk_size
        # If yes, we need to try the next separator (more aggressive splitting)
        if any(self.length_function(split) > self.chunk_size for split in separator_splits):
            # Recursively try next separator with lower priority
            return self._split_text_recursive(text, separators[1:])
        
        # All chunks fit within chunk_size, return them
        # Filter out empty strings that can result from consecutive separators
        return [split for split in separator_splits if split]
    
    def _split_by_character(self, text: str) -> List[str]:
        """
        Fallback method: split text into fixed-size character chunks using sliding window.
        
        This is used when no natural boundaries can be found within chunk_size.
        It's a last resort to ensure we don't exceed the maximum chunk size.
        Uses the same sliding window approach as _add_overlap for consistency.
        
        Args:
            text: Text to split character-by-character
            
        Returns:
            List of character-level chunks within chunk_size
        """
        chunks = []
        text_length = self.length_function(text)
        
        # Calculate the stride (step size) between chunk start positions
        # This ensures consistent overlap when applied
        stride = self.chunk_size - self.chunk_overlap
        
        # Iterate through text with stride, extracting chunks
        for i in range(0, text_length, stride):
            # Extract chunk from current position to current position + chunk_size
            chunk = text[i:i + self.chunk_size]
            if chunk:  # Only add non-empty chunks
                chunks.append(chunk)
        
        return chunks
    
    def _add_overlap(self, chunks: List[str]) -> List[str]:
        """
        Add overlap between consecutive chunks using sliding window approach.
        
        Overlap is crucial for RAG systems because:
        - It preserves context that might be split across chunk boundaries
        - It improves retrieval by providing multiple entry points to the same content
        - It reduces the chance of missing relevant information at chunk edges
        
        Uses a sliding window approach where each chunk starts chunk_overlap characters
        before the previous chunk's end position. This ensures consistent overlap size.
        
        Args:
            chunks: List of chunks without overlap
            
        Returns:
            List of chunks with overlap applied between consecutive chunks
        """
        if len(chunks) <= 1:
            return chunks
        
        # Reconstruct the full text from chunks to apply sliding window
        full_text = "".join(chunks)
        text_length = self.length_function(full_text)
        
        chunks_with_overlap = []
        # Calculate stride: how many characters to move forward for each chunk
        # This ensures consistent overlap between all consecutive chunks
        stride = self.chunk_size - self.chunk_overlap
        
        # Build chunks using sliding window
        for i in range(0, text_length, stride):
            chunk = full_text[i:i + self.chunk_size]
            if chunk:  # Only add non-empty chunks
                chunks_with_overlap.append(chunk)
        
        return chunks_with_overlap
