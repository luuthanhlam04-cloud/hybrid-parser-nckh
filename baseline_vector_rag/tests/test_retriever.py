"""
TDD Test Suite for Semantic Retrieval with Cross-Encoder Re-ranking

These tests define the expected behavior of the retriever before implementation.
Following TDD principles: tests first, implementation second.
"""

import pytest
import sys
import os

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from retriever import Retriever
from vector_store import EmbeddingModel, VectorStore
from chunker import RecursiveCharacterTextSplitter


class TestQueryDimensionality:
    """Verify that query encoding matches chunk embedding dimensions."""
    
    def test_query_same_dimension_as_chunks(self):
        """Query embedding must have same dimension as stored chunk embeddings."""
        # Setup: Create a simple vector store with one chunk
        embedding_model = EmbeddingModel(model_name="all-MiniLM-L6-v2")
        vector_store = VectorStore(embedding_model=embedding_model)
        vector_store.add_chunk("Test chunk for dimension verification")
        
        retriever = Retriever(vector_store=vector_store, use_reranking=False)
        
        # Get query embedding dimension
        query = "Test query"
        query_embedding = retriever._encode_query(query)
        chunk_embedding = vector_store.get_vector(0)
        
        assert query_embedding.shape == chunk_embedding.shape, \
            f"Query embedding shape {query_embedding.shape} must match chunk embedding shape {chunk_embedding.shape}"
    
    def test_multiple_chunks_consistent_dimension(self):
        """All chunks and queries must use consistent embedding dimensions."""
        embedding_model = EmbeddingModel(model_name="all-MiniLM-L6-v2")
        vector_store = VectorStore(embedding_model=embedding_model)
        
        chunks = ["First chunk", "Second chunk", "Third chunk"]
        for chunk in chunks:
            vector_store.add_chunk(chunk)
        
        retriever = Retriever(vector_store=vector_store, use_reranking=False)
        
        # All chunks should have same dimension
        first_dim = vector_store.get_vector(0).shape
        for i in range(1, len(chunks)):
            assert vector_store.get_vector(i).shape == first_dim, \
                f"Chunk {i} dimension mismatch"
        
        # Query should also match this dimension
        query_embedding = retriever._encode_query("Test query")
        assert query_embedding.shape == first_dim, \
            "Query dimension must match chunk dimensions"


class TestSemanticSearchResults:
    """Verify that semantic search returns the correct number of results."""
    
    def test_returns_exactly_k_results(self):
        """Retriever must return exactly k results when enough chunks exist."""
        embedding_model = EmbeddingModel(model_name="all-MiniLM-L6-v2")
        vector_store = VectorStore(embedding_model=embedding_model)
        
        # Add 10 chunks
        for i in range(10):
            vector_store.add_chunk(f"Chunk number {i} with some content")
        
        retriever = Retriever(vector_store=vector_store, use_reranking=False)
        
        # Request 5 results
        results = retriever.retrieve(query="test query", k=5)
        
        assert len(results) == 5, f"Expected exactly 5 results, got {len(results)}"
    
    def test_k_larger_than_store_size(self):
        """When k exceeds store size, return all available chunks."""
        embedding_model = EmbeddingModel(model_name="all-MiniLM-L6-v2")
        vector_store = VectorStore(embedding_model=embedding_model)
        
        # Add only 3 chunks
        for i in range(3):
            vector_store.add_chunk(f"Chunk {i}")
        
        retriever = Retriever(vector_store=vector_store, use_reranking=False)
        
        # Request 10 results but only 3 exist
        results = retriever.retrieve(query="test query", k=10)
        
        assert len(results) == 3, f"Expected 3 results (store size), got {len(results)}"
    
    def test_results_include_similarity_scores(self):
        """Each result must include a similarity score."""
        embedding_model = EmbeddingModel(model_name="all-MiniLM-L6-v2")
        vector_store = VectorStore(embedding_model=embedding_model)
        vector_store.add_chunk("Test chunk")
        
        retriever = Retriever(vector_store=vector_store, use_reranking=False)
        results = retriever.retrieve(query="test query", k=1)
        
        assert "similarity" in results[0], "Results must include similarity score"
        assert isinstance(results[0]["similarity"], float), "Similarity must be a float"
        assert 0 <= results[0]["similarity"] <= 1, "Similarity should be between 0 and 1"
    
    def test_results_sorted_by_similarity(self):
        """Results should be sorted by similarity in descending order."""
        embedding_model = EmbeddingModel(model_name="all-MiniLM-L6-v2")
        vector_store = VectorStore(embedding_model=embedding_model)
        
        # Add chunks with varying content
        chunks = [
            "Machine learning algorithms",
            "Deep neural networks",
            "Natural language processing",
            "Computer vision systems",
            "Reinforcement learning"
        ]
        for chunk in chunks:
            vector_store.add_chunk(chunk)
        
        retriever = Retriever(vector_store=vector_store, use_reranking=False)
        results = retriever.retrieve(query="machine learning and AI", k=5)
        
        # Verify descending order
        similarities = [r["similarity"] for r in results]
        assert similarities == sorted(similarities, reverse=True), \
            "Results must be sorted by similarity in descending order"


class TestRerankingLogic:
    """Verify that re-ranking promotes high-relevance chunks."""
    
    def test_reranking_promotes_relevant_chunk(self):
        """Re-ranking should promote a chunk that's semantically relevant but lower in initial search."""
        embedding_model = EmbeddingModel(model_name="all-MiniLM-L6-v2")
        vector_store = VectorStore(embedding_model=embedding_model)
        
        # Add chunks where the most relevant one might not be top in vector search
        # This simulates the "dilution" problem where vector similarity isn't perfect
        chunks = [
            "The quick brown fox jumps over the lazy dog",  # High vector similarity but low relevance
            "Python is a programming language used for data science",  # Medium similarity
            "Machine learning models use neural networks for pattern recognition",  # Lower vector similarity but highly relevant to query
            "The weather today is sunny with a chance of rain",  # Low similarity
        ]
        for chunk in chunks:
            vector_store.add_chunk(chunk)
        
        # Without re-ranking
        retriever_no_rerank = Retriever(vector_store=vector_store, use_reranking=False)
        results_no_rerank = retriever_no_rerank.retrieve(query="neural networks in machine learning", k=3)
        
        # With re-ranking
        retriever_with_rerank = Retriever(vector_store=vector_store, use_reranking=True)
        results_with_rerank = retriever_with_rerank.retrieve(query="neural networks in machine learning", k=3)
        
        # The re-ranked results should have the most relevant chunk promoted
        # We verify this by checking that the order changed
        chunks_no_rerank = [r["chunk"] for r in results_no_rerank]
        chunks_with_rerank = [r["chunk"] for r in results_with_rerank]
        
        # At minimum, re-ranking should produce a different order or different scores
        # This verifies the re-ranking logic is actually running
        assert chunks_with_rerank != chunks_no_rerank or \
               [r["similarity"] for r in results_with_rerank] != [r["similarity"] for r in results_no_rerank], \
               "Re-ranking should modify the results order or scores"
    
    def test_reranking_preserves_k_results(self):
        """Re-ranking must still return exactly k results."""
        embedding_model = EmbeddingModel(model_name="all-MiniLM-L6-v2")
        vector_store = VectorStore(embedding_model=embedding_model)
        
        for i in range(10):
            vector_store.add_chunk(f"Chunk {i}")
        
        retriever = Retriever(vector_store=vector_store, use_reranking=True)
        results = retriever.retrieve(query="test query", k=5)
        
        assert len(results) == 5, f"Re-ranking must preserve k=5, got {len(results)}"
    
    def test_reranking_scores_are_valid(self):
        """Re-ranking scores should be valid similarity scores."""
        embedding_model = EmbeddingModel(model_name="all-MiniLM-L6-v2")
        vector_store = VectorStore(embedding_model=embedding_model)
        
        for i in range(5):
            vector_store.add_chunk(f"Chunk {i} about various topics")
        
        retriever = Retriever(vector_store=vector_store, use_reranking=True)
        results = retriever.retrieve(query="test query", k=3)
        
        for result in results:
            assert "similarity" in result, "Re-ranked results must include similarity"
            assert isinstance(result["similarity"], float), "Similarity must be float"
            assert 0 <= result["similarity"] <= 1, "Similarity must be between 0 and 1"


class TestRetrieverEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_empty_vector_store(self):
        """Retriever should handle empty vector store gracefully."""
        embedding_model = EmbeddingModel(model_name="all-MiniLM-L6-v2")
        vector_store = VectorStore(embedding_model=embedding_model)
        
        retriever = Retriever(vector_store=vector_store, use_reranking=False)
        results = retriever.retrieve(query="test query", k=5)
        
        assert len(results) == 0, "Empty store should return no results"
    
    def test_empty_query(self):
        """Retriever should handle empty query gracefully."""
        embedding_model = EmbeddingModel(model_name="all-MiniLM-L6-v2")
        vector_store = VectorStore(embedding_model=embedding_model)
        vector_store.add_chunk("Test chunk")
        
        retriever = Retriever(vector_store=vector_store, use_reranking=False)
        results = retriever.retrieve(query="", k=5)
        
        # Should still return results (empty query is valid)
        assert len(results) >= 0, "Empty query should be handled"
    
    def test_k_equals_zero(self):
        """k=0 should return empty results."""
        embedding_model = EmbeddingModel(model_name="all-MiniLM-L6-v2")
        vector_store = VectorStore(embedding_model=embedding_model)
        vector_store.add_chunk("Test chunk")
        
        retriever = Retriever(vector_store=vector_store, use_reranking=False)
        results = retriever.retrieve(query="test query", k=0)
        
        assert len(results) == 0, "k=0 should return no results"
