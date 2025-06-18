"""
Módulo de integração com LLMs do SynapScale
"""

# Import both services
from .unified_service import unified_service  # Mock service (for fallback)

try:
    from .real_llm_service import real_llm_service
    # Use real service by default
    llm_service = real_llm_service
    print("✅ Real LLM Service loaded successfully")
except ImportError as e:
    print(f"⚠️  Real LLM Service not available, using mock: {e}")
    llm_service = unified_service

# Export both for flexibility
__all__ = ["llm_service", "unified_service", "real_llm_service"]
