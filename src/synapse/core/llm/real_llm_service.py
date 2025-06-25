"""
Real LLM Service - Implementação real com APIs dos provedores
Criado para substituir o mock service com chamadas reais para LLMs
"""

import asyncio
import aiohttp
import json
from typing import Dict, Any, Optional, List, Tuple
from collections.abc import AsyncGenerator
import os
from datetime import datetime, timedelta
import hashlib
import pickle

# Import providers
try:
    import openai
    from openai import AsyncOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

try:
    import google.generativeai as genai
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False

# Token counting libraries
try:
    import tiktoken
    TIKTOKEN_AVAILABLE = True
except ImportError:
    TIKTOKEN_AVAILABLE = False

from synapse.core.config_new import settings
from synapse.logger_config import get_logger
from synapse.core.cache import get_cache_manager
# Import for ListModelsResponse to avoid circular import issues
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from synapse.api.v1.endpoints.llm.schemas import ListModelsResponse

logger = get_logger(__name__)


class TokenBudgetExceededError(Exception):
    """Raised when token budget is exceeded"""
    pass


class OptimizedTokenManager:
    """Advanced token management with caching, budgets, and optimization"""
    
    def __init__(self):
        self.cache_manager = get_cache_manager()
        self.token_cache = {}  # In-memory cache for token counts
        self.budget_cache = {}  # User budget tracking
        self.optimization_cache = {}  # Request optimization cache
        
    async def count_tokens_precise(
        self, 
        text: str, 
        provider: str, 
        model: str,
        cache_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Precise token counting using provider-specific tokenizers
        
        Args:
            text: Text to count tokens for
            provider: LLM provider
            model: Specific model
            cache_key: Optional cache key to avoid recounting identical text
            
        Returns:
            Dict with precise token count and metadata
        """
        # Generate cache key if not provided
        if not cache_key:
            cache_key = hashlib.md5(f"{provider}:{model}:{text}".encode()).hexdigest()
        
        # Check cache first
        cached_result = await self._get_cached_token_count(cache_key)
        if cached_result:
            logger.debug(f"Token count cache hit for key: {cache_key[:8]}...")
            return cached_result
        
        try:
            token_count = 0
            estimation_method = "fallback_estimation"
            
            if provider == "openai" and TIKTOKEN_AVAILABLE:
                # Use tiktoken for precise OpenAI token counting
                try:
                    # Get appropriate encoding for model
                    if model.startswith("gpt-4"):
                        encoding = tiktoken.encoding_for_model("gpt-4")
                    elif model.startswith("gpt-3.5"):
                        encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
                    else:
                        encoding = tiktoken.get_encoding("cl100k_base")
                    
                    token_count = len(encoding.encode(text))
                    estimation_method = "tiktoken_precise"
                    logger.debug(f"Precise OpenAI token count: {token_count}")
                    
                except Exception as e:
                    logger.warning(f"Tiktoken encoding failed: {e}, falling back to estimation")
                    token_count = self._estimate_tokens(text)
                    estimation_method = "fallback_after_tiktoken_error"
                    
            elif provider == "anthropic":
                # Anthropic uses similar tokenization, estimate more conservatively
                token_count = max(len(text) // 3.5, len(text.split()) * 1.4)
                estimation_method = "anthropic_conservative_estimation"
                
            elif provider == "google":
                # Google models have different tokenization patterns
                token_count = max(len(text) // 3.8, len(text.split()) * 1.2)
                estimation_method = "google_estimation"
                
            else:
                # Fallback estimation
                token_count = self._estimate_tokens(text)
                estimation_method = "generic_estimation"
            
            token_count = max(1, int(token_count))  # Ensure at least 1 token
            
            result = {
                "text_preview": text[:100] + "..." if len(text) > 100 else text,
                "token_count": token_count,
                "character_count": len(text),
                "word_count": len(text.split()),
                "provider": provider,
                "model": model,
                "estimation_method": estimation_method,
                "cache_key": cache_key,
                "timestamp": datetime.now().isoformat(),
                "tokens_per_word": token_count / max(1, len(text.split())),
                "tokens_per_char": token_count / max(1, len(text)),
            }
            
            # Cache the result
            await self._cache_token_count(cache_key, result)
            
            return result
            
        except Exception as e:
            logger.error(f"Token counting failed: {e}")
            # Return fallback estimation
            fallback_count = self._estimate_tokens(text)
            return {
                "text_preview": text[:100] + "..." if len(text) > 100 else text,
                "token_count": fallback_count,
                "character_count": len(text),
                "word_count": len(text.split()),
                "provider": provider,
                "model": model,
                "estimation_method": "error_fallback",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }
    
    def _estimate_tokens(self, text: str) -> int:
        """Fallback token estimation"""
        # Use multiple estimation methods and take the maximum for safety
        char_estimate = max(1, len(text) // 4)
        word_estimate = max(1, int(len(text.split()) * 1.3))
        return max(char_estimate, word_estimate)
    
    async def _get_cached_token_count(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get cached token count"""
        try:
            # Check in-memory cache first
            if cache_key in self.token_cache:
                cached_data = self.token_cache[cache_key]
                # Check if cache is still valid (1 hour)
                cache_time = datetime.fromisoformat(cached_data["timestamp"])
                if datetime.now() - cache_time < timedelta(hours=1):
                    return cached_data
                else:
                    del self.token_cache[cache_key]
            
            # Check Redis cache if available
            if self.cache_manager:
                cached_data = await self.cache_manager.get(f"tokens:{cache_key}")
                if cached_data:
                    return json.loads(cached_data)
            
            return None
            
        except Exception as e:
            logger.warning(f"Cache retrieval failed: {e}")
            return None
    
    async def _cache_token_count(self, cache_key: str, result: Dict[str, Any]):
        """Cache token count result"""
        try:
            # Store in memory cache
            self.token_cache[cache_key] = result
            
            # Limit memory cache size
            if len(self.token_cache) > 1000:
                # Remove oldest 200 entries
                sorted_items = sorted(
                    self.token_cache.items(),
                    key=lambda x: x[1]["timestamp"]
                )
                for key, _ in sorted_items[:200]:
                    del self.token_cache[key]
            
            # Store in Redis cache if available
            if self.cache_manager:
                await self.cache_manager.set(
                    f"tokens:{cache_key}",
                    json.dumps(result),
                    ttl=3600  # 1 hour TTL
                )
                
        except Exception as e:
            logger.warning(f"Cache storage failed: {e}")
    
    async def check_token_budget(
        self, 
        user_id: str, 
        estimated_tokens: int,
        provider: str,
        model: str
    ) -> Dict[str, Any]:
        """
        Check if user has sufficient token budget
        
        Args:
            user_id: User identifier
            estimated_tokens: Estimated tokens for the request
            provider: LLM provider
            model: Specific model
            
        Returns:
            Dict with budget status and recommendations
        """
        try:
            # Get user's current usage for today
            daily_usage = await self._get_daily_usage(user_id)
            
            # Get user's budget limits (this would typically come from a database)
            budget_limits = await self._get_user_budget_limits(user_id)
            
            # Calculate estimated cost
            estimated_cost = await self._estimate_cost(provider, model, estimated_tokens)
            
            # Check various budget constraints
            checks = {
                "daily_token_limit": {
                    "current": daily_usage.get("total_tokens", 0),
                    "limit": budget_limits.get("daily_tokens", 100000),
                    "requested": estimated_tokens,
                    "passed": daily_usage.get("total_tokens", 0) + estimated_tokens <= budget_limits.get("daily_tokens", 100000)
                },
                "daily_cost_limit": {
                    "current": daily_usage.get("total_cost", 0.0),
                    "limit": budget_limits.get("daily_cost", 10.0),
                    "requested": estimated_cost,
                    "passed": daily_usage.get("total_cost", 0.0) + estimated_cost <= budget_limits.get("daily_cost", 10.0)
                },
                "hourly_request_limit": {
                    "current": daily_usage.get("hourly_requests", 0),
                    "limit": budget_limits.get("hourly_requests", 100),
                    "requested": 1,
                    "passed": daily_usage.get("hourly_requests", 0) < budget_limits.get("hourly_requests", 100)
                }
            }
            
            all_passed = all(check["passed"] for check in checks.values())
            
            result = {
                "budget_approved": all_passed,
                "checks": checks,
                "estimated_cost": estimated_cost,
                "estimated_tokens": estimated_tokens,
                "daily_usage": daily_usage,
                "budget_limits": budget_limits,
                "timestamp": datetime.now().isoformat()
            }
            
            if not all_passed:
                # Provide recommendations for optimization
                result["recommendations"] = await self._generate_budget_recommendations(
                    checks, provider, model, estimated_tokens
                )
            
            return result
            
        except Exception as e:
            logger.error(f"Budget check failed: {e}")
            # In case of error, allow the request but log the issue
            return {
                "budget_approved": True,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "fallback": True
            }
    
    async def _get_daily_usage(self, user_id: str) -> Dict[str, Any]:
        """Get user's usage for today from the database"""
        try:
            from synapse.database import get_db
            from synapse.models.usage_log import UsageLog
            from datetime import datetime, timedelta
            from sqlalchemy import func
            from sqlalchemy.orm import Session
            
            # Get database session
            db_gen = get_db()
            db: Session = next(db_gen)
            
            try:
                # Calculate today's date range
                today = datetime.now().date()
                start_of_day = datetime.combine(today, datetime.min.time())
                end_of_day = datetime.combine(today, datetime.max.time())
                
                # Query today's usage logs for the user
                today_logs = db.query(UsageLog).filter(
                    UsageLog.user_id == user_id,
                    UsageLog.created_at >= start_of_day,
                    UsageLog.created_at <= end_of_day,
                    UsageLog.status == 'success'
                ).all()
                
                # Calculate totals
                total_tokens = sum(log.total_tokens for log in today_logs)
                total_cost = sum(log.cost_usd for log in today_logs)
                requests_count = len(today_logs)
                
                # Calculate hourly requests (last hour)
                hour_ago = datetime.now() - timedelta(hours=1)
                hourly_logs = db.query(UsageLog).filter(
                    UsageLog.user_id == user_id,
                    UsageLog.created_at >= hour_ago,
                    UsageLog.status == 'success'
                ).count()
                
                logger.debug(f"Daily usage for user {user_id}: {total_tokens} tokens, ${total_cost:.4f}, {requests_count} requests")
                
                return {
                    "total_tokens": total_tokens,
                    "total_cost": total_cost,
                    "hourly_requests": hourly_logs,
                    "requests_count": requests_count
                }
                
            finally:
                db.close()
                
        except Exception as e:
            logger.warning(f"Failed to get daily usage from database for user {user_id}: {e}")
            # Fallback to conservative estimates
            return {
                "total_tokens": 0,
                "total_cost": 0.0,
                "hourly_requests": 0,
                "requests_count": 0
            }
    
    async def _get_user_budget_limits(self, user_id: str) -> Dict[str, Any]:
        """Get user's budget limits based on their subscription plan"""
        try:
            from synapse.database import get_db
            from synapse.models.subscription import UserSubscription, Plan, PlanType, SubscriptionStatus
            from sqlalchemy.orm import Session, joinedload
            
            # Get database session
            db_gen = get_db()
            db: Session = next(db_gen)
            
            try:
                # Get user's active subscription with plan data
                subscription = (
                    db.query(UserSubscription)
                    .options(joinedload(UserSubscription.plan))
                    .filter(
                        UserSubscription.user_id == user_id,
                        UserSubscription.status == SubscriptionStatus.ACTIVE
                    )
                    .first()
                )
                
                if not subscription or not subscription.plan:
                    logger.warning(f"No active subscription found for user {user_id}, using minimal limits")
                    return {
                        "daily_tokens": 1000,
                        "daily_cost": 0.50,
                        "hourly_requests": 10,
                        "max_tokens_per_request": 1000
                    }
                
                plan = subscription.plan
                plan_type = plan.type
                
                # Map subscription plans to LLM token limits
                # These limits are designed to be reasonable for each tier
                if plan_type == PlanType.FREE:
                    limits = {
                        "daily_tokens": 10000,    # 10K tokens daily
                        "daily_cost": 2.00,       # $2 daily limit
                        "hourly_requests": 20,    # 20 requests per hour
                        "max_tokens_per_request": 2000  # 2K max per request
                    }
                elif plan_type == PlanType.BASIC:
                    limits = {
                        "daily_tokens": 50000,    # 50K tokens daily
                        "daily_cost": 10.00,      # $10 daily limit
                        "hourly_requests": 100,   # 100 requests per hour
                        "max_tokens_per_request": 4000  # 4K max per request
                    }
                elif plan_type == PlanType.PRO:
                    limits = {
                        "daily_tokens": 200000,   # 200K tokens daily
                        "daily_cost": 50.00,      # $50 daily limit
                        "hourly_requests": 500,   # 500 requests per hour
                        "max_tokens_per_request": 8000  # 8K max per request
                    }
                elif plan_type == PlanType.ENTERPRISE:
                    limits = {
                        "daily_tokens": 1000000,  # 1M tokens daily
                        "daily_cost": 200.00,     # $200 daily limit
                        "hourly_requests": 2000,  # 2000 requests per hour
                        "max_tokens_per_request": 16000  # 16K max per request
                    }
                else:
                    # Fallback for unknown plan types
                    limits = {
                        "daily_tokens": 5000,
                        "daily_cost": 1.00,
                        "hourly_requests": 10,
                        "max_tokens_per_request": 1000
                    }
                
                # Add metadata about the plan for debugging/logging
                limits.update({
                    "plan_id": str(plan.id),
                    "plan_name": plan.name,
                    "plan_type": plan_type.value,
                    "subscription_id": str(subscription.id),
                    "subscription_status": subscription.status.value
                })
                
                logger.debug(f"Budget limits for user {user_id} ({plan_type.value}): {limits}")
                
                return limits
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Failed to get budget limits from database for user {user_id}: {e}")
            # Fallback to conservative limits if database access fails
            return {
                "daily_tokens": 1000,
                "daily_cost": 0.50,
                "hourly_requests": 5,
                "max_tokens_per_request": 500,
                "error": "Database error - using fallback limits"
            }
    
    async def _estimate_cost(self, provider: str, model: str, tokens: int) -> float:
        """Estimate cost for tokens"""
        # Simplified cost calculation - should use real pricing from LLM model
        cost_per_1k_tokens = {
            "openai": {
                "gpt-4o": 0.005,
                "gpt-4-turbo": 0.01,
                "gpt-3.5-turbo": 0.001
            },
            "anthropic": {
                "claude-3-opus-20240229": 0.015,
                "claude-3-sonnet-20240229": 0.003,
                "claude-3-haiku-20240307": 0.00025
            },
            "google": {
                "gemini-1.5-pro": 0.0035,
                "gemini-1.5-flash": 0.0007,
                "gemini-1.0-pro": 0.0005
            }
        }
        
        provider_costs = cost_per_1k_tokens.get(provider, {})
        model_cost = provider_costs.get(model, 0.001)  # Default fallback
        
        return (tokens / 1000) * model_cost
    
    async def _generate_budget_recommendations(
        self, 
        checks: Dict[str, Any], 
        provider: str, 
        model: str, 
        tokens: int
    ) -> List[str]:
        """Generate recommendations for budget optimization"""
        recommendations = []
        
        for check_name, check_data in checks.items():
            if not check_data["passed"]:
                if check_name == "daily_token_limit":
                    recommendations.append(
                        f"Daily token limit exceeded. Consider using a more efficient model "
                        f"or reducing prompt length by {tokens - (check_data['limit'] - check_data['current'])} tokens."
                    )
                elif check_name == "daily_cost_limit":
                    recommendations.append(
                        f"Daily cost limit exceeded. Try using a cheaper model like gpt-3.5-turbo "
                        f"or reduce max_tokens parameter."
                    )
                elif check_name == "hourly_request_limit":
                    recommendations.append(
                        "Hourly request limit exceeded. Please wait before making more requests "
                        "or consider upgrading your plan."
                    )
        
        # Add general optimization suggestions
        if tokens > 2000:
            recommendations.append(
                "Large prompt detected. Consider breaking down into smaller requests "
                "or optimizing prompt length for better cost efficiency."
            )
        
        return recommendations
    
    async def optimize_request(
        self, 
        prompt: str, 
        provider: str, 
        model: str,
        max_tokens: int,
        user_budget: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Optimize request for token efficiency
        
        Args:
            prompt: Original prompt
            provider: LLM provider
            model: Specific model
            max_tokens: Maximum tokens for response
            user_budget: User's budget constraints
            
        Returns:
            Optimized request parameters and suggestions
        """
        try:
            # Count tokens in prompt
            token_info = await self.count_tokens_precise(prompt, provider, model)
            prompt_tokens = token_info["token_count"]
            
            # Check if request needs optimization
            total_estimated_tokens = prompt_tokens + max_tokens
            
            optimizations = {
                "original_prompt_tokens": prompt_tokens,
                "original_max_tokens": max_tokens,
                "total_estimated_tokens": total_estimated_tokens,
                "optimizations_applied": [],
                "final_prompt": prompt,
                "final_max_tokens": max_tokens,
                "optimization_summary": ""
            }
            
            # Check if prompt is too long
            if prompt_tokens > 3000:
                # Suggest prompt compression techniques
                optimizations["optimizations_applied"].append("prompt_length_warning")
                optimizations["optimization_summary"] += "Consider shortening prompt. "
            
            # Check if max_tokens is excessive for budget
            budget_info = await self.check_token_budget(
                user_budget.get("user_id", "unknown"),
                total_estimated_tokens,
                provider,
                model
            )
            
            if not budget_info["budget_approved"]:
                # Reduce max_tokens to fit budget
                available_tokens = (
                    budget_info["budget_limits"]["daily_tokens"] - 
                    budget_info["daily_usage"]["total_tokens"] - 
                    prompt_tokens
                )
                
                if available_tokens > 0 and available_tokens < max_tokens:
                    optimizations["final_max_tokens"] = min(available_tokens, max_tokens)
                    optimizations["optimizations_applied"].append("max_tokens_reduced")
                    optimizations["optimization_summary"] += f"Reduced max_tokens to {available_tokens} to fit budget. "
            
            # Suggest more efficient model if needed
            if provider == "openai" and model == "gpt-4o" and prompt_tokens < 1000:
                optimizations["optimizations_applied"].append("model_suggestion")
                optimizations["optimization_summary"] += "Consider using gpt-3.5-turbo for this simple request. "
                optimizations["suggested_model"] = "gpt-3.5-turbo"
            
            return optimizations
            
        except Exception as e:
            logger.error(f"Request optimization failed: {e}")
            return {
                "error": str(e),
                "original_prompt_tokens": 0,
                "final_prompt": prompt,
                "final_max_tokens": max_tokens
            }


class LLMResponse:
    """Resposta padrão dos LLMs"""
    def __init__(self, content: str, model: str, provider: str, usage: dict = None, metadata: dict = None):
        self.content = content
        self.model = model
        self.provider = provider
        self.usage = usage or {}
        self.metadata = metadata or {}


class RealLLMService:
    """Serviço real para integração com múltiplos provedores de LLM"""

    def __init__(self):
        self.settings = settings
        self.providers = {}
        self.clients = {}
        self.token_manager = OptimizedTokenManager()
        self._initialize_providers()

    def _initialize_providers(self):
        """Inicializa os provedores de LLM disponíveis com suas configurações reais"""
        
        # OpenAI - Enhanced Configuration
        if OPENAI_AVAILABLE and self.settings.OPENAI_API_KEY:
            try:
                # Validate OpenAI configuration first
                validation_result = self.settings.validate_openai_config()
                if not validation_result["valid"]:
                    logger.error(f"Invalid OpenAI configuration: {validation_result['errors']}")
                    self.providers["openai"] = {"available": False, "error": "Invalid configuration"}
                    return
                
                # Log warnings if any
                for warning in validation_result.get("warnings", []):
                    logger.warning(f"OpenAI configuration warning: {warning}")
                
                # Get optimized client configuration
                client_config = self.settings.get_openai_client_config()
                
                # Initialize OpenAI client with enhanced configuration
                if self.settings.OPENAI_API_TYPE == "azure":
                    from openai import AsyncAzureOpenAI
                    self.clients["openai"] = AsyncAzureOpenAI(**client_config)
                    logger.info("Azure OpenAI client initialized successfully")
                else:
                    self.clients["openai"] = AsyncOpenAI(**client_config)
                    logger.info("OpenAI client initialized successfully")
                
                # Enhanced provider information
                self.providers["openai"] = {
                    "name": "OpenAI",
                    "models": ["gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"],
                    "default_model": self.settings.OPENAI_DEFAULT_MODEL,
                    "api_type": self.settings.OPENAI_API_TYPE,
                    "organization": self.settings.OPENAI_ORG_ID,
                    "timeout": self.settings.OPENAI_TIMEOUT,
                    "max_retries": self.settings.OPENAI_MAX_RETRIES,
                    "available": True
                }
                
                logger.info(f"OpenAI provider initialized: type={self.settings.OPENAI_API_TYPE}, org={self.settings.OPENAI_ORG_ID}, timeout={self.settings.OPENAI_TIMEOUT}s")
                
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI: {e}")
                self.providers["openai"] = {"available": False, "error": str(e)}

        # Anthropic
        anthropic_key = getattr(self.settings, 'ANTHROPIC_API_KEY', None) or getattr(self.settings, 'CLAUDE_API_KEY', None)
        if ANTHROPIC_AVAILABLE and anthropic_key:
            try:
                self.clients["anthropic"] = anthropic.AsyncAnthropic(api_key=anthropic_key)
                self.providers["anthropic"] = {
                    "name": "Anthropic",
                    "models": ["claude-3-opus-20240229", "claude-3-sonnet-20240229", "claude-3-haiku-20240307"],
                    "available": True
                }
                logger.info("Anthropic provider initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Anthropic: {e}")
                self.providers["anthropic"] = {"available": False, "error": str(e)}

        # Google Gemini
        google_key = getattr(self.settings, 'GOOGLE_API_KEY', None) or getattr(self.settings, 'GEMINI_API_KEY', None)
        if GOOGLE_AVAILABLE and google_key:
            try:
                genai.configure(api_key=google_key)
                self.providers["google"] = {
                    "name": "Google",
                    "models": ["gemini-1.5-pro", "gemini-1.5-flash", "gemini-1.0-pro"],
                    "available": True
                }
                logger.info("Google provider initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Google: {e}")
                self.providers["google"] = {"available": False, "error": str(e)}

        logger.info(f"Initialized {len([p for p in self.providers.values() if p.get('available')])} LLM providers")
        logger.info(f"Token management system initialized with {'tiktoken' if TIKTOKEN_AVAILABLE else 'fallback estimation'}")

    async def generate_text(
        self,
        prompt: str,
        model: str | None = None,
        provider: str | None = None,
        user_id: str | None = None,
        **kwargs,
    ) -> LLMResponse:
        """
        Gera texto usando o LLM especificado com otimização avançada de tokens

        Args:
            prompt: Prompt para o LLM
            model: Modelo específico (opcional)
            provider: Provedor específico (opcional)
            user_id: ID do usuário para controle de budget (opcional)
            **kwargs: Parâmetros adicionais

        Returns:
            LLMResponse: Resposta do LLM
        """
        # Determine provider and model
        if not provider:
            provider = getattr(self.settings, 'LLM_DEFAULT_PROVIDER', 'openai')
        
        if not model:
            model = self._get_default_model(provider)

        # Token management and optimization
        if user_id:
            try:
                # Count tokens precisely
                token_info = await self.token_manager.count_tokens_precise(prompt, provider, model)
                logger.debug(f"Precise token count: {token_info['token_count']} using {token_info['estimation_method']}")
                
                # Check budget constraints
                max_tokens = kwargs.get("max_tokens", 1000)
                budget_check = await self.token_manager.check_token_budget(
                    user_id, 
                    token_info["token_count"] + max_tokens,
                    provider,
                    model
                )
                
                if not budget_check["budget_approved"]:
                    logger.warning(f"Budget exceeded for user {user_id}: {budget_check}")
                    # Create error response with budget information
                    return LLMResponse(
                        content="",
                        model=model,
                        provider=provider,
                        usage={},
                        metadata={
                            "error": True,
                            "error_type": "budget_exceeded",
                            "budget_check": budget_check,
                            "token_info": token_info
                        }
                    )
                
                # Optimize request if needed
                user_budget = {"user_id": user_id}
                optimization = await self.token_manager.optimize_request(
                    prompt, provider, model, max_tokens, user_budget
                )
                
                if optimization.get("optimizations_applied"):
                    logger.info(f"Applied optimizations for user {user_id}: {optimization['optimization_summary']}")
                    # Use optimized parameters
                    kwargs["max_tokens"] = optimization["final_max_tokens"]
                
            except Exception as e:
                logger.warning(f"Token management failed for user {user_id}: {e}, proceeding without optimization")

        # Route to appropriate provider
        if provider == "openai" and self.providers.get("openai", {}).get("available"):
            return await self._generate_openai(prompt, model, **kwargs)
        elif provider == "anthropic" and self.providers.get("anthropic", {}).get("available"):
            return await self._generate_anthropic(prompt, model, **kwargs)
        elif provider == "google" and self.providers.get("google", {}).get("available"):
            return await self._generate_google(prompt, model, **kwargs)
        else:
            # Fallback to mock if provider not available
            return LLMResponse(
                content=f"Provider {provider} not available. Mock response for: {prompt[:50]}...",
                model=model or "mock-model",
                provider=provider or "mock",
                usage={"tokens": 100},
                metadata={"mock": True, "reason": "provider_not_available"}
            )

    async def _generate_openai(self, prompt: str, model: str, **kwargs) -> LLMResponse:
        """Generate text using OpenAI with enhanced error handling"""
        try:
            client = self.clients["openai"]
            provider_info = self.providers["openai"]
            
            # Log request details for debugging
            logger.debug(f"OpenAI request: model={model}, prompt_length={len(prompt)}, kwargs={kwargs}")
            
            response = await client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=kwargs.get("max_tokens", 1000),
                temperature=kwargs.get("temperature", 0.7),
                top_p=kwargs.get("top_p", 1.0),
                frequency_penalty=kwargs.get("frequency_penalty", 0.0),
                presence_penalty=kwargs.get("presence_penalty", 0.0),
            )
            
            # Log successful response
            logger.debug(f"OpenAI response successful: model={model}, tokens_used={response.usage.total_tokens}")
            
            return LLMResponse(
                content=response.choices[0].message.content,
                model=model,
                provider="openai",
                usage={
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens,
                },
                metadata={
                    "finish_reason": response.choices[0].finish_reason,
                    "created": response.created,
                    "api_type": provider_info.get("api_type", "openai"),
                    "organization": provider_info.get("organization"),
                    "request_id": getattr(response, "id", None),
                }
            )
            
        except Exception as e:
            # Enhanced error categorization and handling
            error_context = {
                "provider": "openai",
                "model": model,
                "prompt_length": len(prompt),
                "kwargs": kwargs,
                "timestamp": datetime.now().isoformat(),
            }
            
            # Import OpenAI exceptions for precise error handling
            try:
                import openai
                
                # Handle specific OpenAI exceptions
                if isinstance(e, openai.AuthenticationError):
                    logger.error(f"OpenAI authentication error: {e}", extra=error_context)
                    return self._create_error_response(
                        "authentication_error",
                        "Invalid API key or authentication credentials. Please check your OpenAI API configuration.",
                        model,
                        error_context,
                        is_retryable=False,
                        suggested_action="Verify your OpenAI API key and organization ID in settings."
                    )
                    
                elif isinstance(e, openai.PermissionDeniedError):
                    logger.error(f"OpenAI permission denied: {e}", extra=error_context)
                    return self._create_error_response(
                        "permission_denied",
                        "Access denied to the requested model or endpoint. Check your plan and billing status.",
                        model,
                        error_context,
                        is_retryable=False,
                        suggested_action="Upgrade your OpenAI plan or check billing status."
                    )
                    
                elif isinstance(e, openai.RateLimitError):
                    logger.warning(f"OpenAI rate limit exceeded: {e}", extra=error_context)
                    return self._create_error_response(
                        "rate_limit_exceeded",
                        "Rate limit exceeded. Please wait before making more requests.",
                        model,
                        error_context,
                        is_retryable=True,
                        suggested_action="Wait 60 seconds before retrying, or upgrade your plan for higher limits."
                    )
                    
                elif isinstance(e, openai.BadRequestError):
                    logger.error(f"OpenAI bad request: {e}", extra=error_context)
                    return self._create_error_response(
                        "invalid_request",
                        "Invalid request parameters. Check your model selection and request format.",
                        model,
                        error_context,
                        is_retryable=False,
                        suggested_action="Review the request parameters and ensure the model is available."
                    )
                    
                elif isinstance(e, openai.NotFoundError):
                    logger.error(f"OpenAI model/endpoint not found: {e}", extra=error_context)
                    return self._create_error_response(
                        "model_not_found",
                        f"Model '{model}' not found or not accessible with your current plan.",
                        model,
                        error_context,
                        is_retryable=False,
                        suggested_action=f"Use a different model or verify '{model}' is available in your plan."
                    )
                    
                elif isinstance(e, openai.ConflictError):
                    logger.error(f"OpenAI conflict error: {e}", extra=error_context)
                    return self._create_error_response(
                        "conflict_error",
                        "Request conflicts with current state. Please retry or modify your request.",
                        model,
                        error_context,
                        is_retryable=True,
                        suggested_action="Wait a moment and retry, or modify your request parameters."
                    )
                    
                elif isinstance(e, openai.UnprocessableEntityError):
                    logger.error(f"OpenAI unprocessable entity: {e}", extra=error_context)
                    return self._create_error_response(
                        "unprocessable_entity",
                        "Request format is correct but contains invalid parameters or data.",
                        model,
                        error_context,
                        is_retryable=False,
                        suggested_action="Check your input parameters and ensure they meet OpenAI's requirements."
                    )
                    
                elif isinstance(e, openai.InternalServerError):
                    logger.error(f"OpenAI internal server error: {e}", extra=error_context)
                    return self._create_error_response(
                        "internal_server_error",
                        "OpenAI service is temporarily unavailable. Please try again later.",
                        model,
                        error_context,
                        is_retryable=True,
                        suggested_action="Wait a few minutes and retry your request."
                    )
                    
                elif isinstance(e, openai.APITimeoutError):
                    logger.warning(f"OpenAI timeout error: {e}", extra=error_context)
                    return self._create_error_response(
                        "timeout_error",
                        "Request timed out. The model may be overloaded or your request too complex.",
                        model,
                        error_context,
                        is_retryable=True,
                        suggested_action="Retry with a shorter prompt or try again later."
                    )
                    
                elif isinstance(e, openai.APIConnectionError):
                    logger.warning(f"OpenAI connection error: {e}", extra=error_context)
                    return self._create_error_response(
                        "connection_error",
                        "Unable to connect to OpenAI servers. Check your internet connection.",
                        model,
                        error_context,
                        is_retryable=True,
                        suggested_action="Check your internet connection and retry."
                    )
                    
                elif isinstance(e, openai.APIStatusError):
                    logger.error(f"OpenAI API status error: {e}", extra=error_context)
                    return self._create_error_response(
                        "api_status_error",
                        f"OpenAI API returned status {getattr(e, 'status_code', 'unknown')}: {str(e)}",
                        model,
                        error_context,
                        is_retryable=False,
                        suggested_action="Check OpenAI status page or contact support if the issue persists."
                    )
                    
            except ImportError:
                logger.warning("OpenAI library not available for precise error handling")
            
            # Fallback for unhandled exceptions or when OpenAI library is not available
            error_message = str(e)
            
            # General error categorization based on error message
            if any(term in error_message.lower() for term in ["authentication", "unauthorized", "api key"]):
                error_type = "authentication_error"
                user_message = "Authentication failed. Please check your API key configuration."
                is_retryable = False
                suggested_action = "Verify your OpenAI API key in settings."
            elif any(term in error_message.lower() for term in ["rate limit", "too many requests"]):
                error_type = "rate_limit_exceeded"
                user_message = "Too many requests. Please wait before trying again."
                is_retryable = True
                suggested_action = "Wait 60 seconds before retrying."
            elif any(term in error_message.lower() for term in ["quota", "billing", "insufficient"]):
                error_type = "quota_exceeded"
                user_message = "Quota exceeded or billing issue. Check your OpenAI account."
                is_retryable = False
                suggested_action = "Check your OpenAI billing and usage quotas."
            elif any(term in error_message.lower() for term in ["timeout", "timed out"]):
                error_type = "timeout_error"
                user_message = "Request timed out. Please try again."
                is_retryable = True
                suggested_action = "Retry with a shorter prompt or try again later."
            elif any(term in error_message.lower() for term in ["connection", "network"]):
                error_type = "connection_error"
                user_message = "Network connection failed. Check your internet connection."
                is_retryable = True
                suggested_action = "Check your internet connection and retry."
            elif any(term in error_message.lower() for term in ["model", "not found"]):
                error_type = "model_not_found"
                user_message = f"Model '{model}' is not available or accessible."
                is_retryable = False
                suggested_action = "Choose a different model or check your access permissions."
            else:
                error_type = "unknown_error"
                user_message = "An unexpected error occurred while processing your request."
                is_retryable = False
                suggested_action = "Please try again or contact support if the issue persists."
            
            logger.error(f"OpenAI error ({error_type}): {error_message}", extra=error_context)
            
            return self._create_error_response(
                error_type,
                user_message,
                model,
                error_context,
                is_retryable,
                suggested_action
            )
    
    def _create_error_response(
        self, 
        error_type: str, 
        user_message: str, 
        model: str, 
        context: dict, 
        is_retryable: bool,
        suggested_action: str
    ) -> LLMResponse:
        """Create a standardized error response"""
        return LLMResponse(
            content=f"Error: {user_message}",
            model=model,
            provider="openai",
            usage={"tokens": 0},
            metadata={
                "error": True,
                "error_type": error_type,
                "error_message": user_message,
                "is_retryable": is_retryable,
                "suggested_action": suggested_action,
                "context": context,
                "fallback_available": True
            }
        )

    async def _generate_anthropic(self, prompt: str, model: str, **kwargs) -> LLMResponse:
        """Generate text using Anthropic Claude"""
        try:
            client = self.clients["anthropic"]
            
            response = await client.messages.create(
                model=model,
                max_tokens=kwargs.get("max_tokens", 1000),
                temperature=kwargs.get("temperature", 0.7),
                messages=[{"role": "user", "content": prompt}]
            )
            
            return LLMResponse(
                content=response.content[0].text,
                model=model,
                provider="anthropic",
                usage={
                    "prompt_tokens": response.usage.input_tokens,
                    "completion_tokens": response.usage.output_tokens,
                    "total_tokens": response.usage.input_tokens + response.usage.output_tokens,
                },
                metadata={
                    "stop_reason": response.stop_reason,
                }
            )
        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            raise Exception(f"Anthropic API error: {str(e)}")

    async def _generate_google(self, prompt: str, model: str, **kwargs) -> LLMResponse:
        """Generate text using Google Gemini"""
        try:
            model_obj = genai.GenerativeModel(model)
            
            generation_config = genai.types.GenerationConfig(
                temperature=kwargs.get("temperature", 0.7),
                top_p=kwargs.get("top_p", 0.95),
                top_k=kwargs.get("top_k", 40),
                max_output_tokens=kwargs.get("max_tokens", 1000),
            )
            
            response = await model_obj.generate_content_async(
                prompt,
                generation_config=generation_config
            )
            
            return LLMResponse(
                content=response.text,
                model=model,
                provider="google",
                usage={
                    "prompt_tokens": response.usage_metadata.prompt_token_count if hasattr(response, 'usage_metadata') else 0,
                    "completion_tokens": response.usage_metadata.candidates_token_count if hasattr(response, 'usage_metadata') else 0,
                    "total_tokens": response.usage_metadata.total_token_count if hasattr(response, 'usage_metadata') else 0,
                },
                metadata={
                    "finish_reason": response.candidates[0].finish_reason.name if response.candidates else "stop",
                }
            )
        except Exception as e:
            logger.error(f"Google API error: {e}")
            raise Exception(f"Google API error: {str(e)}")

    def _get_default_model(self, provider: str) -> str:
        """Get default model for provider"""
        defaults = {
            "openai": "gpt-4o",
            "anthropic": "claude-3-sonnet-20240229",
            "google": "gemini-1.5-pro",
        }
        return defaults.get(provider, "gpt-4o")

    async def chat_completion(
        self,
        messages: list[dict[str, str]],
        model: str | None = None,
        provider: str | None = None,
        **kwargs,
    ) -> LLMResponse:
        """
        Chat completion using the specified LLM

        Args:
            messages: Lista de mensagens do chat
            model: Modelo específico (opcional)
            provider: Provedor específico (opcional)
            **kwargs: Parâmetros adicionais

        Returns:
            LLMResponse: Resposta do LLM
        """
        # Convert messages to a single prompt for providers that don't support chat format
        if messages:
            prompt = "\n".join([f"{msg.get('role', 'user')}: {msg.get('content', '')}" for msg in messages])
        else:
            prompt = ""

        return await self.generate_text(prompt, model, provider, **kwargs)

    def get_available_models(self, provider: str | None = None) -> list[str]:
        """
        Retorna lista de modelos disponíveis

        Args:
            provider: Provedor específico (opcional)

        Returns:
            List[str]: Lista de modelos disponíveis
        """
        if provider and provider in self.providers:
            return self.providers[provider].get("models", [])
        
        # Return all available models
        all_models = []
        for prov_info in self.providers.values():
            if prov_info.get("available"):
                all_models.extend(prov_info.get("models", []))
        
        return all_models

    def get_available_providers(self) -> dict[str, Any]:
        """
        Retorna lista de provedores disponíveis

        Returns:
            Dict[str, Any]: Informações dos provedores
        """
        providers_info = []
        
        for provider_id, info in self.providers.items():
            if info.get("available"):
                providers_info.append({
                    "id": provider_id,
                    "name": info.get("name", provider_id.title()),
                    "description": f"Provedor {info.get('name', provider_id)} com modelos de linguagem",
                    "models_count": len(info.get("models", [])),
                    "status": "operational",
                    "documentation_url": self._get_provider_docs(provider_id),
                })

        return {
            "providers": providers_info,
            "count": len(providers_info),
        }

    def _get_provider_docs(self, provider: str) -> str:
        """Get documentation URL for provider"""
        docs = {
            "openai": "https://platform.openai.com/docs",
            "anthropic": "https://docs.anthropic.com",
            "google": "https://ai.google.dev/docs",
        }
        return docs.get(provider)

    async def health_check(self, provider: str | None = None) -> dict[str, Any]:
        """
        Verifica a saúde dos provedores de LLM

        Args:
            provider: Provedor específico (opcional)

        Returns:
            Dict[str, Any]: Status de saúde
        """
        if provider:
            if provider in self.providers:
                return {
                    "status": "healthy" if self.providers[provider].get("available") else "unhealthy",
                    "provider": provider,
                    "available": self.providers[provider].get("available", False),
                    "models": self.providers[provider].get("models", []),
                }
            else:
                return {"status": "not_found", "provider": provider}
        
        # Overall health check
        available_providers = sum(1 for p in self.providers.values() if p.get("available"))
        total_providers = len(self.providers)
        
        return {
            "status": "healthy" if available_providers > 0 else "unhealthy",
            "providers_available": available_providers,
            "providers_total": total_providers,
            "providers": {
                provider_id: {
                    "available": info.get("available", False),
                    "models": info.get("models", []),
                }
                for provider_id, info in self.providers.items()
            },
        }

    async def count_tokens(
        self, text: str, provider: str | None = None, model: str | None = None
    ) -> dict[str, Any]:
        """
        Conta o número de tokens em um texto

        Args:
            text: Texto para contar tokens
            provider: Provedor específico (opcional)
            model: Modelo específico (opcional)

        Returns:
            Dict[str, Any]: Informações sobre contagem de tokens
        """
        # For now, use simple estimation
        # In production, could use tiktoken for OpenAI or provider-specific tokenizers
        
        # Estimativa básica: ~4 caracteres por token (média para inglês)
        estimated_tokens = max(1, len(text) // 4)

        # Contagem mais precisa por palavras
        words = len(text.split())
        word_based_tokens = max(1, int(words * 1.3))  # ~1.3 tokens por palavra

        # Usar a maior estimativa para ser conservador
        token_count = max(estimated_tokens, word_based_tokens)

        return {
            "text": text[:100] + "..." if len(text) > 100 else text,
            "token_count": token_count,
            "character_count": len(text),
            "word_count": words,
            "provider": provider or "default",
            "model": model or "default",
            "estimation_method": "character_and_word_based",
            "note": "Estimation based on character and word count. For precise count, use provider-specific tokenizers.",
        }

    async def list_models(self, provider: str | None = None):
        """
        Lista todos os modelos disponíveis, agrupados por provedor.
        """
        # Import here to avoid circular imports
        from synapse.api.v1.endpoints.llm.schemas import ListModelsResponse, ModelInfo
        
        # Real models data based on initialized providers
        all_models = {}
        
        for provider_id, info in self.providers.items():
            if info.get("available"):
                models_list = []
                for model_id in info.get("models", []):
                    # Create proper ModelInfo objects
                    model_info = ModelInfo(
                        id=model_id,
                        name=self._get_model_display_name(model_id),
                        provider=provider_id,
                        capabilities=self._get_model_capabilities(model_id),
                        context_window=self._get_model_context_window(model_id),
                        status="available"
                    )
                    models_list.append(model_info)
                
                if models_list:
                    all_models[provider_id] = models_list

        # Filter by provider if requested
        if provider and provider in all_models:
            models = {provider: all_models[provider]}
        else:
            models = all_models

        count = sum(len(m) for m in models.values())
        
        return ListModelsResponse(models=models, count=count)

    def _get_model_display_name(self, model_id: str) -> str:
        """Get display name for model"""
        names = {
            "gpt-4o": "GPT-4o",
            "gpt-4-turbo": "GPT-4 Turbo",
            "gpt-3.5-turbo": "GPT-3.5 Turbo",
            "claude-3-opus-20240229": "Claude 3 Opus",
            "claude-3-sonnet-20240229": "Claude 3 Sonnet",
            "claude-3-haiku-20240307": "Claude 3 Haiku",
            "gemini-1.5-pro": "Gemini 1.5 Pro",
            "gemini-1.5-flash": "Gemini 1.5 Flash",
            "gemini-1.0-pro": "Gemini 1.0 Pro",
        }
        return names.get(model_id, model_id.title())

    def _get_model_capabilities(self, model_id: str) -> list:
        """Get capabilities for model"""
        from synapse.api.v1.endpoints.llm.schemas import ModelCapability
        
        capabilities = {
            "gpt-4o": [ModelCapability.text, ModelCapability.vision, ModelCapability.function_calling],
            "gpt-4-turbo": [ModelCapability.text, ModelCapability.vision],
            "gpt-3.5-turbo": [ModelCapability.text],
            "claude-3-opus-20240229": [ModelCapability.text, ModelCapability.vision, ModelCapability.reasoning],
            "claude-3-sonnet-20240229": [ModelCapability.text, ModelCapability.vision, ModelCapability.reasoning],
            "claude-3-haiku-20240307": [ModelCapability.text, ModelCapability.reasoning],
            "gemini-1.5-pro": [ModelCapability.text, ModelCapability.vision, ModelCapability.code],
            "gemini-1.5-flash": [ModelCapability.text, ModelCapability.vision, ModelCapability.code],
            "gemini-1.0-pro": [ModelCapability.text],
        }
        return capabilities.get(model_id, [ModelCapability.text])

    def _get_model_context_window(self, model_id: str) -> int:
        """Get context window for model"""
        contexts = {
            "gpt-4o": 128000,
            "gpt-4-turbo": 128000,
            "gpt-3.5-turbo": 16385,
            "claude-3-opus-20240229": 200000,
            "claude-3-sonnet-20240229": 200000,
            "claude-3-haiku-20240307": 200000,
            "gemini-1.5-pro": 2097152,
            "gemini-1.5-flash": 1048576,
            "gemini-1.0-pro": 30720,
        }
        return contexts.get(model_id, 4096)


# Create global instance
real_llm_service = RealLLMService() 