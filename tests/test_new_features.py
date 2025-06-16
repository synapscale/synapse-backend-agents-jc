import pytest
from httpx import AsyncClient

from synapse.models.conversation import Conversation
from synapse.models.workflow_execution import WorkflowExecution


@pytest.mark.asyncio
async def test_workflow_execute_and_list(
    async_client: AsyncClient, db_session, test_user, test_utils, auth_headers
):
    workflow = await test_utils.create_test_workflow(db_session, test_user)

    resp = await async_client.post(f"/api/v1/workflows/{workflow.id}/execute", json={}, headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "pending"

    list_resp = await async_client.get(f"/api/v1/workflows/{workflow.id}/executions", headers=auth_headers)
    assert list_resp.status_code == 200
    list_data = list_resp.json()
    assert list_data["total"] >= 1
    assert len(list_data["items"]) >= 1


@pytest.mark.asyncio
async def test_node_rating(
    async_client: AsyncClient, db_session, test_user, test_utils, auth_headers
):
    node = await test_utils.create_test_node(db_session, test_user)

    resp = await async_client.post(
        f"/api/v1/nodes/{node.id}/rate", params={"rating": 4}, headers=auth_headers
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["rating_average"] == 4
    assert data["rating_count"] == 1


@pytest.mark.asyncio
async def test_conversation_agent_message(
    async_client: AsyncClient, db_session, test_user, test_utils, auth_headers
):
    agent = await test_utils.create_test_agent(db_session, test_user)
    # Criar conversa via API
    resp_conv = await async_client.post(
        "/api/v1/conversations/",
        json={"agent_id": str(agent.id)},
        headers=auth_headers,
    )
    assert resp_conv.status_code == 200
    conversation_id = resp_conv.json()["id"]

    resp = await async_client.post(
        f"/api/v1/conversations/{conversation_id}/messages", json={"content": "Hello"}, headers=auth_headers
    )
    assert resp.status_code == 200

    messages_resp = await async_client.get(
        f"/api/v1/conversations/{conversation_id}/messages", headers=auth_headers
    )
    assert messages_resp.status_code == 200
    assert messages_resp.json()["total"] == 2
