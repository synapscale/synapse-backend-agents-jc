"""
Agent Logic for Sub-agent 4 (Example: Content Generation Sub-agent)

This sub-agent specializes in generating creative content, such as text snippets,
summaries, or even (mocked) image descriptions, based on a given topic or input.
"""
import os
import yaml
import json
from jinja2 import Environment, FileSystemLoader
from typing import Union, Dict, Any

class SubAgent4:
    def __init__(self, agent_id: str = "sub_agent_4"):
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
        # Initialize LLM client if this sub-agent uses one directly
        # if self.model_config.get("provider") == "openai":
        #     self.llm_client = OpenAI(api_key=os.getenv(self.model_config.get("api_key_env_var", "OPENAI_API_KEY")))
        #     print(f"{self.agent_id} LLM configured with model: {os.getenv(self.model_config.get("model_name_env_var"))}")
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

    def _call_content_generation_logic(self, task_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Placeholder for this sub-agent's core content generation logic.
        For this example, it simulates generating text based on topic and type.
        """
        print(f"\n--- {self.agent_id} ({self.config.get("agent_name")}) - Core Logic (Mock) ---")
        content_topic = task_input.get("topic", "general AI")
        content_type = task_input.get("content_type", "short_summary") # e.g., "blog_post_idea", "tweet", "product_description"
        target_length = task_input.get("target_length_words", 50)

        mock_generation_result = {
            "topic_processed": content_topic,
            "type_generated": content_type,
            "generated_content": "",
            "status": "failed",
            "message": "Content generation failed or type not supported."
        }

        # Simulate generation
        if content_type == "short_summary":
            mock_generation_result["generated_content"] = f"Este é um breve resumo sobre {content_topic}. Ele aborda os pontos principais de forma concisa, ideal para uma visão geral em aproximadamente {target_length} palavras."
            mock_generation_result["status"] = "success"
            mock_generation_result["message"] = "Short summary generated successfully."
        elif content_type == "tweet":
            mock_generation_result["generated_content"] = f"Confira as últimas novidades sobre {content_topic}! #Hashtag{content_topic.replace(' ','')} #AI #Tech. Saiba mais em nosso site! (Mock tweet, {target_length} palavras aprox.)"
            mock_generation_result["status"] = "success"
            mock_generation_result["message"] = "Tweet generated successfully."
        elif content_type == "product_description_hook":
            mock_generation_result["generated_content"] = f"Cansado de {content_topic}? Descubra nossa nova solução inovadora que revolucionará sua experiência! (Gancho de descrição do produto, {target_length} palavras)."
            mock_generation_result["status"] = "success"
            mock_generation_result["message"] = "Product description hook generated successfully."
        else:
            mock_generation_result["message"] = f"Content type '{content_type}' not supported by this mock generator."

        # Ensure generated content roughly respects length (very naively for mock)
        if mock_generation_result["status"] == "success":
            words = mock_generation_result["generated_content"].split()
            if len(words) > target_length * 1.5: # Allow some leeway
                mock_generation_result["generated_content"] = " ".join(words[:int(target_length*1.2)]) + "... (truncated for length)"

        print(f"Mock generation result: {mock_generation_result["message"]}")
        print(f"--- End {self.agent_id} Core Logic ---")
        return mock_generation_result

    def run(self, task_input: dict) -> dict:
        """
        Main execution method for the sub-agent.
        Args:
            task_input: Dict conforming to input_schema.yaml.
                        Example: {"topic": "renewable energy", "content_type": "tweet", "target_length_words": 25}
        Returns:
            A dictionary containing the sub-agent's result.
        """
        print(f"\n--- {self.agent_id} ({self.config.get("agent_name")}) Run --- \nTask Input: {task_input}")

        if not all(key in task_input for key in self.input_schema.get("required", [])):
            error_msg = f"{self.agent_id} Error: Missing required input fields. Expected: {self.input_schema.get("required")}"
            print(error_msg)
            return {"error": error_msg, "status": "input_validation_failed"}
        
        result_payload = self._call_content_generation_logic(task_input)

        final_output = {
            "sub_agent_id": self.agent_id,
            "status": result_payload.get("status", "failed"),
            "result": result_payload
        }
        
        print(f"Final Output from {self.agent_id}: {final_output}")
        print(f"--- End {self.agent_id} Run ---")
        return final_output

if __name__ == "__main__":
    print(f"Testing {SubAgent4().agent_id} directly...")
    sub_agent_instance = SubAgent4()

    test_input_summary = {
        "topic": "Quantum Computing",
        "content_type": "short_summary",
        "target_length_words": 30
    }
    response_summary = sub_agent_instance.run(test_input_summary)
    print(f"\nResponse from Short Summary Test:\n{json.dumps(response_summary, indent=2)}")

    test_input_tweet = {
        "topic": "sustainable fashion",
        "content_type": "tweet",
        "target_length_words": 20
    }
    response_tweet = sub_agent_instance.run(test_input_tweet)
    print(f"\nResponse from Tweet Generation Test:\n{json.dumps(response_tweet, indent=2)}")

    test_input_unsupported = {
        "topic": "ancient history",
        "content_type": "research_paper_abstract"
    }
    response_unsupported = sub_agent_instance.run(test_input_unsupported)
    print(f"\nResponse from Unsupported Type Test:\n{json.dumps(response_unsupported, indent=2)}")

