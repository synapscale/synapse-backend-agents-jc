"""
Error schemas
"""

from pydantic import BaseModel
from typing import List, Optional


class ErrorDetail(BaseModel):
    """Detalhe do erro"""

    message: str
    code: Optional[str] = None


class ErrorResponse(BaseModel):
    """Resposta de erro"""

    detail: str
    errors: Optional[List[ErrorDetail]] = None
