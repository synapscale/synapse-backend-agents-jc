"""
Response Parsers for the Main Agent

This module contains functions to parse and structure the raw response from the LLM
before it is further processed or sent to post-response callbacks.

Use cases:
- Extracting structured data (e.g., JSON, XML) if the LLM was prompted to produce it.
- Cleaning up common LLM artifacts (e.g., preamble, apologies, self-corrections).
- Identifying if the LLM intends to use a specific tool or delegate to a sub-agent
  (though more complex tool use is often handled by dedicated LLM features like function calling).
- Normalizing the response format.
"""
import json
from typing import Union, Dict, Any, Optional, List

def extract_json_from_llm_response(llm_output: str, agent_config: Dict[str, Any]) -> Optional[Union[Dict[str, Any], List[Any]]]:
    """
    Attempts to extract a JSON object or array from the LLM's text output.
    This is useful if the LLM was explicitly prompted to return JSON.
    Looks for JSON within ```json ... ``` or ``` ... ``` blocks or as the whole string.
    """
    import re
    # Regex to find JSON within ```json ... ``` or ``` ... ``` code blocks
    # It handles optional "json" language specifier and potential leading/trailing newlines within the block.
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", llm_output, re.DOTALL)
    
    json_str_to_parse = None
    if match:
        json_str_to_parse = match.group(1).strip()
        print(f"[PARSER] Found JSON block: {json_str_to_parse[:100]}...")
    else:
        # If no explicit block, try to parse the whole string, or a significant part of it
        # This is less reliable and should be used if the LLM is expected to return ONLY JSON.
        # For safety, we might only try if the string starts with { or [
        stripped_output = llm_output.strip()
        if stripped_output.startswith("{") and stripped_output.endswith("}") or \
           stripped_output.startswith("[") and stripped_output.endswith("]"):
            json_str_to_parse = stripped_output
            print(f"[PARSER] Attempting to parse entire LLM output as JSON: {json_str_to_parse[:100]}...")

    if json_str_to_parse:
        try:
            parsed_json = json.loads(json_str_to_parse)
            print(f"[PARSER] Successfully parsed JSON from LLM response.")
            return parsed_json
        except json.JSONDecodeError as e:
            print(f"[PARSER] Failed to decode JSON from LLM response: {e}. String was: {json_str_to_parse[:200]}...")
            return None
    else:
        # print(f"[PARSER] No JSON block found in LLM response: {llm_output[:100]}...")
        return None

def clean_llm_text_artifacts(llm_output: str, agent_config: Dict[str, Any]) -> str:
    """
    Removes common conversational artifacts or preambles from LLM text responses.
    Example: "Okay, here is the information you requested: ..."
    """
    cleaned_text = llm_output
    
    # Patterns to remove (case-insensitive)
    # These are examples; they would need to be tailored.
    preambles = [
        r"Okay, here is the information you requested:?",
        r"Sure, I can help with that!",
        r"Here's the answer:?",
        r"Certainly, here you go:?",
        r"As an AI language model, I found that:?"
        # Add more common preambles
    ]
    
    import re
    for preamble_pattern in preambles:
        # Using re.IGNORECASE for case-insensitivity, and ensuring the pattern matches at the beginning (^) after stripping whitespace.
        # We strip leading whitespace from the text before matching, then add it back if the preamble was removed.
        leading_whitespace = len(cleaned_text) - len(cleaned_text.lstrip())
        stripped_text = cleaned_text.lstrip()
        
        match = re.match(preamble_pattern, stripped_text, re.IGNORECASE)
        if match:
            # Remove the matched preamble and any immediate following whitespace (like a newline)
            stripped_text = stripped_text[match.end():].lstrip()
            cleaned_text = " " * leading_whitespace + stripped_text # Restore leading whitespace
            print(f"[PARSER] Removed preamble: {match.group(0)}")
            # break # Remove only the first found preamble, or loop to remove all

    # Remove trailing self-promotional or closing remarks if necessary
    # postambles = [r"Is there anything else I can help you with today\??"] 
    # for postamble_pattern in postambles:
    #    cleaned_text = re.sub(postamble_pattern + r"\s*$", "", cleaned_text, flags=re.IGNORECASE).rstrip()

    return cleaned_text.strip() # Final strip for good measure

# List of parser functions. The agent might apply them sequentially or selectively.
# The order can matter.
RESPONSE_PARSERS = {
    "extract_json": extract_json_from_llm_response,
    "clean_text": clean_llm_text_artifacts
}

if __name__ == "__main__":
    print("Testing response parsers...")
    mock_config = {"agent_name": "TestAgentForParsers"}

    # Test JSON extraction
    llm_response_with_json_block = "Some text before... ```json\n{\"name\": \"Test JSON\", \"value\": 123, \"nested\": {\"key\": \"val\"}}\n``` Some text after."
    print(f"\nTesting JSON extraction from: {llm_response_with_json_block}")
    parsed_data = extract_json_from_llm_response(llm_response_with_json_block, mock_config)
    if parsed_data:
        print(f"Extracted JSON: {parsed_data}")
    else:
        print("No JSON extracted or parse error.")

    llm_response_pure_json = "{\"status\": \"success\", \"data\": [1, 2, 3]}"
    print(f"\nTesting JSON extraction from pure JSON string: {llm_response_pure_json}")
    parsed_data_pure = extract_json_from_llm_response(llm_response_pure_json, mock_config)
    if parsed_data_pure:
        print(f"Extracted JSON: {parsed_data_pure}")
    else:
        print("No JSON extracted or parse error.")
        
    llm_response_no_json = "This is a plain text response without any JSON."
    print(f"\nTesting JSON extraction from no JSON string: {llm_response_no_json}")
    parsed_data_no_json = extract_json_from_llm_response(llm_response_no_json, mock_config)
    if parsed_data_no_json:
        print(f"Extracted JSON: {parsed_data_no_json}") # Should be None
    else:
        print("Correctly no JSON extracted.")

    # Test text cleaning
    llm_response_with_preamble = "Okay, here is the information you requested: The capital of France is Paris."
    print(f"\nTesting text cleaning from: {llm_response_with_preamble}")
    cleaned_text = clean_llm_text_artifacts(llm_response_with_preamble, mock_config)
    print(f"Cleaned text: {cleaned_text}")
    
    llm_response_with_preamble_variation = "  Sure, I can help with that! The main point is X."
    print(f"\nTesting text cleaning from: {llm_response_with_preamble_variation}")
    cleaned_text_var = clean_llm_text_artifacts(llm_response_with_preamble_variation, mock_config)
    print(f"Cleaned text: {cleaned_text_var}")

    llm_response_clean = "This is a direct answer."
    print(f"\nTesting text cleaning from already clean text: {llm_response_clean}")
    cleaned_text_clean = clean_llm_text_artifacts(llm_response_clean, mock_config)
    print(f"Cleaned text: {cleaned_text_clean}")

