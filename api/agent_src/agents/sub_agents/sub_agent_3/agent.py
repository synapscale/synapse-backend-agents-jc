"""
Agent Logic for Sub-agent 3 (Example: Task Execution Sub-agent)

This sub-agent specializes in executing specific tasks, such as calling an external API 
(mocked here) or performing a defined computation.
"""
import os
import yaml
import json
import time # For simulating API call latency
from jinja2 import Environment, FileSystemLoader
from typing import Union, Dict, Any

class SubAgent3:
    def __init__(self, agent_id: str = "sub_agent_3"):
        self.agent_id = agent_id
        self.base_path = f"src/agents/sub_agents/{self.agent_id}"
        
        print(f"Initializing {self.agent_id}...")
        self.config = self._load_yaml_config(f"{self.base_path}/config.yaml")
        self.model_config = self._load_yaml_config(f"{self.base_path}/model/config.yaml") # If it uses an LLM
        self.input_schema = self._load_yaml_config(f"{self.base_path}/inputs/schema.yaml")

        self.jinja_env = Environment(
            loader=FileSystemLoader(f"{self.base_path}/inputs/"),
            autoescape=False
        )
        print(f"{self.agent_id} ({self.config.get("agent_name")}) initialized.")

    def _load_yaml_config(self, path: str) -> dict:
        try:
            with open(path, "r") as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            print(f"Warning: {self.agent_id} - Config file not found at {path}")
            return {}
        except yaml.YAMLError as e:
            print(f"Error: {self.agent_id} - Parsing YAML file at {path}: {e}")
            return {}

    def _execute_task_logic(self, task_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Placeholder for this sub-agent's core task execution logic.
        For this example, it simulates calling an external API or performing a computation.
        """
        print(f"\n--- {self.agent_id} ({self.config.get("agent_name")}) - Core Logic (Mock) ---")
        action_to_perform = task_input.get("action_name", "default_computation")
        action_params = task_input.get("action_parameters", {})

        mock_execution_result = {
            "action_performed": action_to_perform,
            "parameters_used": action_params,
            "status_code": 500, # Default to error
            "result_payload": None,
            "message": "Action not recognized or failed."
        }

        print(f"Simulating execution of action: {action_to_perform} with params: {action_params}")
        time.sleep(0.5) # Simulate some processing time

        if action_to_perform == "submit_order":
            order_id = action_params.get("order_id")
            if order_id:
                mock_execution_result["status_code"] = 200
                mock_execution_result["result_payload"] = {"confirmation_id": f"CONF-{order_id}-XYZ", "status": "Order Submitted"}
                mock_execution_result["message"] = f"Order {order_id} submitted successfully."
            else:
                mock_execution_result["message"] = "Missing order_id for submit_order action."
                mock_execution_result["status_code"] = 400
        elif action_to_perform == "calculate_metrics":
            data_points = action_params.get("data", [])
            if isinstance(data_points, list) and all(isinstance(x, (int, float)) for x in data_points) and data_points:
                mean_val = sum(data_points) / len(data_points)
                sum_val = sum(data_points)
                mock_execution_result["status_code"] = 200
                mock_execution_result["result_payload"] = {"mean": mean_val, "sum": sum_val, "count": len(data_points)}
                mock_execution_result["message"] = "Metrics calculated successfully."
            else:
                mock_execution_result["message"] = "Invalid or empty data points for calculate_metrics action."
                mock_execution_result["status_code"] = 400
        else:
            mock_execution_result["message"] = f"Action '{action_to_perform}' is not implemented in this mock."

        print(f"Mock execution result: {mock_execution_result["message"]}")
        print(f"--- End {self.agent_id} Core Logic ---")
        return mock_execution_result

    def run(self, task_input: dict) -> dict:
        """
        Main execution method for the sub-agent.
        Args:
            task_input: Dict conforming to input_schema.yaml.
                        Example: {"action_name": "submit_order", "action_parameters": {"order_id": "12345"}}
        Returns:
            A dictionary containing the sub-agent's result.
        """
        print(f"\n--- {self.agent_id} ({self.config.get("agent_name")}) Run --- \nTask Input: {task_input}")

        if not all(key in task_input for key in self.input_schema.get("required", [])):
            error_msg = f"{self.agent_id} Error: Missing required input fields. Expected: {self.input_schema.get("required")}"
            print(error_msg)
            return {"error": error_msg, "status": "input_validation_failed"}
        
        result_payload = self._execute_task_logic(task_input)

        final_output = {
            "sub_agent_id": self.agent_id,
            "status": "success" if result_payload.get("status_code") == 200 else "failed",
            "result": result_payload
        }
        
        print(f"Final Output from {self.agent_id}: {final_output}")
        print(f"--- End {self.agent_id} Run ---")
        return final_output

if __name__ == "__main__":
    print(f"Testing {SubAgent3().agent_id} directly...")
    sub_agent_instance = SubAgent3()

    test_input_order = {
        "action_name": "submit_order",
        "action_parameters": {"order_id": "ORD789", "items": [{"sku": "ABC", "qty": 1}]}
    }
    response_order = sub_agent_instance.run(test_input_order)
    print(f"\nResponse from Submit Order Test:\n{json.dumps(response_order, indent=2)}")

    test_input_metrics = {
        "action_name": "calculate_metrics",
        "action_parameters": {"data": [10, 20, 30, 25, 15]}
    }
    response_metrics = sub_agent_instance.run(test_input_metrics)
    print(f"\nResponse from Calculate Metrics Test:\n{json.dumps(response_metrics, indent=2)}")

    test_input_unknown_action = {
        "action_name": "unknown_operation",
        "action_parameters": {}
    }
    response_unknown = sub_agent_instance.run(test_input_unknown_action)
    print(f"\nResponse from Unknown Action Test:\n{json.dumps(response_unknown, indent=2)}")

