"""
Agent Logic for Sub-agent 5 (Example: User Profile Sub-agent)

This sub-agent specializes in managing user profile information, such as retrieving
preferences, updating details, or checking user permissions (mocked).
"""
import os
import yaml
import json
from jinja2 import Environment, FileSystemLoader
from typing import Union, Dict, Any

class SubAgent5:
    def __init__(self, agent_id: str = "sub_agent_5"):
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
        # Mock user data store for this sub-agent
        self._mock_user_profiles = {
            "user123": {"name": "Alice Wonderland", "email": "alice@example.com", "preferences": {"language": "en-US", "theme": "dark"}, "permissions": ["read_content"]},
            "user456": {"name": "Bob The Builder", "email": "bob@example.com", "preferences": {"language": "es-ES", "theme": "light"}, "permissions": ["read_content", "write_comments"]}
        }
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

    def _call_user_profile_logic(self, task_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Placeholder for this sub-agent's core user profile management logic.
        """
        print(f"\n--- {self.agent_id} ({self.config.get("agent_name")}) - Core Logic (Mock) ---")
        profile_action = task_input.get("profile_action", "get_preferences") # e.g., "get_profile", "update_preference", "check_permission"
        user_id = task_input.get("user_id")
        action_payload = task_input.get("action_payload", {})

        mock_profile_result = {
            "action_performed": profile_action,
            "user_id_processed": user_id,
            "status": "failed",
            "message": "User ID not provided or action failed.",
            "data": None
        }

        if not user_id:
            print(f"{self.agent_id} Error: User ID is required for profile actions.")
            return mock_profile_result

        user_profile = self._mock_user_profiles.get(user_id)

        if not user_profile and profile_action != "create_profile": # Allow create for non-existent user
            mock_profile_result["message"] = f"User profile for {user_id} not found."
            print(mock_profile_result["message"])
            return mock_profile_result

        if profile_action == "get_profile":
            mock_profile_result["data"] = user_profile
            mock_profile_result["status"] = "success"
            mock_profile_result["message"] = f"Profile for {user_id} retrieved successfully."
        elif profile_action == "get_preferences":
            mock_profile_result["data"] = user_profile.get("preferences", {})
            mock_profile_result["status"] = "success"
            mock_profile_result["message"] = f"Preferences for {user_id} retrieved successfully."
        elif profile_action == "update_preference":
            preference_key = action_payload.get("preference_key")
            preference_value = action_payload.get("preference_value")
            if preference_key and preference_value is not None:
                if "preferences" not in user_profile:
                    user_profile["preferences"] = {}
                user_profile["preferences"][preference_key] = preference_value
                self._mock_user_profiles[user_id] = user_profile # Update mock store
                mock_profile_result["status"] = "success"
                mock_profile_result["message"] = f"Preference '{preference_key}' for {user_id} updated to '{preference_value}'."
                mock_profile_result["data"] = user_profile["preferences"]
            else:
                mock_profile_result["message"] = "Missing preference_key or preference_value for update."
        elif profile_action == "check_permission":
            permission_needed = action_payload.get("permission_needed")
            if permission_needed:
                has_permission = permission_needed in user_profile.get("permissions", [])
                mock_profile_result["data"] = {"permission_checked": permission_needed, "has_permission": has_permission}
                mock_profile_result["status"] = "success"
                mock_profile_result["message"] = f"Permission check for '{permission_needed}' for user {user_id} complete."
            else:
                mock_profile_result["message"] = "Missing permission_needed for check."
        else:
            mock_profile_result["message"] = f"Profile action '{profile_action}' not supported by this mock agent."

        print(f"Mock profile action result: {mock_profile_result["message"]}")
        print(f"--- End {self.agent_id} Core Logic ---")
        return mock_profile_result

    def run(self, task_input: dict) -> dict:
        """
        Main execution method for the sub-agent.
        Args:
            task_input: Dict conforming to input_schema.yaml.
                        Example: {"user_id": "user123", "profile_action": "get_preferences"}
        Returns:
            A dictionary containing the sub-agent's result.
        """
        print(f"\n--- {self.agent_id} ({self.config.get("agent_name")}) Run --- \nTask Input: {task_input}")

        if not all(key in task_input for key in self.input_schema.get("required", [])):
            error_msg = f"{self.agent_id} Error: Missing required input fields. Expected: {self.input_schema.get("required")}"
            print(error_msg)
            return {"error": error_msg, "status": "input_validation_failed"}
        
        result_payload = self._call_user_profile_logic(task_input)

        final_output = {
            "sub_agent_id": self.agent_id,
            "status": result_payload.get("status", "failed"),
            "result": result_payload
        }
        
        print(f"Final Output from {self.agent_id}: {final_output}")
        print(f"--- End {self.agent_id} Run ---")
        return final_output

if __name__ == "__main__":
    print(f"Testing {SubAgent5().agent_id} directly...")
    sub_agent_instance = SubAgent5()

    # Test 1: Get preferences for user123
    test_input_get_prefs = {
        "user_id": "user123",
        "profile_action": "get_preferences"
    }
    response_get_prefs = sub_agent_instance.run(test_input_get_prefs)
    print(f"\nResponse from Get Preferences (user123) Test:\n{json.dumps(response_get_prefs, indent=2)}")

    # Test 2: Update preference for user456
    test_input_update_pref = {
        "user_id": "user456",
        "profile_action": "update_preference",
        "action_payload": {"preference_key": "notifications", "preference_value": "email_only"}
    }
    response_update_pref = sub_agent_instance.run(test_input_update_pref)
    print(f"\nResponse from Update Preference (user456) Test:\n{json.dumps(response_update_pref, indent=2)}")
    # Verify update (optional, check internal state or re-fetch)
    updated_prefs_user456 = sub_agent_instance.run({"user_id": "user456", "profile_action": "get_preferences"})
    print(f"Post-update preferences for user456: {updated_prefs_user456["result"]["data"]}")

    # Test 3: Check permission for user123
    test_input_check_perm = {
        "user_id": "user123",
        "profile_action": "check_permission",
        "action_payload": {"permission_needed": "write_content"}
    }
    response_check_perm = sub_agent_instance.run(test_input_check_perm)
    print(f"\nResponse from Check Permission (user123, write_content) Test:\n{json.dumps(response_check_perm, indent=2)}")

    # Test 4: Get full profile for non-existent user
    test_input_get_unknown = {
        "user_id": "user789",
        "profile_action": "get_profile"
    }
    response_get_unknown = sub_agent_instance.run(test_input_get_unknown)
    print(f"\nResponse from Get Profile (unknown user) Test:\n{json.dumps(response_get_unknown, indent=2)}")

