#!/usr/bin/env python3
"""
Script para corrigir classes faltantes no error.py
"""

error_classes = """

class NotFoundErrorResponse(BaseModel):
    \"\"\"Schema para resposta de erro 404 - Não encontrado\"\"\"
    message: str = Field(default="Recurso não encontrado", description="Mensagem de erro")
    error_code: str = Field(default="NOT_FOUND", description="Código do erro")
    details: Optional[dict] = Field(None, description="Detalhes adicionais")
    timestamp: datetime = Field(default_factory=datetime.now, description="Timestamp do erro")

class ConflictErrorResponse(BaseModel):
    \"\"\"Schema para resposta de erro 409 - Conflito\"\"\"
    message: str = Field(default="Conflito de recursos", description="Mensagem de erro")
    error_code: str = Field(default="CONFLICT", description="Código do erro")
    details: Optional[dict] = Field(None, description="Detalhes adicionais")
    timestamp: datetime = Field(default_factory=datetime.now, description="Timestamp do erro")

class InternalServerErrorResponse(BaseModel):
    \"\"\"Schema para resposta de erro 500 - Erro interno do servidor\"\"\"
    message: str = Field(default="Erro interno do servidor", description="Mensagem de erro")
    error_code: str = Field(default="INTERNAL_SERVER_ERROR", description="Código do erro")
    details: Optional[dict] = Field(None, description="Detalhes adicionais")
    timestamp: datetime = Field(default_factory=datetime.now, description="Timestamp do erro")

class BadGatewayErrorResponse(BaseModel):
    \"\"\"Schema para resposta de erro 502 - Bad Gateway\"\"\"
    message: str = Field(default="Gateway inválido", description="Mensagem de erro")
    error_code: str = Field(default="BAD_GATEWAY", description="Código do erro")
    details: Optional[dict] = Field(None, description="Detalhes adicionais")
    timestamp: datetime = Field(default_factory=datetime.now, description="Timestamp do erro")
"""

with open('src/synapse/schemas/error.py', 'r') as f:
    content = f.read()

# Adicionar as classes faltantes
if 'class NotFoundErrorResponse' not in content:
    content += error_classes

with open('src/synapse/schemas/error.py', 'w') as f:
    f.write(content)

print("Classes adicionadas ao error.py!") 