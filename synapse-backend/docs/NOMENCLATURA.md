# Guia de Padronização de Nomenclatura

Este documento estabelece as convenções de nomenclatura a serem seguidas em todo o código do SynapScale, garantindo consistência e legibilidade.

## Convenções Gerais

### Arquivos e Módulos
- Nomes em minúsculas, separados por underscore (snake_case)
- Exemplos: `file_storage.py`, `auth_service.py`, `rate_limiter.py`
- Evitar abreviações não óbvias

### Classes
- CamelCase (PascalCase)
- Substantivos, não verbos
- Exemplos: `FileStorage`, `UserAuthentication`, `RateLimiter`

### Funções e Métodos
- snake_case
- Verbos ou frases verbais
- Exemplos: `validate_token()`, `save_file()`, `get_user_by_id()`

### Variáveis
- snake_case
- Nomes descritivos que indicam o propósito
- Exemplos: `user_id`, `file_content`, `max_size`

### Constantes
- MAIÚSCULAS, separadas por underscore
- Exemplos: `MAX_FILE_SIZE`, `DEFAULT_TIMEOUT`, `ALLOWED_MIME_TYPES`

### Parâmetros de API
- snake_case para parâmetros de query e path
- Exemplos: `user_id`, `file_type`, `page_size`

### Campos JSON
- snake_case para campos em respostas e requisições JSON
- Exemplos: `user_id`, `created_at`, `file_name`

## Exemplos de Refatoração

### Antes:
```python
class fileHandler:
    def SaveFile(self, fileContent, fileName):
        # implementação

    def GetFileById(self, fileId):
        # implementação
```

### Depois:
```python
class FileHandler:
    def save_file(self, file_content, file_name):
        # implementação

    def get_file_by_id(self, file_id):
        # implementação
```

## Casos Especiais

### Acrônimos
- Tratar acrônimos como palavras normais em nomes de classes
- Exemplos: `HttpClient` (não `HTTPClient`), `JsonParser` (não `JSONParser`)
- Em snake_case, manter tudo em minúsculas: `http_client`, `json_parser`

### Prefixos e Sufixos
- Evitar prefixos de tipo húngaro (como `str_name`, `int_count`)
- Sufixos podem ser usados para indicar tipos quando relevante: `user_ids`, `name_list`

### Nomes Privados
- Prefixar com underscore para indicar uso interno/privado
- Exemplos: `_validate_internally()`, `_cached_result`

## Verificação de Conformidade

Para verificar a conformidade com estas convenções, utilize as ferramentas de linting configuradas no projeto:

```bash
black .
isort .
flake8
```

## Estratégia de Migração

Para código legado que não segue estas convenções:

1. Identificar inconsistências usando ferramentas de análise estática
2. Refatorar gradualmente, começando pelos módulos mais críticos
3. Atualizar todas as referências ao renomear elementos públicos
4. Adicionar testes para garantir que a refatoração não introduziu bugs
5. Documentar mudanças de API que possam afetar integrações externas
