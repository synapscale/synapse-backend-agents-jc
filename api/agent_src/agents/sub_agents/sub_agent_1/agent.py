"""
Agent Logic for Sub-agent 1 (Example: Data Analysis Sub-agent)

This sub-agent is specialized in performing some form of data analysis based on input.
It demonstrates how a sub-agent can have its own configuration, prompt, and logic.
"""
import os
import yaml
import json
from jinja2 import Environment, FileSystemLoader

# Assuming access to a shared logger or its own logger setup
# from ....outputs.logger import get_logger # Adjust relative path if needed
# logger = get_logger("SubAgent_1_DataAnalyzer")

# Placeholder for actual LLM interaction if this sub-agent uses one
# from openai import OpenAI

class SubAgent1:
    def __init__(self, agent_id: str = "sub_agent_1"):
        self.agent_id = agent_id
        self.base_path = f"src/agents/sub_agents/{self.agent_id}"
        
        print(f"Initializing {self.agent_id}...")
        self.config = self._load_yaml_config(f"{self.base_path}/config.yaml")
        self.model_config = self._load_yaml_config(f"{self.base_path}/model/config.yaml")
        self.input_schema = self._load_yaml_config(f"{self.base_path}/inputs/schema.yaml")
        # self.tools_config = self._load_yaml_config(f"{self.base_path}/tools/tools.yaml") # If sub-agent has its own tools

        self.jinja_env = Environment(
            loader=FileSystemLoader(f"{self.base_path}/inputs/"),
            autoescape=False
        )

        # Initialize LLM client if this sub-agent uses one directly
        # if self.model_config.get("provider") == "openai":
        #     self.llm_client = OpenAI(api_key=os.getenv(self.model_config.get("api_key_env_var", "OPENAI_API_KEY")))
        #     print(f"{self.agent_id} LLM configured with model: {os.getenv(self.model_config.get("model_name_env_var"))}")
        print(f"{self.agent_id} (Data Analyzer) initialized with name: {self.config.get("agent_name")}")

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

    def _render_prompt(self, template_name: str, context: dict) -> str:
        template = self.jinja_env.get_template(template_name)
        return template.render(context)

    def _call_llm_or_logic(self, prompt_or_input: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Placeholder for this sub-agent's core logic.
        It might call an LLM, run a Python script for analysis, or use a specific library.
        For this example, it will perform a mock analysis.
        """
        print(f"\n--- {self.agent_id} ({self.config.get("agent_name")}) - Core Logic (Mock) ---")
        
        # If it were LLM-based:
        # print(f"Prompt/Input: {str(prompt_or_input)[:200]}...")
        # response = self.llm_client.chat.completions.create(...)
        # llm_result_text = response.choices[0].message.content
        # For now, simulate analysis based on input_data
        
        input_data = prompt_or_input if isinstance(prompt_or_input, dict) else {"raw_text_prompt": prompt_or_input}
        analysis_type = input_data.get("analysis_type", "general_summary")
        data_to_analyze = input_data.get("data_payload", "No data provided for analysis.")

        mock_analysis_result = {
            "analysis_type_performed": analysis_type,
            "input_data_summary": f"Analyzed data starting with: {str(data_to_analyze)[:50]}...",
            "findings": [],
            "confidence": 0.85 # Mock confidence
        }

        if analysis_type == "sentiment_analysis":
            # Simulate sentiment analysis
            if "positive" in str(data_to_analyze).lower():
                mock_analysis_result["findings"].append({"sentiment": "positive", "score": 0.9})
            elif "negative" in str(data_to_analyze).lower():
                mock_analysis_result["findings"].append({"sentiment": "negative", "score": 0.8})
            else:
                mock_analysis_result["findings"].append({"sentiment": "neutral", "score": 0.7})
            mock_analysis_result["summary"] = f"Sentiment analysis complete. Overall sentiment appears to be {mock_analysis_result['findings'][0]['sentiment']}."
        elif analysis_type == "keyword_extraction":
            # Simulate keyword extraction
            keywords = [word for word in str(data_to_analyze).lower().split() if len(word) > 4 and word.isalpha()]
            mock_analysis_result["findings"].append({"keywords_found": list(set(keywords))[:5]})
            mock_analysis_result["summary"] = f"Keyword extraction complete. Found {len(mock_analysis_result['findings'][0]['keywords_found'])} keywords."
        else:
            mock_analysis_result["summary"] = f"General mock analysis performed on the provided data for type '{analysis_type}'."
            mock_analysis_result["findings"].append("No specific findings for this general mock analysis.")

        print(f"Mock analysis result: {mock_analysis_result["summary"]}")
        print(f"--- End {self.agent_id} Core Logic ---")
        return mock_analysis_result

    def run(self, task_input: dict) -> dict:
        """
        Main execution method for the sub-agent.

        Args:
            task_input: A dictionary containing the input for this sub-agent,
                        expected to conform to its input_schema.yaml.
                        Example from MainAgent: {"query": "Analyze this data...", "data_payload": {...}, "analysis_type": "..."}
        
        Returns:
            A dictionary containing the sub-agent's result.
        """
        print(f"\n--- {self.agent_id} ({self.config.get("agent_name")}) Run --- \nTask Input: {task_input}")

        # 1. Validate input against schema (basic check here, use jsonschema for full validation)
        if not all(key in task_input for key in self.input_schema.get("required", [])):
            error_msg = f"{self.agent_id} Error: Missing required input fields. Expected: {self.input_schema.get("required")}"
            print(error_msg)
            return {"error": error_msg, "status": "input_validation_failed"}
        
        # 2. Prepare context for prompt or direct logic
        # For this example, we pass task_input directly to the mock logic
        # If using an LLM, you would render a prompt:
        # prompt_context = {
        #     "sub_agent_name": self.config.get("agent_name"),
        #     "sub_agent_task_description": self.config.get("description"),
        #     "specific_input_for_sub_agent_1": task_input.get("query"), # Map from task_input
        #     "data_to_process": task_input.get("data_payload")
        # }
        # current_prompt = self._render_prompt("prompt_template.j2", prompt_context)
        # result_payload = self._call_llm_or_logic(current_prompt)
        
        result_payload = self._call_llm_or_logic(task_input) # Pass the whole task_input for mock logic

        # 3. Format final output (could use an output schema)
        final_output = {
            "sub_agent_id": self.agent_id,
            "status": "success",
            "result": result_payload
        }
        
        print(f"Final Output from {self.agent_id}: {final_output}")
        print(f"--- End {self.agent_id} Run ---")
        return final_output

if __name__ == "__main__":
    # This allows testing the sub-agent directly.
    # Ensure necessary environment variables are set if sub-agent uses LLM/external services.
    print(f"Testing {SubAgent1().agent_id} directly...")
    sub_agent_instance = SubAgent1()

    # Example 1: Sentiment Analysis
    test_input_sentiment = {
        "query": "Perform sentiment analysis on the provided customer feedback.",
        "data_payload": "The product is amazing and the customer service was excellent! Very positive experience.",
        "analysis_type": "sentiment_analysis" # This matches a key in input_schema.yaml
    }
    response_sentiment = sub_agent_instance.run(test_input_sentiment)
    print(f"\nResponse from Sentiment Analysis Test:\n{json.dumps(response_sentiment, indent=2)}")

    # Example 2: Keyword Extraction
    test_input_keywords = {
        "query": "Extract keywords from this document abstract.",
        "data_payload": "This research paper discusses advanced techniques in machine learning, neural networks, and artificial intelligence for natural language processing.",
        "analysis_type": "keyword_extraction"
    }
    response_keywords = sub_agent_instance.run(test_input_keywords)
    print(f"\nResponse from Keyword Extraction Test:\n{json.dumps(response_keywords, indent=2)}")

    # Example 3: Missing required input
    test_input_missing = {
        "query": "Analyze this."
        # Missing 'data_payload' and 'analysis_type' which might be required by schema.yaml
    }
    response_missing = sub_agent_instance.run(test_input_missing)
    print(f"\nResponse from Missing Input Test:\n{json.dumps(response_missing, indent=2)}")

