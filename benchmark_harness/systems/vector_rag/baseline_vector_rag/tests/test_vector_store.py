"""
TDD Test Suite for Vector Store and Embeddings

These tests define the expected behavior of the vector store before implementation.
Following TDD principles: tests first, implementation second.
"""

import pytest
import sys
import os
import numpy as np

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from vector_store import EmbeddingModel, VectorStore


class TestEmbeddingDimensions:
    """Verify the embedding model produces vectors of consistent and correct dimensions."""
    
    def test_single_text_chunk_dimension(self):
        """Single text chunk should produce expected dimension (384 for all-MiniLM-L6-v2)."""
        model = EmbeddingModel(model_name="all-MiniLM-L6-v2")
        text = "This is a test sentence."
        embedding = model.embed(text)
        
        # all-MiniLM-L6-v2 produces 384-dimensional vectors
        assert embedding.shape == (384,), f"Expected shape (384,), got {embedding.shape}"
        assert embedding.dtype == np.float32, f"Expected dtype float32, got {embedding.dtype}"
    
    def test_multiple_chunks_same_dimension(self):
        """Multiple text chunks should produce vectors with identical dimensions."""
        model = EmbeddingModel(model_name="all-MiniLM-L6-v2")
        texts = [
            "First sentence about machine learning.",
            "Second sentence about deep learning.",
            "Third sentence about neural networks."
        ]
        
        embeddings = [model.embed(text) for text in texts]
        
        # All embeddings should have the same dimension
        dimensions = [emb.shape[0] for emb in embeddings]
        assert all(dim == 384 for dim in dimensions), \
            f"All embeddings should be 384-dimensional, got {dimensions}"
        
        # All embeddings should have the same shape
        shapes = [emb.shape for emb in embeddings]
        assert len(set(shapes)) == 1, f"All embeddings should have same shape, got {shapes}"
    
    def test_empty_input_handling(self):
        """Empty input should be handled gracefully."""
        model = EmbeddingModel(model_name="all-MiniLM-L6-v2")
        
        # Empty string should still produce a valid embedding
        embedding = model.embed("")
        assert embedding.shape == (384,), "Empty string should still produce valid embedding"
        
        # Single space should also work
        embedding = model.embed(" ")
        assert embedding.shape == (384,), "Single space should produce valid embedding"


class TestVectorNormalization:
    """Verify vector normalization for cosine similarity."""
    
    def test_normalized_vectors_unit_length(self):
        """Normalized vectors should have unit length (L2 norm = 1.0)."""
        model = EmbeddingModel(model_name="all-MiniLM-L6-v2")
        text = "This is a test sentence for normalization."
        
        # Get embedding (should be normalized by the model)
        embedding = model.embed(text)
        
        # Calculate L2 norm
        l2_norm = np.linalg.norm(embedding)
        
        # Should be very close to 1.0 (allowing for floating point precision)
        assert abs(l2_norm - 1.0) < 1e-6, \
            f"Normalized vector should have L2 norm of 1.0, got {l2_norm}"
    
    def test_normalization_preserves_direction(self):
        """Normalization should preserve the direction of the vector."""
        model = EmbeddingModel(model_name="all-MiniLM-L6-v2")
        text = "Direction preservation test."
        
        # Get normalized embedding
        normalized = model.embed(text)
        
        # Create a scaled version (multiply by 2)
        scaled = normalized * 2
        
        # Normalize the scaled version
        scaled_normalized = scaled / np.linalg.norm(scaled)
        
        # The direction should be preserved (normalized vectors should be identical)
        # Use cosine similarity to check direction (should be 1.0 for identical direction)
        cosine_sim = np.dot(normalized, scaled_normalized)
        assert abs(cosine_sim - 1.0) < 1e-6, \
            f"Normalization should preserve direction, cosine similarity: {cosine_sim}"
    
    def test_normalization_enables_cosine_similarity(self):
        """Normalization enables accurate cosine similarity via dot product."""
        model = EmbeddingModel(model_name="all-MiniLM-L6-v2")
        
        # Two similar texts
        text1 = "Machine learning is a subset of artificial intelligence."
        text2 = "ML is a branch of AI."
        
        embedding1 = model.embed(text1)
        embedding2 = model.embed(text2)
        
        # Since vectors are normalized, dot product equals cosine similarity
        cosine_sim = np.dot(embedding1, embedding2)
        
        # Should be high (similar texts) and between 0 and 1
        assert 0.0 <= cosine_sim <= 1.0, \
            f"Cosine similarity should be between 0 and 1, got {cosine_sim}"
        assert cosine_sim > 0.5, \
            f"Similar texts should have high cosine similarity, got {cosine_sim}"


class TestSimilaritySearch:
    """Verify nearest neighbor search functionality."""
    
    def test_query_returns_most_similar_chunk(self):
        """Query should return the most semantically similar chunk."""
        model = EmbeddingModel(model_name="all-MiniLM-L6-v2")
        store = VectorStore(embedding_model=model)
        
        # Add chunks with different topics
        chunks = [
            "Machine learning algorithms process data to make predictions.",
            "Baking bread requires flour, water, yeast, and time.",
            "Deep learning uses neural networks with multiple layers.",
            "Cooking pasta involves boiling water and adding sauce."
        ]
        
        for chunk in chunks:
            store.add_chunk(chunk)
        
        # Query about machine learning
        query = "AI and neural networks for prediction"
        results = store.search(query, k=2)
        
        # Should return machine learning related chunks first
        assert len(results) == 2, f"Expected 2 results, got {len(results)}"
        
        # The top result should be about machine learning or deep learning
        top_chunk = results[0]["chunk"]
        top_score = results[0]["similarity"]
        
        assert top_score > 0.5, \
            f"Top result should have high similarity, got {top_score}"
        assert "machine" in top_chunk.lower() or "learning" in top_chunk.lower() or "neural" in top_chunk.lower(), \
            f"Top result should be ML-related, got: {top_chunk}"
    
    def test_similarity_scores_range(self):
        """Similarity scores should be between 0 and 1 for cosine similarity."""
        model = EmbeddingModel(model_name="all-MiniLM-L6-v2")
        store = VectorStore(embedding_model=model)
        
        chunks = [
            "The sky is blue.",
            "Grass is green.",
            "Machine learning is fascinating."
        ]
        
        for chunk in chunks:
            store.add_chunk(chunk)
        
        # Various queries
        queries = [
            "The color of the sky",
            "Green plants",
            "Artificial intelligence"
        ]
        
        for query in queries:
            results = store.search(query, k=3)
            for result in results:
                similarity = result["similarity"]
                assert 0.0 <= similarity <= 1.0, \
                    f"Similarity should be between 0 and 1, got {similarity}"
    
    def test_search_returns_correct_number_of_results(self):
        """Search should return exactly k results (or fewer if store has less)."""
        model = EmbeddingModel(model_name="all-MiniLM-L6-v2")
        store = VectorStore(embedding_model=model)
        
        # Add 5 chunks
        chunks = [f"Chunk number {i}" for i in range(5)]
        for chunk in chunks:
            store.add_chunk(chunk)
        
        # Request 3 results
        results = store.search("query", k=3)
        assert len(results) == 3, f"Expected 3 results, got {len(results)}"
        
        # Request 10 results (more than available)
        results = store.search("query", k=10)
        assert len(results) == 5, f"Expected 5 results (max available), got {len(results)}"
        
        # Request 1 result
        results = store.search("query", k=1)
        assert len(results) == 1, f"Expected 1 result, got {len(results)}"
    
    def test_search_handles_empty_store(self):
        """Search should handle empty store gracefully."""
        model = EmbeddingModel(model_name="all-MiniLM-L6-v2")
        store = VectorStore(embedding_model=model)
        
        # Search in empty store
        results = store.search("query", k=5)
        
        # Should return empty list
        assert results == [], f"Empty store should return empty results, got {results}"
    
    def test_results_include_similarity_scores(self):
        """Results should include both chunks and similarity scores."""
        model = EmbeddingModel(model_name="all-MiniLM-L6-v2")
        store = VectorStore(embedding_model=model)
        
        chunks = ["First chunk", "Second chunk", "Third chunk"]
        for chunk in chunks:
            store.add_chunk(chunk)
        
        results = store.search("query", k=2)
        
        for result in results:
            assert "chunk" in result, "Result should include 'chunk' key"
            assert "similarity" in result, "Result should include 'similarity' key"
            assert isinstance(result["chunk"], str), "Chunk should be a string"
            assert isinstance(result["similarity"], (float, np.floating)), \
                "Similarity should be a float"


class TestVectorStoreOperations:
    """Verify store management operations."""
    
    def test_adding_vectors_to_store(self):
        """Adding chunks should increase store size."""
        model = EmbeddingModel(model_name="all-MiniLM-L6-v2")
        store = VectorStore(embedding_model=model)
        
        # Initially empty
        assert store.size() == 0, "Store should be empty initially"
        
        # Add first chunk
        store.add_chunk("First chunk")
        assert store.size() == 1, "Store should have 1 chunk after adding"
        
        # Add more chunks
        store.add_chunk("Second chunk")
        store.add_chunk("Third chunk")
        assert store.size() == 3, "Store should have 3 chunks after adding"
    
    def test_clearing_the_store(self):
        """Clearing should remove all chunks from store."""
        model = EmbeddingModel(model_name="all-MiniLM-L6-v2")
        store = VectorStore(embedding_model=model)
        
        # Add chunks
        for i in range(5):
            store.add_chunk(f"Chunk {i}")
        
        assert store.size() == 5, "Store should have 5 chunks"
        
        # Clear store
        store.clear()
        
        assert store.size() == 0, "Store should be empty after clearing"
        results = store.search("query", k=5)
        assert results == [], "Cleared store should return no results"
    
    def test_chunk_to_vector_mapping(self):
        """Store should maintain correct mapping between chunks and vectors."""
        model = EmbeddingModel(model_name="all-MiniLM-L6-v2")
        store = VectorStore(embedding_model=model)
        
        chunks = [
            "Specific chunk one",
            "Specific chunk two", 
            "Specific chunk three"
        ]
        
        for chunk in chunks:
            store.add_chunk(chunk)
        
        # Search for each chunk and verify it can find itself
        for chunk in chunks:
            results = store.search(chunk, k=1)
            assert len(results) == 1, f"Should find exact match for: {chunk}"
            # The top result should be the chunk itself or very similar
            assert results[0]["similarity"] > 0.8, \
                f"Chunk should find itself with high similarity, got {results[0]['similarity']}"
    
    def test_duplicate_chunks(self):
        """Adding duplicate chunks should be handled appropriately."""
        model = EmbeddingModel(model_name="all-MiniLM-L6-v2")
        store = VectorStore(embedding_model=model)
        
        # Add same chunk twice
        chunk = "Duplicate chunk content"
        store.add_chunk(chunk)
        store.add_chunk(chunk)
        
        # Store should have 2 entries
        assert store.size() == 2, "Duplicate chunks should be stored separately"
        
        # Search should return both
        results = store.search(chunk, k=5)
        assert len(results) == 2, "Should return both duplicate chunks"