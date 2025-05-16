"""
Agent Logic for Sub-agent 2 (Example: Information Retrieval Sub-agent)

This sub-agent specializes in retrieving specific information, possibly from 
predefined sources or by querying external APIs (mocked here).
"""
import os
import yaml
import json
from jinja2 import Environment, FileSystemLoader
from typing import Union, Dict, Any

class SubAgent2:
    def __init__(self, agent_id: str = "sub_agent_2"):
        self.agent_id = agent_id
        self.base_path = f"src/agents/sub_agents/{self.agent_id}"
        
        print(f"Initializing {self.agent_id}...")
        self.config = self._load_yaml_config(f"{self.base_path}/config.yaml")
        self.model_config = self._load_yaml_config(f"{self.base_path}/model/config.yaml")
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

    def _call_retrieval_logic(self, task_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Placeholder for this sub-agent's core information retrieval logic.
        For this example, it performs a mock retrieval based on keywords.
        """
        print(f"\n--- {self.agent_id} ({self.config.get("agent_name")}) - Core Logic (Mock) ---")
        query = task_input.get("information_query", "general information")
        target_source = task_input.get("target_source", "internal_db") # e.g., "api_news", "internal_docs"

        mock_retrieval_result = {
            "query_processed": query,
            "source_queried": target_source,
            "retrieved_items": [],
            "summary": "No information found for the query.",
            "confidence": 0.3 # Default low confidence
        }

        # Simulate retrieval
        if "product specifications" in query.lower() and target_source == "internal_db":
            mock_retrieval_result["retrieved_items"].append({"doc_id": "SPEC-001", "title": "Product X Specs", "content_snippet": "Dimension: 10x5x2cm, Weight: 150g..."})
            mock_retrieval_result["summary"] = "Retrieved product specifications for Product X."
            mock_retrieval_result["confidence"] = 0.9
        elif "latest news" in query.lower() and target_source == "api_news":
            mock_retrieval_result["retrieved_items"].append({"article_id": "NEWS-123", "headline": "AI Breakthrough Announced", "source_url": "http://example.com/news/ai-breakthrough"})
            mock_retrieval_result["summary"] = "Fetched latest AI news headline."
            mock_retrieval_result["confidence"] = 0.8
        else:
            mock_retrieval_result["summary"] = f"Could not find specific information for '{query}' from source '{target_source}'."

        print(f"Mock retrieval result: {mock_retrieval_result["summary"]}")
        print(f"--- End {self.agent_id} Core Logic ---")
        return mock_retrieval_result

    def run(self, task_input: dict) -> dict:
        """
        Main execution method for the sub-agent.
        Args:
            task_input: Dict conforming to input_schema.yaml.
                        Example: {"information_query": "latest news on AI", "target_source": "api_news"}
        Returns:
            A dictionary containing the sub-agent's result.
        """
        print(f"\n--- {self.agent_id} ({self.config.get("agent_name")}) Run --- \nTask Input: {task_input}")

        if not all(key in task_input for key in self.input_schema.get("required", [])):
            error_msg = f"{self.agent_id} Error: Missing required input fields. Expected: {self.input_schema.get("required")}"
            print(error_msg)
            return {"error": error_msg, "status": "input_validation_failed"}
        
        result_payload = self._call_retrieval_logic(task_input)

        final_output = {
            "sub_agent_id": self.agent_id,
            "status": "success" if result_payload.get("confidence", 0) > 0.5 else "partial_success",
            "result": result_payload
        }
        
        print(f"Final Output from {self.agent_id}: {final_output}")
        print(f"--- End {self.agent_id} Run ---")
        return final_output

if __name__ == "__main__":
    print(f"Testing {SubAgent2().agent_id} directly...")
    sub_agent_instance = SubAgent2()

    test_input_specs = {
        "information_query": "Get product specifications for X123",
        "target_source": "internal_db"
    }
    response_specs = sub_agent_instance.run(test_input_specs)
    print(f"\nResponse from Product Specs Test:\n{json.dumps(response_specs, indent=2)}")

    test_input_news = {
        "information_query": "What is the latest news on renewable energy?",
        "target_source": "api_news"
    }
    response_news = sub_agent_instance.run(test_input_news)
    print(f"\nResponse from News API Test:\n{json.dumps(response_news, indent=2)}")

    test_input_fail = {
        "information_query": "Obscure information request",
        "target_source": "unknown_source"
    }
    response_fail = sub_agent_instance.run(test_input_fail)
    print(f"\nResponse from Failed Retrieval Test:\n{json.dumps(response_fail, indent=2)}")

