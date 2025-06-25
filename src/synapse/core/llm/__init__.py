"""
Módulo de integração com LLMs do SynapScale
"""

# Import services from the main services module
try:
    from synapse.services.llm_service import UnifiedLLMService, get_llm_service, get_llm_service_direct
    
    # Use UnifiedLLMService as the main service
    llm_service = get_llm_service_direct
    print("✅ UnifiedLLMService loaded successfully (with full LLM capabilities)")
except ImportError as e:
    print(f"⚠️  UnifiedLLMService not available: {e}")
    llm_service = None

# Export services for flexibility
__all__ = [
    "llm_service", 
    "UnifiedLLMService",
    "get_llm_service",
    "get_llm_service_direct"
]
