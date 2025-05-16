"""
Entrypoint for the Vertical Agent Application.

This script provides a basic Command Line Interface (CLI) to interact with
the MainAgent. It can be expanded to be an HTTP server (e.g., using FastAPI)
or any other type of application entrypoint.

To run:
1. Ensure all dependencies in requirements.txt are installed.
2. Ensure config/.env is populated with necessary API keys and configurations.
3. From the project root (my_vertical_agent/../), run:
   python -m my_vertical_agent.src.entrypoint
"""
import argparse
import os
import sys
import uuid

# Ensure the src directory is in the Python path for imports
# This is often needed when running scripts directly from within a package structure.
# Adjust if your project structure or execution method differs.
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from my_vertical_agent.src.agents.main_agent.agent import MainAgent
from my_vertical_agent.src.agents.main_agent.outputs.logger import setup_agent_logger, get_logger

# Attempt to load .env file if python-dotenv is available
try:
    from dotenv import load_dotenv
    # Construct the path to the .env file relative to this entrypoint script
    # Assuming entrypoint.py is in src/ and .env is in config/
    dotenv_path = os.path.join(os.path.dirname(PROJECT_ROOT), "config", ".env")
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path=dotenv_path)
        # print(f"Loaded .env file from: {dotenv_path}")
    else:
        # print(f".env file not found at {dotenv_path}. Relying on globally set environment variables.")
        pass
except ImportError:
    # print("python-dotenv not installed. Relying on globally set environment variables.")
    pass

# Initialize logger for the entrypoint itself
entrypoint_logger = setup_agent_logger(agent_name="Entrypoint", default_level=os.getenv("AGENT_LOG_LEVEL", "INFO").upper())

def run_cli():
    """Runs a simple command-line interface to interact with the MainAgent."""
    entrypoint_logger.info("Initializing MainAgent for CLI interaction...")
    
    # Check for essential environment variables needed by the agent
    required_env_vars = ["OPENAI_API_KEY", "REDIS_HOST", "SUPABASE_URL", "SUPABASE_ANON_KEY"]
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    if missing_vars:
        entrypoint_logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        entrypoint_logger.error("Please ensure your config/.env file is correctly populated or environment variables are set.")
        return

    try:
        main_agent = MainAgent() # Assumes MainAgent can load its config from default paths
    except Exception as e:
        entrypoint_logger.error(f"Failed to initialize MainAgent: {e}", exc_info=True)
        return

    entrypoint_logger.info("MainAgent initialized. CLI is ready.")
    print("\nVertical Agent CLI - Type 'quit' or 'exit' to end.")

    # Generate a persistent session ID for this CLI run, or allow user to specify
    session_id = str(uuid.uuid4())
    print(f"Using Session ID: {session_id}")

    while True:
        try:
            user_input_text = input("\nVocê: ")
            if user_input_text.lower() in ["quit", "exit"]:
                print("Saindo do CLI do Agente Vertical.")
                break
            if not user_input_text.strip():
                continue

            # Prepare input data for the agent
            # This should align with the MainAgent's input schema (if one is strictly enforced)
            agent_input_data = {
                "user_input": user_input_text,
                "session_id": session_id,
                "user_profile": { # Example user profile data
                    "name": "CLI User",
                    "preferences": {"language": "pt-BR"} 
                },
                "request_config": { # Example request-specific config
                    "output_format": "text", # Could be "json"
                    "output_language": "pt-BR"
                }
            }
            
            entrypoint_logger.info(f"Sending to MainAgent (Session: {session_id}): {user_input_text}")
            agent_response = main_agent.run(agent_input_data)
            
            # The agent_response format depends on the agent's output logic.
            # For CLI, a simple string is usually best.
            print(f"\nAgente: {agent_response}")
            entrypoint_logger.info(f"Received from MainAgent (Session: {session_id}): {str(agent_response)[:200]}...")

        except KeyboardInterrupt:
            print("\nSaindo do CLI do Agente Vertical (Interrupção do teclado).")
            break
        except Exception as e:
            entrypoint_logger.error(f"An error occurred in the CLI loop: {e}", exc_info=True)
            print(f"Erro: {e}")
            # Optionally, decide if the CLI should exit on all errors or try to continue
            # break 

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Vertical Agent Application Entrypoint.")
    parser.add_argument("--mode", type=str, default="cli", choices=["cli"], help="Mode to run the application in (default: cli).")
    # Add other arguments here if needed, e.g., for different modes like "server"

    args = parser.parse_args()

    if args.mode == "cli":
        run_cli()
    # elif args.mode == "server":
    #     run_server() # Placeholder for a web server function
    else:
        entrypoint_logger.error(f"Unsupported mode: {args.mode}")
        print(f"Modo não suportado: {args.mode}")

