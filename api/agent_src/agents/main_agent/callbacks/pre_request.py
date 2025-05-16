"""
Callbacks de Pré-Requisição para o Agente Principal
Arquivo: src/agents/main_agent/callbacks/pre_request.py

Este módulo contém funções (callbacks) que podem ser executadas ANTES que o
agente principal processe uma requisição de entrada ou ANTES que ele chame o LLM.

Casos de Uso Comuns para Callbacks de Pré-Requisição:
- **Logging Detalhado:** Registrar os detalhes da requisição recebida para depuração,
  auditoria ou análise de uso.
- **Modificação e Enriquecimento do Payload:** Adicionar metadados (ex: timestamp do servidor),
  sanitizar inputs do usuário, ou transformar a estrutura da requisição antes do processamento.
- **Verificações de Autenticação/Autorização:** Embora verificações mais robustas devam ocorrer
  no nível do entrypoint (ex: API Gateway, middleware), callbacks podem adicionar uma camada
  adicional ou verificações específicas do agente.
- **Injeção de Contexto Dinâmico no Prompt:** Modificar o contexto que será usado para renderizar
  o prompt do LLM, adicionando informações dinâmicas (ex: saudação baseada na hora do dia,
  informações contextuais recentes sobre o usuário).

Boas Práticas e Considerações AI-Friendly:
- **Modularidade:** Callbacks permitem adicionar funcionalidades transversais (como logging)
  sem poluir a lógica principal do agente. Cada callback foca em uma tarefa específica.
- **Clareza de Fluxo:** O agente principal pode ter uma lista de callbacks a serem executados
  em sequência, tornando o fluxo de pré-processamento explícito e fácil de entender.
- **Impacto na Latência:** Callbacks adicionam processamento. Mantenha-os eficientes para
  não impactar significativamente a latência da resposta do agente.
- **Tratamento de Erros em Callbacks:** Decida como erros dentro de um callback devem ser
  tratados. Eles devem impedir o processamento da requisição ou apenas serem logados?
- **Modificação de Dados:** Seja claro se um callback modifica os dados da requisição
  "in-place" ou se retorna uma nova versão dos dados. Retornar uma nova versão é
  geralmente mais seguro e fácil de testar (imutabilidade).
- **Referência Cruzada:**
    - Estes callbacks são tipicamente invocados no início do método `run` ou `process_request`
      do `MainAgent` em `src/agents/main_agent/agent.py`.
    - O `agent.py` carregaria as listas `PRE_REQUEST_CALLBACKS` e
      `PRE_PROMPT_RENDERING_CALLBACKS` deste arquivo.
"""
from typing import Dict, Any, List, Callable
import datetime

# Importar o logger configurado (se existir um central)
# from my_vertical_agent.src.utils.logger import get_logger
# logger = get_logger(__name__)

def log_incoming_request(request_data: Dict[str, Any], agent_config: Dict[str, Any]) -> None:
    """
    Callback para registrar detalhes da requisição de entrada.

    Em um sistema real, utilizaria um logger estruturado (ex: structlog, logging padrão do Python
    configurado com formatters JSON) para facilitar a análise e busca de logs.

    Args:
        request_data (Dict[str, Any]): O payload da requisição recebida pelo agente.
        agent_config (Dict[str, Any]): A configuração carregada para o agente principal.
                                         Pode ser usada para, por exemplo, obter o nome do agente para o log.
    """
    session_id = request_data.get("session_id", "N/A")
    user_input_preview = str(request_data.get("user_input", "N/A"))[:100] # Preview do input
    agent_name = agent_config.get("agent_name", "MainAgent")
    
    log_message = f"[CALLBACK PRE-REQUEST] Agente: {agent_name} - Sessão: {session_id} - Input Recebido: {user_input_preview}..."
    # logger.info(log_message, extra={"session_id": session_id, "agent_name": agent_name, "user_input_preview": user_input_preview})
    print(f"DEBUG: {log_message}")
    # Este callback não modifica request_data, então não retorna nada (None implicitamente).

def enrich_request_with_server_timestamp(request_data: Dict[str, Any], agent_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Callback para adicionar um timestamp do lado do servidor ao payload da requisição,
    geralmente dentro de um campo `request_context`.

    Args:
        request_data (Dict[str, Any]): O payload da requisição.
        agent_config (Dict[str, Any]): A configuração do agente.

    Returns:
        Dict[str, Any]: O payload `request_data` modificado com o timestamp.
    """
    timestamp_utc = datetime.datetime.utcnow().isoformat() + "Z" # Formato ISO 8601 com Z para UTC
    
    # Garante que request_context exista e seja um dicionário
    if "request_context" not in request_data or not isinstance(request_data.get("request_context"), dict):
        request_data["request_context"] = {}
    
    request_data["request_context"]["server_received_timestamp_utc"] = timestamp_utc
    
    session_id = request_data.get("session_id", "N/A")
    # logger.info(f"[CALLBACK PRE-REQUEST] Sessão: {session_id} - Requisição enriquecida com timestamp: {timestamp_utc}")
    print(f"DEBUG: [CALLBACK PRE-REQUEST] Sessão: {session_id} - Timestamp do servidor adicionado: {timestamp_utc}")
    return request_data # Retorna o dicionário modificado

def inject_dynamic_greeting_to_prompt_context(prompt_context: Dict[str, Any], agent_config: Dict[str, Any], request_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Exemplo de callback para injetar uma saudação dinâmica no contexto do prompt
    com base na hora do dia (UTC).

    Este tipo de callback seria executado ANTES da renderização do template de prompt
    (ex: `prompt_template.j2`).

    Args:
        prompt_context (Dict[str, Any]): O dicionário de contexto que será usado para renderizar o prompt.
        agent_config (Dict[str, Any]): A configuração do agente.
        request_data (Dict[str, Any]): O payload original da requisição (pode ser útil para obter user_id, etc.).

    Returns:
        Dict[str, Any]: O `prompt_context` modificado.
    """
    current_hour_utc = datetime.datetime.utcnow().hour
    greeting = "Olá! Como posso ajudar hoje?"

    if 5 <= current_hour_utc < 12:
        greeting = "Bom dia! Como posso te ajudar?"
    elif 12 <= current_hour_utc < 18:
        greeting = "Boa tarde! Em que posso ser útil?"
    elif 18 <= current_hour_utc < 24 or 0 <= current_hour_utc < 5:
        greeting = "Boa noite! Como posso te assistir agora?"
    
    # Adiciona a saudação ao contexto do prompt. O template de prompt (`.j2`)
    # precisaria ter uma variável como {{ dynamic_greeting }} para usá-la.
    prompt_context["dynamic_greeting"] = greeting
    
    session_id = request_data.get("session_id", "N/A")
    # logger.info(f"[CALLBACK PRE-PROMPT] Sessão: {session_id} - Saudação dinâmica injetada: {greeting}")
    print(f"DEBUG: [CALLBACK PRE-PROMPT] Sessão: {session_id} - Saudação dinâmica: {greeting}")
    return prompt_context

# --- Definição das Listas de Callbacks ---
# O agente principal (`agent.py`) pode iterar sobre estas listas e executar cada função.

# Callbacks executados logo após o recebimento da requisição, antes de qualquer lógica principal do agente.
PRE_REQUEST_PROCESSING_CALLBACKS: List[Callable[[Dict[str, Any], Dict[str, Any]], Optional[Dict[str, Any]]]] = [
    log_incoming_request,                # Apenas loga, não modifica request_data
    enrich_request_with_server_timestamp # Modifica e retorna request_data
]

# Callbacks executados imediatamente antes da renderização do template de prompt.
# Eles recebem e podem modificar o `prompt_context`.
PRE_PROMPT_RENDERING_CALLBACKS: List[Callable[[Dict[str, Any], Dict[str, Any], Dict[str, Any]], Dict[str, Any]]] = [
    inject_dynamic_greeting_to_prompt_context # Modifica e retorna prompt_context
]

# Bloco de exemplo para teste direto do módulo
if __name__ == "__main__":
    print("--- Testando Callbacks de Pré-Requisição e Pré-Prompt ---")
    
    mock_request_payload = {
        "user_input": "Gostaria de saber sobre o produto X.",
        "session_id": "test_callback_session_123",
        "user_profile": {"name": "Usuário Teste", "preferences": {"language": "pt-BR"}}
    }
    mock_agent_configuration = {"agent_name": "AgenteDeTesteCallbacks", "default_language": "pt-BR"}

    print(f"\nPayload da Requisição Original: {mock_request_payload}")
    
    # Simula a execução dos callbacks de pré-processamento da requisição
    current_request_data = mock_request_payload.copy() # Trabalha com uma cópia
    for callback_fn in PRE_REQUEST_PROCESSING_CALLBACKS:
        # Lida com callbacks que podem ou não retornar dados (modificação in-place vs. retorno)
        returned_value = callback_fn(current_request_data, mock_agent_configuration)
        if returned_value is not None:
            current_request_data = returned_value # Atualiza se o callback retornou um novo dicionário
    print(f"Payload da Requisição Após Callbacks de Pré-Processamento: {current_request_data}")

    # Simula a preparação do contexto do prompt e execução dos callbacks de pré-renderização
    initial_prompt_context = {
        "user_query": current_request_data.get("user_input"),
        "chat_history": "[Histórico de exemplo...]",
        "relevant_docs": "[Documentos relevantes da RAG...]"
    }
    print(f"\nContexto do Prompt Inicial: {initial_prompt_context}")
    
    current_prompt_context = initial_prompt_context.copy()
    for callback_fn in PRE_PROMPT_RENDERING_CALLBACKS:
        returned_value = callback_fn(current_prompt_context, mock_agent_configuration, current_request_data)
        if returned_value is not None:
            current_prompt_context = returned_value
    print(f"Contexto do Prompt Após Callbacks de Pré-Renderização: {current_prompt_context}")

    print("\n--- Testes dos Callbacks Concluídos ---")

