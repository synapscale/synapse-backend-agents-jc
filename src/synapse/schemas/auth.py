"""
Schemas Pydantic para autenticação e validação de dados
"""
from pydantic import BaseModel, EmailStr, validator, Field
from typing import Optional, List
from datetime import datetime
import re

class UserBase(BaseModel):
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=100)
    
    @validator('password')
    def validate_password(cls, v):
        """Valida força da senha"""
        if len(v) < 8:
            raise ValueError('Senha deve ter pelo menos 8 caracteres')
        
        if not re.search(r'[A-Z]', v):
            raise ValueError('Senha deve conter pelo menos uma letra maiúscula')
        
        if not re.search(r'[a-z]', v):
            raise ValueError('Senha deve conter pelo menos uma letra minúscula')
        
        if not re.search(r'\d', v):
            raise ValueError('Senha deve conter pelo menos um número')
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Senha deve conter pelo menos um caractere especial')
        
        return v
    
    @validator('first_name', 'last_name')
    def validate_names(cls, v):
        """Valida nomes"""
        if v and len(v.strip()) < 2:
            raise ValueError('Nome deve ter pelo menos 2 caracteres')
        return v.strip() if v else v

class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    avatar_url: Optional[str] = None
    
    @validator('first_name', 'last_name')
    def validate_names(cls, v):
        """Valida nomes"""
        if v and len(v.strip()) < 2:
            raise ValueError('Nome deve ter pelo menos 2 caracteres')
        return v.strip() if v else v

class UserResponse(BaseModel):
    id: str
    email: str
    first_name: Optional[str]
    last_name: Optional[str]
    full_name: str
    avatar_url: Optional[str]
    is_active: bool
    is_verified: bool
    role: str
    subscription_plan: str
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8, max_length=100)
    
    @validator('new_password')
    def validate_password(cls, v):
        """Valida força da senha"""
        if len(v) < 8:
            raise ValueError('Senha deve ter pelo menos 8 caracteres')
        
        if not re.search(r'[A-Z]', v):
            raise ValueError('Senha deve conter pelo menos uma letra maiúscula')
        
        if not re.search(r'[a-z]', v):
            raise ValueError('Senha deve conter pelo menos uma letra minúscula')
        
        if not re.search(r'\d', v):
            raise ValueError('Senha deve conter pelo menos um número')
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Senha deve conter pelo menos um caractere especial')
        
        return v

class EmailVerificationRequest(BaseModel):
    token: str

class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=100)
    
    @validator('new_password')
    def validate_password(cls, v):
        """Valida força da senha"""
        if len(v) < 8:
            raise ValueError('Senha deve ter pelo menos 8 caracteres')
        
        if not re.search(r'[A-Z]', v):
            raise ValueError('Senha deve conter pelo menos uma letra maiúscula')
        
        if not re.search(r'[a-z]', v):
            raise ValueError('Senha deve conter pelo menos uma letra minúscula')
        
        if not re.search(r'\d', v):
            raise ValueError('Senha deve conter pelo menos um número')
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Senha deve conter pelo menos um caractere especial')
        
        return v

# Schemas para Workflow
class WorkflowBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = []
    is_public: bool = False

class WorkflowCreate(WorkflowBase):
    definition: dict = Field(..., description="Estrutura completa do workflow")
    
    @validator('definition')
    def validate_definition(cls, v):
        """Valida estrutura da definição"""
        if not isinstance(v, dict):
            raise ValueError('Definição deve ser um objeto JSON válido')
        
        required_keys = ['nodes', 'connections']
        for key in required_keys:
            if key not in v:
                raise ValueError(f'Definição deve conter a chave "{key}"')
        
        if not isinstance(v['nodes'], list):
            raise ValueError('Nodes deve ser uma lista')
        
        if not isinstance(v['connections'], list):
            raise ValueError('Connections deve ser uma lista')
        
        return v

class WorkflowUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    is_public: Optional[bool] = None
    definition: Optional[dict] = None
    status: Optional[str] = None

class WorkflowResponse(WorkflowBase):
    id: str
    user_id: str
    workspace_id: Optional[str]
    version: str
    status: str
    thumbnail_url: Optional[str]
    downloads_count: int
    rating_average: float
    rating_count: int
    execution_count: int
    last_executed_at: Optional[datetime]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    definition: Optional[dict] = None
    
    class Config:
        from_attributes = True

# Schemas para Node
class NodeBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    type: str
    category: Optional[str] = None
    is_public: bool = False

class NodeCreate(NodeBase):
    code_template: str = Field(..., min_length=1)
    input_schema: dict
    output_schema: dict
    parameters_schema: Optional[dict] = {}
    icon: Optional[str] = "🔧"
    color: Optional[str] = "#6366f1"
    documentation: Optional[str] = None
    examples: Optional[List[dict]] = []
    
    @validator('input_schema', 'output_schema')
    def validate_schemas(cls, v):
        """Valida schemas JSON"""
        if not isinstance(v, dict):
            raise ValueError('Schema deve ser um objeto JSON válido')
        
        required_keys = ['type', 'properties']
        for key in required_keys:
            if key not in v:
                raise ValueError(f'Schema deve conter a chave "{key}"')
        
        return v

class NodeUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    category: Optional[str] = None
    is_public: Optional[bool] = None
    code_template: Optional[str] = None
    input_schema: Optional[dict] = None
    output_schema: Optional[dict] = None
    parameters_schema: Optional[dict] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    documentation: Optional[str] = None
    examples: Optional[List[dict]] = None

class NodeResponse(NodeBase):
    id: str
    user_id: str
    workspace_id: Optional[str]
    status: str
    version: str
    icon: str
    color: str
    documentation: Optional[str]
    examples: List[dict]
    downloads_count: int
    usage_count: int
    rating_average: float
    rating_count: int
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    code_template: Optional[str] = None
    input_schema: Optional[dict] = None
    output_schema: Optional[dict] = None
    parameters_schema: Optional[dict] = None
    
    class Config:
        from_attributes = True

# Schemas para Agent
class AgentBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    agent_type: str = "general"

class AgentCreate(AgentBase):
    personality: Optional[str] = None
    instructions: Optional[str] = None
    model_provider: str = "openai"
    model_name: str = "gpt-4"
    temperature: float = Field(0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(1000, ge=1, le=4000)
    tools: Optional[List[str]] = []
    knowledge_base: Optional[dict] = {}
    avatar_url: Optional[str] = None

class AgentUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    personality: Optional[str] = None
    instructions: Optional[str] = None
    model_provider: Optional[str] = None
    model_name: Optional[str] = None
    temperature: Optional[float] = Field(None, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(None, ge=1, le=4000)
    tools: Optional[List[str]] = None
    knowledge_base: Optional[dict] = None
    avatar_url: Optional[str] = None
    status: Optional[str] = None

class AgentResponse(AgentBase):
    id: str
    user_id: str
    workspace_id: Optional[str]
    model_provider: str
    model_name: str
    temperature: float
    max_tokens: int
    status: str
    avatar_url: Optional[str]
    conversation_count: int
    message_count: int
    rating_average: float
    rating_count: int
    last_active_at: Optional[datetime]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

# Schemas para Conversation
class ConversationCreate(BaseModel):
    agent_id: Optional[str] = None
    title: Optional[str] = None
    context: Optional[dict] = {}

class ConversationResponse(BaseModel):
    id: str
    user_id: str
    agent_id: Optional[str]
    workspace_id: Optional[str]
    title: Optional[str]
    status: str
    message_count: int
    total_tokens_used: int
    last_message_at: Optional[datetime]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

# Schemas para Message
class MessageCreate(BaseModel):
    content: str = Field(..., min_length=1)
    attachments: Optional[List[dict]] = []

class MessageResponse(BaseModel):
    id: str
    conversation_id: str
    role: str
    content: str
    attachments: List[dict]
    model_used: Optional[str]
    tokens_used: int
    processing_time_ms: int
    created_at: Optional[datetime]
    
    class Config:
        from_attributes = True

# Schemas para paginação
class PaginationParams(BaseModel):
    page: int = Field(1, ge=1)
    size: int = Field(20, ge=1, le=100)

class PaginatedResponse(BaseModel):
    items: List[dict]
    total: int
    page: int
    size: int
    pages: int

