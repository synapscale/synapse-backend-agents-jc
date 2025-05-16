"""
Callbacks de Tratamento de Erros para o Agente Principal
Arquivo: src/agents/main_agent/callbacks/on_error.py

Este módulo pode conter funções (callbacks) que são executadas quando um erro
ou exceção ocorre durante o ciclo de processamento do agente.

Casos de Uso Comuns para Callbacks de Tratamento de Erros:
- **Logging Detalhado de Erros:** Registrar informações completas sobre a exceção,
  incluindo tipo, mensagem, stack trace e o contexto da requisição, para facilitar
  a depuração e análise post-mortem.
- **Notificações de Erros Críticos:** Enviar alertas (ex: e-mail, Slack, PagerDuty)
  para administradores ou equipes de desenvolvimento quando erros críticos ocorrem,
  permitindo uma resposta rápida.
- **Geração de Respostas de Fallback:** Fornecer uma resposta genérica e amigável ao
  usuário em caso de erro não recuperável, em vez de deixar a requisição falhar
  silenciosamente ou retornar um erro técnico.
- **Limpeza de Recursos:** Se um erro deixar o sistema ou recursos externos em um estado
  inconsistente, callbacks podem tentar realizar uma limpeza (embora isso deva ser
  manuseado com cuidado para não causar mais problemas).
- **Tentativas de Recuperação (Retry Logic):** Para erros transitórios (ex: falhas de rede),
  um callback poderia, teoricamente, implementar uma lógica de retry, mas isso geralmente
  é mais complexo e pode ser melhor tratado por bibliotecas dedicadas ou no nível da
  chamada da ferramenta/LLM.

Boas Práticas e Considerações AI-Friendly:
- **Granularidade do Logging:** Logar informações suficientes para entender a causa raiz
  do erro e o estado do sistema no momento da falha.
- **Segurança em Logs:** Cuidado para não logar informações sensíveis (PII, segredos) nos
  detalhes do erro ou stack traces. Use técnicas de sanitização se necessário.
- **Resiliência:** O próprio callback de erro não deve introduzir novas falhas. Mantenha-os
  simples e robustos.
- **Experiência do Usuário:** Mesmo em caso de erro, tente fornecer uma experiência o mais
  suave possível, informando o usuário sobre o problema (se apropriado) e sugerindo
  próximos passos (ex: tentar novamente mais tarde).
- **Referência Cruzada:**
    - Estes callbacks são tipicamente invocados dentro de blocos `try...except` na lógica
      principal do agente (`src/agents/main_agent/agent.py`) ou nos wrappers de ferramentas
      (`src/agents/main_agent/tools/wrappers.py`).
    - O `agent.py` carregaria a lista `ERROR_HANDLING_CALLBACKS` deste arquivo e decidiria
      quais executar com base no tipo de erro ou no contexto.
"""
from typing import Dict, Any, Optional, Union, List, Callable
import traceback # Para formatar o stack trace da exceção
import datetime

# Importar o logger configurado (se existir um central)
# from my_vertical_agent.src.utils.logger import get_logger
# logger = get_logger(__name__)

def log_exception_details(
    exception: Exception, 
    request_data: Optional[Dict[str, Any]] = None, 
    agent_config: Optional[Dict[str, Any]] = None, 
    context_message: str = "Erro durante o processamento do agente"
) -> None:
    """
    Callback para registrar informações detalhadas sobre uma exceção ocorrida.

    Args:
        exception (Exception): A instância da exceção que foi capturada.
        request_data (Optional[Dict[str, Any]]): O payload da requisição original, se disponível.
        agent_config (Optional[Dict[str, Any]]): A configuração do agente, se disponível.
        context_message (str): Uma mensagem de contexto adicional para indicar onde/quando o erro ocorreu.
    """
    session_id = request_data.get("session_id", "N/A") if request_data else "N/A"
    agent_name = agent_config.get("agent_name", "MainAgent") if agent_config else "MainAgent"
    error_type_name = type(exception).__name__
    error_message_str = str(exception)
    full_stack_trace = traceback.format_exc() # Captura o stack trace completo
    timestamp_utc = datetime.datetime.utcnow().isoformat() + "Z"

    log_entry = (
        f"[CALLBACK ON-ERROR] Timestamp: {timestamp_utc}\n"
        f"Agente: {agent_name} - Sessão: {session_id}\n"
        f"Contexto do Erro: {context_message}\n"
        f"Tipo de Erro: {error_type_name}\n"
        f"Mensagem de Erro: {error_message_str}\n"
        f"--- Stack Trace ---\n{full_stack_trace}"
        f"--- Fim do Stack Trace ---"
    )
    
    # Em um sistema de produção, isso seria escrito em um arquivo de log dedicado
    # ou enviado para um sistema de gerenciamento de logs (ex: ELK, Splunk, Sentry).
    # logger.error(log_entry, exc_info=True, extra={
    #     "session_id": session_id,
    #     "agent_name": agent_name,
    #     "error_type": error_type_name,
    #     "error_context": context_message
    # })
    print(f"DEBUG:\n{log_entry}")
    # Este callback não retorna valor, apenas realiza o logging.

def notify_admin_on_critical_error(
    exception: Exception, 
    request_data: Optional[Dict[str, Any]] = None, 
    agent_config: Optional[Dict[str, Any]] = None,
    context_message: str = "Erro crítico no agente"
) -> None:
    """
    Callback placeholder para enviar uma notificação (ex: e-mail, Slack) a um administrador
    em caso de erros considerados críticos.

    Args:
        exception (Exception): A exceção capturada.
        request_data (Optional[Dict[str, Any]]): O payload da requisição original.
        agent_config (Optional[Dict[str, Any]]): A configuração do agente.
        context_message (str): Mensagem de contexto sobre o erro.
    """
    # Lógica para determinar se o erro é "crítico" (ex: tipos específicos de exceção)
    # Aqui, como exemplo, consideramos ConnectionError ou RuntimeError como críticos.
    is_critical = isinstance(exception, (ConnectionError, RuntimeError, MemoryError))

    if is_critical:
        session_id = request_data.get("session_id", "N/A") if request_data else "N/A"
        agent_name = agent_config.get("agent_name", "MainAgent") if agent_config else "MainAgent"
        admin_contact = agent_config.get("admin_notification_contact", "admins@example.com") if agent_config else "admins@example.com"
        error_type_name = type(exception).__name__
        error_message_str = str(exception)
        
        notification_subject = f"Erro Crítico no Agente: {agent_name} - {error_type_name}"
        notification_body = (
            f"Um erro crítico ({error_type_name}) ocorreu no agente {agent_name}.\n"
            f"Sessão ID: {session_id}\n"
            f"Contexto: {context_message}\n"
            f"Mensagem: {error_message_str}\n\n"
            f"Por favor, verifique os logs para mais detalhes."
        )
        
        # Em um sistema real, aqui você integraria com um serviço de e-mail, Slack API, etc.
        # logger.critical(f"SIMULANDO notificação de erro crítico para {admin_contact}. Assunto: {notification_subject}", extra={
        #     "session_id": session_id, "agent_name": agent_name, "error_type": error_type_name
        # })
        print(f"DEBUG: [CALLBACK ON-ERROR] Agente: {agent_name} - Sessão: {session_id} - SIMULANDO envio de notificação de erro crítico para {admin_contact} sobre {error_type_name}: {error_message_str}")
    # Este callback não retorna valor.

def generate_standard_fallback_response(
    exception: Exception, 
    request_data: Optional[Dict[str, Any]] = None, 
    agent_config: Optional[Dict[str, Any]] = None
) -> Union[str, Dict[str, Any]]:
    """
    Gera uma resposta de fallback padronizada para ser enviada ao usuário em caso de erro.
    A estrutura da resposta (string ou dicionário) deve ser consistente com o que o
    agente normalmente retorna.

    Args:
        exception (Exception): A exceção capturada.
        request_data (Optional[Dict[str, Any]]): O payload da requisição original.
        agent_config (Optional[Dict[str, Any]]): A configuração do agente.

    Returns:
        Union[str, Dict[str, Any]]: A resposta de fallback.
    """
    session_id = request_data.get("session_id", "N/A") if request_data else "N/A"
    agent_name = agent_config.get("agent_name", "MainAgent") if agent_config else "MainAgent"
    error_type_name = type(exception).__name__

    # logger.warning(f"[CALLBACK ON-ERROR] Agente: {agent_name} - Sessão: {session_id} - Gerando resposta de fallback devido a: {error_type_name}", extra={
    #     "session_id": session_id, "agent_name": agent_name, "error_type": error_type_name
    # })
    print(f"DEBUG: [CALLBACK ON-ERROR] Agente: {agent_name} - Sessão: {session_id} - Gerando resposta de fallback devido a: {error_type_name}")
    
    # Mensagem de fallback genérica para o usuário
    user_facing_message = "Desculpe, ocorreu um erro inesperado ao processar sua solicitação. Nossa equipe técnica já foi notificada. Por favor, tente novamente mais tarde ou contate o suporte se o problema persistir."
    
    # Decida o formato da resposta de fallback. Se o agente usualmente retorna um dicionário:
    # return {
    #     "answer": user_facing_message, # Ou "output", "text", "message"
    #     "status": "error",
    #     "error_type": error_type_name, # Pode ser útil para o cliente, mas não exponha detalhes internos
    #     "session_id": session_id
    # }
    # Se o agente retorna uma string simples:
    return user_facing_message

# --- Definição da Lista de Callbacks de Tratamento de Erros ---
# O agente principal (`agent.py`) pode iterar sobre esta lista (ou uma subseleção)
# dentro de seus blocos `except`.
ERROR_HANDLING_CALLBACKS: List[Callable[[Exception, Optional[Dict[str, Any]], Optional[Dict[str, Any]], str], None]] = [
    # Callbacks que não retornam valor e são para logging/notificação
    log_exception_details,
    notify_admin_on_critical_error,
    # A função `generate_standard_fallback_response` retorna um valor e deve ser chamada
    # separadamente pelo agente para obter a resposta a ser enviada ao usuário.
]

# Bloco de exemplo para teste direto do módulo
if __name__ == "__main__":
    print("--- Testando Callbacks de Tratamento de Erros ---")
    
    mock_request_payload_err = {"session_id": "test_error_session_789", "user_input": "Uma pergunta que pode causar um erro..."}
    mock_agent_configuration_err = {"agent_name": "AgenteDeTesteErros", "admin_notification_contact": "suporte_dev@example.com"}

    print("\n--- Simulando um ValueError ---")
    try:
        raise ValueError("Ocorreu um erro de valor específico no processamento.")
    except ValueError as ve:
        for callback_fn in ERROR_HANDLING_CALLBACKS:
            callback_fn(ve, mock_request_payload_err, mock_agent_configuration_err, context_message="Simulação de ValueError no fluxo X")
        
        fallback_resp_ve = generate_standard_fallback_response(ve, mock_request_payload_err, mock_agent_configuration_err)
        print(f"Resposta de Fallback para ValueError: {fallback_resp_ve}")

    print("\n--- Simulando um ConnectionError (crítico) ---")
    try:
        raise ConnectionError("Falha de conexão com um serviço externo essencial.")
    except ConnectionError as ce:
        for callback_fn in ERROR_HANDLING_CALLBACKS:
            callback_fn(ce, mock_request_payload_err, mock_agent_configuration_err, context_message="Simulação de ConnectionError ao chamar API Y")
        
        fallback_resp_ce = generate_standard_fallback_response(ce, mock_request_payload_err, mock_agent_configuration_err)
        print(f"Resposta de Fallback para ConnectionError: {fallback_resp_ce}")

    print("\n--- Simulando uma Exceção Genérica (ZeroDivisionError) ---")
    try:
        result = 10 / 0
    except Exception as e_gen:
        # Exemplo de chamada direta a um callback específico + fallback
        log_exception_details(e_gen, mock_request_payload_err, mock_agent_configuration_err, context_message="Divisão por zero inesperada")
        # notify_admin_on_critical_error(e_gen, mock_request_payload_err, mock_agent_configuration_err) # Poderia ser chamado se considerado crítico
        
        fallback_resp_gen = generate_standard_fallback_response(e_gen, mock_request_payload_err, mock_agent_configuration_err)
        print(f"Resposta de Fallback para Exceção Genérica: {fallback_resp_gen}")

    print("\n--- Testes dos Callbacks de Tratamento de Erros Concluídos ---")

