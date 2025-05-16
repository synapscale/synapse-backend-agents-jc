"""
Custom Logger for the Main Agent

This module provides a configurable logger for the agent, allowing for structured
logging to console and/or files. It uses the standard Python `logging` module
and can be configured via a YAML file (e.g., `config/logging.yaml`).

Use cases:
- Centralized logging setup for the entire agent.
- Different log levels for development and production.
- Structured log formats (e.g., JSON) for easier parsing by log management systems.
- Routing logs to different handlers (console, file, external services).
"""
import logging
import logging.config
import yaml
import os
from typing import Optional, Dict, Any

DEFAULT_LOGGING_CONFIG_PATH = "config/logging.yaml"
DEFAULT_LOG_LEVEL = logging.INFO

_logger_initialized = False
_agent_logger: Optional[logging.Logger] = None

def setup_agent_logger(
    agent_name: str = "VerticalAgent", 
    config_path: Optional[str] = None,
    default_level: int = DEFAULT_LOG_LEVEL
) -> logging.Logger:
    """
    Sets up and returns a logger for the agent based on a YAML configuration file.
    If the configuration file is not found or is invalid, a basic logger is configured.

    Args:
        agent_name: The name of the logger to create/get (e.g., "MainAgent", "SubAgent_DataAnalysis").
        config_path: Path to the YAML logging configuration file.
        default_level: The default logging level if configuration fails.

    Returns:
        A configured logging.Logger instance.
    """
    global _logger_initialized, _agent_logger

    # Return existing logger if already initialized for this agent_name (or a generic one)
    # For simplicity in this template, we use one main logger instance that can be shared
    # or reconfigured. A more complex system might have hierarchical loggers.
    if _logger_initialized and _agent_logger and _agent_logger.name == agent_name:
        return _agent_logger

    actual_config_path = config_path or os.getenv("AGENT_LOGGING_CONFIG", DEFAULT_LOGGING_CONFIG_PATH)
    
    try:
        if os.path.exists(actual_config_path):
            with open(actual_config_path, "rt") as f:
                log_config_dict = yaml.safe_load(f.read())
            
            # Ensure logs directory exists if file handlers are used
            # This is a common pattern in logging configs
            if "handlers" in log_config_dict:
                for handler_name, handler_config in log_config_dict["handlers"].items():
                    if "filename" in handler_config:
                        log_dir = os.path.dirname(handler_config["filename"])
                        if log_dir and not os.path.exists(log_dir):
                            os.makedirs(log_dir, exist_ok=True)
            
            logging.config.dictConfig(log_config_dict)
            logger = logging.getLogger(agent_name)
            # logger.info(f"Logging configured for '{agent_name}' from: {actual_config_path}")
        else:
            # print(f"Warning: Logging config file not found at {actual_config_path}. Using basicConfig.")
            logging.basicConfig(level=default_level, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
            logger = logging.getLogger(agent_name)
            logger.info(f"Basic logging configured for '{agent_name}' at level {logging.getLevelName(default_level)}.")
    except Exception as e:
        # print(f"Error configuring logging from {actual_config_path}: {e}. Using basicConfig.")
        logging.basicConfig(level=default_level, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        logger = logging.getLogger(agent_name)
        logger.error(f"Error during logging setup for '{agent_name}', basic logging used: {e}", exc_info=True)
    
    _agent_logger = logger
    _logger_initialized = True
    return _agent_logger

def get_logger(agent_name: str = "VerticalAgent") -> logging.Logger:
    """
    Convenience function to get the initialized agent logger.
    If not initialized, it will set up with default parameters.
    """
    if not _logger_initialized or not _agent_logger or _agent_logger.name != agent_name:
        # print(f"Logger for '{agent_name}' not explicitly set up, initializing with defaults.")
        return setup_agent_logger(agent_name=agent_name)
    return _agent_logger

# Example logging.yaml (to be placed in config/logging.yaml)
"""
version: 1
disable_existing_loggers: False

formatters:
  simple:
    format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  detailed:
    format: "%(asctime)s - %(name)s - %(module)s - %(funcName)s - %(lineno)d - %(levelname)s - %(message)s"
  json:
    format: "{\"timestamp\": \"%(asctime)s\", \"logger_name\": \"%(name)s\", \"level\": \"%(levelname)s\", \"module\": \"%(module)s\", \"function\": \"%(funcName)s\", \"line\": \"%(lineno)d\", \"message\": \"%(message)s\"}"
    # For actual JSON logging, consider using python-json-logger library

handlers:
  console:
    class: logging.StreamHandler
    level: DEBUG
    formatter: simple
    stream: ext://sys.stdout

  info_file_handler:
    class: logging.handlers.RotatingFileHandler
    level: INFO
    formatter: detailed
    filename: logs/info.log  # Ensure logs/ directory exists or is created by setup
    maxBytes: 10485760 # 10MB
    backupCount: 10
    encoding: utf8

  error_file_handler:
    class: logging.handlers.RotatingFileHandler
    level: ERROR
    formatter: detailed
    filename: logs/error.log # Ensure logs/ directory exists
    maxBytes: 10485760 # 10MB
    backupCount: 10
    encoding: utf8

loggers:
  VerticalAgent: # Default logger for the main agent
    level: INFO
    handlers: [console, info_file_handler, error_file_handler]
    propagate: no # Do not pass messages to the root logger

  SubAgent_Generic:
    level: DEBUG
    handlers: [console, info_file_handler]
    propagate: no

  # Add specific loggers for other modules or sub-agents if needed
  # Example: 
  #   SubAgent_DataProcessor:
  #     level: DEBUG
  #     handlers: [console]
  #     propagate: no

root:
  level: WARNING
  handlers: [console]
"""

if __name__ == "__main__":
    # Create a dummy config/logging.yaml for testing this module directly
    # In a real run, this file would exist at the project root's config/ directory.
    dummy_config_dir = "config"
    dummy_logs_dir = "logs"
    if not os.path.exists(dummy_config_dir):
        os.makedirs(dummy_config_dir)
    if not os.path.exists(dummy_logs_dir):
        os.makedirs(dummy_logs_dir)
    
    dummy_logging_yaml_content = """
version: 1
disable_existing_loggers: False
formatters:
  simple:
    format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
handlers:
  console:
    class: logging.StreamHandler
    level: DEBUG
    formatter: simple
    stream: ext://sys.stdout
  test_file_handler:
    class: logging.FileHandler
    level: DEBUG
    formatter: simple
    filename: logs/test_logger_output.log
    encoding: utf8
    mode: 'w' # Overwrite for test
loggers:
  TestLogger:
    level: DEBUG
    handlers: [console, test_file_handler]
    propagate: no
root:
  level: INFO
  handlers: [console]
"""
    with open(os.path.join(dummy_config_dir, "logging.yaml"), "w") as f:
        f.write(dummy_logging_yaml_content)

    print(f"Testing agent logger setup (using dummy {DEFAULT_LOGGING_CONFIG_PATH})...")
    
    # Test with default agent name
    logger1 = get_logger()
    logger1.debug("This is a debug message from logger1 (default name).")
    logger1.info("This is an info message from logger1.")
    logger1.warning("This is a warning from logger1.")
    logger1.error("This is an error from logger1.")
    logger1.critical("This is a critical message from logger1.")

    # Test with a specific agent name, configured in dummy yaml
    logger_test = get_logger("TestLogger")
    logger_test.info("INFO message from TestLogger. Should go to console and logs/test_logger_output.log")
    logger_test.debug("DEBUG message from TestLogger.")

    # Test logger not in config (should use root or basicConfig based on setup logic)
    logger_other = get_logger("OtherModuleLogger")
    logger_other.info("INFO message from OtherModuleLogger (should use root/basic config).")

    print(f"\nCheck 'logs/test_logger_output.log' for file output from TestLogger.")
    
    # Clean up dummy files/dirs if needed (optional)
    # import shutil
    # if os.path.exists(dummy_logs_dir): shutil.rmtree(dummy_logs_dir)
    # if os.path.exists(dummy_config_dir): shutil.rmtree(dummy_config_dir)

