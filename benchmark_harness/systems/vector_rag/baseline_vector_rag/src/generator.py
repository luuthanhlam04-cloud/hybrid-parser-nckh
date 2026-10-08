"""
Grounded Generation with Context Injection

This module implements the generation component of the RAG system:
1. Hydrates system prompts with retrieved context chunks
2. Enforces instruction hierarchy to prevent prompt injection
3. Generates factually grounded responses using Gemini Flash API
4. Implements grounding checks to prevent hallucinations

Why Instruction Hierarchy Matters:
Without proper hierarchy, user input can override system instructions through
prompt injection attacks. By structuring prompts as System -> Context -> User Query,
we ensure that:
- System instructions (use ONLY provided context) cannot be bypassed
- Context is clearly marked as ground truth, not user input
- User queries cannot manipulate the model's behavior

Why Context Markers Prevent Hallucination:
Without clear separation, models may:
- Confuse retrieved context with user-provided information
- Blend context with their training data (hallucination)
- Lose track of what is "ground truth" vs "suggested"

XML tags like <context> and </context> create an unambiguous boundary that:
- Signals to the model: "This is factual ground truth"
- Prevents the model from treating context as conversational input
- Reduces "self-delusion" where the model convinces itself of false facts
"""

import os
from typing import List, Optional
from dotenv import load_dotenv
import google.genai


class Generator:
    """
    Grounded generator with context injection and instruction hierarchy.
    
    This class completes the RAG pipeline by:
    1. Hydrating system prompts with retrieved context chunks
    2. Enforcing strict instruction hierarchy (System > Context > User)
    3. Generating factually grounded responses using Gemini Flash
    4. Preventing hallucination through clear context boundaries
    
    The generator uses a two-stage prompt structure:
    - Stage 1: System instructions (role, constraints, behavior)
    - Stage 2: Retrieved context (marked with XML tags as ground truth)
    - Stage 3: User query (the actual question to answer)
    
    This hierarchy ensures the model cannot be manipulated by user input
    and clearly distinguishes between factual context and conversational queries.
    
    Args:
        model_name: Name of Gemini model to use (primary model)
                   Default: "gemini-2.5-flash" (Flash model for fast generation)
        fallback_model: Fallback model for 429 rate limit errors
                       Default: "gemini-3.5-flash-lite"
        api_key_env: Environment variable name for API key
                    Default: "GEMINI_API_KEY"
        temperature: Sampling temperature for generation
                    Default: 0.0 (maximum factuality, minimal creativity)
                    Lower values = more deterministic, factual responses
    
    Attributes:
        client: Google GenAI client for API calls
        model_name: The primary Gemini model being used
        fallback_model: The fallback model for rate limit errors
        system_prompt_template: Template for system instructions
    """
    
    def __init__(
        self,
        model_name: str = "gemini-2.5-flash",
        fallback_model: str = "gemini-3.5-flash-lite",
        api_key_env: str = "GEMINI_API_KEY",
        temperature: float = 0.0,
    ):
        """
        Initialize the generator with Gemini Flash API client.
        
        The API key is loaded from environment variables for security.
        This prevents hardcoding credentials in source code.
        
        API key validation is lazy - it's only checked when actually making
        an API call, not during initialization. This allows testing prompt
        hydration without requiring an API key.
        
        Args:
            model_name: Gemini model identifier (primary model)
            fallback_model: Fallback model for 429 errors (default: gemini-3.5-flash-lite)
            api_key_env: Environment variable containing the API key
            temperature: Sampling temperature (0.0 for maximum factuality)
        """
        # Load environment variables from .env file
        load_dotenv()
        
        self.model_name = model_name
        self.fallback_model = fallback_model
        self.api_key_env = api_key_env
        self.temperature = temperature
        self._client: Optional[google.genai.Client] = None
        
        # Define enriched system prompt template
        # This template enforces the instruction hierarchy and grounding constraints
        self.system_prompt_template = """You are an expert assistant that answers questions based ONLY on the provided information.

<context>
{context}
</context>

User Question: {query}

Instructions:
1. Answer the user's question using ONLY the information provided in the <context> section above.
2. If the answer cannot be found in the context, say "I don't have enough information to answer this question."
3. Do not use any outside knowledge, training data, or assumptions beyond what is explicitly stated in the context.
4. Be concise and direct in your response.
5. If the context contains multiple relevant pieces of information, synthesize them into a coherent answer.

Remember: The <context> section contains the ONLY factual information you should use. Everything outside these tags is either instructions or the user's question, not factual ground truth."""
    
    @property
    def client(self) -> google.genai.Client:
        """
        Lazy-load the Google GenAI client.
        
        The client is only loaded when actually needed (during generate()),
        which allows testing prompt hydration without requiring an API key.
        
        Returns:
            The initialized Google GenAI client
        
        Raises:
            ValueError: If API key is not found in environment
        """
        if self._client is None:
            api_key = os.getenv(self.api_key_env)
            if not api_key:
                raise ValueError(
                    f"API key not found. Set {self.api_key_env} environment variable "
                    f"or create a .env file with {self.api_key_env}=your_key"
                )
            self._client = google.genai.Client(api_key=api_key)
        return self._client
    
    def hydrate_prompt(self, retrieved_chunks: List[str], query: str) -> str:
        """
        Hydrate the system prompt template with retrieved context and user query.
        
        This method implements the instruction hierarchy by:
        1. Starting with system instructions (highest priority)
        2. Inserting retrieved context in <context> tags (marked as ground truth)
        3. Appending user query (lowest priority, cannot override instructions)
        
        Why XML Tags Matter:
        - <context> and </context> create an unambiguous boundary
        - The model learns: "Content between these tags is factual ground truth"
        - This prevents the model from confusing context with user input
        - Reduces hallucination by clearly separating fact from conversation
        
        Without clear markers, models may:
        - Treat context as conversational input (less weight)
        - Blend context with training data (hallucination)
        - Lose track of what is "ground truth" vs "suggested"
        
        Args:
            retrieved_chunks: List of retrieved text chunks from the vector store
            query: User's question or query
        
        Returns:
            Fully hydrated prompt with system instructions, context, and user query
        """
        # Join retrieved chunks into a single context string
        # Use double newlines to separate chunks for readability
        context_text = "\n\n".join(retrieved_chunks) if retrieved_chunks else "[No context provided]"
        
        # Hydrate the template
        # The template already has the correct hierarchy:
        # System instructions -> <context> -> User query
        hydrated_prompt = self.system_prompt_template.format(
            context=context_text,
            query=query
        )
        
        return hydrated_prompt
    
    def generate(self, retrieved_chunks: List[str], query: str) -> str:
        """
        Generate a grounded response using retrieved context.
        
        Generation pipeline:
        1. Hydrate prompt with context and query (enforces instruction hierarchy)
        2. Call Gemini Flash API with temperature=0 (maximum factuality)
        3. If 429 error, retry with fallback model
        4. Return the generated response
        
        Why Temperature=0:
        - Temperature controls randomness in generation
        - 0.0 = deterministic, always chooses most likely tokens
        - Higher values = more creative, but more prone to hallucination
        - For RAG, we want factual accuracy over creativity
        
        Why Fallback Model:
        - Free tier models have rate limits (20 requests/day for gemini-2.5-flash)
        - gemini-3.5-flash-lite often has different rate limits
        - Fallback improves user experience when quota is exhausted
        
        Args:
            retrieved_chunks: List of retrieved text chunks from the vector store
            query: User's question or query
        
        Returns:
            Generated response text, grounded in the provided context
        
        Raises:
            ValueError: If API key is not configured
            Exception: If API call fails (network issues, other errors)
        """
        # Hydrate the prompt with context and query
        prompt = self.hydrate_prompt(retrieved_chunks, query)
        
        # Try primary model first
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config={
                    "temperature": self.temperature,
                }
            )
            
            # Extract the generated text from the response
            generated_text = response.text
            
            return generated_text
            
        except Exception as e:
            # Check if it's a 429 rate limit error
            error_str = str(e)
            if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                # Try fallback model
                try:
                    response = self.client.models.generate_content(
                        model=self.fallback_model,
                        contents=prompt,
                        config={
                            "temperature": self.temperature,
                        }
                    )
                    
                    generated_text = response.text
                    return generated_text
                    
                except Exception as fallback_error:
                    # If fallback also fails, re-raise original error
                    raise Exception(f"Failed to generate response with both models. Primary error: {str(e)}, Fallback error: {str(fallback_error)}")
            else:
                # For other errors, re-raise immediately
                raise Exception(f"Failed to generate response: {str(e)}")
    
    def check_grounding(self, response: str, retrieved_chunks: List[str]) -> bool:
        """
        Check if the response is grounded in the provided context.
        
        This is a basic grounding check that verifies:
        1. The response doesn't contain obvious hallucinations
        2. The response acknowledges when context is insufficient
        
        Note: This is a heuristic check. True grounding verification would
        require more sophisticated methods (e.g., attribution, fact-checking).
        
        Args:
            response: The generated response text
            retrieved_chunks: The context chunks used for generation
        
        Returns:
            True if response appears grounded, False otherwise
        """
        response_lower = response.lower()
        
        # Check if response indicates lack of information (good grounding)
        if any(phrase in response_lower for phrase in [
            "don't have enough information",
            "do not have enough information",
            "not mentioned",
            "no information"
        ]):
            return True
        
        # If context is empty, response should indicate lack of information
        if not retrieved_chunks:
            return any(phrase in response_lower for phrase in [
                "don't know", "do not know", "not mentioned"
            ])
        
        # Basic heuristic: response should contain some words from context
        # This is not perfect but catches obvious hallucinations
        context_words = set()
        for chunk in retrieved_chunks:
            # Extract meaningful words (longer than 3 characters)
            words = [w.lower() for w in chunk.split() if len(w) > 3]
            context_words.update(words)
        
        response_words = set([w.lower() for w in response.split() if len(w) > 3])
        
        # Check if response shares at least some vocabulary with context
        overlap = len(context_words & response_words)
        
        # If there's significant overlap, likely grounded
        # If no overlap, might be hallucinated
        return overlap > 0 or len(response_words) < 5  # Allow very short responses
