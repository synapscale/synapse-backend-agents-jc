# flake8: noqa
import os
import sys

# Add the parent directory of 'agent_src' to the Python path
# This allows us to import modules from agent_src
# Vercel serverless functions run from the API directory (e.g., /var/task/api)
# So, agent_src will be at /var/task/api/agent_src
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir) # Add /api to path
sys.path.append(os.path.join(current_dir, "agent_src")) # Add /api/agent_src to path

from flask import Flask, request, jsonify
from flask_cors import CORS

# Ensure that the working directory is the root of the agent_src for config loading
# This might be tricky with Vercel's environment. We'll try to load configs relative to agent_src.
agent_root_path = os.path.join(current_dir, "agent_src")

# It's crucial to set environment variables for the agent to work
# These would typically be set in Vercel's environment variable settings
# For local testing, you might use a .env file loaded by a library like python-dotenv
# Example (ensure these are set in Vercel):
# os.environ["OPENAI_API_KEY"] = "your_openai_key"
# os.environ["REDIS_HOST"] = "your_redis_host"
# os.environ["REDIS_PASSWORD"] = "your_redis_password"
# ... and so on for all LLMs and services

# Attempt to import the MainAgent
try:
    from agent_src.agents.main_agent.agent import MainAgent
    from agent_src.config_loader import load_config
    # The main_agent expects to be run from the project root or have paths adjusted.
    # We will try to load its config by specifying the config path relative to agent_src
    main_agent_config_path = os.path.join(agent_root_path, "agents", "main_agent", "config.yaml")
    # The entrypoint.py usually handles this, let's see if we can replicate parts of it.
except ImportError as e:
    # This will help debug path issues on Vercel
    print(f"Error importing agent modules: {e}")
    print(f"Current sys.path: {sys.path}")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Files in api/: {os.listdir(current_dir)}")
    if os.path.exists(os.path.join(current_dir, "agent_src")):
        print(f"Files in api/agent_src/: {os.listdir(os.path.join(current_dir, "agent_src"))}")
    else:
        print("api/agent_src/ directory not found")
    MainAgent = None # Set to None if import fails
    load_config = None

app = Flask(__name__)
CORS(app) # Enable CORS for all routes, allowing requests from the Next.js frontend

# Initialize the agent (this might be better done on first request or with a global lock)
# For Vercel, serverless functions are stateless, so the agent might be re-initialized on each call.
# This has implications for memory (e.g., Redis becomes more important).

agent_instance = None

def get_agent_instance():
    global agent_instance
    if agent_instance is None and MainAgent and load_config:
        try:
            # We need to ensure all paths within the agent's config are relative to agent_root_path
            # or absolute if they point to something outside (like a global /tmp for Vercel)
            # The original agent loads configs assuming a certain CWD.
            # We might need to adjust how configs are loaded or temporarily change CWD.
            original_cwd = os.getcwd()
            os.chdir(agent_root_path) # Change CWD to agent_src for config loading
            
            # Load the main agent's specific configuration
            # The entrypoint.py does: config = load_config("src/agents/main_agent/config.yaml")
            # So, we adjust the path from agent_root_path
            agent_config_relative_path = "agents/main_agent/config.yaml"
            config = load_config(agent_config_relative_path) # This path is now relative to agent_root_path
            
            agent_instance = MainAgent(config=config)
            print("MainAgent initialized successfully.")
            os.chdir(original_cwd) # Change back CWD
        except Exception as e:
            print(f"Error initializing MainAgent: {e}")
            # If initialization fails, print more debug info
            print(f"Attempted to load config from: {os.path.join(agent_root_path, agent_config_relative_path)}")
            os.chdir(original_cwd) # Ensure CWD is reset
            agent_instance = None # Ensure it's None if failed
    return agent_instance

@app.route("/api/chat", methods=["POST"])
def chat_handler():
    if not MainAgent or not load_config:
        return jsonify({"error": "Agent module not loaded correctly. Check server logs."}), 500

    data = request.get_json()
    if not data or "message" not in data:
        return jsonify({"error": "Missing 'message' in request body"}), 400

    user_message = data["message"]
    # chat_history = data.get("history", []) # Optional: handle chat history if needed by agent

    agent = get_agent_instance()
    if not agent:
        return jsonify({"error": "Agent could not be initialized. Check server logs."}), 500

    try:
        # The agent's run method might need adjustment or the input format confirmed.
        # Assuming agent.run(user_input) is the way to interact.
        # The entrypoint.py uses: agent.run(user_input=user_input)
        # Ensure all necessary environment variables (API keys etc.) are set in Vercel.
        original_cwd = os.getcwd()
        os.chdir(agent_root_path) # Agent might expect to run from its root
        agent_response = agent.run(user_input=user_message)
        os.chdir(original_cwd)
        
        # The response format from agent.run() needs to be known.
        # Assuming it's a string or a dict that can be JSONified.
        # If it's a complex object, extract the relevant part.
        # For now, let's assume it's a string.
        return jsonify({"reply": agent_response})
    except Exception as e:
        print(f"Error during agent execution: {e}")
        # It's good to log the full traceback here for debugging on Vercel
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"An error occurred while processing your message: {str(e)}"}), 500

# This is the entry point for Vercel
# Vercel will look for an 'app' object (Flask instance)
# The file should be in the /api directory (e.g., /api/chat.py)
# Vercel's build process will install dependencies from requirements.txt in the root or /api folder.

if __name__ == "__main__":
    # For local development testing only (not used by Vercel directly)
    # You would need to set environment variables locally for this to work.
    print("Starting Flask app for local development...")
    print("Ensure all required environment variables (API keys, Redis, Supabase) are set.")
    # Example: os.environ['OPENAI_API_KEY'] = 'your_key_here'
    app.run(debug=True, port=5001) # Run on a different port if Next.js is on 3000

