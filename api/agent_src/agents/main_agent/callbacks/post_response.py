"""
Callbacks de Pós-Resposta para o Agente Principal
Arquivo: src/agents/main_agent/callbacks/post_response.py

Este módulo pode conter funções (callbacks) que são executadas DEPOIS que o LLM
gerou uma resposta, mas ANTES que ela seja enviada de volta ao usuário ou ao
orquestrador chamador.

Casos de Uso Comuns para Callbacks de Pós-Resposta:
- **Logging da Resposta Final:** Registrar a resposta que está sendo enviada para fins
  de depuração, auditoria ou análise de qualidade.
- **Sanitização da Resposta:** Remover informações pessoalmente identificáveis (PII),
  filtrar conteúdo potencialmente prejudicial ou inadequado, ou garantir que a resposta
  esteja em conformidade com políticas de conteúdo.
- **Formatação da Resposta:** Se o LLM não formatar a resposta exatamente como desejado
  (ex: para um canal específico como Slack, ou para garantir uma estrutura JSON específica),
  um callback pode realizar essa formatação final.
- **Acionamento de Efeitos Colaterais:** Com base na resposta, acionar ações secundárias,
  como enviar uma notificação, atualizar um sistema externo, ou registrar métricas.
- **Validação da Resposta:** Verificar se a resposta do LLM atende a certos critérios de
  qualidade ou formato antes de ser enviada.

Boas Práticas e Considerações AI-Friendly:
- **Ordem de Execução:** A ordem dos callbacks de pós-resposta é importante. Por exemplo,
  a sanitização deve ocorrer antes do logging da resposta final para não logar dados sensíveis.
- **Impacto na Latência:** Assim como os callbacks de pré-requisição, mantenha-os eficientes.
- **Modificação da Resposta:** Callbacks podem modificar a resposta. Deixe claro se a
  modificação é "in-place" ou se uma nova estrutura de resposta é retornada.
- **Tratamento de Erros em Callbacks:** Defina como lidar com erros que ocorrem durante
  a execução de um callback de pós-resposta.
- **Referência Cruzada:**
    - Estes callbacks são tipicamente invocados no final do método `run` ou `process_request`
      do `MainAgent` em `src/agents/main_agent/agent.py`, após o LLM ter gerado sua resposta.
    - O `agent.py` carregaria a lista `POST_RESPONSE_CALLBACKS` deste arquivo.
"""
from typing import Dict, Any, Union, List, Callable
import re # Para sanitização básica com regex

# Importar o logger configurado (se existir um central)
# from my_vertical_agent.src.utils.logger import get_logger
# logger = get_logger(__name__)

def log_final_agent_response(
    response_payload: Union[str, Dict[str, Any]], 
    request_data: Dict[str, Any], 
    agent_config: Dict[str, Any]
) -> None:
    """
    Callback para registrar a resposta final que está sendo enviada pelo agente.

    Args:
        response_payload (Union[str, Dict[str, Any]]): A resposta final gerada pelo agente
            (pode ser uma string simples ou um dicionário estruturado).
        request_data (Dict[str, Any]): O payload da requisição original (útil para correlação de logs).
        agent_config (Dict[str, Any]): A configuração do agente.
    """
    session_id = request_data.get("session_id", "N/A")
    agent_name = agent_config.get("agent_name", "MainAgent")
    
    # Extrai uma prévia da resposta textual para o log
    if isinstance(response_payload, dict):
        # Tenta obter a resposta textual de campos comuns como "answer", "output", "text", "message"
        textual_response_preview = str(response_payload.get("answer", 
                                      response_payload.get("output", 
                                      response_payload.get("text", 
                                      response_payload.get("message", str(response_payload)))))[:200]
    else:
        textual_response_preview = str(response_payload)[:200]
    
    log_message = f"[CALLBACK POST-RESPONSE] Agente: {agent_name} - Sessão: {session_id} - Resposta Final: {textual_response_preview}..."
    # logger.info(log_message, extra={"session_id": session_id, "agent_name": agent_name, "response_preview": textual_response_preview})
    print(f"DEBUG: {log_message}")
    # Este callback não modifica a resposta, apenas loga.

def sanitize_response_for_pii(
    response_payload: Union[str, Dict[str, Any]], 
    request_data: Dict[str, Any], 
    agent_config: Dict[str, Any]
) -> Union[str, Dict[str, Any]]:
    """
    Callback placeholder para sanitizar PII (Informações Pessoalmente Identificáveis) da resposta.
    
    IMPORTANTE: Esta é uma implementação MUITO BÁSICA e apenas para fins de demonstração.
    A detecção e sanitização de PII em produção requerem ferramentas e técnicas robustas
    (ex: bibliotecas especializadas como Microsoft Presidio, Google DLP, ou serviços de PII).
    Não confie neste exemplo para proteção real de PII.

    Args:
        response_payload (Union[str, Dict[str, Any]]): A resposta gerada pelo LLM.
        request_data (Dict[str, Any]): O payload da requisição original.
        agent_config (Dict[str, Any]): A configuração do agente.

    Returns:
        Union[str, Dict[str, Any]]: A resposta (potencialmente sanitizada).
    """
    session_id = request_data.get("session_id", "N/A")
    agent_name = agent_config.get("agent_name", "MainAgent")
    
    # Padrões regex de exemplo (extremamente simplificados e não exaustivos)
    # Em produção, use bibliotecas dedicadas ou serviços de PII.
    pii_patterns_map = {
        "[EMAIL_ADDRESS]": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
        "[PHONE_NUMBER]": r"(?:\+?\d{1,3}[-.\s]?)?(?:\(?\d{2,3}\)?[-.\s]?)?\d{3,4}[-.\s]?\d{4}\b",
        "[CREDIT_CARD_NUMBER]": r"\b(?:\d[ -]*?){13,16}\b" # Muito genérico, pode causar falsos positivos
    }
    
    sanitized_payload = response_payload
    modified = False

    if isinstance(response_payload, str):
        temp_str_response = response_payload
        for placeholder, pattern in pii_patterns_map.items():
            temp_str_response, count = re.subn(pattern, placeholder, temp_str_response)
            if count > 0:
                modified = True
        if modified:
            sanitized_payload = temp_str_response
            
    elif isinstance(response_payload, dict):
        # Se for um dicionário, idealmente você percorreria os valores de string.
        # Para este exemplo, vamos focar em chaves comuns que podem conter texto livre.
        # Uma solução real precisaria de uma abordagem recursiva para sanitizar strings em estruturas aninhadas.
        for key in ["answer", "output", "text", "message", "details"]:
            if key in response_payload and isinstance(response_payload[key], str):
                original_text_field = response_payload[key]
                sanitized_text_field = original_text_field
                for placeholder, pattern in pii_patterns_map.items():
                    sanitized_text_field, count = re.subn(pattern, placeholder, sanitized_text_field)
                    if count > 0:
                        modified = True
                if modified:
                    response_payload[key] = sanitized_text_field # Modifica o dicionário in-place
        # Se o dicionário foi modificado, sanitized_payload já é a referência correta.
        # Se não, sanitized_payload ainda é o response_payload original.
        if modified:
             sanitized_payload = response_payload # Garante que estamos retornando o objeto modificado

    if modified:
        log_message = f"[CALLBACK POST-RESPONSE] Agente: {agent_name} - Sessão: {session_id} - PII potencialmente sanitizada da resposta."
        # logger.warning(log_message, extra={"session_id": session_id, "agent_name": agent_name})
        print(f"DEBUG: {log_message}")
        
    return sanitized_payload

# --- Definição da Lista de Callbacks de Pós-Resposta ---
# O agente principal (`agent.py`) pode iterar sobre esta lista.
# A ORDEM É IMPORTANTE: sanitizar antes de logar a resposta final.
POST_RESPONSE_PROCESSING_CALLBACKS: List[Callable[[Union[str, Dict[str, Any]], Dict[str, Any], Dict[str, Any]], Optional[Union[str, Dict[str, Any]]]]] = [
    sanitize_response_for_pii,    # Primeiro, tenta sanitizar PII. Pode modificar a resposta.
    log_final_agent_response,     # Depois, loga a resposta (potencialmente sanitizada). Não modifica.
]

# Bloco de exemplo para teste direto do módulo
if __name__ == "__main__":
    print("--- Testando Callbacks de Pós-Resposta ---")
    
    mock_request_payload_post = {
        "user_input": "Quais são meus dados de contato registrados?",
        "session_id": "test_post_callback_session_456",
    }
    mock_agent_configuration_post = {"agent_name": "AgenteDeTestePostCallbacks"}
    
    # Teste com resposta em string contendo PII
    raw_response_string = "Seu e-mail é usuario@dominio.com e seu telefone é (11) 98765-4321. Seu cartão é 1234-5678-9012-3456."
    print(f"\nResposta String Original: {raw_response_string}")
    
    current_response_data_str = raw_response_string
    for callback_fn in POST_RESPONSE_PROCESSING_CALLBACKS:
        returned_value = callback_fn(current_response_data_str, mock_request_payload_post, mock_agent_configuration_post)
        if returned_value is not None: # Alguns callbacks podem modificar in-place, outros retornam o novo valor
            current_response_data_str = returned_value
    print(f"Resposta String Processada: {current_response_data_str}")

    # Teste com resposta em dicionário contendo PII em um campo específico
    raw_response_dict = {
        "answer": "Os detalhes de contato são: email joao.silva@emailteste.com, tel +5521999990000.",
        "source": "internal_db",
        "confidence_score": 0.92
    }
    print(f"\nResposta Dicionário Original: {raw_response_dict}")
    
    current_response_data_dict = raw_response_dict.copy() # Trabalha com uma cópia
    for callback_fn in POST_RESPONSE_PROCESSING_CALLBACKS:
        returned_value = callback_fn(current_response_data_dict, mock_request_payload_post, mock_agent_configuration_post)
        if returned_value is not None:
            current_response_data_dict = returned_value
    print(f"Resposta Dicionário Processada: {current_response_data_dict}")

    print("\n--- Testes dos Callbacks de Pós-Resposta Concluídos ---")

