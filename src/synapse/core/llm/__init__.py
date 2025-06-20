"""
Módulo de integração com LLMs do SynapScale
"""

# Import all services
from .unified_service import unified_service  # Mock service (for fallback)

try:
    from .real_llm_service import real_llm_service
    from .user_variables_llm_service import user_variables_llm_service
    
    # Use user_variables service by default (supports DB API keys)
    llm_service = user_variables_llm_service
    print("✅ UserVariablesLLMService loaded successfully (with DB API keys support)")
except ImportError as e:
    try:
        from .real_llm_service import real_llm_service
        llm_service = real_llm_service
        print("✅ Real LLM Service loaded successfully")
    except ImportError as e2:
        print(f"⚠️  Real LLM Service not available, using mock: {e2}")
        llm_service = unified_service

# Export both for flexibility
__all__ = ["llm_service", "unified_service", "real_llm_service", "user_variables_llm_service"]
