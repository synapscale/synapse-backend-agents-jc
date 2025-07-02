import pytest

from synapse.core.websockets.manager import WebSocketHandler
from synapse.services.llm_service import UnifiedLLMService
from synapse.schemas.llm import LLMResponse
from synapse.models.conversation import Conversation


@pytest.mark.asyncio
async def test_handle_chat_message_success(
    conversation_service, test_user, test_utils, mock_websocket, monkeypatch
):
    """Test successful chat message handling using ConversationService"""
    agent = await test_utils.create_test_agent(test_utils.db, test_user)

    # Use ConversationService to create conversation
    conversation = conversation_service.create_conversation(
        user_id=test_user.id, agent_id=agent.id
    )

    async def fake_chat_completion(*args, **kwargs):
        return LLMResponse(content="ok", model="m", provider="p", usage={"tokens": 5})

    # Mock the UnifiedLLMService.chat_completion method
    monkeypatch.setattr(UnifiedLLMService, "chat_completion", fake_chat_completion)

    handler = WebSocketHandler(mock_websocket, test_user, test_utils.db)
    await handler._handle_chat_message(
        {"conversation_id": conversation.id, "content": "hi"}
    )

    # Refresh conversation to get updated values
    updated_conversation = conversation_service.get_conversation_by_id(conversation.id)
    assert updated_conversation.message_count == 2
    assert updated_conversation.total_tokens_used == 5


@pytest.mark.asyncio
async def test_handle_chat_message_failure(
    conversation_service, test_user, test_utils, mock_websocket, monkeypatch
):
    """Test chat message handling failure using ConversationService"""
    agent = await test_utils.create_test_agent(test_utils.db, test_user)

    # Use ConversationService to create conversation
    conversation = conversation_service.create_conversation(
        user_id=test_user.id, agent_id=agent.id
    )

    async def fake_fail(*args, **kwargs):
        raise RuntimeError("fail")

    # Mock the UnifiedLLMService.chat_completion method to fail
    monkeypatch.setattr(UnifiedLLMService, "chat_completion", fake_fail)

    handler = WebSocketHandler(mock_websocket, test_user, test_utils.db)
    await handler._handle_chat_message(
        {"conversation_id": conversation.id, "content": "hi"}
    )

    # Refresh conversation to get updated values
    updated_conversation = conversation_service.get_conversation_by_id(conversation.id)
    assert updated_conversation.message_count == 1
    assert updated_conversation.total_tokens_used == 0
