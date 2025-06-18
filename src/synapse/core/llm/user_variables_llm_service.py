"""
Serviço LLM que usa a tabela user_variables existente para API keys
Reutiliza a infraestrutura já existente de variáveis de usuário
"""

from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session

from synapse.core.llm.real_llm_service import RealLLMService, LLMResponse
from synapse.models.user_variable import UserVariable
from synapse.logger_config import get_logger

logger = get_logger(__name__)


class UserVariablesLLMService(RealLLMService):
    """
    Extensão do RealLLMService que usa user_variables para API keys específicas de usuários
    """
    
    def __init__(self):
        super().__init__()
    
    def get_user_api_key(self, db: Session, user_id: str, provider: str) -> Optional[str]:
        """
        Obtém a API key específica do usuário a partir da tabela user_variables
        
        Args:
            db: Sessão do banco de dados
            user_id: ID do usuário
            provider: Nome do provedor (openai, anthropic, google, etc.)
            
        Returns:
            str | None: API key descriptografada ou None se não encontrada
        """
        try:
            # Mapear provedor para nome da chave de variável
            provider_key_mapping = {
                "openai": "OPENAI_API_KEY",
                "anthropic": "ANTHROPIC_API_KEY",
                "claude": "ANTHROPIC_API_KEY",  # Alias
                "google": "GOOGLE_API_KEY",
                "gemini": "GOOGLE_API_KEY",  # Alias
                "grok": "GROK_API_KEY",
                "deepseek": "DEEPSEEK_API_KEY",
                "llama": "LLAMA_API_KEY",
            }
            
            key_name = provider_key_mapping.get(provider.lower())
            if not key_name:
                logger.warning(f"Provedor {provider} não suportado")
                return None
            
            # Buscar a variável do usuário na categoria 'api_keys'
            user_variable = db.query(UserVariable).filter(
                UserVariable.user_id == user_id,
                UserVariable.key == key_name,
                UserVariable.category == "api_keys",
                UserVariable.is_active == True
            ).first()
            
            if user_variable:
                return user_variable.get_decrypted_value()
            
            return None
            
        except Exception as e:
            logger.error(f"Erro ao obter API key do usuário {user_id} para {provider}: {e}")
            return None
    
    def create_or_update_user_api_key(
        self, 
        db: Session, 
        user_id: str, 
        provider: str, 
        api_key: str
    ) -> bool:
        """
        Cria ou atualiza uma API key do usuário usando user_variables
        
        Args:
            db: Sessão do banco de dados
            user_id: ID do usuário
            provider: Nome do provedor
            api_key: Chave da API
            
        Returns:
            bool: True se sucesso
        """
        try:
            # Mapear provedor para nome da chave
            provider_key_mapping = {
                "openai": "OPENAI_API_KEY",
                "anthropic": "ANTHROPIC_API_KEY",
                "google": "GOOGLE_API_KEY",
                "grok": "GROK_API_KEY",
                "deepseek": "DEEPSEEK_API_KEY",
                "llama": "LLAMA_API_KEY",
            }
            
            key_name = provider_key_mapping.get(provider.lower())
            if not key_name:
                return False
            
            # Verificar se já existe
            existing_variable = db.query(UserVariable).filter(
                UserVariable.user_id == user_id,
                UserVariable.key == key_name,
                UserVariable.category == "api_keys"
            ).first()
            
            if existing_variable:
                # Atualizar existente
                existing_variable.set_encrypted_value(api_key)
                existing_variable.is_active = True
                db.commit()
                logger.info(f"API key {provider} atualizada para usuário {user_id}")
            else:
                # Criar nova
                new_variable = UserVariable.create_variable(
                    user_id=user_id,
                    key=key_name,
                    value=api_key,
                    category="api_keys",
                    description=f"Chave da API {provider.title()}",
                    is_encrypted=True
                )
                db.add(new_variable)
                db.commit()
                logger.info(f"API key {provider} criada para usuário {user_id}")
            
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"Erro ao criar/atualizar API key para usuário {user_id}: {e}")
            return False
    
    def list_user_api_keys(self, db: Session, user_id: str) -> List[Dict[str, Any]]:
        """
        Lista todas as API keys configuradas pelo usuário
        
        Args:
            db: Sessão do banco de dados
            user_id: ID do usuário
            
        Returns:
            List[Dict]: Lista de API keys (com valores mascarados)
        """
        try:
            api_keys = db.query(UserVariable).filter(
                UserVariable.user_id == user_id,
                UserVariable.category == "api_keys"
            ).all()
            
            result = []
            for key in api_keys:
                # Mascarar a chave para segurança
                decrypted_value = key.get_decrypted_value()
                masked_value = f"****{decrypted_value[-4:] if len(decrypted_value) >= 4 else '****'}"
                
                # Mapear de volta para o nome do provedor
                provider_mapping = {
                    "OPENAI_API_KEY": "openai",
                    "ANTHROPIC_API_KEY": "anthropic",
                    "GOOGLE_API_KEY": "google",
                    "GROK_API_KEY": "grok",
                    "DEEPSEEK_API_KEY": "deepseek",
                    "LLAMA_API_KEY": "llama",
                }
                
                provider_name = provider_mapping.get(key.key, key.key.lower())
                
                result.append({
                    "id": str(key.id),
                    "provider_name": provider_name,
                    "key_name": key.key,
                    "masked_value": masked_value,
                    "is_active": key.is_active,
                    "description": key.description,
                    "created_at": key.created_at.isoformat() if key.created_at else None,
                    "updated_at": key.updated_at.isoformat() if key.updated_at else None
                })
            
            return result
            
        except Exception as e:
            logger.error(f"Erro ao listar API keys do usuário {user_id}: {e}")
            return []
    
    def delete_user_api_key(self, db: Session, user_id: str, provider: str) -> bool:
        """
        Remove uma API key do usuário
        
        Args:
            db: Sessão do banco de dados
            user_id: ID do usuário
            provider: Nome do provedor
            
        Returns:
            bool: True se removido com sucesso
        """
        try:
            provider_key_mapping = {
                "openai": "OPENAI_API_KEY",
                "anthropic": "ANTHROPIC_API_KEY",
                "google": "GOOGLE_API_KEY",
                "grok": "GROK_API_KEY",
                "deepseek": "DEEPSEEK_API_KEY",
                "llama": "LLAMA_API_KEY",
            }
            
            key_name = provider_key_mapping.get(provider.lower())
            if not key_name:
                return False
            
            api_key = db.query(UserVariable).filter(
                UserVariable.user_id == user_id,
                UserVariable.key == key_name,
                UserVariable.category == "api_keys"
            ).first()
            
            if api_key:
                db.delete(api_key)
                db.commit()
                logger.info(f"API key {provider} removida para usuário {user_id}")
                return True
            
            return False
            
        except Exception as e:
            db.rollback()
            logger.error(f"Erro ao remover API key para usuário {user_id}: {e}")
            return False
    
    async def generate_text_for_user(
        self,
        prompt: str,
        user_id: str,
        db: Session,
        model: str | None = None,
        provider: str | None = None,
        **kwargs,
    ) -> LLMResponse:
        """
        Gera texto usando API key específica do usuário (se disponível)
        Fallback para API keys globais se necessário
        """
        # Determinar provedor padrão se não especificado
        if not provider:
            provider = getattr(self.settings, 'LLM_DEFAULT_PROVIDER', 'openai')
        
        # Tentar obter API key específica do usuário
        user_api_key = self.get_user_api_key(db, user_id, provider)
        
        if user_api_key:
            logger.info(f"Usando API key específica do usuário {user_id} para {provider}")
            
            # Usar API key do usuário temporariamente
            return await self._generate_with_custom_key(
                prompt, provider, model, user_api_key, **kwargs
            )
        else:
            logger.info(f"Usando API key global para usuário {user_id} (provider: {provider})")
            
            # Fallback para API keys globais
            return await self.generate_text(prompt, model, provider, **kwargs)
    
    async def chat_completion_for_user(
        self,
        messages: list[dict[str, str]],
        user_id: str,
        db: Session,
        model: str | None = None,
        provider: str | None = None,
        **kwargs,
    ) -> LLMResponse:
        """
        Chat completion usando API key específica do usuário
        """
        # Determinar provedor padrão se não especificado
        if not provider:
            provider = getattr(self.settings, 'LLM_DEFAULT_PROVIDER', 'openai')
        
        # Tentar obter API key específica do usuário
        user_api_key = self.get_user_api_key(db, user_id, provider)
        
        if user_api_key:
            logger.info(f"Chat usando API key específica do usuário {user_id} para {provider}")
            
            # Usar API key do usuário temporariamente
            return await self._chat_with_custom_key(
                messages, provider, model, user_api_key, **kwargs
            )
        else:
            logger.info(f"Chat usando API key global para usuário {user_id} (provider: {provider})")
            
            # Fallback para API keys globais
            return await self.chat_completion(messages, model, provider, **kwargs)
    
    # Métodos auxiliares (mesmos da implementação anterior)
    async def _generate_with_custom_key(self, prompt: str, provider: str, model: str | None, api_key: str, **kwargs) -> LLMResponse:
        """Gera texto usando uma API key específica"""
        if not model:
            model = self._get_default_model(provider)
        
        try:
            if provider == "openai":
                return await self._generate_openai_with_key(prompt, model, api_key, **kwargs)
            elif provider == "anthropic":
                return await self._generate_anthropic_with_key(prompt, model, api_key, **kwargs)
            elif provider == "google":
                return await self._generate_google_with_key(prompt, model, api_key, **kwargs)
            else:
                # Fallback para mock se provedor não suportado
                return LLMResponse(
                    content=f"Provider {provider} not supported for user API keys. Mock response for: {prompt[:50]}...",
                    model=model or "mock-model",
                    provider=provider,
                    usage={"tokens": 100},
                    metadata={"mock": True, "reason": "provider_not_supported"}
                )
        except Exception as e:
            logger.error(f"Erro ao gerar texto com API key customizada ({provider}): {e}")
            raise Exception(f"Erro na geração de texto: {str(e)}")
    
    async def _chat_with_custom_key(self, messages: list, provider: str, model: str | None, api_key: str, **kwargs) -> LLMResponse:
        """Chat completion usando uma API key específica"""
        if not model:
            model = self._get_default_model(provider)
        
        try:
            if provider == "openai":
                return await self._chat_openai_with_key(messages, model, api_key, **kwargs)
            elif provider == "anthropic":
                return await self._chat_anthropic_with_key(messages, model, api_key, **kwargs)
            elif provider == "google":
                return await self._chat_google_with_key(messages, model, api_key, **kwargs)
            else:
                # Fallback para mock
                last_message = messages[-1] if messages else {"content": ""}
                return LLMResponse(
                    content=f"Provider {provider} not supported for user API keys. Mock response for: {last_message.get('content', '')[:50]}...",
                    model=model or "mock-model",
                    provider=provider,
                    usage={"tokens": 100},
                    metadata={"mock": True, "reason": "provider_not_supported"}
                )
        except Exception as e:
            logger.error(f"Erro no chat com API key customizada ({provider}): {e}")
            raise Exception(f"Erro no chat: {str(e)}")
    
    async def _generate_openai_with_key(self, prompt: str, model: str, api_key: str, **kwargs) -> LLMResponse:
        """Gera texto usando OpenAI com API key específica"""
        try:
            from openai import AsyncOpenAI
            
            client = AsyncOpenAI(api_key=api_key)
            
            response = await client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=kwargs.get("max_tokens", 1000),
                temperature=kwargs.get("temperature", 0.7),
                top_p=kwargs.get("top_p", 1.0),
                frequency_penalty=kwargs.get("frequency_penalty", 0.0),
                presence_penalty=kwargs.get("presence_penalty", 0.0),
            )
            
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
                    "user_api_key": True,
                }
            )
        except Exception as e:
            logger.error(f"OpenAI API error with user key: {e}")
            raise Exception(f"OpenAI API error: {str(e)}")
    
    async def _chat_openai_with_key(self, messages: list, model: str, api_key: str, **kwargs) -> LLMResponse:
        """Chat completion usando OpenAI com API key específica"""
        try:
            from openai import AsyncOpenAI
            
            client = AsyncOpenAI(api_key=api_key)
            
            response = await client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=kwargs.get("max_tokens", 1000),
                temperature=kwargs.get("temperature", 0.7),
                top_p=kwargs.get("top_p", 1.0),
                frequency_penalty=kwargs.get("frequency_penalty", 0.0),
                presence_penalty=kwargs.get("presence_penalty", 0.0),
            )
            
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
                    "user_api_key": True,
                }
            )
        except Exception as e:
            logger.error(f"OpenAI chat error with user key: {e}")
            raise Exception(f"OpenAI chat error: {str(e)}")
    
    async def _generate_anthropic_with_key(self, prompt: str, model: str, api_key: str, **kwargs) -> LLMResponse:
        """Placeholder para implementação Anthropic com API key específica"""
        return LLMResponse(
            content=f"[Anthropic] {prompt[:50]}... (implementação pendente)",
            model=model,
            provider="anthropic",
            usage={"tokens": 100},
            metadata={"user_api_key": True, "pending_implementation": True}
        )
    
    async def _chat_anthropic_with_key(self, messages: list, model: str, api_key: str, **kwargs) -> LLMResponse:
        """Placeholder para chat Anthropic com API key específica"""
        last_message = messages[-1] if messages else {"content": ""}
        return LLMResponse(
            content=f"[Anthropic Chat] {last_message.get('content', '')[:50]}... (implementação pendente)",
            model=model,
            provider="anthropic",
            usage={"tokens": 100},
            metadata={"user_api_key": True, "pending_implementation": True}
        )
    
    async def _generate_google_with_key(self, prompt: str, model: str, api_key: str, **kwargs) -> LLMResponse:
        """Placeholder para implementação Google com API key específica"""
        return LLMResponse(
            content=f"[Google] {prompt[:50]}... (implementação pendente)",
            model=model,
            provider="google",
            usage={"tokens": 100},
            metadata={"user_api_key": True, "pending_implementation": True}
        )
    
    async def _chat_google_with_key(self, messages: list, model: str, api_key: str, **kwargs) -> LLMResponse:
        """Placeholder para chat Google com API key específica"""
        last_message = messages[-1] if messages else {"content": ""}
        return LLMResponse(
            content=f"[Google Chat] {last_message.get('content', '')[:50]}... (implementação pendente)",
            model=model,
            provider="google",
            usage={"tokens": 100},
            metadata={"user_api_key": True, "pending_implementation": True}
        )


# Instância global do serviço
user_variables_llm_service = UserVariablesLLMService() 