"""
Response Senders for the Main Agent

This module contains functions or classes responsible for sending the agent's
final, formatted response to its destination (e.g., back to an HTTP client,
writing to a message queue, printing to console).

This layer is kept separate to allow flexibility in how the agent communicates
its results without embedding sending logic directly into the core agent.py.
"""
from typing import Dict, Any, Union

def send_to_console(formatted_response: Union[str, Dict[str, Any]], request_data: Dict[str, Any], agent_config: Dict[str, Any]) -> None:
    """
    Sends the formatted response to the console.
    Useful for CLI applications or debugging.
    """
    session_id = request_data.get("session_id", "N/A")
    print(f"\n[SENDER] MainAgent - Session: {session_id} - Sending response to CONSOLE:")
    if isinstance(formatted_response, dict):
        import json
        print(json.dumps(formatted_response, indent=2, ensure_ascii=False))
    else:
        print(formatted_response)
    print("--- End of Console Output ---")

def send_to_http_client(formatted_response: Union[str, Dict[str, Any]], http_response_object: Any, agent_config: Dict[str, Any]) -> None:
    """
    Placeholder for sending the response back via an HTTP client response object.
    The `http_response_object` would be specific to the web framework (e.g., FastAPI Response, Flask Response).
    
    Args:
        formatted_response: The agent's final response (string or dict).
        http_response_object: The response object from the web framework.
        agent_config: Agent configuration.
    """
    # This is highly dependent on the web framework being used.
    # Example for FastAPI (conceptual):
    # if isinstance(http_response_object, fastapi.Response):
    #     if isinstance(formatted_response, dict):
    #         http_response_object.media_type = "application/json"
    #         http_response_object.body = json.dumps(formatted_response).encode("utf-8")
    #     else:
    #         http_response_object.media_type = "text/plain"
    #         http_response_object.body = str(formatted_response).encode("utf-8")
    #     http_response_object.status_code = 200
    #     print(f"[SENDER] MainAgent - Sent response via HTTP (FastAPI conceptual)")
    # else:
    #     print(f"[SENDER] MainAgent - ERROR: http_response_object not a recognized type for sending.")
    print(f"[SENDER] MainAgent - SIMULATING: Sending response via HTTP. Response: {str(formatted_response)[:100]}...")
    # In a real scenario, you would modify the http_response_object here.
    pass

# Dictionary to map sender names to functions
RESPONSE_SENDERS = {
    "console": send_to_console,
    "http": send_to_http_client # This would need the http_response_object passed in kwargs
}

if __name__ == "__main__":
    print("Testing response senders...")
    mock_request = {
        "session_id": "sender_test_session",
        "user_input": "Test input for sender"
    }
    mock_config = {"agent_name": "SenderTestAgent"}

    # Test sending to console
    response_data_dict = {"message": "Hello from agent!", "status": "ok"}
    print(f"\nTesting send_to_console with dict: {response_data_dict}")
    send_to_console(response_data_dict, mock_request, mock_config)

    response_data_str = "This is a plain text response for the console."
    print(f"\nTesting send_to_console with str: {response_data_str}")
    send_to_console(response_data_str, mock_request, mock_config)

    # Test sending to HTTP (simulated)
    # In a real app, the http_response_object would come from your web framework (e.g., FastAPI, Flask)
    class MockHttpResponse:
        def __init__(self):
            self.body = None
            self.status_code = None
            self.media_type = None
        def __str__(self):
            return f"MockHttpResponse(status={self.status_code}, media_type='{self.media_type}', body='{str(self.body)[:50]}...')"

    mock_http_resp_obj = MockHttpResponse()
    print(f"\nTesting send_to_http_client (simulated) with dict: {response_data_dict}")
    send_to_http_client(response_data_dict, mock_http_resp_obj, mock_config)
    print(f"State of mock_http_resp_obj after send (conceptual): {mock_http_resp_obj}")

    mock_http_resp_obj_str = MockHttpResponse()
    print(f"\nTesting send_to_http_client (simulated) with str: {response_data_str}")
    send_to_http_client(response_data_str, mock_http_resp_obj_str, mock_config)
    print(f"State of mock_http_resp_obj_str after send (conceptual): {mock_http_resp_obj_str}")

