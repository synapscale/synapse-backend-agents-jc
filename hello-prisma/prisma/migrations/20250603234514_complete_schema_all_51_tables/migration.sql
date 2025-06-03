/*
  Warnings:

  - You are about to drop the `Post` table. If the table is not empty, all the data it contains will be lost.
  - You are about to drop the `User` table. If the table is not empty, all the data it contains will be lost.

*/
-- DropForeignKey
ALTER TABLE "Post" DROP CONSTRAINT "Post_authorId_fkey";

-- DropTable
DROP TABLE "Post";

-- DropTable
DROP TABLE "User";

-- CreateTable
CREATE TABLE "agents" (
    "id" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "description" TEXT,
    "user_id" TEXT NOT NULL,
    "workspace_id" TEXT,
    "personality" TEXT,
    "instructions" TEXT,
    "agent_type" TEXT,
    "model_provider" TEXT,
    "model_name" TEXT,
    "temperature" DOUBLE PRECISION,
    "max_tokens" INTEGER,
    "top_p" DOUBLE PRECISION,
    "frequency_penalty" DOUBLE PRECISION,
    "presence_penalty" DOUBLE PRECISION,
    "tools" JSONB,
    "knowledge_base" JSONB,
    "capabilities" JSONB,
    "status" TEXT,
    "avatar_url" TEXT,
    "configuration" JSONB,
    "conversation_count" INTEGER,
    "message_count" INTEGER,
    "total_tokens_used" INTEGER,
    "average_response_time" DOUBLE PRECISION,
    "rating_average" DOUBLE PRECISION,
    "rating_count" INTEGER,
    "last_active_at" TIMESTAMP(3),
    "created_at" TIMESTAMP(3) DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "agents_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "analytics_alerts" (
    "id" SERIAL NOT NULL,
    "user_id" INTEGER NOT NULL,
    "name" TEXT NOT NULL,
    "description" TEXT,
    "rule_config" TEXT,
    "notification_config" TEXT,
    "status" TEXT,
    "last_triggered" TIMESTAMP(3),
    "created_at" TIMESTAMP(3) DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "analytics_alerts_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "analytics_dashboards" (
    "id" SERIAL NOT NULL,
    "user_id" INTEGER NOT NULL,
    "name" TEXT NOT NULL,
    "description" TEXT,
    "layout" TEXT,
    "widgets" TEXT,
    "is_public" BOOLEAN,
    "created_at" TIMESTAMP(3) DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "analytics_dashboards_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "analytics_events" (
    "id" SERIAL NOT NULL,
    "user_id" INTEGER,
    "session_id" TEXT,
    "event_type" TEXT NOT NULL,
    "event_name" TEXT NOT NULL,
    "properties" TEXT,
    "timestamp" TIMESTAMP(3) DEFAULT CURRENT_TIMESTAMP,
    "ip_address" TEXT,
    "user_agent" TEXT,
    "page_url" TEXT,
    "referrer" TEXT,

    CONSTRAINT "analytics_events_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "analytics_exports" (
    "id" SERIAL NOT NULL,
    "user_id" INTEGER NOT NULL,
    "export_type" TEXT NOT NULL,
    "query_config" TEXT,
    "format" TEXT NOT NULL,
    "status" TEXT,
    "file_path" TEXT,
    "file_size" INTEGER,
    "created_at" TIMESTAMP(3) DEFAULT CURRENT_TIMESTAMP,
    "completed_at" TIMESTAMP(3),
    "expires_at" TIMESTAMP(3),

    CONSTRAINT "analytics_exports_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "analytics_metrics" (
    "id" SERIAL NOT NULL,
    "metric_type" TEXT NOT NULL,
    "metric_name" TEXT NOT NULL,
    "value" TEXT NOT NULL,
    "dimensions" TEXT,
    "timestamp" TIMESTAMP(3) NOT NULL,
    "granularity" TEXT NOT NULL,
    "created_at" TIMESTAMP(3) DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "analytics_metrics_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "analytics_reports" (
    "id" SERIAL NOT NULL,
    "user_id" INTEGER NOT NULL,
    "name" TEXT NOT NULL,
    "description" TEXT,
    "query_config" TEXT,
    "schedule_config" TEXT,
    "status" TEXT,
    "created_at" TIMESTAMP(3) DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "analytics_reports_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "business_metrics" (
    "id" SERIAL NOT NULL,
    "date" TIMESTAMP(3) NOT NULL,
    "period_type" TEXT NOT NULL,
    "total_users" INTEGER NOT NULL,
    "new_users" INTEGER NOT NULL,
    "active_users" INTEGER NOT NULL,
    "churned_users" INTEGER NOT NULL,
    "total_sessions" INTEGER NOT NULL,
    "avg_session_duration" DOUBLE PRECISION NOT NULL,
    "total_page_views" INTEGER NOT NULL,
    "bounce_rate" DOUBLE PRECISION NOT NULL,
    "workflows_created" INTEGER NOT NULL,
    "workflows_executed" INTEGER NOT NULL,
    "components_published" INTEGER NOT NULL,
    "components_downloaded" INTEGER NOT NULL,
    "workspaces_created" INTEGER NOT NULL,
    "teams_formed" INTEGER NOT NULL,
    "collaborative_sessions" INTEGER NOT NULL,
    "total_revenue" DOUBLE PRECISION NOT NULL,
    "recurring_revenue" DOUBLE PRECISION NOT NULL,
    "marketplace_revenue" DOUBLE PRECISION NOT NULL,
    "avg_revenue_per_user" DOUBLE PRECISION NOT NULL,
    "error_rate" DOUBLE PRECISION NOT NULL,
    "avg_response_time" DOUBLE PRECISION NOT NULL,
    "uptime_percentage" DOUBLE PRECISION NOT NULL,
    "customer_satisfaction" DOUBLE PRECISION NOT NULL,
    "created_at" TIMESTAMP(3) NOT NULL,
    "updated_at" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "business_metrics_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "component_downloads" (
    "id" SERIAL NOT NULL,
    "component_id" INTEGER NOT NULL,
    "user_id" INTEGER NOT NULL,
    "version" TEXT,
    "download_date" TIMESTAMP(3) DEFAULT CURRENT_TIMESTAMP,
    "ip_address" TEXT,
    "user_agent" TEXT,

    CONSTRAINT "component_downloads_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "component_favorites" (
    "id" SERIAL NOT NULL,
    "component_id" INTEGER NOT NULL,
    "user_id" INTEGER NOT NULL,
    "created_at" TIMESTAMP(3) DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "component_favorites_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "component_purchases" (
    "id" SERIAL NOT NULL,
    "component_id" INTEGER NOT NULL,
    "user_id" INTEGER NOT NULL,
    "amount" TEXT NOT NULL,
    "currency" TEXT,
    "payment_method" TEXT,
    "transaction_id" TEXT,
    "status" TEXT,
    "purchased_at" TIMESTAMP(3) DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "component_purchases_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "component_ratings" (
    "id" SERIAL NOT NULL,
    "component_id" INTEGER NOT NULL,
    "user_id" INTEGER NOT NULL,
    "rating" INTEGER NOT NULL,
    "review" TEXT,
    "helpful_count" INTEGER,
    "created_at" TIMESTAMP(3) DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "component_ratings_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "component_versions" (
    "id" SERIAL NOT NULL,
    "component_id" INTEGER NOT NULL,
    "version" TEXT NOT NULL,
    "content" TEXT,
    "changelog" TEXT,
    "file_path" TEXT,
    "file_size" INTEGER,
    "downloads_count" INTEGER,
    "is_latest" BOOLEAN,
    "created_at" TIMESTAMP(3) DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "component_versions_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "conversations" (
    "id" TEXT NOT NULL,
    "user_id" TEXT NOT NULL,
    "agent_id" TEXT,
    "workspace_id" TEXT,
    "title" TEXT,
    "status" TEXT,
    "message_count" INTEGER,
    "total_tokens_used" INTEGER,
    "context" JSONB,
    "settings" JSONB,
    "last_message_at" TIMESTAMP(3),
    "created_at" TIMESTAMP(3) DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "conversations_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "custom_reports" (
    "id" SERIAL NOT NULL,
    "user_id" INTEGER NOT NULL,
    "workspace_id" INTEGER,
    "name" TEXT NOT NULL,
    "description" TEXT,
    "category" TEXT,
    "query_config" JSONB NOT NULL,
    "visualization_config" JSONB,
    "filters" JSONB,
    "is_scheduled" BOOLEAN NOT NULL,
    "schedule_config" JSONB,
    "last_run_at" TIMESTAMP(3),
    "next_run_at" TIMESTAMP(3),
    "is_public" BOOLEAN NOT NULL,
    "shared_with" JSONB,
    "cached_data" JSONB,
    "cache_expires_at" TIMESTAMP(3),
    "status" TEXT NOT NULL,
    "created_at" TIMESTAMP(3) NOT NULL,
    "updated_at" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "custom_reports_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "email_verification_tokens" (
    "id" TEXT NOT NULL,
    "token" TEXT NOT NULL,
    "user_id" TEXT NOT NULL,
    "expires_at" TIMESTAMP(3) NOT NULL,
    "is_used" BOOLEAN,
    "created_at" TIMESTAMP(3) DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "email_verification_tokens_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "execution_metrics" (
    "id" SERIAL NOT NULL,
    "workflow_execution_id" INTEGER NOT NULL,
    "node_execution_id" INTEGER,
    "metric_type" TEXT NOT NULL,
    "metric_name" TEXT NOT NULL,
    "value_numeric" INTEGER,
    "value_float" TEXT,
    "value_text" TEXT,
    "value_json" JSONB,
    "context" TEXT,
    "tags" JSONB,
    "measured_at" TIMESTAMP(3) DEFAULT CURRENT_TIMESTAMP,
    "created_at" TIMESTAMP(3) DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "execution_metrics_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "execution_queue" (
    "id" SERIAL NOT NULL,
    "queue_id" TEXT NOT NULL,
    "workflow_execution_id" INTEGER NOT NULL,
    "user_id" INTEGER NOT NULL,
    "priority" INTEGER,
    "scheduled_at" TIMESTAMP(3),
    "started_at" TIMESTAMP(3),
    "completed_at" TIMESTAMP(3),
    "status" TEXT,
    "worker_id" TEXT,
    "max_execution_time" INTEGER,
    "retry_count" INTEGER,
    "max_retries" INTEGER,
    "metadata" JSONB,
    "created_at" TIMESTAMP(3) DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "execution_queue_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "files" (
    "id" SERIAL NOT NULL,
    "filename" TEXT NOT NULL,
    "original_filename" TEXT NOT NULL,
    "content_type" TEXT NOT NULL,
    "file_size" INTEGER NOT NULL,
    "file_hash" TEXT NOT NULL,
    "storage_path" TEXT NOT NULL,
    "tags" TEXT,
    "description" TEXT,
    "is_public" TEXT NOT NULL DEFAULT '''false''',
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "files_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "marketplace_components" (
    "id" SERIAL NOT NULL,
    "name" TEXT NOT NULL,
    "description" TEXT,
    "category" TEXT NOT NULL,
    "component_type" TEXT NOT NULL,
    "tags" TEXT,
    "price" TEXT,
    "is_free" BOOLEAN,
    "author_id" INTEGER NOT NULL,
    "version" TEXT NOT NULL DEFAULT '''1.0.0''',
    "content" TEXT,
    "metadata" TEXT,
    "downloads_count" INTEGER,
    "rating_average" TEXT,
    "rating_count" INTEGER,
    "is_featured" BOOLEAN,
    "is_approved" BOOLEAN,
    "status" TEXT,
    "created_at" TIMESTAMP(3) DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "marketplace_components_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "messages" (
    "id" TEXT NOT NULL,
    "conversation_id" TEXT NOT NULL,
    "role" TEXT NOT NULL,
    "content" TEXT NOT NULL,
    "attachments" JSONB,
    "model_used" TEXT,
    "model_provider" TEXT,
    "tokens_used" INTEGER,
    "processing_time_ms" INTEGER,
    "temperature" DOUBLE PRECISION,
    "max_tokens" INTEGER,
    "status" TEXT,
    "error_message" TEXT,
    "rating" INTEGER,
    "feedback" TEXT,
    "created_at" TIMESTAMP(3) DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "messages_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "node_categories" (
    "id" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "description" TEXT,
    "icon" TEXT,
    "color" TEXT,
    "parent_id" TEXT,
    "sort_order" INTEGER,
    "is_active" BOOLEAN,
    "created_at" TIMESTAMP(3) DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "node_categories_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "node_executions" (
    "id" SERIAL NOT NULL,
    "execution_id" TEXT NOT NULL,
    "workflow_execution_id" INTEGER NOT NULL,
    "node_id" INTEGER NOT NULL,
    "node_key" TEXT NOT NULL,
    "node_type" TEXT NOT NULL,
    "node_name" TEXT,
    "status" TEXT,
    "execution_order" INTEGER NOT NULL,
    "input_data" JSONB,
    "output_data" JSONB,
    "config_data" JSONB,
    "started_at" TIMESTAMP(3),
    "completed_at" TIMESTAMP(3),
    "timeout_at" TIMESTAMP(3),
    "duration_ms" INTEGER,
    "execution_log" TEXT,
    "error_message" TEXT,
    "error_details" JSONB,
    "debug_info" JSONB,
    "retry_count" INTEGER,
    "max_retries" INTEGER,
    "retry_delay" INTEGER,
    "dependencies" JSONB,
    "dependents" JSONB,
    "metadata" JSONB,
    "created_at" TIMESTAMP(3) DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "node_executions_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "node_templates" (
    "id" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "description" TEXT,
    "type" TEXT NOT NULL,
    "category" TEXT,
    "code_template" TEXT NOT NULL,
    "input_schema" JSONB NOT NULL,
    "output_schema" JSONB NOT NULL,
    "parameters_schema" JSONB,
    "icon" TEXT,
    "color" TEXT,
    "documentation" TEXT,
    "examples" JSONB,
    "is_system" BOOLEAN,
    "is_active" BOOLEAN,
    "created_at" TIMESTAMP(3) DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "node_templates_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "nodes" (
    "id" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "description" TEXT,
    "type" TEXT NOT NULL,
    "category" TEXT,
    "user_id" TEXT NOT NULL,
    "workspace_id" TEXT,
    "is_public" BOOLEAN,
    "status" TEXT,
    "code_template" TEXT NOT NULL,
    "input_schema" JSONB NOT NULL,
    "output_schema" JSONB NOT NULL,
    "parameters_schema" JSONB,
    "version" TEXT,
    "icon" TEXT,
    "color" TEXT,
    "documentation" TEXT,
    "examples" JSONB,
    "downloads_count" INTEGER,
    "usage_count" INTEGER,
    "rating_average" INTEGER,
    "rating_count" INTEGER,
    "created_at" TIMESTAMP(3) DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "nodes_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "password_reset_tokens" (
    "id" TEXT NOT NULL,
    "token" TEXT NOT NULL,
    "user_id" TEXT NOT NULL,
    "expires_at" TIMESTAMP(3) NOT NULL,
    "is_used" BOOLEAN,
    "created_at" TIMESTAMP(3) DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "password_reset_tokens_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "project_collaborators" (
    "id" SERIAL NOT NULL,
    "project_id" INTEGER NOT NULL,
    "user_id" INTEGER NOT NULL,
    "permissions" TEXT,
    "added_by" INTEGER NOT NULL,
    "added_at" TIMESTAMP(3) DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "project_collaborators_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "project_comments" (
    "id" SERIAL NOT NULL,
    "project_id" INTEGER NOT NULL,
    "user_id" INTEGER NOT NULL,
    "content" TEXT NOT NULL,
    "node_id" TEXT,
    "position_x" TEXT,
    "position_y" TEXT,
    "is_resolved" BOOLEAN,
    "resolved_by" INTEGER,
    "resolved_at" TIMESTAMP(3),
    "created_at" TIMESTAMP(3) DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "project_comments_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "project_versions" (
    "id" SERIAL NOT NULL,
    "project_id" INTEGER NOT NULL,
    "version" TEXT NOT NULL,
    "workflow_data" TEXT,
    "description" TEXT,
    "created_by" INTEGER NOT NULL,
    "created_at" TIMESTAMP(3) DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "project_versions_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "refresh_tokens" (
    "id" TEXT NOT NULL,
    "token" TEXT NOT NULL,
    "user_id" TEXT NOT NULL,
    "expires_at" TIMESTAMP(3) NOT NULL,
    "is_revoked" BOOLEAN,
    "created_at" TIMESTAMP(3) DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "refresh_tokens_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "report_executions" (
    "id" SERIAL NOT NULL,
    "report_id" INTEGER NOT NULL,
    "status" TEXT,
    "result_data" TEXT,
    "error_message" TEXT,
    "started_at" TIMESTAMP(3) DEFAULT CURRENT_TIMESTAMP,
    "completed_at" TIMESTAMP(3),

    CONSTRAINT "report_executions_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "system_performance_metrics" (
    "id" SERIAL NOT NULL,
    "metric_name" TEXT NOT NULL,
    "metric_type" TEXT NOT NULL,
    "service" TEXT NOT NULL,
    "environment" TEXT NOT NULL,
    "value" DOUBLE PRECISION NOT NULL,
    "unit" TEXT,
    "tags" JSONB,
    "timestamp" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "system_performance_metrics_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "template_collections" (
    "id" SERIAL NOT NULL,
    "collection_id" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "description" TEXT,
    "creator_id" INTEGER NOT NULL,
    "is_public" BOOLEAN,
    "is_featured" BOOLEAN,
    "template_ids" JSONB NOT NULL,
    "tags" JSONB,
    "thumbnail_url" TEXT,
    "view_count" INTEGER,
    "follow_count" INTEGER,
    "created_at" TIMESTAMP(3) DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "template_collections_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "template_downloads" (
    "id" SERIAL NOT NULL,
    "template_id" INTEGER NOT NULL,
    "user_id" INTEGER NOT NULL,
    "download_type" TEXT,
    "ip_address" TEXT,
    "user_agent" TEXT,
    "template_version" TEXT,
    "downloaded_at" TIMESTAMP(3) DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "template_downloads_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "template_favorites" (
    "id" SERIAL NOT NULL,
    "template_id" INTEGER NOT NULL,
    "user_id" INTEGER NOT NULL,
    "notes" TEXT,
    "created_at" TIMESTAMP(3) DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "template_favorites_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "template_reviews" (
    "id" SERIAL NOT NULL,
    "template_id" INTEGER NOT NULL,
    "user_id" INTEGER NOT NULL,
    "rating" INTEGER NOT NULL,
    "title" TEXT,
    "comment" TEXT,
    "ease_of_use" INTEGER,
    "documentation_quality" INTEGER,
    "performance" INTEGER,
    "value_for_money" INTEGER,
    "is_verified_purchase" BOOLEAN,
    "is_helpful_count" INTEGER,
    "is_reported" BOOLEAN,
    "version_reviewed" TEXT,
    "created_at" TIMESTAMP(3) DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "template_reviews_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "template_usage" (
    "id" SERIAL NOT NULL,
    "template_id" INTEGER NOT NULL,
    "user_id" INTEGER NOT NULL,
    "workflow_id" INTEGER,
    "usage_type" TEXT NOT NULL,
    "success" BOOLEAN,
    "template_version" TEXT,
    "modifications_made" JSONB,
    "execution_time" INTEGER,
    "ip_address" TEXT,
    "user_agent" TEXT,
    "used_at" TIMESTAMP(3) DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "template_usage_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "user_behavior_metrics" (
    "id" SERIAL NOT NULL,
    "user_id" INTEGER NOT NULL,
    "date" TIMESTAMP(3) NOT NULL,
    "period_type" TEXT NOT NULL,
    "session_count" INTEGER NOT NULL,
    "total_session_duration" INTEGER NOT NULL,
    "avg_session_duration" DOUBLE PRECISION NOT NULL,
    "page_views" INTEGER NOT NULL,
    "unique_pages_visited" INTEGER NOT NULL,
    "workflows_created" INTEGER NOT NULL,
    "workflows_executed" INTEGER NOT NULL,
    "components_used" INTEGER NOT NULL,
    "collaborations_initiated" INTEGER NOT NULL,
    "marketplace_purchases" INTEGER NOT NULL,
    "revenue_generated" DOUBLE PRECISION NOT NULL,
    "components_published" INTEGER NOT NULL,
    "error_count" INTEGER NOT NULL,
    "support_tickets" INTEGER NOT NULL,
    "feature_requests" INTEGER NOT NULL,
    "engagement_score" DOUBLE PRECISION NOT NULL,
    "satisfaction_score" DOUBLE PRECISION NOT NULL,
    "value_score" DOUBLE PRECISION NOT NULL,
    "created_at" TIMESTAMP(3) NOT NULL,
    "updated_at" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "user_behavior_metrics_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "user_insights" (
    "id" SERIAL NOT NULL,
    "user_id" INTEGER NOT NULL,
    "insight_type" TEXT NOT NULL,
    "category" TEXT NOT NULL,
    "priority" TEXT NOT NULL,
    "title" TEXT NOT NULL,
    "description" TEXT NOT NULL,
    "recommendation" TEXT,
    "supporting_data" JSONB,
    "confidence_score" DOUBLE PRECISION NOT NULL,
    "suggested_action" TEXT,
    "action_url" TEXT,
    "action_data" JSONB,
    "is_read" BOOLEAN NOT NULL,
    "is_dismissed" BOOLEAN NOT NULL,
    "is_acted_upon" BOOLEAN NOT NULL,
    "user_feedback" TEXT,
    "expires_at" TIMESTAMP(3),
    "is_evergreen" BOOLEAN NOT NULL,
    "created_at" TIMESTAMP(3) NOT NULL,
    "read_at" TIMESTAMP(3),
    "acted_at" TIMESTAMP(3),

    CONSTRAINT "user_insights_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "user_variables" (
    "id" SERIAL NOT NULL,
    "user_id" INTEGER NOT NULL,
    "key" TEXT NOT NULL,
    "value" TEXT NOT NULL,
    "description" TEXT,
    "is_encrypted" BOOLEAN NOT NULL,
    "is_active" BOOLEAN NOT NULL,
    "category" TEXT,
    "created_at" TIMESTAMP(3) NOT NULL,
    "updated_at" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "user_variables_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "users" (
    "id" TEXT NOT NULL,
    "email" TEXT NOT NULL,
    "password_hash" TEXT NOT NULL,
    "first_name" TEXT,
    "last_name" TEXT,
    "avatar_url" TEXT,
    "is_active" BOOLEAN,
    "is_verified" BOOLEAN,
    "role" TEXT,
    "subscription_plan" TEXT,
    "preferences" JSONB,
    "created_at" TIMESTAMP(3) DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "users_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "workflow_connections" (
    "id" TEXT NOT NULL,
    "workflow_id" TEXT NOT NULL,
    "source_node_id" TEXT NOT NULL,
    "target_node_id" TEXT NOT NULL,
    "source_port" TEXT,
    "target_port" TEXT,
    "created_at" TIMESTAMP(3) DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "workflow_connections_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "workflow_executions" (
    "id" SERIAL NOT NULL,
    "execution_id" TEXT NOT NULL,
    "workflow_id" INTEGER NOT NULL,
    "user_id" INTEGER NOT NULL,
    "status" TEXT,
    "priority" INTEGER,
    "input_data" JSONB,
    "output_data" JSONB,
    "context_data" JSONB,
    "variables" JSONB,
    "total_nodes" INTEGER,
    "completed_nodes" INTEGER,
    "failed_nodes" INTEGER,
    "progress_percentage" INTEGER,
    "started_at" TIMESTAMP(3),
    "completed_at" TIMESTAMP(3),
    "timeout_at" TIMESTAMP(3),
    "estimated_duration" INTEGER,
    "actual_duration" INTEGER,
    "execution_log" TEXT,
    "error_message" TEXT,
    "error_details" JSONB,
    "debug_info" JSONB,
    "retry_count" INTEGER,
    "max_retries" INTEGER,
    "auto_retry" BOOLEAN,
    "notify_on_completion" BOOLEAN,
    "notify_on_failure" BOOLEAN,
    "tags" JSONB,
    "metadata" JSONB,
    "created_at" TIMESTAMP(3) DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "workflow_executions_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "workflow_nodes" (
    "id" TEXT NOT NULL,
    "workflow_id" TEXT NOT NULL,
    "node_id" TEXT NOT NULL,
    "instance_name" TEXT,
    "position_x" INTEGER NOT NULL,
    "position_y" INTEGER NOT NULL,
    "configuration" JSONB,
    "created_at" TIMESTAMP(3) DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "workflow_nodes_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "workflow_templates" (
    "id" SERIAL NOT NULL,
    "template_id" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "title" TEXT NOT NULL,
    "description" TEXT NOT NULL,
    "short_description" TEXT,
    "author_id" INTEGER NOT NULL,
    "original_workflow_id" INTEGER,
    "category" TEXT NOT NULL,
    "tags" JSONB,
    "status" TEXT,
    "is_public" BOOLEAN,
    "is_featured" BOOLEAN,
    "is_verified" BOOLEAN,
    "license_type" TEXT,
    "price" DOUBLE PRECISION,
    "workflow_data" JSONB NOT NULL,
    "nodes_data" JSONB NOT NULL,
    "connections_data" JSONB,
    "required_variables" JSONB,
    "optional_variables" JSONB,
    "default_config" JSONB,
    "version" TEXT,
    "compatibility_version" TEXT,
    "estimated_duration" INTEGER,
    "complexity_level" INTEGER,
    "download_count" INTEGER,
    "usage_count" INTEGER,
    "rating_average" DOUBLE PRECISION,
    "rating_count" INTEGER,
    "view_count" INTEGER,
    "keywords" JSONB,
    "use_cases" JSONB,
    "industries" JSONB,
    "thumbnail_url" TEXT,
    "preview_images" JSONB,
    "demo_video_url" TEXT,
    "documentation" TEXT,
    "setup_instructions" TEXT,
    "changelog" JSONB,
    "support_email" TEXT,
    "repository_url" TEXT,
    "documentation_url" TEXT,
    "created_at" TIMESTAMP(3) DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) DEFAULT CURRENT_TIMESTAMP,
    "published_at" TIMESTAMP(3),
    "last_used_at" TIMESTAMP(3),

    CONSTRAINT "workflow_templates_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "workflows" (
    "id" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "description" TEXT,
    "user_id" TEXT NOT NULL,
    "workspace_id" TEXT,
    "is_public" BOOLEAN,
    "category" TEXT,
    "tags" JSONB,
    "version" TEXT,
    "status" TEXT,
    "definition" JSONB NOT NULL,
    "thumbnail_url" TEXT,
    "downloads_count" INTEGER,
    "rating_average" INTEGER,
    "rating_count" INTEGER,
    "execution_count" INTEGER,
    "last_executed_at" TIMESTAMP(3),
    "created_at" TIMESTAMP(3) DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "workflows_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "workspace_activities" (
    "id" SERIAL NOT NULL,
    "workspace_id" INTEGER NOT NULL,
    "project_id" INTEGER,
    "user_id" INTEGER NOT NULL,
    "action" TEXT NOT NULL,
    "target_type" TEXT,
    "target_id" INTEGER,
    "metadata" TEXT,
    "created_at" TIMESTAMP(3) DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "workspace_activities_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "workspace_invitations" (
    "id" SERIAL NOT NULL,
    "workspace_id" INTEGER NOT NULL,
    "email" TEXT NOT NULL,
    "role" TEXT,
    "permissions" TEXT,
    "token" TEXT NOT NULL,
    "invited_by" INTEGER NOT NULL,
    "status" TEXT,
    "expires_at" TIMESTAMP(3) NOT NULL,
    "created_at" TIMESTAMP(3) DEFAULT CURRENT_TIMESTAMP,
    "responded_at" TIMESTAMP(3),

    CONSTRAINT "workspace_invitations_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "workspace_members" (
    "id" TEXT NOT NULL,
    "workspace_id" TEXT NOT NULL,
    "user_id" TEXT NOT NULL,
    "role" TEXT,
    "permissions" JSONB,
    "joined_at" TIMESTAMP(3) DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "workspace_members_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "workspace_projects" (
    "id" SERIAL NOT NULL,
    "workspace_id" INTEGER NOT NULL,
    "name" TEXT NOT NULL,
    "description" TEXT,
    "workflow_data" TEXT,
    "status" TEXT,
    "owner_id" INTEGER NOT NULL,
    "created_at" TIMESTAMP(3) DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "workspace_projects_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "workspaces" (
    "id" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "description" TEXT,
    "owner_id" TEXT NOT NULL,
    "is_public" BOOLEAN,
    "settings" JSONB,
    "created_at" TIMESTAMP(3) DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "workspaces_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE UNIQUE INDEX "component_favorites_component_id_user_id_key" ON "component_favorites"("component_id", "user_id");

-- CreateIndex
CREATE UNIQUE INDEX "component_ratings_component_id_user_id_key" ON "component_ratings"("component_id", "user_id");

-- CreateIndex
CREATE UNIQUE INDEX "component_versions_component_id_version_key" ON "component_versions"("component_id", "version");

-- CreateIndex
CREATE UNIQUE INDEX "project_collaborators_project_id_user_id_key" ON "project_collaborators"("project_id", "user_id");

-- CreateIndex
CREATE UNIQUE INDEX "template_favorites_template_id_user_id_key" ON "template_favorites"("template_id", "user_id");

-- CreateIndex
CREATE UNIQUE INDEX "users_email_key" ON "users"("email");

-- CreateIndex
CREATE UNIQUE INDEX "workspace_invitations_email_key" ON "workspace_invitations"("email");
