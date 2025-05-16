"""
Response Formatters for the Main Agent

This module contains functions to format the agent's final processed response
into the desired output structure before it is sent (e.g., by a sender module
or directly by the entrypoint).

Use cases:
- Structuring the response as JSON, XML, or other formats if not already done.
- Ensuring the response adheres to a predefined API contract.
- Adding metadata to the response (e.g., session ID, timestamps, confidence scores).
"""
import json
from typing import Dict, Any, Union
import datetime

def format_as_json_response(data_to_format: Any, request_data: Dict[str, Any], agent_config: Dict[str, Any]) -> str:
    """
    Formats the given data into a JSON string, potentially adding standard envelope fields.
    """
    session_id = request_data.get("session_id", "N/A")
    response_timestamp = datetime.datetime.utcnow().isoformat()

    # Standard envelope for the response
    response_envelope = {
        "session_id": session_id,
        "timestamp_utc": response_timestamp,
        "agent_name": agent_config.get("agent_name", "VerticalAgent"),
        "payload": data_to_format # This could be a string or a structured dict
    }
    
    try:
        json_response = json.dumps(response_envelope, indent=2, ensure_ascii=False)
        print(f"[FORMATTER] MainAgent - Session: {session_id} - Formatted response as JSON.")
        return json_response
    except TypeError as e:
        print(f"[FORMATTER] MainAgent - Session: {session_id} - Error formatting to JSON: {e}. Returning raw data as string within envelope.")
        response_envelope["payload"] = str(data_to_format) # Fallback for unserializable data
        response_envelope["formatting_error"] = str(e)
        return json.dumps(response_envelope, indent=2, ensure_ascii=False)

def format_as_plain_text_with_header(text_response: str, request_data: Dict[str, Any], agent_config: Dict[str, Any]) -> str:
    """
    Formats a plain text response by adding a simple header.
    """
    session_id = request_data.get("session_id", "N/A")
    header = f"--- Response from {agent_config.get("agent_name", "Agent")} (Session: {session_id}) ---"
    formatted_text = f"{header}\n{text_response}\n---------------------------------------"
    print(f"[FORMATTER] MainAgent - Session: {session_id} - Formatted response as plain text with header.")
    return formatted_text

# Dictionary to map formatter names to functions
RESPONSE_FORMATTERS = {
    "json_envelope": format_as_json_response,
    "plain_text_header": format_as_plain_text_with_header
}

if __name__ == "__main__":
    print("Testing response formatters...")
    mock_request = {
        "session_id": "formatter_test_session",
        "user_input": "Test input"
    }
    mock_config = {"agent_name": "FormattingTestAgent"}

    # Test JSON formatting
    data_for_json = {"answer": "The capital is Paris.", "confidence": 0.95, "sources": ["doc1.pdf"]}
    print(f"\nFormatting data for JSON: {data_for_json}")
    json_output = format_as_json_response(data_for_json, mock_request, mock_config)
    print(f"JSON Formatted Output:\n{json_output}")

    unserializable_data = {"answer": "Data with a set", "unserializable": {1, 2, 3}}
    print(f"\nFormatting unserializable data for JSON: {unserializable_data}")
    json_output_error = format_as_json_response(unserializable_data, mock_request, mock_config)
    print(f"JSON Formatted Output (with error handling):\n{json_output_error}")

    # Test plain text formatting
    data_for_text = "This is a simple text answer from the agent."
    print(f"\nFormatting data for Plain Text: {data_for_text}")
    text_output = format_as_plain_text_with_header(data_for_text, mock_request, mock_config)
    print(f"Plain Text Formatted Output:\n{text_output}")

