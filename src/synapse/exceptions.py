"""Exceções personalizadas para o backend SynapScale.

Este módulo contém exceções personalizadas utilizadas em todo o sistema,
permitindo tratamento específico para diferentes tipos de erros.
"""

from fastapi import HTTPException, status


class SynapseBaseException(Exception):
    """Exceção base para todas as exceções personalizadas do SynapScale.

    Args:
        message (str): Mensagem de erro amigável para o usuário.
        error_code (str, opcional): Código de erro único para rastreamento e padronização (ex: 'AUTH_001').
        details (Any, opcional): Detalhes adicionais para debug ou contexto (ex: dict, str, etc).
    """

    def __init__(
        self, message: str = "Erro interno", error_code: str = None, details=None
    ):
        self.message = message
        self.error_code = error_code
        self.details = details
        super().__init__(self.message)


class ServiceError(SynapseBaseException):
    """Exceção lançada quando ocorre um erro na camada de serviços."""

    def __init__(
        self,
        message: str = "Erro na camada de serviços",
        error_code: str = None,
        details=None,
    ):
        """Inicializa a exceção com uma mensagem.

        Args:
            message: Mensagem de erro
            error_code: Código de erro único para rastreamento e padronização
            details: Detalhes adicionais para debug ou contexto
        """
        super().__init__(message, error_code, details)


class FileValidationError(SynapseBaseException):
    """Exceção lançada quando um arquivo não passa nas validações."""

    def __init__(
        self,
        message: str = "O arquivo não passou nas validações",
        error_code: str = None,
        details=None,
    ):
        """Inicializa a exceção com uma mensagem.

        Args:
            message: Mensagem de erro
            error_code: Código de erro único para rastreamento e padronização
            details: Detalhes adicionais para debug ou contexto
        """
        super().__init__(message, error_code, details)


class StorageError(SynapseBaseException):
    """Exceção lançada quando ocorre um erro no armazenamento."""

    def __init__(
        self,
        message: str = "Erro ao armazenar ou recuperar arquivo",
        error_code: str = None,
        details=None,
    ):
        """Inicializa a exceção com uma mensagem.

        Args:
            message: Mensagem de erro
            error_code: Código de erro único para rastreamento e padronização
            details: Detalhes adicionais para debug ou contexto
        """
        super().__init__(message, error_code, details)


class DatabaseError(SynapseBaseException):
    """Exceção lançada quando ocorre um erro no banco de dados."""

    def __init__(
        self,
        message: str = "Erro no banco de dados",
        error_code: str = None,
        details=None,
    ):
        """Inicializa a exceção com uma mensagem.

        Args:
            message: Mensagem de erro
            error_code: Código de erro único para rastreamento e padronização
            details: Detalhes adicionais para debug ou contexto
        """
        super().__init__(message, error_code, details)


class AuthenticationError(SynapseBaseException):
    """Exceção lançada quando ocorre um erro de autenticação."""

    def __init__(
        self,
        message: str = "Erro de autenticação",
        error_code: str = None,
        details=None,
    ):
        """Inicializa a exceção com uma mensagem.

        Args:
            message: Mensagem de erro
            error_code: Código de erro único para rastreamento e padronização
            details: Detalhes adicionais para debug ou contexto
        """
        super().__init__(message, error_code, details)


class AuthorizationError(SynapseBaseException):
    """Exceção lançada quando ocorre um erro de autorização."""

    def __init__(
        self, message: str = "Permissão negada", error_code: str = None, details=None
    ):
        """Inicializa a exceção com uma mensagem.

        Args:
            message: Mensagem de erro
            error_code: Código de erro único para rastreamento e padronização
            details: Detalhes adicionais para debug ou contexto
        """
        super().__init__(message, error_code, details)


class RateLimitError(SynapseBaseException):
    """Exceção lançada quando o limite de taxa é excedido."""

    def __init__(
        self,
        message: str = "Limite de requisições excedido",
        error_code: str = None,
        details=None,
    ):
        """Inicializa a exceção com uma mensagem.

        Args:
            message: Mensagem de erro
            error_code: Código de erro único para rastreamento e padronização
            details: Detalhes adicionais para debug ou contexto
        """
        super().__init__(message, error_code, details)


class NotFoundError(SynapseBaseException):
    """Exceção lançada quando um recurso não é encontrado."""

    def __init__(
        self,
        message: str = "Recurso não encontrado",
        error_code: str = None,
        details=None,
    ):
        """Inicializa a exceção com uma mensagem.

        Args:
            message: Mensagem de erro
            error_code: Código de erro único para rastreamento e padronização
            details: Detalhes adicionais para debug ou contexto
        """
        super().__init__(message, error_code, details)


class ValidationError(SynapseBaseException):
    """Exceção lançada quando ocorre um erro de validação."""

    def __init__(
        self, message: str = "Erro de validação", error_code: str = None, details=None
    ):
        """Inicializa a exceção com uma mensagem.

        Args:
            message: Mensagem de erro
            error_code: Código de erro único para rastreamento e padronização
            details: Detalhes adicionais para debug ou contexto
        """
        super().__init__(message, error_code, details)


class WorkspaceError(SynapseBaseException):
    """Exceção lançada quando ocorre um erro específico de workspace."""

    def __init__(
        self, message: str = "Erro no workspace", error_code: str = None, details=None
    ):
        """Inicializa a exceção com uma mensagem.

        Args:
            message: Mensagem de erro
            error_code: Código de erro único para rastreamento e padronização
            details: Detalhes adicionais para debug ou contexto
        """
        super().__init__(message, error_code, details)


class ProjectError(SynapseBaseException):
    """Exceção lançada quando ocorre um erro específico de projeto."""

    def __init__(
        self, message: str = "Erro no projeto", error_code: str = None, details=None
    ):
        """Inicializa a exceção com uma mensagem.

        Args:
            message: Mensagem de erro
            error_code: Código de erro único para rastreamento e padronização
            details: Detalhes adicionais para debug ou contexto
        """
        super().__init__(message, error_code, details)


class AnalyticsError(SynapseBaseException):
    """Exceção lançada quando ocorre um erro específico de analytics."""

    def __init__(
        self,
        message: str = "Erro no sistema de analytics",
        error_code: str = None,
        details=None,
    ):
        """Inicializa a exceção com uma mensagem.

        Args:
            message: Mensagem de erro
            error_code: Código de erro único para rastreamento e padronização
            details: Detalhes adicionais para debug ou contexto
        """
        super().__init__(message, error_code, details)


class ConversationError(SynapseBaseException):
    """Exceção lançada quando ocorre um erro específico de conversação."""

    def __init__(
        self, message: str = "Erro na conversação", error_code: str = None, details=None
    ):
        """Inicializa a exceção com uma mensagem.

        Args:
            message: Mensagem de erro
            error_code: Código de erro único para rastreamento e padronização
            details: Detalhes adicionais para debug ou contexto
        """
        super().__init__(message, error_code, details)


class AgentError(SynapseBaseException):
    """Exceção lançada quando ocorre um erro específico de agente."""

    def __init__(
        self, message: str = "Erro no agente", error_code: str = None, details=None
    ):
        """Inicializa a exceção com uma mensagem.

        Args:
            message: Mensagem de erro
            error_code: Código de erro único para rastreamento e padronização
            details: Detalhes adicionais para debug ou contexto
        """
        super().__init__(message, error_code, details)


class WorkflowError(SynapseBaseException):
    """Exceção lançada quando ocorre um erro específico de workflow."""

    def __init__(
        self, message: str = "Erro no workflow", error_code: str = None, details=None
    ):
        """Inicializa a exceção com uma mensagem.

        Args:
            message: Mensagem de erro
            error_code: Código de erro único para rastreamento e padronização
            details: Detalhes adicionais para debug ou contexto
        """
        super().__init__(message, error_code, details)


class LLMServiceError(SynapseBaseException):
    """Exceção lançada quando ocorre um erro específico do serviço LLM."""

    def __init__(
        self, message: str = "Erro no serviço LLM", error_code: str = None, details=None
    ):
        """Inicializa a exceção com uma mensagem.

        Args:
            message: Mensagem de erro
            error_code: Código de erro único para rastreamento e padronização
            details: Detalhes adicionais para debug ou contexto
        """
        super().__init__(message, error_code, details)


class ConfigurationError(SynapseBaseException):
    """Exceção lançada quando ocorre um erro de configuração."""

    def __init__(
        self,
        message: str = "Erro de configuração",
        error_code: str = None,
        details=None,
    ):
        """Inicializa a exceção com uma mensagem.

        Args:
            message: Mensagem de erro
            error_code: Código de erro único para rastreamento e padronização
            details: Detalhes adicionais para debug ou contexto
        """
        super().__init__(message, error_code, details)


class ServiceUnavailableError(SynapseBaseException):
    """Exceção lançada quando um serviço está indisponível."""

    def __init__(
        self,
        message: str = "Serviço indisponível",
        error_code: str = None,
        details=None,
    ):
        """Inicializa a exceção com uma mensagem.

        Args:
            message: Mensagem de erro
            error_code: Código de erro único para rastreamento e padronização
            details: Detalhes adicionais para debug ou contexto
        """
        super().__init__(message, error_code, details)


def file_validation_exception(message: str) -> HTTPException:
    """Cria uma HTTPException para erro de validação de arquivo.

    Args:
        message: Mensagem de erro

    Returns:
        HTTPException configurada
    """
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)


def storage_exception(message: str) -> HTTPException:
    """Cria uma HTTPException para erro de armazenamento.

    Args:
        message: Mensagem de erro

    Returns:
        HTTPException configurada
    """
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=message
    )


def authentication_exception(message: str) -> HTTPException:
    """Cria uma HTTPException para erro de autenticação.

    Args:
        message: Mensagem de erro

    Returns:
        HTTPException configurada
    """
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=message,
        headers={"WWW-Authenticate": "Bearer"},
    )


def authorization_exception(message: str) -> HTTPException:
    """Cria uma HTTPException para erro de autorização.

    Args:
        message: Mensagem de erro

    Returns:
        HTTPException configurada
    """
    return HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=message)


def rate_limit_exception(message: str, reset_time: int) -> HTTPException:
    """Cria uma HTTPException para erro de limite de taxa.

    Args:
        message: Mensagem de erro
        reset_time: Tempo em segundos para reset do limite

    Returns:
        HTTPException configurada
    """
    return HTTPException(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        detail=message,
        headers={"Retry-After": str(reset_time)},
    )


def not_found_exception(message: str) -> HTTPException:
    """Cria uma HTTPException para recurso não encontrado.

    Args:
        message: Mensagem de erro

    Returns:
        HTTPException configurada
    """
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=message)


def validation_exception(message: str) -> HTTPException:
    """Cria uma HTTPException para erro de validação.

    Args:
        message: Mensagem de erro

    Returns:
        HTTPException configurada
    """
    return HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=message
    )


def workspace_exception(message: str) -> HTTPException:
    """Cria uma HTTPException para erro de workspace.

    Args:
        message: Mensagem de erro

    Returns:
        HTTPException configurada
    """
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=message
    )


def project_exception(message: str) -> HTTPException:
    """Cria uma HTTPException para erro de projeto.

    Args:
        message: Mensagem de erro

    Returns:
        HTTPException configurada
    """
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=message
    )


def analytics_exception(message: str) -> HTTPException:
    """Cria uma HTTPException para erro de analytics.

    Args:
        message: Mensagem de erro

    Returns:
        HTTPException configurada
    """
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=message
    )


def conversation_exception(message: str) -> HTTPException:
    """Cria uma HTTPException para erro de conversação.

    Args:
        message: Mensagem de erro

    Returns:
        HTTPException configurada
    """
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=message
    )


def agent_exception(message: str) -> HTTPException:
    """Cria uma HTTPException para erro de agente.

    Args:
        message: Mensagem de erro

    Returns:
        HTTPException configurada
    """
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=message
    )


def workflow_exception(message: str) -> HTTPException:
    """Cria uma HTTPException para erro de workflow.

    Args:
        message: Mensagem de erro

    Returns:
        HTTPException configurada
    """
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=message
    )


def llm_service_exception(message: str) -> HTTPException:
    """Cria uma HTTPException para erro do serviço LLM.

    Args:
        message: Mensagem de erro

    Returns:
        HTTPException configurada
    """
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=message
    )


def configuration_exception(message: str) -> HTTPException:
    """Cria uma HTTPException para erro de configuração.

    Args:
        message: Mensagem de erro

    Returns:
        HTTPException configurada
    """
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=message
    )


def service_unavailable_exception(message: str) -> HTTPException:
    """Cria uma HTTPException para serviço indisponível.

    Args:
        message: Mensagem de erro

    Returns:
        HTTPException configurada
    """
    return HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=message
    )


# Aliases para compatibilidade
NotFoundException = NotFoundError
ForbiddenException = AuthorizationError
BadRequestException = ValidationError


# LLM-specific exceptions
class ModelNotFoundError(NotFoundError):
    """Exceção lançada quando um modelo LLM específico não é encontrado."""

    def __init__(
        self,
        message: str = "Modelo LLM não encontrado",
        error_code: str = "LLM_MODEL_001",
        details=None,
    ):
        """Inicializa a exceção com uma mensagem.

        Args:
            message: Mensagem de erro
            error_code: Código de erro único para rastreamento e padronização
            details: Detalhes adicionais para debug ou contexto
        """
        super().__init__(message, error_code, details)


class ProviderNotFoundError(NotFoundError):
    """Exceção lançada quando um provedor LLM específico não é encontrado."""

    def __init__(
        self,
        message: str = "Provedor LLM não encontrado",
        error_code: str = "LLM_PROVIDER_001",
        details=None,
    ):
        """Inicializa a exceção com uma mensagem.

        Args:
            message: Mensagem de erro
            error_code: Código de erro único para rastreamento e padronização
            details: Detalhes adicionais para debug ou contexto
        """
        super().__init__(message, error_code, details)


class InvalidModelProviderCombinationError(ValidationError):
    """Exceção lançada quando uma combinação modelo/provedor é inválida."""

    def __init__(
        self,
        message: str = "Combinação modelo/provedor inválida",
        error_code: str = "LLM_COMBINATION_001",
        details=None,
    ):
        """Inicializa a exceção com uma mensagem.

        Args:
            message: Mensagem de erro
            error_code: Código de erro único para rastreamento e padronização
            details: Detalhes adicionais para debug ou contexto
        """
        super().__init__(message, error_code, details)


class LLMDatabaseError(DatabaseError):
    """Exceção lançada quando ocorre um erro específico no banco de dados de LLMs."""

    def __init__(
        self,
        message: str = "Erro no banco de dados de LLMs",
        error_code: str = "LLM_DB_001",
        details=None,
    ):
        """Inicializa a exceção com uma mensagem.

        Args:
            message: Mensagem de erro
            error_code: Código de erro único para rastreamento e padronização
            details: Detalhes adicionais para debug ou contexto
        """
        super().__init__(message, error_code, details)


class LLMConfigurationError(ConfigurationError):
    """Exceção lançada quando há erro na configuração do LLM service."""

    def __init__(
        self,
        message: str = "Erro de configuração do LLM service",
        error_code: str = "LLM_CONFIG_001",
        details=None,
    ):
        """Inicializa a exceção com uma mensagem.

        Args:
            message: Mensagem de erro
            error_code: Código de erro único para rastreamento e padronização
            details: Detalhes adicionais para debug ou contexto
        """
        super().__init__(message, error_code, details)
