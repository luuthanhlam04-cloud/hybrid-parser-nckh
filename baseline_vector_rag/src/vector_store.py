"""
Vector Store and Embedding Model for RAG Semantic Search

This module implements semantic search capabilities by:
1. Converting text chunks to dense vector representations using sentence-transformers
2. Storing vectors in a NumPy-based vector store
3. Performing similarity search using cosine similarity

The implementation prioritizes educational value by using pure NumPy operations,
making the underlying mathematics of vector similarity explicit and understandable.
"""

import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Optional


class EmbeddingModel:
    """
    Wrapper around sentence-transformers for consistent text embedding interface.
    
    This class provides a clean interface for converting text to dense vector
    representations that capture semantic meaning. The model transforms text into
    fixed-dimensional vectors where similar meanings are close in vector space.
    
    Args:
        model_name: Name of the pre-trained sentence-transformers model to use.
                   Default: "all-MiniLM-L6-v2" (384 dimensions, ~80MB)
                   This model offers a good balance of performance, size, and speed
                   for minimum viable architecture (AMV) implementations.
    
    Attributes:
        model: The underlying sentence-transformers model
        embedding_dimension: The dimension of output vectors (384 for default model)
    
    Note:
        The first instantiation will download the model weights (~80MB for default model).
        Subsequent uses will load from cache, making initialization much faster.
    """
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the embedding model with lazy loading.
        
        Lazy loading means the model is only loaded when first needed, which is
        efficient for applications that might not always need embedding functionality.
        """
        self.model_name = model_name
        self._model: Optional[SentenceTransformer] = None
        self._embedding_dimension: Optional[int] = None
    
    @property
    def model(self) -> SentenceTransformer:
        """
        Lazy-load the sentence-transformers model.
        
        This property ensures the model is only loaded when first accessed,
        avoiding unnecessary memory usage and download time if embeddings aren't needed.
        
        Returns:
            The loaded SentenceTransformer model
        """
        if self._model is None:
            # Download and load the model (cached automatically by sentence-transformers)
            self._model = SentenceTransformer(self.model_name)
            # Cache the embedding dimension for quick access
            self._embedding_dimension = self._model.get_embedding_dimension()
        return self._model
    
    @property
    def embedding_dimension(self) -> int:
        """
        Get the dimension of embeddings produced by this model.
        
        Returns:
            The embedding dimension (e.g., 384 for all-MiniLM-L6-v2)
        """
        if self._embedding_dimension is None:
            # Access the model property to trigger loading and dimension detection
            _ = self.model
        return self._embedding_dimension
    
    def embed(self, text: str) -> np.ndarray:
        """
        Convert a single text string to a normalized embedding vector.
        
        The embedding process:
        1. Tokenize the text into sub-word pieces
        2. Pass through transformer model to get contextualized representations
        3. Pool token representations to get a single sentence embedding
        4. Normalize the vector to unit length for cosine similarity
        
        Args:
            text: Input text to be embedded (can be empty string)
        
        Returns:
            Normalized embedding vector as numpy array with shape (embedding_dimension,)
            The vector is L2-normalized, meaning its length is exactly 1.0
        
        Note:
            Normalization is crucial because it allows us to use dot product as
            a proxy for cosine similarity, which is much faster to compute.
        """
        # Generate embedding using the sentence-transformers model
        # The model returns a numpy array with shape (1, embedding_dimension)
        embedding = self.model.encode(text, convert_to_numpy=True)
        
        # Remove the batch dimension to get a 1D array
        embedding = embedding.flatten()
        
        # Normalize the vector to unit length using L2 norm
        # L2 norm: sqrt(sum(x_i^2)) - the Euclidean length of the vector
        # Why normalize: Cosine similarity between normalized vectors = dot product
        # This makes similarity calculation much faster (dot product is O(n))
        embedding = self._normalize_vector(embedding)
        
        return embedding
    
    def embed_batch(self, texts: List[str]) -> np.ndarray:
        """
        Convert multiple text strings to normalized embedding vectors.
        
        Batch processing is more efficient than processing texts individually
        because it leverages GPU acceleration and reduces model overhead.
        
        Args:
            texts: List of input text strings to be embedded
        
        Returns:
            2D numpy array of shape (len(texts), embedding_dimension)
            Each row is a normalized embedding vector
        """
        # Generate embeddings for all texts at once
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        
        # Normalize each vector to unit length
        # We use axis=1 to normalize each row independently
        embeddings = self._normalize_batch(embeddings)
        
        return embeddings
    
    def _normalize_vector(self, vector: np.ndarray) -> np.ndarray:
        """
        Normalize a single vector to unit length using L2 norm.
        
        L2 normalization formula: vector = vector / ||vector||
        where ||vector|| is the Euclidean norm (sqrt of sum of squared elements)
        
        Why L2 norm specifically:
        - L2 norm represents the geometric length of the vector in Euclidean space
        - After normalization, the vector lies on the unit sphere (hypersphere)
        - This allows us to focus on direction (semantic meaning) rather than magnitude
        
        Args:
            vector: Input vector to normalize
        
        Returns:
            Normalized vector with L2 norm = 1.0
        """
        # Calculate L2 norm (Euclidean length)
        norm = np.linalg.norm(vector)
        
        # Avoid division by zero for zero vectors
        if norm == 0:
            return vector
        
        # Scale vector to unit length
        return vector / norm
    
    def _normalize_batch(self, vectors: np.ndarray) -> np.ndarray:
        """
        Normalize a batch of vectors to unit length using L2 norm.
        
        This is the batch version of _normalize_vector, optimized for efficiency
        using NumPy's vectorized operations along a specified axis.
        
        Args:
            vectors: 2D array of shape (n_vectors, embedding_dimension)
        
        Returns:
            Normalized vectors where each row has L2 norm = 1.0
        """
        # Calculate L2 norm for each vector (row)
        # axis=1 means compute norm across each row independently
        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        
        # Avoid division by zero
        # Replace zero norms with 1 to avoid division by zero (zero vectors stay zero)
        norms[norms == 0] = 1
        
        # Scale each vector to unit length
        return vectors / norms


class VectorStore:
    """
    NumPy-based vector store with cosine similarity search.
    
    This class provides a simple yet educational implementation of a vector database.
    It stores text chunks as dense vectors and enables efficient similarity search
    using cosine similarity, which measures semantic relatedness between texts.
    
    The implementation uses brute-force search (O(n) per query) which is simple to
    understand and sufficient for small-scale AMV implementations. For production
    use with millions of vectors, indexed structures like FAISS would be preferred.
    
    Args:
        embedding_model: EmbeddingModel instance for converting text to vectors
    
    Attributes:
        embedding_model: The embedding model used for vectorization
        vectors: 2D NumPy array storing all embedded chunks (n_vectors × dimension)
        chunks: List of original text chunks corresponding to each vector
    """
    
    def __init__(self, embedding_model: EmbeddingModel):
        """
        Initialize an empty vector store.
        
        The store starts empty and vectors are added incrementally using add_chunk().
        This allows for dynamic updates to the knowledge base.
        """
        self.embedding_model = embedding_model
        
        # Initialize empty storage
        # vectors will be a 2D array: shape (n_vectors, embedding_dimension)
        self.vectors: np.ndarray = np.empty((0, embedding_model.embedding_dimension), dtype=np.float32)
        
        # chunks stores the original text for each vector
        self.chunks: List[str] = []
    
    def add_chunk(self, chunk: str) -> None:
        """
        Add a text chunk to the vector store.
        
        The chunk is converted to an embedding vector and stored alongside
        the original text for retrieval. This enables both semantic search
        and retrieval of the original content.
        
        Args:
            chunk: Text chunk to be added to the store
        """
        # Convert text to normalized embedding vector
        embedding = self.embedding_model.embed(chunk)
        
        # Add vector to the store
        # Reshape to (1, dimension) for concatenation
        embedding = embedding.reshape(1, -1)
        self.vectors = np.vstack([self.vectors, embedding]) if self.vectors.size > 0 else embedding
        
        # Store original chunk
        self.chunks.append(chunk)
    
    def add_chunks_batch(self, chunks: List[str]) -> None:
        """
        Add multiple text chunks to the vector store efficiently.
        
        Batch processing is more efficient than adding chunks individually
        because it leverages vectorized operations and reduces function call overhead.
        
        Args:
            chunks: List of text chunks to be added to the store
        """
        if not chunks:
            return
        
        # Convert all chunks to embeddings at once
        embeddings = self.embedding_model.embed_batch(chunks)
        
        # Add vectors to the store
        self.vectors = np.vstack([self.vectors, embeddings]) if self.vectors.size > 0 else embeddings
        
        # Store original chunks
        self.chunks.extend(chunks)
    
    def search(self, query: str, k: int = 5) -> List[Dict[str, any]]:
        """
        Find the most semantically similar chunks to the query using cosine similarity.
        
        Search algorithm (brute-force k-NN):
        1. Convert query to embedding vector
        2. Compute cosine similarity between query and all stored vectors
        3. Sort by similarity score (descending)
        4. Return top-k results with their similarity scores
        
        Time complexity: O(n × d) where n is number of vectors, d is embedding dimension
        This is acceptable for AMV scale (thousands of vectors), but would need
        indexed structures (FAISS, HNSW) for production scale (millions of vectors).
        
        Args:
            query: Search query text
            k: Number of results to return (default: 5)
        
        Returns:
            List of dictionaries with keys:
            - "chunk": The original text chunk
            - "similarity": Cosine similarity score (0 to 1, higher is more similar)
            Results are sorted by similarity in descending order.
        
        Note:
            Cosine similarity measures the angle between vectors, ignoring magnitude.
            Range: -1 to 1, where:
            - 1.0: Identical direction (maximum similarity)
            - 0.0: Orthogonal (no similarity)
            - -1.0: Opposite direction (maximum dissimilarity)
            Since we use normalized vectors, scores are typically between 0 and 1.
        """
        if self.vectors.size == 0:
            return []
        
        # Convert query to normalized embedding vector
        query_embedding = self.embedding_model.embed(query)
        
        # Compute cosine similarity between query and all stored vectors
        # Since vectors are normalized, cosine similarity = dot product
        # Matrix multiplication: (1 × d) @ (d × n) = (1 × n) similarity scores
        similarities = np.dot(query_embedding, self.vectors.T)
        
        # Get indices of top-k similarities (using argpartition for efficiency)
        # argpartition is O(n) vs full sort which is O(n log n)
        k = min(k, len(similarities))
        top_k_indices = np.argpartition(similarities, -k)[-k:]
        
        # Sort the top-k results by similarity (descending)
        top_k_indices = top_k_indices[np.argsort(similarities[top_k_indices])[::-1]]
        
        # Build result list with chunks and similarity scores
        results = []
        for idx in top_k_indices:
            results.append({
                "chunk": self.chunks[idx],
                "similarity": float(similarities[idx])  # Convert numpy float to Python float
            })
        
        return results
    
    def size(self) -> int:
        """
        Return the number of chunks currently stored in the vector store.
        
        Returns:
            Number of chunks in the store
        """
        return len(self.chunks)
    
    def clear(self) -> None:
        """
        Remove all chunks and vectors from the store.
        
        This resets the store to its initial empty state, useful for
        rebuilding the knowledge base or managing memory.
        """
        self.vectors = np.empty((0, self.embedding_model.embedding_dimension), dtype=np.float32)
        self.chunks = []
    
    def get_vector(self, index: int) -> np.ndarray:
        """
        Retrieve the embedding vector at a specific index.
        
        This is useful for debugging, visualization, or understanding
        the internal state of the vector store.
        
        Args:
            index: Index of the vector to retrieve
        
        Returns:
            Embedding vector at the specified index
        
        Raises:
            IndexError: If index is out of bounds
        """
        if index < 0 or index >= len(self.chunks):
            raise IndexError(f"Index {index} out of bounds for store with {len(self.chunks)} chunks")
        return self.vectors[index]
    
    def get_chunk(self, index: int) -> str:
        """
        Retrieve the original text chunk at a specific index.
        
        Args:
            index: Index of the chunk to retrieve
        
        Returns:
            Original text chunk at the specified index
        
        Raises:
            IndexError: If index is out of bounds
        """
        if index < 0 or index >= len(self.chunks):
            raise IndexError(f"Index {index} out of bounds for store with {len(self.chunks)} chunks")
        return self.chunks[index]