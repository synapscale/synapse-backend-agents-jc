"""
Main Agent Orchestrator Logic

This is the core orchestrator for the Vertical Agent. It receives input,
manages the conversation flow, delegates tasks to sub-agents, interacts with
the LLM, and formats the final output.
"""
import os
import yaml
import json
import uuid
from jinja2 import Environment, FileSystemLoader
from typing import Dict, Any, Optional, List, Union

# Assuming PROJECT_ROOT is correctly set by the entrypoint or test runner
# For direct execution or debugging, you might need to adjust path logic.
# from ..config.load_config import get_env_variable # If you have a centralized config loader
from my_vertical_agent.src.agents.main_agent.memory.redis_memory import RedisChatMemory
from my_vertical_agent.src.agents.main_agent.data_connectors.embeddings_openai import OpenAIEmbeddings
from my_vertical_agent.src.agents.main_agent.data_connectors.supabase_vector import SupabaseVectorStore
from my_vertical_agent.src.agents.main_agent.outputs.logger import get_logger # Using the new logger
from my_vertical_agent.src.agents.main_agent.callbacks import pre_request, post_response, on_error
from my_vertical_agent.src.agents.main_agent.parsers import parse_response as response_parser_module
from my_vertical_agent.src.agents.main_agent.outputs import formatter as output_formatter_module
from my_vertical_agent.src.agents.main_agent.outputs import sender as output_sender_module

# Import sub-agent classes
from my_vertical_agent.src.agents.sub_agents.sub_agent_1.agent import SubAgent1
from my_vertical_agent.src.agents.sub_agents.sub_agent_2.agent import SubAgent2
from my_vertical_agent.src.agents.sub_agents.sub_agent_3.agent import SubAgent3
from my_vertical_agent.src.agents.sub_agents.sub_agent_4.agent import SubAgent4
from my_vertical_agent.src.agents.sub_agents.sub_agent_5.agent import SubAgent5

# Attempt to load LLM client (e.g., OpenAI)
IS_OPENAI_AVAILABLE = False
try:
    from openai import OpenAI
    IS_OPENAI_AVAILABLE = True
except ImportError:
    # print("OpenAI library not found. LLM functionalities will be limited.")
    pass

class MainAgent:
    def __init__(self, config_path: Optional[str] = None):
        self.agent_name = "MainVerticalAgent"
        self.logger = get_logger(self.agent_name) # Initialize logger for this agent
        self.logger.info(f"Initializing {self.agent_name}...")

        self.base_path = "src/agents/main_agent"
        default_config_file = os.path.join(self.base_path, "config.yaml")
        self.config = self._load_yaml_config(config_path or default_config_file)
        
        self.model_config = self._load_yaml_config(os.path.join(self.base_path, self.config.get("model_config_path", "model/config.yaml")))
        self.memory_config = self._load_yaml_config(os.path.join(self.base_path, self.config.get("memory_config_path", "memory/config.yaml")))
        self.input_schema_config = self._load_yaml_config(os.path.join(self.base_path, self.config.get("input_schema_path", "inputs/schema.yaml")))
        self.output_schema_config = self._load_json_config(os.path.join(self.base_path, self.config.get("output_schema_path", "schemas/output.json")))
        self.tools_config = self._load_yaml_config(os.path.join(self.base_path, self.config.get("tools_config_path", "tools/tools.yaml")))
        self.rag_config = self._load_yaml_config(os.path.join(self.base_path, self.config.get("rag_config_path", "data_connectors/rag_config.yaml")))

        self.jinja_env = Environment(
            loader=FileSystemLoader(os.path.join(self.base_path, "inputs/")),
            autoescape=False # Depending on your template needs
        )

        self.llm_client = None
        if IS_OPENAI_AVAILABLE and self.model_config.get("provider") == "openai":
            try:
                self.llm_client = OpenAI(api_key=os.getenv(self.model_config.get("api_key_env_var", "OPENAI_API_KEY")))
                self.logger.info(f"OpenAI LLM client initialized for model: {os.getenv(self.model_config.get("model_name_env_var"))}")
            except Exception as e:
                self.logger.error(f"Failed to initialize OpenAI client: {e}", exc_info=True)
                self.llm_client = None # Ensure it's None if init fails
        
        self.embedding_generator = None
        self.vector_store = None
        if self.rag_config.get("enabled", False):
            try:
                self.embedding_generator = OpenAIEmbeddings(
                    api_key_env_var=self.rag_config.get("embeddings", {}).get("api_key_env_var", "OPENAI_API_KEY"),
                    model_name_env_var=self.rag_config.get("embeddings", {}).get("model_name_env_var", "OPENAI_EMBEDDING_MODEL_NAME")
                )
                self.vector_store = SupabaseVectorStore(
                    embedding_generator=self.embedding_generator,
                    # Configs below can be overridden by env vars specified in SupabaseVectorStore class
                    table_name=self.rag_config.get("vector_store", {}).get("table_name_env_var"), 
                    content_column=self.rag_config.get("vector_store", {}).get("content_column", "content"),
                    embedding_column=self.rag_config.get("vector_store", {}).get("embedding_column", "embedding"),
                    metadata_column=self.rag_config.get("vector_store", {}).get("metadata_column", "metadata"),
                    rpc_match_function=self.rag_config.get("vector_store", {}).get("rpc_match_function", "match_documents")
                )
                self.logger.info("RAG system (Embeddings & Vector Store) initialized.")
            except Exception as e:
                self.logger.error(f"Failed to initialize RAG components: {e}", exc_info=True)
                self.embedding_generator = None
                self.vector_store = None

        # Initialize Sub-agents
        self.sub_agents = {}
        if self.config.get("enable_sub_agents", True): # Assuming a global toggle
            self.sub_agents["sub_agent_1"] = SubAgent1()
            self.sub_agents["sub_agent_2"] = SubAgent2()
            self.sub_agents["sub_agent_3"] = SubAgent3()
            self.sub_agents["sub_agent_4"] = SubAgent4()
            self.sub_agents["sub_agent_5"] = SubAgent5()
            self.logger.info(f"Initialized {len(self.sub_agents)} sub-agents.")

        self.logger.info(f"{self.agent_name} initialization complete.")

    def _load_yaml_config(self, path: str) -> dict:
        try:
            with open(path, "r") as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            self.logger.warning(f"Config file not found at {path}")
            return {}
        except yaml.YAMLError as e:
            self.logger.error(f"Error parsing YAML file at {path}: {e}", exc_info=True)
            return {}

    def _load_json_config(self, path: str) -> dict:
        try:
            with open(path, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            self.logger.warning(f"Config file not found at {path}")
            return {}
        except json.JSONDecodeError as e:
            self.logger.error(f"Error parsing JSON file at {path}: {e}", exc_info=True)
            return {}

    def _get_chat_memory(self, session_id: str) -> RedisChatMemory:
        return RedisChatMemory(
            session_id=session_id,
            host=os.getenv(self.memory_config.get("host_env_var", "REDIS_HOST")),
            port=int(os.getenv(self.memory_config.get("port_env_var", "REDIS_PORT"), "6379")),
            db=int(os.getenv(self.memory_config.get("db_env_var", "REDIS_DB_CHAT_HISTORY"), "0")),
            password=os.getenv(self.memory_config.get("password_env_var", "REDIS_PASSWORD"), None),
            ttl_seconds=self.memory_config.get("ttl_seconds", 3600)
        )

    def _render_prompt_template(self, template_name: str, context: dict) -> str:
        try:
            template = self.jinja_env.get_template(template_name)
            return template.render(context)
        except Exception as e:
            self.logger.error(f"Error rendering prompt template {template_name}: {e}", exc_info=True)
            return f"Error rendering prompt: {context.get("user_input", "")}" # Fallback

    def _call_llm(self, prompt: str, chat_history: List[Dict[str, str]]) -> Optional[str]:
        if not self.llm_client:
            self.logger.warning("LLM client not available. Cannot call LLM.")
            return "LLM indisponível no momento."
        
        model_name = os.getenv(self.model_config.get("model_name_env_var", "gpt-3.5-turbo"))
        max_tokens = self.model_config.get("max_tokens", 1024)
        temperature = self.model_config.get("temperature", 0.7)
        
        messages = chat_history + [{"role": "user", "content": prompt}]
        self.logger.debug(f"Sending to LLM ({model_name}): {messages}")
        try:
            response = self.llm_client.chat.completions.create(
                model=model_name,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            llm_response_text = response.choices[0].message.content.strip()
            self.logger.info(f"Received from LLM: {llm_response_text[:100]}...")
            return llm_response_text
        except Exception as e:
            self.logger.error(f"Error calling LLM: {e}", exc_info=True)
            # Trigger error callback for LLM failure
            for callback in on_error.ERROR_HANDLING_CALLBACKS:
                callback(e, {"prompt": prompt, "history_len": len(chat_history)}, self.config, context_message="LLM Call Failed")
            return on_error.generate_fallback_response(e) # Return a fallback

    def _process_tool_or_sub_agent_call(self, llm_response_text: str, current_input_data: Dict[str, Any]) -> Optional[str]:
        """
        Parses LLM response for tool/sub-agent calls and executes them.
        This is a simplified version. Real tool use might involve structured output from LLM (e.g., OpenAI Functions).
        For now, we can use keywords or a simple DSL in the LLM response.
        Example: "[SUB_AGENT_CALL: sub_agent_1, INPUT: {"query": "Analyze this data..."}]"
        """
        # Simple keyword-based dispatcher for sub-agents (example)
        # A more robust solution would use LLM function calling or a structured DSL.
        sub_agent_call_prefix = "[SUB_AGENT_CALL:"
        if llm_response_text.startswith(sub_agent_call_prefix):
            self.logger.info(f"Detected potential sub-agent call: {llm_response_text}")
            try:
                # Extremely basic parsing, not robust for complex inputs
                call_details_str = llm_response_text[len(sub_agent_call_prefix):-1] # Remove prefix and trailing ]
                agent_name_part, input_part = call_details_str.split(", INPUT: ", 1)
                agent_name = agent_name_part.strip()
                sub_agent_input_str = input_part.strip()
                sub_agent_input = json.loads(sub_agent_input_str) # Expecting JSON string for input

                if agent_name in self.sub_agents:
                    self.logger.info(f"Calling Sub-agent: {agent_name} with input: {sub_agent_input}")
                    sub_agent_instance = self.sub_agents[agent_name]
                    # Pass relevant parts of current_input_data if needed, or construct fresh input
                    # For now, assume sub_agent_input is self-contained as per the DSL
                    sub_agent_result = sub_agent_instance.run(sub_agent_input)
                    self.logger.info(f"Result from {agent_name}: {str(sub_agent_result)[:200]}...")
                    # We might want to feed this result back to the LLM or use it directly
                    # For this example, let's assume the sub-agent result is the final answer for this turn.
                    # A more complex flow would re-prompt the main LLM with this result.
                    return json.dumps(sub_agent_result) # Return the sub-agent's output as a string
                else:
                    self.logger.warning(f"LLM tried to call unknown sub-agent: {agent_name}")
                    return f"Erro: Sub-agente '{agent_name}' desconhecido."
            except Exception as e:
                self.logger.error(f"Error parsing or executing sub-agent call '{llm_response_text}': {e}", exc_info=True)
                return f"Erro ao processar chamada de sub-agente: {e}"
        return None # No sub-agent call detected or handled

    def run(self, input_data: Dict[str, Any]) -> Union[str, Dict[str, Any]]:
        """
        Main run method for the agent.
        Processes input, interacts with LLM/sub-agents, and returns a response.
        """
        final_response_data: Any = "Ocorreu um erro inesperado."
        request_start_time = self._get_timestamp()
        session_id = input_data.get("session_id", str(uuid.uuid4()))
        input_data["session_id"] = session_id # Ensure session_id is in input_data
        self.logger.info(f"Run started for session {session_id}. Input: {str(input_data)[:200]}...")

        try:
            # 1. Pre-request Callbacks
            for callback in pre_request.PRE_REQUEST_CALLBACKS:
                returned_data = callback(input_data, self.config)
                if returned_data is not None: input_data = returned_data

            # 2. Input Validation (basic, use jsonschema for full validation)
            if not input_data.get("user_input"): 
                raise ValueError("user_input is missing from input_data")

            # 3. Retrieve Chat History
            chat_memory = self._get_chat_memory(session_id)
            history = chat_memory.get_history(limit=self.memory_config.get("history_limit", 10))

            # 4. RAG: Retrieve relevant context if enabled
            rag_context_str = ""
            if self.vector_store and self.rag_config.get("enabled", False):
                try:
                    retrieved_docs = self.vector_store.similarity_search(
                        query_text=input_data["user_input"],
                        match_count=self.rag_config.get("vector_store", {}).get("match_count", 3),
                        similarity_threshold=self.rag_config.get("vector_store", {}).get("similarity_threshold", 0.75)
                    )
                    if retrieved_docs:
                        rag_context_str = "\n\nContexto Relevante da Base de Conhecimento:\n"
                        for i, doc in enumerate(retrieved_docs):
                            rag_context_str += f"{i+1}. {doc.get(self.vector_store.content_column, ')}\n"
                        self.logger.info(f"RAG: Retrieved {len(retrieved_docs)} documents for context.")
                except Exception as e:
                    self.logger.error(f"RAG: Error during similarity search: {e}", exc_info=True)
            
            # 5. Prepare Prompt Context & Render Prompt
            prompt_template_name = self.config.get("default_prompt_template", "prompt_template.j2")
            prompt_context = {
                "user_input": input_data["user_input"],
                "chat_history": history,
                "agent_name": self.agent_name,
                "agent_persona": self.config.get("persona", "um assistente de IA útil"),
                "current_date_time": request_start_time,
                "rag_context": rag_context_str,
                # Add other context variables from input_data or config as needed
                "user_profile": input_data.get("user_profile", {}),
                "task_description": self.config.get("task_description", "Responder à consulta do usuário.")
            }
            for callback in pre_request.PRE_PROMPT_RENDERING_CALLBACKS:
                 returned_ctx = callback(prompt_context, self.config)
                 if returned_ctx is not None: prompt_context = returned_ctx
            
            current_prompt = self._render_prompt_template(prompt_template_name, prompt_context)

            # 6. Call LLM
            llm_response_text = self._call_llm(current_prompt, history)
            if llm_response_text is None: # LLM call failed critically
                llm_response_text = "Desculpe, não consegui processar sua solicitação no momento."

            # 7. Process Potential Tool/Sub-agent call from LLM response
            # This is a simplified flow. A more robust agent might loop here, re-prompting LLM with tool results.
            sub_agent_output_str = self._process_tool_or_sub_agent_call(llm_response_text, input_data)
            if sub_agent_output_str:
                # If a sub-agent was called and returned something, use that as the primary response for now.
                # This could be a JSON string from the sub-agent.
                llm_response_text = sub_agent_output_str 
                # Potentially parse this if it's JSON and structure it
                try:
                    parsed_sub_agent_output = json.loads(sub_agent_output_str)
                    # If you want to use the sub-agent's text directly, you'd extract it here.
                    # For now, the formatter will handle the dict or string.
                    final_response_data = parsed_sub_agent_output 
                except json.JSONDecodeError:
                    final_response_data = llm_response_text # Keep as string if not valid JSON
            else:
                # No sub-agent call, or it didn't return a new primary response. Use original LLM response.
                final_response_data = llm_response_text

            # 8. Parse LLM Response (if not handled by sub-agent output)
            if not sub_agent_output_str: # Only parse if it was a direct LLM response
                if response_parser_module.RESPONSE_PARSERS.get("clean_text") and isinstance(llm_response_text, str):
                    final_response_data = response_parser_module.RESPONSE_PARSERS["clean_text"](llm_response_text, self.config)
                # Add more parsers if needed, e.g., for extracting structured data if LLM was prompted for it

            # 9. Add messages to history
            chat_memory.add_message({"role": "user", "content": input_data["user_input"]})
            # Determine what to save as assistant's response. If it's a dict from sub-agent, maybe just a summary.
            assistant_response_to_save = final_response_data
            if isinstance(final_response_data, dict):
                assistant_response_to_save = final_response_data.get("result", {}).get("summary") or json.dumps(final_response_data.get("result", final_response_data)[:1000]) # Save summary or truncated dict
            chat_memory.add_message({"role": "assistant", "content": str(assistant_response_to_save)})

            # 10. Post-response Callbacks (applied to final_response_data)
            for callback in post_response.POST_RESPONSE_CALLBACKS:
                returned_data = callback(final_response_data, input_data, self.config)
                if returned_data is not None: final_response_data = returned_data

        except Exception as e:
            self.logger.error(f"Unhandled exception in MainAgent run for session {session_id}: {e}", exc_info=True)
            for callback in on_error.ERROR_HANDLING_CALLBACKS:
                callback(e, input_data, self.config, context_message="MainAgent Run Loop")
            final_response_data = on_error.generate_fallback_response(e, input_data, self.config)
            # Ensure final_response_data is in a state the formatter/sender can handle
            if not isinstance(final_response_data, (str, dict)):
                 final_response_data = str(final_response_data)

        # 11. Format and Send Response (moved outside try-except to always attempt formatting/sending)
        # Determine output format (e.g., from request_data or agent config)
        output_format_type = input_data.get("request_config", {}).get("output_format", "text") # default to text for CLI
        
        formatted_agent_response: Union[str, Dict[str, Any]]
        if output_format_type == "json_envelope" and output_formatter_module.RESPONSE_FORMATTERS.get("json_envelope"):
            # The json_envelope formatter expects the core payload. If final_response_data is already an envelope, adjust.
            core_payload = final_response_data
            if isinstance(final_response_data, dict) and "payload" in final_response_data and "session_id" in final_response_data:
                core_payload = final_response_data["payload"] # Already looks like an envelope
            
            # Reconstruct a consistent output structure for the formatter
            # This part needs to align with output.json schema expectations for the payload
            if isinstance(core_payload, str):
                payload_for_schema = {"text_response": core_payload}
            elif isinstance(core_payload, dict):
                payload_for_schema = core_payload # Assume it's already structured (e.g. from sub-agent)
            else:
                payload_for_schema = {"text_response": str(core_payload)} # Fallback

            # Prepare the data for the json_envelope formatter, which adds its own envelope
            # The formatter itself will create the top-level session_id, timestamp, etc.
            # So we pass the *content* of the response.
            # Let's simplify: the formatter should take the agent's final computed result and wrap it.
            # The output.json schema describes the *final* structure after formatting.
            # For now, let's assume the formatter takes the raw `final_response_data` and the `input_data` for context.
            formatted_agent_response = output_formatter_module.RESPONSE_FORMATTERS["json_envelope"](final_response_data, input_data, self.config)
        
        elif output_formatter_module.RESPONSE_FORMATTERS.get("plain_text_header") and isinstance(final_response_data, str):
            formatted_agent_response = output_formatter_module.RESPONSE_FORMATTERS["plain_text_header"](final_response_data, input_data, self.config)
        else: # Default/fallback formatting
            if isinstance(final_response_data, dict):
                try: formatted_agent_response = json.dumps(final_response_data, indent=2, ensure_ascii=False)
                except: formatted_agent_response = str(final_response_data)
            else:
                formatted_agent_response = str(final_response_data)
        
        # Sending logic (e.g., to console for CLI, or part of HTTP response object)
        # For CLI, the entrypoint will print. For a server, this might modify an HTTP response object.
        # The sender module is more for abstracting where it goes (console, queue, etc.)
        # output_sender_module.RESPONSE_SENDERS["console"](formatted_agent_response, input_data, self.config)
        
        self.logger.info(f"Run finished for session {session_id}. Final response type: {type(formatted_agent_response)}")
        return formatted_agent_response # Return the formatted response for the entrypoint to handle

    def _get_timestamp(self) -> str:
        import datetime
        return datetime.datetime.utcnow().isoformat() + "Z"

if __name__ == "__main__":
    # This is for basic testing of MainAgent directly. 
    # For full CLI, use src/entrypoint.py
    print("Testing MainAgent directly...")
    # Ensure .env is loaded or env vars are set
    try:
        from dotenv import load_dotenv
        dotenv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "config", ".env")
        if os.path.exists(dotenv_path):
            load_dotenv(dotenv_path=dotenv_path)
            print(f"Loaded .env from {dotenv_path} for MainAgent direct test.")
        else:
            print(f".env not found at {dotenv_path} for MainAgent direct test.")
    except ImportError:
        print("dotenv not installed, relying on global env vars for MainAgent direct test.")

    # Check for essential env vars
    required_env_vars = ["OPENAI_API_KEY", "REDIS_HOST", "SUPABASE_URL", "SUPABASE_ANON_KEY"]
    if any(not os.getenv(var) for var in required_env_vars):
        print(f"CRITICAL: Missing one or more required environment variables for direct test: {required_env_vars}")
        print("Skipping direct MainAgent test.")
    else:
        try:
            agent = MainAgent()
            test_session_id = "main_agent_direct_test_" + str(uuid.uuid4())
            print(f"MainAgent initialized for direct test. Session: {test_session_id}")

            # Test 1: Simple greeting
            input1 = {"user_input": "Olá, como vai você?", "session_id": test_session_id}
            response1 = agent.run(input1)
            print(f"\nResponse 1 (Greeting):\n{response1}")

            # Test 2: Question that might use RAG (if configured and populated)
            input2 = {"user_input": "O que é um agente vertical em IA?", "session_id": test_session_id}
            response2 = agent.run(input2)
            print(f"\nResponse 2 (RAG/General Knowledge):\n{response2}")

            # Test 3: Mock sub-agent call (requires LLM to be prompted to output the DSL)
            # This is hard to test directly without a fine-tuned LLM or very specific prompt engineering.
            # For now, we assume the LLM *could* produce this. The sub-agent logic itself is tested in its own file.
            # Example of what LLM might output if it decides to call sub_agent_1:
            # llm_output_for_subagent = "[SUB_AGENT_CALL: sub_agent_1, INPUT: {\"query\": \"Analyze customer feedback for sentiment\", \"data_payload\": \"The new interface is fantastic and easy to use!\", \"analysis_type\": \"sentiment_analysis\"}]"
            # To test this path, one would need to mock the _call_llm method to return this string.
            print("\nSkipping direct sub-agent call test via MainAgent LLM output (complex to mock LLM behavior here).")
            print("Sub-agent functionality is tested individually in their respective agent.py files.")
            print("And can be tested via MainAgent if the LLM is prompted correctly or if a direct dispatch mechanism is added.")

        except Exception as e:
            print(f"Error during MainAgent direct test: {e}")
            import traceback
            traceback.print_exc()

