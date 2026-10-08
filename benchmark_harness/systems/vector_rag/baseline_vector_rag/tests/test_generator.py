"""
TDD Test Suite for Grounded Generation with Context Injection

These tests define the expected behavior of the generator before implementation.
Following TDD principles: tests first, implementation second.
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from generator import Generator


class TestPromptHydration:
    """Verify that retrieved chunks are correctly inserted into the system prompt template."""
    
    def test_single_chunk_inserted_correctly(self):
        """Single retrieved chunk should be inserted into context section."""
        generator = Generator()
        retrieved_chunks = ["This is a test chunk about machine learning."]
        query = "What is machine learning?"
        
        hydrated_prompt = generator.hydrate_prompt(retrieved_chunks, query)
        
        assert "<context>" in hydrated_prompt, "Prompt should contain context opening tag"
        assert "</context>" in hydrated_prompt, "Prompt should contain context closing tag"
        assert "This is a test chunk about machine learning." in hydrated_prompt, \
            "Retrieved chunk should be in the prompt"
        assert "What is machine learning?" in hydrated_prompt, "User query should be in the prompt"
    
    def test_multiple_chunks_formatted_correctly(self):
        """Multiple chunks should be formatted with proper separation."""
        generator = Generator()
        retrieved_chunks = [
            "First chunk about neural networks.",
            "Second chunk about deep learning.",
            "Third chunk about AI applications."
        ]
        query = "Explain neural networks"
        
        hydrated_prompt = generator.hydrate_prompt(retrieved_chunks, query)
        
        # All chunks should be present
        for chunk in retrieved_chunks:
            assert chunk in hydrated_prompt, f"Chunk '{chunk}' should be in the prompt"
        
        # Context tags should be present
        assert "<context>" in hydrated_prompt
        assert "</context>" in hydrated_prompt
        
        # User query should be present
        assert query in hydrated_prompt
    
    def test_empty_chunks_handling(self):
        """Empty retrieved chunks should be handled gracefully."""
        generator = Generator()
        retrieved_chunks = []
        query = "Test query"
        
        hydrated_prompt = generator.hydrate_prompt(retrieved_chunks, query)
        
        # Should still have context tags but empty content
        assert "<context>" in hydrated_prompt
        assert "</context>" in hydrated_prompt
        assert query in hydrated_prompt
    
    def test_xml_tags_separate_context_from_query(self):
        """XML tags should clearly separate ground truth context from user query."""
        generator = Generator()
        retrieved_chunks = ["Context information here"]
        query = "User question here"
        
        hydrated_prompt = generator.hydrate_prompt(retrieved_chunks, query)
        
        # Verify structure: system prompt -> <context> -> chunks -> </context> -> user query
        context_start = hydrated_prompt.index("<context>")
        context_end = hydrated_prompt.index("</context>")
        query_pos = hydrated_prompt.index(query)
        
        # Query should come after context closing tag
        assert query_pos > context_end, "User query should come after context section"
    
    def test_system_instructions_present(self):
        """System instructions should be present in the hydrated prompt."""
        generator = Generator()
        retrieved_chunks = ["Test chunk"]
        query = "Test query"
        
        hydrated_prompt = generator.hydrate_prompt(retrieved_chunks, query)
        
        # Should contain key system instruction phrases
        assert "ONLY" in hydrated_prompt or "only" in hydrated_prompt.lower(), \
            "System prompt should instruct to use ONLY provided context"
        assert "expert" in hydrated_prompt.lower() or "assistant" in hydrated_prompt.lower(), \
            "System prompt should define the assistant role"


class TestGroundingCheck:
    """Verify grounding check with actual API calls."""
    
    @pytest.mark.integration
    def test_irrelevant_context_triggers_idk_response(self):
        """When context is irrelevant, model should say 'I don't know' or similar."""
        # Skip if API key not available
        if not os.getenv("GEMINI_API_KEY"):
            pytest.skip("GEMINI_API_KEY not set")
        
        generator = Generator()
        # Context about cooking, query about quantum physics
        retrieved_chunks = [
            "To make a perfect pasta, boil water and add salt.",
            "Cook pasta for 8-10 minutes until al dente."
        ]
        query = "What is quantum entanglement?"
        
        response = generator.generate(retrieved_chunks, query)
        
        # Response should indicate lack of information
        response_lower = response.lower()
        assert any(phrase in response_lower for phrase in [
            "don't know", "do not know", "not mentioned", "no information",
            "cannot answer", "unable to answer", "don't have enough information"
        ]), f"Model should indicate inability to answer. Got: {response}"
    
    @pytest.mark.integration
    def test_relevant_context_provides_grounded_answer(self):
        """When context is relevant, model should provide grounded answer."""
        # Skip if API key not available
        if not os.getenv("GEMINI_API_KEY"):
            pytest.skip("GEMINI_API_KEY not set")
        
        generator = Generator()
        # Context about machine learning, query about machine learning
        retrieved_chunks = [
            "Machine learning is a subset of AI that uses algorithms to learn from data.",
            "Deep learning is a specialized branch using neural networks with multiple layers."
        ]
        query = "What is machine learning?"
        
        response = generator.generate(retrieved_chunks, query)
        
        # Response should contain information from context
        response_lower = response.lower()
        assert any(word in response_lower for word in [
            "machine learning", "algorithms", "data", "learn"
        ]), f"Response should use context. Got: {response}"
        
        # Should not indicate lack of information
        assert not any(phrase in response_lower for phrase in [
            "don't know", "do not know", "not mentioned"
        ]), "Response should not indicate lack of information when context is relevant"
    
    @pytest.mark.integration
    def test_response_stays_within_context_boundaries(self):
        """Model should not hallucinate information outside provided context."""
        # Skip if API key not available
        if not os.getenv("GEMINI_API_KEY"):
            pytest.skip("GEMINI_API_KEY not set")
        
        generator = Generator()
        # Very specific context
        retrieved_chunks = [
            "The Eiffel Tower is 330 meters tall and located in Paris."
        ]
        query = "Tell me about the Eiffel Tower"
        
        response = generator.generate(retrieved_chunks, query)
        
        # Response should only contain information from context
        # It should not add details like "built in 1889" or "engineer Gustave Eiffel"
        # unless those were in the context
        response_lower = response.lower()
        
        # These are facts NOT in our context
        hallucinated_facts = ["1889", "gustave eiffel", "exposition", "world's fair"]
        
        for fact in hallucinated_facts:
            assert fact not in response_lower, \
                f"Response should not hallucinate '{fact}' not in context. Got: {response}"


class TestInstructionHierarchy:
    """Verify that system instructions take precedence over user input."""
    
    def test_system_instructions_precede_user_query(self):
        """System instructions should come before user query in the prompt."""
        generator = Generator()
        retrieved_chunks = ["Context chunk"]
        query = "User query"
        
        hydrated_prompt = generator.hydrate_prompt(retrieved_chunks, query)
        
        # Find positions
        system_instruction_pos = hydrated_prompt.lower().find("expert")
        query_pos = hydrated_prompt.find(query)
        
        # System instruction should come before query
        assert system_instruction_pos < query_pos, \
            "System instructions should precede user query in prompt hierarchy"
    
    def test_context_section_between_system_and_query(self):
        """Context section should be between system instructions and user query."""
        generator = Generator()
        retrieved_chunks = ["Context chunk"]
        query = "User query"
        
        hydrated_prompt = generator.hydrate_prompt(retrieved_chunks, query)
        
        system_pos = hydrated_prompt.lower().find("expert")
        context_start = hydrated_prompt.find("<context>")
        context_end = hydrated_prompt.find("</context>")
        query_pos = hydrated_prompt.find(query)
        
        # Verify hierarchy: System -> Context -> Query
        assert system_pos < context_start < context_end < query_pos, \
            "Prompt should follow hierarchy: System -> Context -> Query"
    
    def test_system_instruction_enforces_context_only(self):
        """System instruction should explicitly enforce using only provided context."""
        generator = Generator()
        retrieved_chunks = ["Context"]
        query = "Query"
        
        hydrated_prompt = generator.hydrate_prompt(retrieved_chunks, query)
        
        # Should contain explicit instruction to use only context
        assert any(phrase in hydrated_prompt.lower() for phrase in [
            "only the following", "only use", "use only", "based on"
        ]), "System instruction should enforce context-only usage"


class TestGeneratorEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_empty_retrieved_context(self):
        """Empty retrieved context should be handled gracefully."""
        generator = Generator()
        retrieved_chunks = []
        query = "Test query"
        
        hydrated_prompt = generator.hydrate_prompt(retrieved_chunks, query)
        
        # Should still produce valid prompt structure
        assert "<context>" in hydrated_prompt
        assert "</context>" in hydrated_prompt
        assert query in hydrated_prompt
    
    def test_empty_query(self):
        """Empty query should be handled gracefully."""
        generator = Generator()
        retrieved_chunks = ["Context chunk"]
        query = ""
        
        hydrated_prompt = generator.hydrate_prompt(retrieved_chunks, query)
        
        # Should still produce valid prompt structure
        assert "<context>" in hydrated_prompt
        assert "</context>" in hydrated_prompt
        assert "Context chunk" in hydrated_prompt
    
    
    def test_very_long_context_handling(self):
        """Very long context should be handled without errors."""
        generator = Generator()
        # Create a large context
        retrieved_chunks = ["Chunk " + str(i) + " " * 100 for i in range(50)]
        query = "Test query"
        
        hydrated_prompt = generator.hydrate_prompt(retrieved_chunks, query)
        
        # Should still have proper structure
        assert "<context>" in hydrated_prompt
        assert "</context>" in hydrated_prompt
        assert query in hydrated_prompt
        # All chunks should be present
        for chunk in retrieved_chunks:
            assert chunk in hydrated_prompt
    
    def test_fallback_model_configuration(self):
        """Test that fallback model is configured correctly."""
        generator = Generator()
        
        assert generator.fallback_model == "gemini-3.5-flash-lite"
    
    def test_custom_fallback_model(self):
        """Test that custom fallback model can be set."""
        generator = Generator(fallback_model="custom-model")
        
        assert generator.fallback_model == "custom-model"
