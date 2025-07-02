"""
Schemas Centralizados do SynapScale.

Este módulo centraliza todas as definições de schema para evitar duplicação
e garantir consistência em toda a aplicação.
"""

from .base_fields import *
from .common_schemas import *
from .validators import *

__all__ = [
    # Base fields
    "CommonFields",
    "CommonConstraints",
    "CommonValidators",
    # Common schemas
    "BaseResponseSchema",
    "PaginationSchema",
    "TimestampSchema",
    "TenantSchema",
    # Validators
    "validate_uuid",
    "validate_tenant_id",
    "validate_description",
    "validate_title",
]
