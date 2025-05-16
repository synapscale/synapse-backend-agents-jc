"""
Response Evaluators for the Main Agent

This module can contain functions to evaluate the quality, relevance, or other aspects
of the agent's responses. This is crucial for monitoring, testing, and improving the agent.

Use cases:
- Scoring response relevance to the user query.
- Checking for factual consistency (e.g., against a ground truth or knowledge base).
- Evaluating response helpfulness, clarity, or tone.
- Detecting hallucinations or undesirable content (though some of this might be in safety filters).
- Comparing responses from different model versions or prompt strategies (A/B testing).

These evaluators might be run offline on logged data or, in some cases, online for 
real-time feedback (though online evaluation needs to be fast).
"""
from typing import Dict, Any, Optional, Union, List

def evaluate_response_relevance_dummy(query: str, response: str, agent_config: Dict[str, Any]) -> float:
    """
    Dummy evaluator for response relevance.
    In a real system, this might use another LLM, embedding similarity, or keyword matching.
    Returns a score between 0.0 (not relevant) and 1.0 (highly relevant).
    """
    # Extremely simple heuristic for demonstration
    query_words = set(query.lower().split())
    response_words = set(response.lower().split())
    common_words = query_words.intersection(response_words)
    
    relevance_score = 0.0
    if query_words:
        relevance_score = len(common_words) / len(query_words)
    
    print(f"[EVALUATOR DUMMY] Relevance for query '{query[:30]}...' and response '{response[:30]}...': {relevance_score:.2f}")
    return min(relevance_score, 1.0) # Cap at 1.0

def check_for_hallucination_keywords_dummy(response: str, agent_config: Dict[str, Any]) -> bool:
    """
    Dummy check for keywords that *might* indicate a hallucination or uncertainty.
    This is a very naive approach.
    Returns True if suspicious keywords are found, False otherwise.
    """
    suspicious_keywords = [
        "as an ai language model, i cannot",
        "i am not able to",
        "i do not have access to real-time information",
        "my knowledge cutoff is",
        "based on my training data up to"
        # Add more specific patterns if needed
    ]
    response_lower = response.lower()
    for keyword in suspicious_keywords:
        if keyword in response_lower:
            print(f"[EVALUATOR DUMMY] Potential hallucination/limitation keyword found: '{keyword}'")
            return True
    return False

# This dictionary could map evaluator names to functions for easier calling
RESPONSE_EVALUATORS = {
    "relevance_dummy": evaluate_response_relevance_dummy,
    "hallucination_keywords_dummy": check_for_hallucination_keywords_dummy
}

if __name__ == "__main__":
    print("Testing response evaluators (dummy implementations)...")
    mock_config = {"agent_name": "TestAgentForEvaluators"}

    test_query_1 = "Tell me about Large Language Models."
    test_response_1_good = "Large Language Models, or LLMs, are advanced AI systems trained on vast amounts of text data to understand and generate human-like language. They are used in various applications."
    test_response_1_bad = "Elephants are large mammals found in Africa and Asia."
    test_response_1_hallucination = "As an AI language model, I cannot provide personal opinions, but LLMs are from the future."

    print(f"\nEvaluating: Query: '{test_query_1}'")
    
    relevance_good = evaluate_response_relevance_dummy(test_query_1, test_response_1_good, mock_config)
    hallucination_good = check_for_hallucination_keywords_dummy(test_response_1_good, mock_config)
    print(f"Good Response - Relevance: {relevance_good:.2f}, Hallucination Keyword Found: {hallucination_good}")

    relevance_bad = evaluate_response_relevance_dummy(test_query_1, test_response_1_bad, mock_config)
    hallucination_bad = check_for_hallucination_keywords_dummy(test_response_1_bad, mock_config)
    print(f"Bad Response - Relevance: {relevance_bad:.2f}, Hallucination Keyword Found: {hallucination_bad}")

    relevance_hallucination = evaluate_response_relevance_dummy(test_query_1, test_response_1_hallucination, mock_config)
    hallucination_hallucination = check_for_hallucination_keywords_dummy(test_response_1_hallucination, mock_config)
    print(f"Hallucination Response - Relevance: {relevance_hallucination:.2f}, Hallucination Keyword Found: {hallucination_hallucination}")

    # Example of using the dictionary
    if "relevance_dummy" in RESPONSE_EVALUATORS:
        score = RESPONSE_EVALUATORS["relevance_dummy"](test_query_1, test_response_1_good, mock_config)
        print(f"Accessed via dict - Relevance: {score:.2f}")

