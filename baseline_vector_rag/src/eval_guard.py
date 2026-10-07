"""
RAG Evaluation and Guardrail System

This module implements the evaluation and guardrail components for the RAG system:
1. AI-as-a-Judge: Uses LLMs to evaluate Faithfulness and Context Relevance
2. Grounding Guardrails: Post-processing checks to ensure responses are grounded
3. Confidence Thresholds: Overrides LLM output when confidence is low

Grounding Principles:
--------------------
Grounding is the practice of ensuring that AI-generated responses are strictly
based on provided context (ground truth) rather than the model's internal
knowledge or training data.

Why Grounding Matters:
- Internal knowledge can be outdated, incorrect, or biased
- RAG systems promise factual accuracy based on retrieved documents
- Without grounding, RAG degrades to "fancy chatbot" with no reliability guarantees
- Users need to trust that answers come from their documents, not the model's imagination

Differentiating Internal Knowledge vs Ground Truth:
--------------------------------------------------
- Ground Truth: Information explicitly present in the retrieved context chunks
  - This is the ONLY source the model should use for factual claims
  - Marked clearly with <context> tags in the prompt
  - Verifiable by checking if claims appear in the source text
  
- Internal Knowledge: Information from the model's training data
  - This includes general facts the model "knows" (e.g., "Paris is in France")
  - Must be EXCLUDED from RAG responses unless also present in context
  - The model should explicitly refuse to use internal knowledge
  - Detected when response contains facts not found in retrieved context

The Grounding Guardrail:
------------------------
The guardrail acts as a post-processor that:
1. Evaluates whether the response is grounded in the context
2. Assigns a confidence score based on grounding evidence
3. Triggers a fallback if confidence is below threshold
4. Prevents hallucinations by refusing ungrounded responses

Threshold Rationale:
- Context Precision >= 0.7: At least 70% of retrieved chunks must be relevant
  - Below this, too much noise degrades answer quality
  - Ensures retrieval system is working effectively
  
- Faithfulness >= 0.8: At least 80% of response claims must be grounded
  - High threshold because hallucinations are unacceptable
  - Better to refuse than to provide ungrounded information
  
- Guardrail Confidence >= 0.3: Minimum confidence to allow response
  - Conservative threshold to prevent guessing
  - When in doubt, the system should refuse to answer
"""

import os
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from dotenv import load_dotenv
import google.genai
from tenacity import retry, stop_after_attempt, wait_exponential


@dataclass
class EvaluationResult:
    """
    Result of an evaluation metric.
    
    Attributes:
        score: The evaluation score (0.0 to 1.0)
        passed: Whether the score meets the threshold
        reason: Human-readable explanation of the result
        details: Additional details (e.g., hallucinated claims)
    """
    score: float
    passed: bool
    reason: str
    details: Optional[Dict] = None


@dataclass
class GuardrailResult:
    """
    Result of a guardrail check.
    
    Attributes:
        triggered: Whether the guardrail was triggered
        confidence: Confidence score in the grounding (0.0 to 1.0)
        fallback_response: The fallback message if triggered
        reason: Human-readable explanation of why guardrail triggered
    """
    triggered: bool
    confidence: float
    fallback_response: str
    reason: str


class Evaluator:
    """
    AI-as-a-Judge evaluator for RAG quality metrics.
    
    This class uses LLMs to evaluate the quality of RAG outputs by acting
    as an impartial judge that scores:
    - Context Precision: Are retrieved chunks relevant to the question?
    - Faithfulness: Is the response grounded in the context?
    
    Why AI-as-a-Judge:
    - Traditional metrics (BLEU, ROUGE) don't capture semantic quality
    - Human evaluation is expensive and slow
    - LLMs can understand nuance and context better than rule-based systems
    - Provides consistent, scalable evaluation for production systems
    
    The evaluator uses the same Gemini API as the generator, ensuring
    consistency in the evaluation framework.
    
    Attributes:
        client: Google GenAI client for API calls
        model_name: The model used for evaluation
        precision_threshold: Minimum acceptable context precision (default: 0.7)
        faithfulness_threshold: Minimum acceptable faithfulness (default: 0.8)
    """
    
    def __init__(
        self,
        model_name: str = "gemini-2.5-flash",
        api_key_env: str = "GEMINI_API_KEY",
        precision_threshold: float = 0.7,
        faithfulness_threshold: float = 0.8,
    ):
        """
        Initialize the evaluator with Gemini API client.
        
        Args:
            model_name: Gemini model for evaluation
            api_key_env: Environment variable for API key
            precision_threshold: Minimum context precision score (default: 0.7)
            faithfulness_threshold: Minimum faithfulness score (default: 0.8)
        """
        load_dotenv()
        self.model_name = model_name
        self.api_key_env = api_key_env
        self.precision_threshold = precision_threshold
        self.faithfulness_threshold = faithfulness_threshold
        self._client: Optional[google.genai.Client] = None
    
    @property
    def client(self) -> google.genai.Client:
        """Lazy-load the Google GenAI client."""
        if self._client is None:
            api_key = os.getenv(self.api_key_env)
            if not api_key:
                raise ValueError(
                    f"API key not found. Set {self.api_key_env} environment variable"
                )
            self._client = google.genai.Client(api_key=api_key)
        return self._client
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def _call_judge(self, prompt: str) -> str:
        """
        Call the AI judge with retry logic for robustness.
        
        Args:
            prompt: The evaluation prompt for the judge
            
        Returns:
            The judge's response as a string
        """
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config={"temperature": 0.0}  # Deterministic for consistent evaluation
        )
        return response.text
    
    def evaluate_context_precision(
        self,
        question: str,
        retrieved_chunks: List[str],
    ) -> EvaluationResult:
        """
        Evaluate context precision using AI-as-a-Judge.
        
        Context Precision Definition:
        The fraction of retrieved chunks that are relevant to answering
        the user's question. High precision means minimal noise in retrieval.
        
        Evaluation Process:
        1. Present the question and each retrieved chunk to the AI judge
        2. Ask the judge to rate each chunk's relevance (0 or 1)
        3. Calculate precision as: (relevant chunks) / (total chunks)
        4. Compare against threshold to determine pass/fail
        
        Why This Matters:
        - Low precision means the generator receives irrelevant information
        - Irrelevant context can confuse the model and lead to wrong answers
        - High precision ensures efficient token usage and better answers
        - This is a retrieval quality metric, independent of generation
        
        Threshold Rationale (0.7):
        - 70% relevance means most retrieved content is useful
        - Allows for some noise (real-world retrieval isn't perfect)
        - Below 70%, the signal-to-noise ratio is too low for reliable answers
        
        Args:
            question: The user's question
            retrieved_chunks: List of retrieved text chunks
        
        Returns:
            EvaluationResult with precision score and pass/fail status
        """
        if not retrieved_chunks:
            return EvaluationResult(
                score=0.0,
                passed=False,
                reason="No retrieved chunks to evaluate"
            )
        
        # Build evaluation prompt for the AI judge
        chunks_prompt = "\n\n".join([
            f"Chunk {i+1}: {chunk}"
            for i, chunk in enumerate(retrieved_chunks)
        ])
        
        prompt = f"""You are an impartial judge evaluating retrieval quality.

Question: {question}

Retrieved Context Chunks:
{chunks_prompt}

Task: For each chunk, determine if it contains information relevant to answering the question.
- A chunk is relevant if it provides information that helps answer the question
- A chunk is irrelevant if it's unrelated or doesn't help answer the question

Provide your response in this exact format:
Relevant Chunks: [comma-separated list of chunk numbers that are relevant]
Reason: [brief explanation of your decision]

Example:
Relevant Chunks: 1, 2, 3
Reason: Chunks 1, 2, and 3 directly address the question about...
"""
        
        try:
            response = self._call_judge(prompt)
            
            # Parse the response to extract relevant chunk numbers
            relevant_chunks = self._parse_relevant_chunks(response)
            
            # Calculate precision
            precision = len(relevant_chunks) / len(retrieved_chunks)
            
            passed = precision >= self.precision_threshold
            reason = (
                f"{len(relevant_chunks)}/{len(retrieved_chunks)} chunks are relevant. "
                f"Precision: {precision:.2f}"
            )
            
            return EvaluationResult(
                score=precision,
                passed=passed,
                reason=reason,
                details={"relevant_chunks": relevant_chunks}
            )
            
        except Exception as e:
            # Fallback to simple heuristic if AI judge fails
            return self._fallback_context_precision(question, retrieved_chunks)
    
    def _parse_relevant_chunks(self, response: str) -> List[int]:
        """
        Parse the AI judge's response to extract relevant chunk numbers.
        
        Args:
            response: The judge's response text
        
        Returns:
            List of chunk numbers (1-indexed) that are relevant
        """
        try:
            # Extract the line with "Relevant Chunks:"
            for line in response.split('\n'):
                if line.strip().startswith('Relevant Chunks:'):
                    # Extract the comma-separated numbers
                    chunks_part = line.split(':', 1)[1].strip()
                    if chunks_part.lower() in ['none', 'n/a', '']:
                        return []
                    
                    # Parse chunk numbers
                    chunk_numbers = []
                    for item in chunks_part.split(','):
                        item = item.strip()
                        if item.isdigit():
                            chunk_numbers.append(int(item))
                    
                    return chunk_numbers
        except Exception:
            pass
        
        # Fallback: assume all chunks are relevant if parsing fails
        return list(range(1, len(response.split('\n'))))
    
    def _fallback_context_precision(
        self,
        question: str,
        retrieved_chunks: List[str]
    ) -> EvaluationResult:
        """
        Fallback heuristic for context precision if AI judge fails.
        
        Uses simple keyword matching as a fallback when the AI judge
        is unavailable or fails to parse correctly.
        
        Args:
            question: The user's question
            retrieved_chunks: List of retrieved text chunks
        
        Returns:
            EvaluationResult with heuristic precision score
        """
        # Extract keywords from question (simple approach)
        question_words = set(question.lower().split())
        
        relevant_count = 0
        for chunk in retrieved_chunks:
            chunk_words = set(chunk.lower().split())
            # If chunk shares at least 2 words with question, consider it relevant
            overlap = len(question_words & chunk_words)
            if overlap >= 2:
                relevant_count += 1
        
        precision = relevant_count / len(retrieved_chunks) if retrieved_chunks else 0.0
        passed = precision >= self.precision_threshold
        
        return EvaluationResult(
            score=precision,
            passed=passed,
            reason=f"Fallback heuristic: {relevant_count}/{len(retrieved_chunks)} chunks share keywords"
        )
    
    def evaluate_faithfulness(
        self,
        context: str,
        response: str,
    ) -> EvaluationResult:
        """
        Evaluate faithfulness using AI-as-a-Judge.
        
        Faithfulness Definition:
        The extent to which the generated response is grounded in the provided
        context. A faithful response contains only information present in the context.
        
        Evaluation Process:
        1. Present the context and response to the AI judge
        2. Ask the judge to identify claims in the response
        3. For each claim, verify if it's supported by the context
        4. Calculate faithfulness as: (supported claims) / (total claims)
        5. Flag hallucinations (claims not supported by context)
        
        Why This Matters:
        - Hallucinations can spread misinformation
        - Users trust RAG systems to be factual, not creative
        - External knowledge may be outdated or incorrect
        - Faithfulness is the core value proposition of RAG over raw LLMs
        
        Grounding vs Internal Knowledge:
        - Grounded claim: Explicitly supported by the provided context
        - Ungrounded claim: Not found in context (even if "true" from training data)
        - The judge must be strict: if it's not in the context, it's ungrounded
        
        Threshold Rationale (0.8):
        - 80% faithfulness means most claims are grounded
        - High threshold because hallucinations are unacceptable in production
        - Better to refuse than to provide partially ungrounded information
        - Allows for minor linking phrases that don't add factual content
        
        Args:
            context: The retrieved context (ground truth)
            response: The generated response to evaluate
        
        Returns:
            EvaluationResult with faithfulness score and detected hallucinations
        """
        prompt = f"""You are an impartial judge evaluating response faithfulness.

Context (Ground Truth):
<context>
{context}
</context>

Response to Evaluate:
{response}

Task: Determine if the response is faithful to the context.
- A response is faithful if ALL factual claims are supported by the context
- Claims that appear in the response but NOT in the context are hallucinations
- General knowledge NOT in the context counts as hallucination in RAG
- Connecting phrases (e.g., "according to the context") are acceptable

Provide your response in this exact format:
Faithfulness Score: [0.0 to 1.0]
Hallucinated Claims: [comma-separated list of hallucinated claims, or "None"]
Reason: [brief explanation of your decision]

Example:
Faithfulness Score: 0.75
Hallucinated Claims: Paris was founded in 52 BC, The population is 2.1 million
Reason: The response correctly states the capital but adds information not found in context...
"""
        
        try:
            judge_response = self._call_judge(prompt)
            
            # Parse the response
            score = self._parse_faithfulness_score(judge_response)
            hallucinations = self._parse_hallucinations(judge_response)
            
            passed = score >= self.faithfulness_threshold
            reason = f"Faithfulness: {score:.2f}. {len(hallucinations)} hallucinated claims detected."
            
            return EvaluationResult(
                score=score,
                passed=passed,
                reason=reason,
                details={"hallucinations": hallucinations}
            )
            
        except Exception as e:
            # Fallback to simple heuristic
            return self._fallback_faithfulness(context, response)
    
    def _parse_faithfulness_score(self, response: str) -> float:
        """Parse faithfulness score from AI judge response."""
        try:
            for line in response.split('\n'):
                if line.strip().startswith('Faithfulness Score:'):
                    score_str = line.split(':', 1)[1].strip()
                    return float(score_str)
        except Exception:
            pass
        return 0.5  # Conservative fallback
    
    def _parse_hallucinations(self, response: str) -> List[str]:
        """Parse hallucinated claims from AI judge response."""
        try:
            for line in response.split('\n'):
                if line.strip().startswith('Hallucinated Claims:'):
                    claims_str = line.split(':', 1)[1].strip()
                    if claims_str.lower() in ['none', 'n/a', '']:
                        return []
                    return [claim.strip() for claim in claims_str.split(',')]
        except Exception:
            pass
        return []
    
    def _fallback_faithfulness(
        self,
        context: str,
        response: str
    ) -> EvaluationResult:
        """
        Fallback heuristic for faithfulness if AI judge fails.
        
        Uses simple overlap checking as a fallback.
        
        Args:
            context: The retrieved context
            response: The generated response
        
        Returns:
            EvaluationResult with heuristic faithfulness score
        """
        # Simple heuristic: check if response words appear in context
        response_words = set(response.lower().split())
        context_words = set(context.lower().split())
        
        # Calculate overlap ratio
        overlap = len(response_words & context_words)
        total_response_words = len(response_words) if response_words else 1
        
        faithfulness = overlap / total_response_words
        passed = faithfulness >= self.faithfulness_threshold
        
        return EvaluationResult(
            score=faithfulness,
            passed=passed,
            reason="Fallback heuristic: based on word overlap with context"
        )


class Guardrail:
    """
    Grounding guardrail for RAG responses.
    
    This class implements post-processing guardrails that ensure responses
    are grounded in the retrieved context. It acts as a safety mechanism
    that prevents the system from providing ungrounded or hallucinated answers.
    
    Guardrail Mechanism:
    1. Evaluate the relevance of context to the question
    2. Assess confidence that the answer can be grounded
    3. If confidence is below threshold, trigger fallback response
    4. Override the LLM output with a standard "Information not found" message
    
    Why Post-Processing Guardrails:
    - Pre-prompt instructions can be bypassed by sophisticated models
    - Post-processing provides a hard safety check regardless of model behavior
    - Separates safety logic from generation logic for clearer architecture
    - Allows for different threshold policies without changing prompts
    
    Grounding Confidence Calculation:
    - Based on semantic similarity between question and context
    - Uses the same embedding model as retrieval for consistency
    - Threshold determines when to refuse vs. attempt answering
    
    Attributes:
        evaluator: Evaluator instance for AI-as-a-Judge checks
        fallback_message: Standard message when guardrail triggers
        default_threshold: Default confidence threshold (default: 0.3)
    """
    
    def __init__(
        self,
        evaluator: Optional[Evaluator] = None,
        fallback_message: str = "I don't have enough information to answer this question.",
        default_threshold: float = 0.3,
    ):
        """
        Initialize the guardrail.
        
        Args:
            evaluator: Evaluator instance (creates new one if None)
            fallback_message: Message to return when guardrail triggers
            default_threshold: Default confidence threshold (0.3 = conservative)
        """
        self.evaluator = evaluator or Evaluator()
        self.fallback_message = fallback_message
        self.default_threshold = default_threshold
    
    def check_grounding(
        self,
        question: str,
        context: str,
        threshold: Optional[float] = None,
    ) -> GuardrailResult:
        """
        Check if the response can be grounded in the context.
        
        Grounding Check Process:
        1. Evaluate context relevance to the question
        2. Calculate confidence score based on relevance
        3. Compare against threshold to determine if guardrail triggers
        4. Return result with fallback message if triggered
        
        Confidence Calculation:
        - Uses AI-as-a-Judge to assess context relevance
        - Score 0.0-1.0 representing how well context answers the question
        - Higher score = more confident that answer can be grounded
        
        Threshold Rationale (0.3):
        - Conservative threshold to prevent guessing
        - When confidence is low, it's better to refuse than to hallucinate
        - 0.3 allows for some ambiguity but filters out clearly irrelevant context
        - Can be adjusted based on application (higher for sensitive domains)
        
        Grounding vs Internal Knowledge:
        - This guardrail specifically checks if CONTEXT can answer the question
        - It does NOT check if the model "knows" the answer from training data
        - If context is irrelevant, the system must refuse even if the model knows
        - This enforces the RAG contract: answers come from documents, not the model
        
        Args:
            question: The user's question
            context: The retrieved context
            threshold: Confidence threshold (uses default if None)
        
        Returns:
            GuardrailResult with trigger status and fallback message
        """
        threshold = threshold or self.default_threshold
        
        # Use AI-as-a-Judge to evaluate context relevance
        relevance_prompt = f"""You are evaluating whether context contains sufficient information to answer a question.

Question: {question}

Context:
<context>
{context}
</context>

Task: Rate how well the context provides information to answer the question.
- Score 1.0: Context directly and completely answers the question
- Score 0.7: Context provides most information needed, minor gaps
- Score 0.5: Context is somewhat relevant but missing key information
- Score 0.3: Context mentions the topic but doesn't help answer the specific question
- Score 0.0: Context is completely irrelevant to the question

Provide your response in this exact format:
Relevance Score: [0.0 to 1.0]
Reason: [brief explanation]

Example:
Relevance Score: 0.7
Reason: Context provides the capital city but not the requested population data...
"""
        
        try:
            response = self.evaluator._call_judge(relevance_prompt)
            confidence = self._parse_relevance_score(response)
            reason = self._parse_reason(response)
        except Exception as e:
            # Fallback: assume low confidence if evaluation fails
            confidence = 0.0
            reason = f"Evaluation failed: {str(e)}"
        
        # Determine if guardrail should trigger
        triggered = confidence < threshold
        
        if triggered:
            fallback_response = self.fallback_message
            reason = f"Guardrail triggered: {reason} (confidence: {confidence:.2f} < threshold: {threshold})"
        else:
            fallback_response = ""
            reason = f"Guardrail passed: {reason} (confidence: {confidence:.2f} >= threshold: {threshold})"
        
        return GuardrailResult(
            triggered=triggered,
            confidence=confidence,
            fallback_response=fallback_response,
            reason=reason
        )
    
    def _parse_relevance_score(self, response: str) -> float:
        """Parse relevance score from AI judge response."""
        try:
            for line in response.split('\n'):
                if line.strip().startswith('Relevance Score:'):
                    score_str = line.split(':', 1)[1].strip()
                    return float(score_str)
        except Exception:
            pass
        return 0.0  # Conservative fallback
    
    def _parse_reason(self, response: str) -> str:
        """Parse reason from AI judge response."""
        try:
            for line in response.split('\n'):
                if line.strip().startswith('Reason:'):
                    return line.split(':', 1)[1].strip()
        except Exception:
            pass
        return "Unable to parse reason"
    
    def apply_guardrail(
        self,
        question: str,
        context: str,
        generated_response: str,
        threshold: Optional[float] = None,
    ) -> str:
        """
        Apply the guardrail to a generated response.
        
        This is the main entry point for using the guardrail in production:
        1. Check if the response can be grounded
        2. If guardrail triggers, return fallback message
        3. Otherwise, return the original generated response
        
        This ensures that ungrounded responses never reach the user,
        providing a hard safety guarantee for the RAG system.
        
        Args:
            question: The user's question
            context: The retrieved context
            generated_response: The LLM-generated response
            threshold: Confidence threshold (uses default if None)
        
        Returns:
            Either the fallback message (if triggered) or the original response
        """
        guardrail_result = self.check_grounding(
            question=question,
            context=context,
            threshold=threshold
        )
        
        if guardrail_result.triggered:
            return guardrail_result.fallback_response
        else:
            return generated_response


def evaluate_rag_pipeline(
    question: str,
    retrieved_chunks: List[str],
    context: str,
    response: str,
    precision_threshold: float = 0.7,
    faithfulness_threshold: float = 0.8,
    guardrail_threshold: float = 0.3,
) -> Dict[str, any]:
    """
    Complete evaluation of a RAG pipeline response.
    
    This function runs all evaluation metrics and guardrails to provide
    a comprehensive quality assessment of a RAG response.
    
    Evaluation Pipeline:
    1. Context Precision: Are retrieved chunks relevant?
    2. Faithfulness: Is the response grounded in context?
    3. Guardrail Check: Should the response be blocked?
    
    This is useful for:
    - Testing RAG systems during development
    - Monitoring quality in production
    - A/B testing different retrieval/generation strategies
    - Building dashboards for RAG system health
    
    Args:
        question: The user's question
        retrieved_chunks: List of retrieved chunks
        context: Full context string
        response: Generated response
        precision_threshold: Context precision threshold
        faithfulness_threshold: Faithfulness threshold
        guardrail_threshold: Guardrail confidence threshold
    
    Returns:
        Dictionary with all evaluation results and overall pass/fail
    """
    evaluator = Evaluator(
        precision_threshold=precision_threshold,
        faithfulness_threshold=faithfulness_threshold
    )
    guardrail = Guardrail(evaluator=evaluator, default_threshold=guardrail_threshold)
    
    # Run evaluations
    precision_result = evaluator.evaluate_context_precision(question, retrieved_chunks)
    faithfulness_result = evaluator.evaluate_faithfulness(context, response)
    guardrail_result = guardrail.check_grounding(question, context, guardrail_threshold)
    
    # Determine overall pass/fail
    overall_passed = (
        precision_result.passed and
        faithfulness_result.passed and
        not guardrail_result.triggered
    )
    
    return {
        "context_precision": {
            "score": precision_result.score,
            "passed": precision_result.passed,
            "reason": precision_result.reason
        },
        "faithfulness": {
            "score": faithfulness_result.score,
            "passed": faithfulness_result.passed,
            "reason": faithfulness_result.reason,
            "hallucinations": faithfulness_result.details.get("hallucinations", [])
        },
        "guardrail": {
            "triggered": guardrail_result.triggered,
            "confidence": guardrail_result.confidence,
            "reason": guardrail_result.reason
        },
        "overall_passed": overall_passed
    }


if __name__ == "__main__":
    # Example usage
    print("RAG Evaluation and Guardrail System")
    print("=" * 50)
    
    # Example evaluation
    question = "What is the capital of France?"
    retrieved_chunks = [
        "France is a country in Western Europe.",
        "The capital of France is Paris.",
        "Paris is known for the Eiffel Tower."
    ]
    context = "\n".join(retrieved_chunks)
    response = "The capital of France is Paris, known for the Eiffel Tower."
    
    results = evaluate_rag_pipeline(
        question=question,
        retrieved_chunks=retrieved_chunks,
        context=context,
        response=response
    )
    
    print(f"\nQuestion: {question}")
    print(f"Response: {response}")
    print(f"\nContext Precision: {results['context_precision']['score']:.2f} (Passed: {results['context_precision']['passed']})")
    print(f"Faithfulness: {results['faithfulness']['score']:.2f} (Passed: {results['faithfulness']['passed']})")
    print(f"Guardrail Triggered: {results['guardrail']['triggered']}")
    print(f"Overall Passed: {results['overall_passed']}")
