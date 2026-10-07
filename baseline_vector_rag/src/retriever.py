"""
Semantic Retrieval with Cross-Encoder Re-ranking

This module implements the retrieval component of the RAG system:
1. Encodes user queries using the same embedding model as document chunks
2. Performs semantic search via vector similarity (cosine similarity)
3. Optionally re-ranks results using a Cross-Encoder for improved precision

Why Re-ranking is Necessary:
Bi-encoder models (like our embedding model) compress documents into fixed-dimensional vectors.
This compression leads to "dilution" - loss of fine-grained semantic information that's
critical for precise relevance matching. The vector similarity is a coarse approximation.

Cross-encoders solve this by scoring query-document pairs directly, allowing them to
consider the full interaction between query and document without compression loss.
This makes them more accurate but slower, hence the two-stage approach:
- Stage 1: Fast bi-encoder retrieval (vector search) to get candidate documents
- Stage 2: Precise cross-encoder re-ranking to refine the order of top candidates
"""

import numpy as np
from typing import List, Dict, Optional
from sentence_transformers import CrossEncoder
from vector_store import VectorStore


class Retriever:
    """
    Semantic retriever with optional cross-encoder re-ranking.
    
    This class bridges the gap between user queries and stored knowledge by:
    1. Encoding queries using the same model used for document ingestion
    2. Retrieving top-k similar chunks via vector similarity search
    3. Re-ranking results with a cross-encoder for improved precision
    
    The two-stage approach balances speed and accuracy:
    - Vector search is fast (O(n) brute-force) but can miss fine-grained relevance
    - Cross-encoder re-ranking is slower but significantly improves result quality
    
    Args:
        vector_store: VectorStore instance containing embedded document chunks
        use_reranking: Whether to use cross-encoder re-ranking (default: False)
        rerank_model: Name of cross-encoder model for re-ranking
                      Default: "ms-marco-MiniLM-L-6-v2" (lightweight, ~80MB)
                      This model is trained on MS MARCO dataset for passage ranking
        top_k_for_rerank: Number of candidates to retrieve before re-ranking
                          Only used when use_reranking=True (default: 20)
                          We retrieve more candidates than needed to give the
                          cross-encoder more options to select the best ones
    
    Attributes:
        vector_store: The underlying vector store for semantic search
        use_reranking: Whether re-ranking is enabled
        cross_encoder: Lazy-loaded cross-encoder model (if re-ranking enabled)
        top_k_for_rerank: Number of candidates for re-ranking stage
    """
    
    def __init__(
        self,
        vector_store: VectorStore,
        use_reranking: bool = False,
        rerank_model: str = "ms-marco-MiniLM-L-6-v2",
        top_k_for_rerank: int = 20,
    ):
        """
        Initialize the retriever with optional re-ranking capability.
        
        The cross-encoder is lazy-loaded on first use to avoid unnecessary
        model downloads and memory usage when re-ranking isn't needed.
        """
        self.vector_store = vector_store
        self.use_reranking = use_reranking
        self.rerank_model_name = rerank_model
        self.top_k_for_rerank = top_k_for_rerank
        self._cross_encoder: Optional[CrossEncoder] = None
    
    @property
    def cross_encoder(self) -> CrossEncoder:
        """
        Lazy-load the cross-encoder model.
        
        The model is only loaded when re-ranking is actually used, which:
        - Avoids unnecessary downloads (~80MB for default model)
        - Reduces memory footprint when re-ranking isn't needed
        - Speeds up initialization for retrieval-only use cases
        
        Returns:
            The loaded CrossEncoder model
        """
        if self._cross_encoder is None:
            self._cross_encoder = CrossEncoder(self.rerank_model_name)
        return self._cross_encoder
    
    def _encode_query(self, query: str) -> np.ndarray:
        """
        Encode a user query into a normalized embedding vector.
        
        Critical: This uses the EXACT same model as document chunking.
        Using different models would create incompatible vector spaces,
        making similarity scores meaningless.
        
        The embedding process:
        1. Tokenize the query (same tokenizer as documents)
        2. Pass through the same transformer model
        3. Pool to get a single query embedding
        4. Normalize to unit length for cosine similarity
        
        Args:
            query: User query string to encode
        
        Returns:
            Normalized embedding vector with shape (embedding_dimension,)
            The dimension matches the document chunk embeddings exactly
        """
        # Use the same embedding model from the vector store
        # This ensures query and document vectors are in the same space
        embedding = self.vector_store.embedding_model.embed(query)
        return embedding
    
    def retrieve(self, query: str, k: int = 5) -> List[Dict[str, any]]:
        """
        Retrieve the most relevant chunks for a given query.
        
        Retrieval pipeline:
        1. Encode query using the same model as document chunks
        2. Perform vector similarity search to get candidate chunks
        3. If re-ranking enabled: refine order using cross-encoder
        4. Return top-k results with similarity scores
        
        Why Two-Stage Retrieval:
        - Vector search is fast but can miss fine-grained relevance
          (due to compression loss in fixed-dimensional embeddings)
        - Cross-encoder is accurate but slow (requires scoring each pair)
        - Combined: fast retrieval of candidates + precise re-ranking of top results
        
        Args:
            query: User query string
            k: Number of results to return (default: 5)
        
        Returns:
            List of dictionaries with keys:
            - "chunk": The retrieved text chunk
            - "similarity": Relevance score (0 to 1, higher is more relevant)
            Results are sorted by relevance in descending order.
        """
        # Handle edge cases
        if k <= 0:
            return []
        
        if self.vector_store.size() == 0:
            return []
        
        # Stage 1: Vector similarity search (bi-encoder retrieval)
        # This is fast and gives us a broad set of candidate documents
        if self.use_reranking:
            # Retrieve more candidates than we need for re-ranking
            # This gives the cross-encoder more options to select from
            candidates = self.vector_store.search(query, k=min(self.top_k_for_rerank, self.vector_store.size()))
        else:
            # No re-ranking, just get exactly k results
            candidates = self.vector_store.search(query, k=min(k, self.vector_store.size()))
        
        # If we got fewer results than requested (small store), return as-is
        if len(candidates) <= k:
            return candidates
        
        # Stage 2: Cross-encoder re-ranking (if enabled)
        if self.use_reranking:
            candidates = self._rerank_results(query, candidates)
        
        # Return top-k results
        return candidates[:k]
    
    def _rerank_results(self, query: str, candidates: List[Dict[str, any]]) -> List[Dict[str, any]]:
        """
        Re-rank candidate results using a cross-encoder for improved precision.
        
        Why Re-ranking Improves Quality:
        Bi-encoder models (our vector embeddings) compress documents to fixed vectors.
        This compression loses fine-grained semantic details - the "dilution" problem.
        For example, "machine learning" and "deep learning" might have similar vectors
        even though they're distinct concepts in specific contexts.
        
        Cross-encoders avoid this by:
        1. Taking the full query and document as input (no compression)
        2. Using attention mechanisms to model query-document interactions
        3. Producing a relevance score that considers the full context
        
        This makes cross-encoders more accurate but slower, hence the two-stage approach:
        - Fast bi-encoder narrows down from millions to hundreds of candidates
        - Accurate cross-encoder refines the top candidates for final ranking
        
        Args:
            query: Original user query
            candidates: List of candidate results from vector search
                        Each has "chunk" and "similarity" keys
        
        Returns:
            Re-ranked list of candidates with updated similarity scores
            Sorted by cross-encoder relevance score in descending order
        """
        if not candidates:
            return candidates
        
        # Prepare query-document pairs for cross-encoder
        # The cross-encoder expects pairs as a list of [query, document] tuples
        query_doc_pairs = [[query, candidate["chunk"]] for candidate in candidates]
        
        # Score each pair using the cross-encoder
        # The model outputs a relevance score (higher = more relevant)
        # These scores are not normalized to [0,1] like cosine similarity
        cross_encoder_scores = self.cross_encoder.predict(query_doc_pairs)
        
        # Update candidates with cross-encoder scores
        # We normalize scores to [0,1] range for consistency with vector similarity
        # Using sigmoid to convert raw scores to probabilities
        normalized_scores = self._sigmoid_normalize(cross_encoder_scores)
        
        for i, candidate in enumerate(candidates):
            candidate["similarity"] = float(normalized_scores[i])
        
        # Sort by cross-encoder score (descending)
        candidates.sort(key=lambda x: x["similarity"], reverse=True)
        
        return candidates
    
    def _sigmoid_normalize(self, scores: np.ndarray) -> np.ndarray:
        """
        Normalize cross-encoder scores to [0,1] range using sigmoid function.
        
        Cross-encoder outputs raw logits that can be any real number.
        We normalize these to [0,1] for consistency with cosine similarity scores.
        
        Sigmoid function: σ(x) = 1 / (1 + e^(-x))
        - Maps any real number to (0, 1)
        - Preserves relative ordering (higher input → higher output)
        - Provides probabilistic interpretation (closer to 1 = more relevant)
        
        Args:
            scores: Raw cross-encoder scores (can be any real number)
        
        Returns:
            Normalized scores in [0, 1] range
        """
        return 1 / (1 + np.exp(-scores))
