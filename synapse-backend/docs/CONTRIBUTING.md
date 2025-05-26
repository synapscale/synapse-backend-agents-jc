# Guia de Contribuição

Obrigado pelo interesse em contribuir com o SynapScale! Este documento fornece diretrizes e padrões para contribuir com o projeto, garantindo consistência e qualidade no código.

## Índice

- [Código de Conduta](#código-de-conduta)
- [Como Contribuir](#como-contribuir)
  - [Reportando Bugs](#reportando-bugs)
  - [Sugerindo Melhorias](#sugerindo-melhorias)
  - [Contribuindo com Código](#contribuindo-com-código)
- [Padrões de Código](#padrões-de-código)
  - [Estilo de Código](#estilo-de-código)
  - [Documentação de Código](#documentação-de-código)
  - [Convenções de Nomenclatura](#convenções-de-nomenclatura)
  - [Testes](#testes)
- [Processo de Revisão](#processo-de-revisão)
- [Fluxo de Trabalho Git](#fluxo-de-trabalho-git)
- [Ambiente de Desenvolvimento](#ambiente-de-desenvolvimento)

## Código de Conduta

Este projeto segue um Código de Conduta que esperamos que todos os participantes sigam. Por favor, leia [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) para entender quais ações serão e não serão toleradas.

## Como Contribuir

### Reportando Bugs

Bugs são rastreados como issues no GitHub. Ao criar uma issue para reportar um bug, inclua:

- Um título claro e descritivo
- Passos detalhados para reproduzir o bug
- Comportamento esperado vs. comportamento observado
- Versões relevantes (Python, FastAPI, sistema operacional, etc.)
- Logs ou screenshots, se aplicável

### Sugerindo Melhorias

Melhorias também são rastreadas como issues no GitHub. Ao sugerir uma melhoria, inclua:

- Um título claro e descritivo
- Descrição detalhada da melhoria proposta
- Justificativa para a melhoria (benefícios, casos de uso, etc.)
- Exemplos de como a melhoria funcionaria, se aplicável

### Contribuindo com Código

1. Faça um fork do repositório
2. Clone seu fork: `git clone https://github.com/seu-usuario/synapse-backend-agents-jc.git`
3. Crie uma branch para sua feature: `git checkout -b feature/nome-da-feature`
4. Implemente suas mudanças
5. Execute os testes: `pytest`
6. Formate seu código: `black . && isort . && flake8`
7. Commit suas mudanças: `git commit -m "feat: adiciona nova funcionalidade"`
8. Push para a branch: `git push origin feature/nome-da-feature`
9. Abra um Pull Request

## Padrões de Código

### Estilo de Código

Este projeto segue o [PEP 8](https://www.python.org/dev/peps/pep-0008/) com algumas modificações. Utilizamos as seguintes ferramentas para garantir a consistência do código:

- **Black**: Formatador de código automático
- **isort**: Organizador de imports
- **Flake8**: Linter para verificar a qualidade do código

Configurações específicas para estas ferramentas estão disponíveis nos arquivos `.flake8`, `pyproject.toml` e `setup.cfg` na raiz do projeto.

Para formatar seu código automaticamente, execute:

```bash
black .
isort .
flake8
```

### Documentação de Código

Todo código deve ser documentado seguindo o padrão de docstrings do Google:

```python
def funcao_exemplo(param1, param2):
    """Breve descrição da função.

    Descrição mais detalhada da função, explicando o que ela faz,
    como funciona e quaisquer detalhes importantes.

    Args:
        param1 (tipo): Descrição do primeiro parâmetro.
        param2 (tipo): Descrição do segundo parâmetro.

    Returns:
        tipo: Descrição do valor retornado.

    Raises:
        ExcecaoTipo: Quando e por que esta exceção é levantada.
    """
    # Implementação da função
```

Para classes:

```python
class ClasseExemplo:
    """Breve descrição da classe.

    Descrição mais detalhada da classe, explicando seu propósito,
    comportamento e quaisquer detalhes importantes.

    Attributes:
        atributo1 (tipo): Descrição do primeiro atributo.
        atributo2 (tipo): Descrição do segundo atributo.
    """

    def __init__(self, param1, param2):
        """Inicializa a classe.

        Args:
            param1 (tipo): Descrição do primeiro parâmetro.
            param2 (tipo): Descrição do segundo parâmetro.
        """
        self.atributo1 = param1
        self.atributo2 = param2
```

### Convenções de Nomenclatura

- **Arquivos**: Nomes em minúsculas, separados por underscore (snake_case): `nome_do_arquivo.py`
- **Módulos**: Nomes em minúsculas, separados por underscore: `nome_do_modulo`
- **Classes**: CamelCase (PascalCase): `NomeDaClasse`
- **Funções e Métodos**: snake_case: `nome_da_funcao`, `nome_do_metodo`
- **Variáveis**: snake_case: `nome_da_variavel`
- **Constantes**: Maiúsculas, separadas por underscore: `NOME_DA_CONSTANTE`
- **Parâmetros de API**: snake_case para parâmetros de query e path
- **Campos JSON**: snake_case para campos em respostas e requisições JSON

### Testes

Todos os novos recursos devem incluir testes. Utilizamos pytest para testes unitários e de integração.

- Testes unitários devem ser colocados no diretório `tests/unit/`
- Testes de integração devem ser colocados no diretório `tests/integration/`
- Nomes de arquivos de teste devem começar com `test_`
- Nomes de funções de teste devem começar com `test_`

Exemplo de teste:

```python
def test_funcionalidade_especifica():
    # Arrange
    entrada = "valor de entrada"
    resultado_esperado = "valor esperado"

    # Act
    resultado_real = funcao_a_ser_testada(entrada)

    # Assert
    assert resultado_real == resultado_esperado
```

Para executar os testes:

```bash
pytest                     # Executa todos os testes
pytest tests/unit/         # Executa apenas testes unitários
pytest tests/integration/  # Executa apenas testes de integração
pytest -v                  # Modo verboso
pytest -xvs                # Modo verboso com saída detalhada e parada no primeiro erro
```

## Processo de Revisão

Todos os Pull Requests passam pelo seguinte processo de revisão:

1. **Verificação Automatizada**: CI executa testes, linting e verificações de cobertura
2. **Revisão de Código**: Pelo menos um mantenedor deve aprovar as mudanças
3. **Verificação de Documentação**: A documentação deve ser atualizada conforme necessário
4. **Verificação de Testes**: Novos recursos devem incluir testes adequados

Critérios para aprovação:

- Código segue os padrões de estilo
- Testes passam e cobrem adequadamente as mudanças
- Documentação está atualizada
- Mudanças atendem aos requisitos da issue relacionada

## Fluxo de Trabalho Git

Seguimos um fluxo de trabalho baseado em feature branches:

- `main`: Branch principal, sempre estável e pronta para produção
- `develop`: Branch de desenvolvimento, integra features concluídas
- `feature/*`: Branches para desenvolvimento de novas features
- `bugfix/*`: Branches para correção de bugs
- `hotfix/*`: Branches para correções urgentes em produção

Convenções para mensagens de commit:

Seguimos o padrão [Conventional Commits](https://www.conventionalcommits.org/):

```
<tipo>(<escopo opcional>): <descrição>

[corpo opcional]

[rodapé(s) opcional(is)]
```

Tipos comuns:
- `feat`: Nova funcionalidade
- `fix`: Correção de bug
- `docs`: Alterações na documentação
- `style`: Alterações que não afetam o significado do código (espaços em branco, formatação, etc.)
- `refactor`: Refatoração de código
- `test`: Adição ou correção de testes
- `chore`: Alterações no processo de build, ferramentas, etc.

Exemplos:
```
feat(auth): adiciona autenticação com Google OAuth
fix(uploads): corrige validação de tipos MIME
docs: atualiza documentação da API
```

## Ambiente de Desenvolvimento

### Pré-requisitos

- Python 3.11 ou superior
- Docker e Docker Compose (para desenvolvimento local com serviços)
- Git

### Configuração

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/synapse-backend-agents-jc.git
cd synapse-backend-agents-jc
```

2. Crie e ative um ambiente virtual:
```bash
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
```

3. Instale as dependências de desenvolvimento:
```bash
pip install -r requirements-dev.txt
```

4. Configure as ferramentas de linting:
```bash
pre-commit install
```

5. Configure as variáveis de ambiente:
```bash
cp .env.example .env
# Edite o arquivo .env com suas configurações
```

6. Inicie os serviços de banco de dados com Docker:
```bash
docker-compose up -d postgres
```

7. Execute as migrações do banco de dados:
```bash
alembic upgrade head
```

8. Inicie o servidor de desenvolvimento:
```bash
uvicorn api-gateway.main:app --reload
```

---

Agradecemos suas contribuições para tornar o SynapScale melhor para todos!
