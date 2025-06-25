"""
Adiciona tabelas essenciais para otimização LLM completa
Baseado na análise de estrutura de banco otimizada para chat LLM
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = 'a5f72854'
down_revision = '10fc63eb296d'
branch_labels = None
depends_on = None

def upgrade():
    """Adiciona tabelas de otimização LLM"""
    
    # 1. Tabela de catálogo de LLMs disponíveis
    op.create_table(
        'llms',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('provider', sa.String(50), nullable=False),
        sa.Column('model_version', sa.String(50), nullable=True),
        sa.Column('cost_per_token_input', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('cost_per_token_output', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('max_tokens_supported', sa.Integer(), nullable=True),
        sa.Column('supports_function_calling', sa.Boolean(), server_default='false'),
        sa.Column('supports_vision', sa.Boolean(), server_default='false'),
        sa.Column('supports_streaming', sa.Boolean(), server_default='true'),
        sa.Column('context_window', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default='true'),
        sa.Column('llm_metadata', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        schema='synapscale_db'
    )
    op.create_index('ix_llms_provider', 'llms', ['provider'], schema='synapscale_db')
    op.create_index('ix_llms_name', 'llms', ['name'], schema='synapscale_db')
    op.create_index('ix_llms_is_active', 'llms', ['is_active'], schema='synapscale_db')

    # 2. Relacionamento conversations <-> LLMs
    op.create_table(
        'llms_conversations_turns',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('conversation_id', sa.UUID(), nullable=False),
        sa.Column('llm_id', sa.UUID(), nullable=False),
        sa.Column('first_used_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('last_used_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('message_count', sa.Integer(), server_default='0'),
        sa.Column('total_input_tokens', sa.Integer(), server_default='0'),
        sa.Column('total_output_tokens', sa.Integer(), server_default='0'),
        sa.Column('total_cost_usd', sa.Float(), server_default='0.0'),
        sa.ForeignKeyConstraint(['conversation_id'], ['synapscale_db.llms_conversations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['llm_id'], ['synapscale_db.llms.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        schema='synapscale_db'
    )
    op.create_index('ix_llms_conversations_turns_conversation_id', 'llms_conversations_turns', ['conversation_id'], schema='synapscale_db')
    op.create_index('ix_llms_conversations_turns_llm_id', 'llms_conversations_turns', ['llm_id'], schema='synapscale_db')

    # 3. Logs de uso detalhados para billing e analytics
    op.create_table(
        'llms_usage_logs',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('message_id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('conversation_id', sa.UUID(), nullable=False),
        sa.Column('llm_id', sa.UUID(), nullable=False),
        sa.Column('workspace_id', sa.UUID(), nullable=True),
        sa.Column('input_tokens', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('output_tokens', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_tokens', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('cost_usd', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('latency_ms', sa.Integer(), nullable=True),
        sa.Column('api_status_code', sa.Integer(), nullable=True),
        sa.Column('api_request_payload', sa.JSON(), nullable=True),
        sa.Column('api_response_metadata', sa.JSON(), nullable=True),
        sa.Column('user_api_key_used', sa.Boolean(), server_default='false'),
        sa.Column('model_settings', sa.JSON(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('status', sa.String(20), server_default='success'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['message_id'], ['synapscale_db.llms_messages.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['synapscale_db.users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['conversation_id'], ['synapscale_db.llms_conversations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['llm_id'], ['synapscale_db.llms.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['workspace_id'], ['synapscale_db.workspaces.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        schema='synapscale_db'
    )
    op.create_index('ix_llms_usage_logs_user_id', 'llms_usage_logs', ['user_id'], schema='synapscale_db')
    op.create_index('ix_llms_usage_logs_conversation_id', 'llms_usage_logs', ['conversation_id'], schema='synapscale_db')
    op.create_index('ix_llms_usage_logs_llm_id', 'llms_usage_logs', ['llm_id'], schema='synapscale_db')
    op.create_index('ix_llms_usage_logs_created_at', 'llms_usage_logs', ['created_at'], schema='synapscale_db')
    op.create_index('ix_llms_usage_logs_workspace_id', 'llms_usage_logs', ['workspace_id'], schema='synapscale_db')

    # 4. Eventos de billing para cobrança e controle de saldo
    op.create_table(
        'billing_events',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('workspace_id', sa.UUID(), nullable=True),
        sa.Column('event_type', sa.String(50), nullable=False),  # usage, subscription, credit, refund
        sa.Column('amount_usd', sa.Float(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('related_usage_log_id', sa.UUID(), nullable=True),
        sa.Column('related_message_id', sa.UUID(), nullable=True),
        sa.Column('invoice_id', sa.String(100), nullable=True),
        sa.Column('payment_provider', sa.String(50), nullable=True),
        sa.Column('payment_transaction_id', sa.String(100), nullable=True),
        sa.Column('billing_metadata', sa.JSON(), nullable=True),
        sa.Column('status', sa.String(20), server_default='pending'),  # pending, completed, failed, refunded
        sa.Column('processed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['synapscale_db.users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['workspace_id'], ['synapscale_db.workspaces.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['related_usage_log_id'], ['synapscale_db.llms_usage_logs.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['related_message_id'], ['synapscale_db.llms_messages.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        schema='synapscale_db'
    )
    op.create_index('ix_billing_events_user_id', 'billing_events', ['user_id'], schema='synapscale_db')
    op.create_index('ix_billing_events_workspace_id', 'billing_events', ['workspace_id'], schema='synapscale_db')
    op.create_index('ix_billing_events_event_type', 'billing_events', ['event_type'], schema='synapscale_db')
    op.create_index('ix_billing_events_created_at', 'billing_events', ['created_at'], schema='synapscale_db')
    op.create_index('ix_billing_events_status', 'billing_events', ['status'], schema='synapscale_db')

    # 5. Sistema de feedback melhorado
    op.create_table(
        'llms_message_feedbacks',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('message_id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('rating_type', sa.String(20), nullable=False),  # thumbs_up, thumbs_down, star_rating
        sa.Column('rating_value', sa.Integer(), nullable=True),  # 1-5 para stars, 1/-1 para thumbs
        sa.Column('feedback_text', sa.Text(), nullable=True),
        sa.Column('feedback_category', sa.String(50), nullable=True),  # helpful, accurate, creative, etc
        sa.Column('improvement_suggestions', sa.Text(), nullable=True),
        sa.Column('is_public', sa.Boolean(), server_default='false'),
        sa.Column('feedback_metadata', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['message_id'], ['synapscale_db.llms_messages.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['synapscale_db.users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        schema='synapscale_db'
    )
    op.create_index('ix_llms_message_feedbacks_message_id', 'llms_message_feedbacks', ['message_id'], schema='synapscale_db')
    op.create_index('ix_llms_message_feedbacks_user_id', 'llms_message_feedbacks', ['user_id'], schema='synapscale_db')
    op.create_index('ix_llms_message_feedbacks_rating_type', 'llms_message_feedbacks', ['rating_type'], schema='synapscale_db')

    # Inserir LLMs padrão
    op.execute("""
        INSERT INTO synapscale_db.llms (id, name, provider, model_version, cost_per_token_input, cost_per_token_output, max_tokens_supported, supports_function_calling, supports_vision, context_window) VALUES
        -- OpenAI
        (gen_random_uuid(), 'gpt-4o', 'openai', '2024-05-13', 0.000005, 0.000015, 4096, true, true, 128000),
        (gen_random_uuid(), 'gpt-4o-mini', 'openai', '2024-07-18', 0.00000015, 0.0000006, 16384, true, true, 128000),
        (gen_random_uuid(), 'gpt-4-turbo', 'openai', '2024-04-09', 0.00001, 0.00003, 4096, true, true, 128000),
        (gen_random_uuid(), 'gpt-3.5-turbo', 'openai', '2024-01-25', 0.0000005, 0.0000015, 4096, true, false, 16385),
        -- Anthropic
        (gen_random_uuid(), 'claude-3-opus', 'anthropic', '20240229', 0.000015, 0.000075, 4096, true, true, 200000),
        (gen_random_uuid(), 'claude-3-sonnet', 'anthropic', '20240229', 0.000003, 0.000015, 4096, true, true, 200000),
        (gen_random_uuid(), 'claude-3-haiku', 'anthropic', '20240307', 0.00000025, 0.00000125, 4096, true, true, 200000),
        -- Google
        (gen_random_uuid(), 'gemini-1.5-pro', 'google', 'latest', 0.0000035, 0.0000105, 8192, true, true, 2000000),
        (gen_random_uuid(), 'gemini-1.5-flash', 'google', 'latest', 0.000000075, 0.0000003, 8192, true, true, 1000000),
        -- Outros
        (gen_random_uuid(), 'grok-2', 'grok', 'latest', 0.000002, 0.00001, 8192, false, false, 131072),
        (gen_random_uuid(), 'deepseek-chat', 'deepseek', 'latest', 0.00000014, 0.00000028, 4096, false, false, 32768),
        (gen_random_uuid(), 'llama-3.1-405b', 'llama', 'latest', 0.000002, 0.000002, 4096, false, false, 128000)
    """)

def downgrade():
    """Remove tabelas de otimização LLM"""
    op.drop_table('llms_message_feedbacks', schema='synapscale_db')
    op.drop_table('billing_events', schema='synapscale_db')
    op.drop_table('llms_usage_logs', schema='synapscale_db')
    op.drop_table('llms_conversations_turns', schema='synapscale_db')
    op.drop_table('llms', schema='synapscale_db') 