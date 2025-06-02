"""Aplicação principal do backend SynapScale.

Este módulo configura e inicializa a aplicação FastAPI, incluindo
middlewares, rotas, documentação e ciclo de vida.
"""

import logging
import os
from contextlib import asynccontextmanager
from typing import Callable
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.responses import HTMLResponse

from .api.v1 import router as v1_router
from .config import settings
from .db import init_db
from .logging import setup_logging
from .middlewares import setup_rate_limiting

# Configurar logging
setup_logging()

# Logger
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia o ciclo de vida da aplicação.

    Args:
        app: Aplicação FastAPI
    """
    # Startup
    logger.info("🚀 Iniciando serviço de uploads...")

    # Inicializar banco de dados
    await init_db()

    # Criar diretórios necessários
    os.makedirs(settings.STORAGE_BASE_PATH, exist_ok=True)
    for category in settings.ALLOWED_EXTENSIONS:
        os.makedirs(os.path.join(settings.STORAGE_BASE_PATH, category), exist_ok=True)

    logger.info("✅ Serviço de uploads inicializado com sucesso")

    yield

    # Shutdown
    logger.info("👋 Encerrando serviço de uploads...")


# Criar aplicação
app = FastAPI(
    title="SynapScale Backend API",
    description="""
API completa para integração com múltiplos provedores de LLM, gerenciamento de arquivos e processamento de dados.

## 📚 Recursos Principais

* **Integração Multi-LLM**: Acesso unificado a diversos provedores de LLM (OpenAI, Claude, Gemini, etc.)
* **Gerenciamento de Arquivos**: Upload, download e manipulação de arquivos
* **Processamento de Dados**: Análise e transformação de dados

## 🔐 Autenticação

A API utiliza autenticação via Bearer Token (JWT). Inclua o token no header `Authorization` de todas as requisições:

```
Authorization: Bearer seu_token_jwt
```

Para obter um token, utilize o endpoint de autenticação.

## 🚀 Provedores LLM Suportados

| Provedor | Modelos Disponíveis | Capacidades |
| --- | --- | --- |
| OpenAI | GPT-4o, GPT-4-turbo, GPT-3.5-turbo | Text, Vision, Function Calling |
| Claude | Claude 3 Opus, Sonnet, Haiku | Text, Vision, Reasoning |
| Gemini | Gemini 1.5 Pro, Flash | Text, Vision, Code |
| Llama | Llama 3 70B, 8B, Llama 2 70B | Text Generation |
| Grok | Grok-1 | Text, Function Calling |
| DeepSeek | DeepSeek Chat, Coder | Text, Code Generation |
| Tess | Múltiplos via orquestração | Text, Reasoning |

## 📋 Parâmetros Comuns

* `prompt`: Texto de entrada para o modelo (obrigatório)
* `provider`: Provedor LLM a ser usado (opcional, padrão: openai)
* `model`: Modelo específico do provedor (opcional)
* `temperature`: Controle de aleatoriedade (0.0-1.0, padrão: 0.7)
* `max_tokens`: Limite de tokens na resposta (padrão: 1000)

Consulte a documentação detalhada para mais informações sobre parâmetros específicos por provedor.
    """,
    version="1.0.0",
    docs_url=None,  # Desabilitar Swagger UI padrão
    redoc_url=None,  # Desabilitar ReDoc padrão
    lifespan=lifespan,
)

# Configurar CORS
origins = settings.BACKEND_CORS_ORIGINS
if origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    logger.info(f"CORS configurado com origens: {origins}")

# Configurar rate limiting
setup_rate_limiting(app)

# Montar arquivos estáticos
app.mount("/static", StaticFiles(directory="src/synapse/static"), name="static")


# Middleware para logging de requisições
@app.middleware("http")
async def log_requests(request: Request, call_next: Callable) -> Response:
    """Middleware para logging de requisições.

    Args:
        request: Requisição HTTP
        call_next: Próxima função na cadeia de middlewares

    Returns:
        Resposta HTTP
    """
    path = request.url.path
    method = request.method

    # Não logar requisições de health check
    if path == "/health" or path == "/":
        return await call_next(request)

    logger.info(f"{method} {path}")

    # Processar requisição
    response = await call_next(request)

    logger.info(f"{method} {path} - {response.status_code}")
    return response


# Rotas de documentação personalizada
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    """Endpoint para Swagger UI personalizado com CSS customizado.

    Returns:
        HTML do Swagger UI
    """
    swagger_ui_html = get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title="SynapScale API - Documentação Interativa",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css",
    )
    
    # Converter para string para manipulação
    content = swagger_ui_html.body.decode("utf-8")
    
    # Adicionar link para CSS customizado
    head_end = "</head>"
    custom_css = f'<link rel="stylesheet" type="text/css" href="/static/custom-swagger-ui.css">\n{head_end}'
    content = content.replace(head_end, custom_css)
    
    # Adicionar script para melhorar a experiência de usuário
    body_end = "</body>"
    custom_script = """
    <script>
    // Aguardar carregamento completo do Swagger UI
    window.onload = function() {
        // Dar tempo para o Swagger UI renderizar completamente
        setTimeout(function() {
            // Corrigir cores dos exemplos de código
            fixCodeExampleColors();
            
            // Melhorar visibilidade dos parâmetros
            enhanceParameters();
            
            // Corrigir cores específicas em elementos de autenticação
            fixAuthColors();
            
            // Corrigir cores em parâmetros comuns
            fixCommonParamsColors();
            
            // Observar mudanças no DOM para aplicar melhorias em elementos dinâmicos
            observeDOMChanges();
        }, 1000);
    };
    
    // Corrigir cores dos exemplos de código
    function fixCodeExampleColors() {
        // Selecionar todos os blocos de código
        const codeBlocks = document.querySelectorAll('.microlight');
        
        codeBlocks.forEach(block => {
            // Garantir que o fundo seja escuro
            block.style.backgroundColor = '#1E1E1E';
            
            // Garantir que o texto seja visível
            const allElements = block.querySelectorAll('*');
            allElements.forEach(el => {
                // Substituir qualquer cor roxa/rosa por preto
                const computedStyle = window.getComputedStyle(el);
                const color = computedStyle.color;
                
                // Verificar se a cor é roxa/rosa (aproximadamente)
                if (color.includes('rgb(144, 18, 254)') || 
                    color.includes('#9012fe') || 
                    color.includes('#9012FE') ||
                    color.includes('rgb(128, 0, 128)') ||
                    color.includes('#800080') ||
                    color.includes('rgb(153, 0, 153)') ||
                    color.includes('#990099') ||
                    color.includes('rgb(102, 0, 204)') ||
                    color.includes('#6600cc') ||
                    color.includes('purple') ||
                    color.includes('magenta') ||
                    color.includes('violet')) {
                    el.style.color = '#000000';
                }
            });
            
            // Garantir que todos os spans dentro do bloco de código tenham cor preta
            const textElements = block.querySelectorAll('span');
            textElements.forEach(span => {
                span.style.color = '#000000';
            });
        });
        
        // Selecionar especificamente exemplos de código Python
        const pythonExamples = document.querySelectorAll('pre');
        pythonExamples.forEach(example => {
            const spans = example.querySelectorAll('span');
            spans.forEach(span => {
                span.style.color = '#000000';
            });
        });
    }
    
    // Melhorar visibilidade dos parâmetros
    function enhanceParameters() {
        // Destacar parâmetros obrigatórios
        const requiredLabels = document.querySelectorAll('.parameter__name .required');
        requiredLabels.forEach(label => {
            label.style.color = '#FF0000';
            label.style.fontWeight = 'bold';
        });
        
        // Melhorar descrições de parâmetros
        const paramDescriptions = document.querySelectorAll('.parameter__description');
        paramDescriptions.forEach(desc => {
            desc.style.color = '#000000';
            desc.style.fontSize = '14px';
        });
        
        // Melhorar nomes de parâmetros
        const paramNames = document.querySelectorAll('.parameter__name');
        paramNames.forEach(name => {
            name.style.color = '#000000';
            name.style.fontWeight = 'bold';
        });
        
        // Melhorar tipos de parâmetros
        const paramTypes = document.querySelectorAll('.parameter__type');
        paramTypes.forEach(type => {
            type.style.color = '#666666';
        });
        
        // Melhorar exemplos de parâmetros
        const paramExamples = document.querySelectorAll('.parameter__example');
        paramExamples.forEach(example => {
            example.style.color = '#000000';
            example.style.backgroundColor = '#f5f5f5';
            example.style.padding = '2px 5px';
            example.style.borderRadius = '3px';
            example.style.fontFamily = 'monospace';
        });
    }
    
    // Corrigir cores em elementos de autenticação
    function fixAuthColors() {
        // Selecionar todos os elementos relacionados à autenticação
        const authElements = document.querySelectorAll('.auth-wrapper *');
        authElements.forEach(el => {
            // Verificar se é um elemento de texto
            if (el.childNodes.length === 1 && el.childNodes[0].nodeType === 3) {
                el.style.color = '#000000';
            }
        });
        
        // Corrigir especificamente o texto "Authorization"
        const authTexts = document.querySelectorAll('*');
        authTexts.forEach(el => {
            if (el.textContent === 'Authorization' || 
                el.textContent.includes('Authorization:') || 
                el.textContent.includes('Bearer')) {
                el.style.color = '#000000';
            }
        });
    }
    
    // Corrigir cores em parâmetros comuns
    function fixCommonParamsColors() {
        // Selecionar todos os elementos que podem conter parâmetros comuns
        const paramElements = document.querySelectorAll('code, .parameter__name, .parameter__type, .parameter__in');
        paramElements.forEach(el => {
            el.style.color = '#000000';
        });
        
        // Corrigir especificamente os nomes dos parâmetros comuns
        const commonParams = ['prompt', 'provider', 'model', 'temperature', 'max_tokens'];
        commonParams.forEach(param => {
            const paramElements = document.querySelectorAll('*');
            paramElements.forEach(el => {
                if (el.textContent === param) {
                    el.style.color = '#000000';
                }
            });
        });
    }
    
    // Observar mudanças no DOM para aplicar melhorias em elementos dinâmicos
    function observeDOMChanges() {
        // Criar um observador de mutações
        const observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                // Verificar se foram adicionados novos nós
                if (mutation.addedNodes.length) {
                    // Corrigir cores dos exemplos de código
                    fixCodeExampleColors();
                    
                    // Melhorar visibilidade dos parâmetros
                    enhanceParameters();
                    
                    // Corrigir cores em elementos de autenticação
                    fixAuthColors();
                    
                    // Corrigir cores em parâmetros comuns
                    fixCommonParamsColors();
                }
            });
        });
        
        // Configurar o observador
        const config = { childList: true, subtree: true };
        
        // Iniciar a observação
        observer.observe(document.body, config);
    }
    
    // Aplicar estilos globais para garantir que não haja texto roxo/rosa
    function applyGlobalStyles() {
        // Criar um elemento de estilo
        const style = document.createElement('style');
        style.type = 'text/css';
        style.innerHTML = `
            /* Garantir que não haja texto roxo/rosa em nenhum lugar */
            .microlight span, 
            pre span, 
            code span, 
            .parameter__name, 
            .parameter__type, 
            .parameter__in, 
            .parameter__name code, 
            .info code, 
            .info .parameter__name, 
            .info .parameter__type, 
            .info .parameter__in {
                color: #000000 !important;
            }
            
            /* Garantir que elementos de autenticação não tenham cor roxa/rosa */
            .auth-wrapper *, 
            .auth-container * {
                color: #000000 !important;
            }
            
            /* Garantir que exemplos de código não tenham cor roxa/rosa */
            .example pre *, 
            .example code *, 
            .example .microlight * {
                color: #000000 !important;
            }
            
            /* Melhorar contraste no Request Body */
            .swagger-ui .model-example .example {
                background-color: #000000 !important;
            }
            
            .swagger-ui .model-example .example pre,
            .swagger-ui .model-example .example pre span {
                color: #FFFFFF !important;
            }
        `;
        
        // Adicionar o elemento de estilo ao head
        document.head.appendChild(style);
    }
    
    // Aplicar estilos globais
    applyGlobalStyles();
    </script>
    """
    content = content.replace(body_end, custom_script + body_end)
    
    return HTMLResponse(content=content)


@app.get("/redoc", include_in_schema=False)
async def redoc_html():
    """Endpoint para ReDoc.

    Returns:
        HTML do ReDoc
    """
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title="SynapScale API - Documentação",
        redoc_js_url="https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js",
    )


# Customizar OpenAPI
def custom_openapi():
    """Customizar esquema OpenAPI.

    Returns:
        Esquema OpenAPI customizado
    """
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    # Adicionar componentes de segurança sem sobrescrever os schemas existentes
    if "components" not in openapi_schema:
        openapi_schema["components"] = {}
    
    # Preservar schemas existentes
    if "schemas" not in openapi_schema["components"]:
        openapi_schema["components"]["schemas"] = {}
    
    # Adicionar securitySchemes sem afetar outros componentes
    openapi_schema["components"]["securitySchemes"] = {
        "Bearer": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Insira seu token JWT no formato: Bearer {token}",
        }
    }

    # Aplicar segurança globalmente
    openapi_schema["security"] = [{"Bearer": []}]

    # Adicionar exemplos e melhorar descrições
    for path in openapi_schema["paths"]:
        for method in openapi_schema["paths"][path]:
            if method.lower() in ["get", "post", "put", "delete", "patch"]:
                # Garantir que todos os parâmetros tenham descrições claras
                if "parameters" in openapi_schema["paths"][path][method]:
                    for param in openapi_schema["paths"][path][method]["parameters"]:
                        if "description" not in param or not param["description"]:
                            param["description"] = f"Parâmetro {param['name']}"
                
                # Garantir que todos os requestBody tenham exemplos e schemas corretos
                if "requestBody" in openapi_schema["paths"][path][method]:
                    if "content" in openapi_schema["paths"][path][method]["requestBody"]:
                        for content_type in openapi_schema["paths"][path][method]["requestBody"]["content"]:
                            # Verificar se há referência a schema e corrigir se necessário
                            if "schema" in openapi_schema["paths"][path][method]["requestBody"]["content"][content_type]:
                                schema = openapi_schema["paths"][path][method]["requestBody"]["content"][content_type]["schema"]
                                if "$ref" in schema:
                                    # Corrigir referência se necessário
                                    ref_path = schema["$ref"]
                                    if ref_path.startswith("#/components/schemas/"):
                                        # Referência já está correta
                                        pass
                                    else:
                                        # Tentar corrigir referência
                                        schema_name = ref_path.split("/")[-1]
                                        schema["$ref"] = f"#/components/schemas/{schema_name}"
                            
                            # Adicionar exemplo se não existir
                            if "example" not in openapi_schema["paths"][path][method]["requestBody"]["content"][content_type]:
                                # Adicionar exemplo padrão baseado no schema
                                if "schema" in openapi_schema["paths"][path][method]["requestBody"]["content"][content_type]:
                                    schema = openapi_schema["paths"][path][method]["requestBody"]["content"][content_type]["schema"]
                                    if "$ref" in schema:
                                        # Referência a um schema, não podemos gerar exemplo automaticamente
                                        pass
                                    elif "properties" in schema:
                                        # Gerar exemplo baseado nas propriedades
                                        example = {}
                                        for prop, prop_schema in schema["properties"].items():
                                            if "example" in prop_schema:
                                                example[prop] = prop_schema["example"]
                                            elif "type" in prop_schema:
                                                if prop_schema["type"] == "string":
                                                    example[prop] = f"Exemplo de {prop}"
                                                elif prop_schema["type"] == "integer":
                                                    example[prop] = 42
                                                elif prop_schema["type"] == "number":
                                                    example[prop] = 3.14
                                                elif prop_schema["type"] == "boolean":
                                                    example[prop] = True
                                                elif prop_schema["type"] == "array":
                                                    example[prop] = []
                                                elif prop_schema["type"] == "object":
                                                    example[prop] = {}
                                        
                                        if example:
                                            openapi_schema["paths"][path][method]["requestBody"]["content"][content_type]["example"] = example
                
                # Garantir que os parâmetros do requestBody sejam exibidos como parâmetros na interface
                if "requestBody" in openapi_schema["paths"][path][method]:
                    if "content" in openapi_schema["paths"][path][method]["requestBody"]:
                        for content_type in openapi_schema["paths"][path][method]["requestBody"]["content"]:
                            if "schema" in openapi_schema["paths"][path][method]["requestBody"]["content"][content_type]:
                                schema = openapi_schema["paths"][path][method]["requestBody"]["content"][content_type]["schema"]
                                
                                # Se o schema for uma referência, tentar resolver
                                if "$ref" in schema:
                                    ref_path = schema["$ref"]
                                    schema_name = ref_path.split("/")[-1]
                                    
                                    # Verificar se o schema existe em components
                                    if "schemas" in openapi_schema["components"] and schema_name in openapi_schema["components"]["schemas"]:
                                        # Usar o schema diretamente em vez de referência para garantir que os parâmetros apareçam
                                        resolved_schema = openapi_schema["components"]["schemas"][schema_name]
                                        
                                        # Substituir a referência pelo schema resolvido
                                        openapi_schema["paths"][path][method]["requestBody"]["content"][content_type]["schema"] = resolved_schema

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

# Incluir rotas da API v1
app.include_router(v1_router, prefix="/api/v1")


# Rota raiz
@app.get("/", include_in_schema=False)
async def root():
    """Rota raiz.

    Returns:
        Mensagem de boas-vindas
    """
    return {
        "message": "Bem-vindo à API SynapScale",
        "version": settings.VERSION,
        "docs": "/docs",
        "redoc": "/redoc",
    }


# Rota de health check
@app.get("/health", include_in_schema=False)
async def health():
    """Rota de health check.

    Returns:
        Status da aplicação
    """
    return {"status": "ok", "version": settings.VERSION}
