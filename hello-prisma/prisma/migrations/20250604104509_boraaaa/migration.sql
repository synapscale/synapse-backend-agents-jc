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
CREATE TABLE "users" (
    "id" VARCHAR(30) NOT NULL,
    "email" VARCHAR(255) NOT NULL,
    "username" VARCHAR(100) NOT NULL,
    "full_name" VARCHAR(255),
    "hashed_password" VARCHAR(255) NOT NULL,
    "is_active" BOOLEAN NOT NULL DEFAULT true,
    "is_superuser" BOOLEAN NOT NULL DEFAULT false,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "users_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "agents" (
    "id" VARCHAR(30) NOT NULL,
    "name" VARCHAR(255) NOT NULL,
    "description" TEXT,
    "provider" VARCHAR(100) NOT NULL,
    "model" VARCHAR(100) NOT NULL,
    "system_prompt" TEXT,
    "temperature" DECIMAL(3,2) DEFAULT 0.7,
    "max_tokens" INTEGER DEFAULT 1000,
    "is_active" BOOLEAN NOT NULL DEFAULT true,
    "user_id" VARCHAR(30) NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "agents_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "conversations" (
    "id" VARCHAR(30) NOT NULL,
    "title" VARCHAR(255),
    "user_id" VARCHAR(30) NOT NULL,
    "agent_id" VARCHAR(30),
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "conversations_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "messages" (
    "id" VARCHAR(30) NOT NULL,
    "content" TEXT NOT NULL,
    "role" VARCHAR(20) NOT NULL,
    "conversation_id" VARCHAR(30) NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "messages_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "files" (
    "id" VARCHAR(30) NOT NULL,
    "filename" VARCHAR(255) NOT NULL,
    "original_name" VARCHAR(255) NOT NULL,
    "file_path" VARCHAR(500) NOT NULL,
    "file_size" INTEGER NOT NULL,
    "mime_type" VARCHAR(100) NOT NULL,
    "category" VARCHAR(50) NOT NULL,
    "is_public" BOOLEAN NOT NULL DEFAULT false,
    "user_id" VARCHAR(30) NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "files_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "workflows" (
    "id" VARCHAR(30) NOT NULL,
    "name" VARCHAR(255) NOT NULL,
    "description" TEXT,
    "definition" JSONB NOT NULL,
    "is_active" BOOLEAN NOT NULL DEFAULT true,
    "user_id" VARCHAR(30) NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "workflows_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "workflow_executions" (
    "id" VARCHAR(30) NOT NULL,
    "status" VARCHAR(20) NOT NULL DEFAULT 'pending',
    "input_data" JSONB,
    "output_data" JSONB,
    "error_message" TEXT,
    "workflow_id" VARCHAR(30) NOT NULL,
    "started_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "completed_at" TIMESTAMPTZ,

    CONSTRAINT "workflow_executions_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "nodes" (
    "id" VARCHAR(30) NOT NULL,
    "name" VARCHAR(255) NOT NULL,
    "category" VARCHAR(100) NOT NULL,
    "description" TEXT,
    "version" VARCHAR(50) NOT NULL DEFAULT '1.0.0',
    "definition" JSONB NOT NULL,
    "is_public" BOOLEAN NOT NULL DEFAULT false,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "nodes_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "user_variables" (
    "id" VARCHAR(30) NOT NULL,
    "key" VARCHAR(255) NOT NULL,
    "value" TEXT NOT NULL,
    "is_secret" BOOLEAN NOT NULL DEFAULT false,
    "user_id" VARCHAR(30) NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "user_variables_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "node_executions" (
    "id" VARCHAR(30) NOT NULL,
    "workflow_execution_id" VARCHAR(30) NOT NULL,
    "node_id" VARCHAR(30) NOT NULL,
    "status" VARCHAR(20) NOT NULL DEFAULT 'pending',
    "input_data" JSONB,
    "output_data" JSONB,
    "error_message" TEXT,
    "execution_time_ms" INTEGER NOT NULL DEFAULT 0,
    "started_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "completed_at" TIMESTAMPTZ,

    CONSTRAINT "node_executions_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "execution_queue" (
    "id" VARCHAR(30) NOT NULL,
    "workflow_execution_id" VARCHAR(30) NOT NULL,
    "node_id" VARCHAR(30) NOT NULL,
    "priority" INTEGER NOT NULL DEFAULT 0,
    "scheduled_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "status" VARCHAR(20) NOT NULL DEFAULT 'queued',
    "attempts" INTEGER NOT NULL DEFAULT 0,
    "max_attempts" INTEGER NOT NULL DEFAULT 3,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "execution_queue_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "execution_metrics" (
    "id" VARCHAR(30) NOT NULL,
    "workflow_execution_id" VARCHAR(30) NOT NULL,
    "total_nodes" INTEGER NOT NULL DEFAULT 0,
    "completed_nodes" INTEGER NOT NULL DEFAULT 0,
    "failed_nodes" INTEGER NOT NULL DEFAULT 0,
    "total_execution_time_ms" INTEGER NOT NULL DEFAULT 0,
    "memory_usage_mb" DECIMAL(10,2) NOT NULL DEFAULT 0,
    "cpu_usage_percent" DECIMAL(5,2) NOT NULL DEFAULT 0,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "execution_metrics_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "workflow_templates" (
    "id" VARCHAR(30) NOT NULL,
    "name" VARCHAR(255) NOT NULL,
    "description" TEXT,
    "category" VARCHAR(100) NOT NULL,
    "tags" TEXT,
    "workflow_definition" JSONB NOT NULL,
    "preview_image" VARCHAR(500),
    "author_id" VARCHAR(30) NOT NULL,
    "version" VARCHAR(50) NOT NULL DEFAULT '1.0.0',
    "is_public" BOOLEAN NOT NULL DEFAULT false,
    "is_featured" BOOLEAN NOT NULL DEFAULT false,
    "downloads_count" INTEGER NOT NULL DEFAULT 0,
    "rating_average" DECIMAL(3,2) NOT NULL DEFAULT 0.00,
    "rating_count" INTEGER NOT NULL DEFAULT 0,
    "price" DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    "is_free" BOOLEAN NOT NULL DEFAULT true,
    "license" VARCHAR(50) NOT NULL DEFAULT 'MIT',
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "workflow_templates_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "template_reviews" (
    "id" VARCHAR(30) NOT NULL,
    "template_id" VARCHAR(30) NOT NULL,
    "user_id" VARCHAR(30) NOT NULL,
    "rating" INTEGER NOT NULL,
    "comment" TEXT,
    "is_verified_purchase" BOOLEAN NOT NULL DEFAULT false,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "template_reviews_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "template_downloads" (
    "id" VARCHAR(30) NOT NULL,
    "template_id" VARCHAR(30) NOT NULL,
    "user_id" VARCHAR(30) NOT NULL,
    "download_date" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "ip_address" TEXT,
    "user_agent" TEXT,

    CONSTRAINT "template_downloads_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "template_favorites" (
    "id" VARCHAR(30) NOT NULL,
    "template_id" VARCHAR(30) NOT NULL,
    "user_id" VARCHAR(30) NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "template_favorites_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "template_collections" (
    "id" VARCHAR(30) NOT NULL,
    "name" VARCHAR(255) NOT NULL,
    "description" TEXT,
    "owner_id" VARCHAR(30) NOT NULL,
    "is_public" BOOLEAN NOT NULL DEFAULT false,
    "template_ids" TEXT,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "template_collections_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "template_usage" (
    "id" VARCHAR(30) NOT NULL,
    "template_id" VARCHAR(30) NOT NULL,
    "user_id" VARCHAR(30) NOT NULL,
    "workflow_id" VARCHAR(30),
    "usage_date" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "usage_context" VARCHAR(100),

    CONSTRAINT "template_usage_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "executor_configs" (
    "id" VARCHAR(30) NOT NULL,
    "name" VARCHAR(255) NOT NULL,
    "executor_type" VARCHAR(100) NOT NULL,
    "config" JSONB NOT NULL,
    "is_active" BOOLEAN NOT NULL DEFAULT true,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "executor_configs_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "http_cache" (
    "id" VARCHAR(30) NOT NULL,
    "url_hash" VARCHAR(64) NOT NULL,
    "url" TEXT NOT NULL,
    "method" VARCHAR(10) NOT NULL DEFAULT 'GET',
    "headers" JSONB,
    "response_data" JSONB,
    "status_code" INTEGER,
    "expires_at" TIMESTAMPTZ,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "http_cache_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "executor_metrics" (
    "id" VARCHAR(30) NOT NULL,
    "executor_type" VARCHAR(100) NOT NULL,
    "total_executions" INTEGER NOT NULL DEFAULT 0,
    "successful_executions" INTEGER NOT NULL DEFAULT 0,
    "failed_executions" INTEGER NOT NULL DEFAULT 0,
    "average_execution_time_ms" DECIMAL(10,2) NOT NULL DEFAULT 0,
    "last_execution_at" TIMESTAMPTZ,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "executor_metrics_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "marketplace_components" (
    "id" VARCHAR(30) NOT NULL,
    "name" VARCHAR(255) NOT NULL,
    "description" TEXT,
    "category" VARCHAR(100) NOT NULL,
    "component_type" VARCHAR(50) NOT NULL,
    "tags" TEXT,
    "price" DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    "is_free" BOOLEAN NOT NULL DEFAULT true,
    "author_id" VARCHAR(30) NOT NULL,
    "version" VARCHAR(50) NOT NULL DEFAULT '1.0.0',
    "content" TEXT,
    "metadata" TEXT,
    "downloads_count" INTEGER NOT NULL DEFAULT 0,
    "rating_average" DECIMAL(3,2) NOT NULL DEFAULT 0.00,
    "rating_count" INTEGER NOT NULL DEFAULT 0,
    "is_featured" BOOLEAN NOT NULL DEFAULT false,
    "is_approved" BOOLEAN NOT NULL DEFAULT false,
    "status" VARCHAR(20) NOT NULL DEFAULT 'pending',
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "marketplace_components_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "component_ratings" (
    "id" VARCHAR(30) NOT NULL,
    "component_id" VARCHAR(30) NOT NULL,
    "user_id" VARCHAR(30) NOT NULL,
    "rating" INTEGER NOT NULL,
    "comment" TEXT,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "component_ratings_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "component_downloads" (
    "id" VARCHAR(30) NOT NULL,
    "component_id" VARCHAR(30) NOT NULL,
    "user_id" VARCHAR(30) NOT NULL,
    "download_date" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "ip_address" TEXT,
    "user_agent" TEXT,

    CONSTRAINT "component_downloads_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "component_purchases" (
    "id" VARCHAR(30) NOT NULL,
    "component_id" VARCHAR(30) NOT NULL,
    "user_id" VARCHAR(30) NOT NULL,
    "purchase_price" DECIMAL(10,2) NOT NULL,
    "payment_method" VARCHAR(50),
    "transaction_id" VARCHAR(255),
    "purchase_date" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "component_purchases_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "component_favorites" (
    "id" VARCHAR(30) NOT NULL,
    "component_id" VARCHAR(30) NOT NULL,
    "user_id" VARCHAR(30) NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "component_favorites_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "component_versions" (
    "id" VARCHAR(30) NOT NULL,
    "component_id" VARCHAR(30) NOT NULL,
    "version" VARCHAR(50) NOT NULL,
    "changelog" TEXT,
    "content" TEXT,
    "is_active" BOOLEAN NOT NULL DEFAULT true,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "component_versions_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "workspaces" (
    "id" VARCHAR(30) NOT NULL,
    "name" VARCHAR(255) NOT NULL,
    "description" TEXT,
    "owner_id" VARCHAR(30) NOT NULL,
    "is_public" BOOLEAN NOT NULL DEFAULT false,
    "settings" JSONB NOT NULL DEFAULT '{}',
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "workspaces_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "workspace_members" (
    "id" VARCHAR(30) NOT NULL,
    "workspace_id" VARCHAR(30) NOT NULL,
    "user_id" VARCHAR(30) NOT NULL,
    "role" VARCHAR(20) NOT NULL DEFAULT 'member',
    "permissions" JSONB NOT NULL DEFAULT '{}',
    "joined_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "workspace_members_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "workspace_invitations" (
    "id" VARCHAR(30) NOT NULL,
    "workspace_id" VARCHAR(30) NOT NULL,
    "email" VARCHAR(255) NOT NULL,
    "role" VARCHAR(20) NOT NULL DEFAULT 'member',
    "invited_by" VARCHAR(30) NOT NULL,
    "token" VARCHAR(255) NOT NULL,
    "expires_at" TIMESTAMPTZ NOT NULL,
    "accepted_at" TIMESTAMPTZ,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "workspace_invitations_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "workspace_projects" (
    "id" VARCHAR(30) NOT NULL,
    "workspace_id" VARCHAR(30) NOT NULL,
    "name" VARCHAR(255) NOT NULL,
    "description" TEXT,
    "status" VARCHAR(20) NOT NULL DEFAULT 'active',
    "created_by" VARCHAR(30) NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "workspace_projects_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "project_collaborators" (
    "id" VARCHAR(30) NOT NULL,
    "project_id" VARCHAR(30) NOT NULL,
    "user_id" VARCHAR(30) NOT NULL,
    "role" VARCHAR(20) NOT NULL DEFAULT 'collaborator',
    "added_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "project_collaborators_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "project_comments" (
    "id" VARCHAR(30) NOT NULL,
    "project_id" VARCHAR(30) NOT NULL,
    "user_id" VARCHAR(30) NOT NULL,
    "content" TEXT NOT NULL,
    "parent_comment_id" VARCHAR(30),
    "is_resolved" BOOLEAN NOT NULL DEFAULT false,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "project_comments_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "workspace_activities" (
    "id" VARCHAR(30) NOT NULL,
    "workspace_id" VARCHAR(30) NOT NULL,
    "user_id" VARCHAR(30) NOT NULL,
    "activity_type" VARCHAR(50) NOT NULL,
    "entity_type" VARCHAR(50),
    "entity_id" VARCHAR(30),
    "description" TEXT,
    "metadata" JSONB NOT NULL DEFAULT '{}',
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "workspace_activities_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "project_versions" (
    "id" VARCHAR(30) NOT NULL,
    "project_id" VARCHAR(30) NOT NULL,
    "version" VARCHAR(50) NOT NULL,
    "description" TEXT,
    "data" JSONB NOT NULL,
    "created_by" VARCHAR(30) NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "project_versions_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "analytics_events" (
    "id" VARCHAR(30) NOT NULL,
    "event_type" VARCHAR(100) NOT NULL,
    "user_id" VARCHAR(30),
    "session_id" VARCHAR(255),
    "properties" JSONB NOT NULL DEFAULT '{}',
    "timestamp" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "ip_address" TEXT,
    "user_agent" TEXT,

    CONSTRAINT "analytics_events_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "analytics_metrics" (
    "id" VARCHAR(30) NOT NULL,
    "metric_name" VARCHAR(100) NOT NULL,
    "metric_value" DECIMAL(15,4) NOT NULL,
    "dimensions" JSONB NOT NULL DEFAULT '{}',
    "timestamp" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "analytics_metrics_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "analytics_dashboards" (
    "id" VARCHAR(30) NOT NULL,
    "name" VARCHAR(255) NOT NULL,
    "description" TEXT,
    "owner_id" VARCHAR(30) NOT NULL,
    "config" JSONB NOT NULL,
    "is_public" BOOLEAN NOT NULL DEFAULT false,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "analytics_dashboards_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "analytics_reports" (
    "id" VARCHAR(30) NOT NULL,
    "name" VARCHAR(255) NOT NULL,
    "description" TEXT,
    "query" JSONB NOT NULL,
    "schedule" VARCHAR(50),
    "owner_id" VARCHAR(30) NOT NULL,
    "is_active" BOOLEAN NOT NULL DEFAULT true,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "analytics_reports_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "report_executions" (
    "id" VARCHAR(30) NOT NULL,
    "report_id" VARCHAR(30) NOT NULL,
    "status" VARCHAR(20) NOT NULL DEFAULT 'pending',
    "result" JSONB,
    "error_message" TEXT,
    "executed_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "completed_at" TIMESTAMPTZ,

    CONSTRAINT "report_executions_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "analytics_alerts" (
    "id" VARCHAR(30) NOT NULL,
    "name" VARCHAR(255) NOT NULL,
    "description" TEXT,
    "condition" JSONB NOT NULL,
    "notification_config" JSONB NOT NULL,
    "is_active" BOOLEAN NOT NULL DEFAULT true,
    "owner_id" VARCHAR(30) NOT NULL,
    "last_triggered_at" TIMESTAMPTZ,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "analytics_alerts_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "analytics_exports" (
    "id" VARCHAR(30) NOT NULL,
    "name" VARCHAR(255) NOT NULL,
    "export_type" VARCHAR(50) NOT NULL,
    "query" JSONB NOT NULL,
    "file_path" VARCHAR(500),
    "status" VARCHAR(20) NOT NULL DEFAULT 'pending',
    "owner_id" VARCHAR(30) NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "completed_at" TIMESTAMPTZ,

    CONSTRAINT "analytics_exports_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "user_behavior_metrics" (
    "id" VARCHAR(30) NOT NULL,
    "user_id" VARCHAR(30),
    "metric_type" VARCHAR(100) NOT NULL,
    "metric_value" DECIMAL(15,4) NOT NULL,
    "context" JSONB NOT NULL DEFAULT '{}',
    "timestamp" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "user_behavior_metrics_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "system_performance_metrics" (
    "id" VARCHAR(30) NOT NULL,
    "metric_type" VARCHAR(100) NOT NULL,
    "metric_value" DECIMAL(15,4) NOT NULL,
    "component" VARCHAR(100),
    "metadata" JSONB NOT NULL DEFAULT '{}',
    "timestamp" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "system_performance_metrics_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "business_metrics" (
    "id" VARCHAR(30) NOT NULL,
    "metric_type" VARCHAR(100) NOT NULL,
    "metric_value" DECIMAL(15,4) NOT NULL,
    "period" VARCHAR(50),
    "dimensions" JSONB NOT NULL DEFAULT '{}',
    "timestamp" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "business_metrics_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "user_insights" (
    "id" VARCHAR(30) NOT NULL,
    "user_id" VARCHAR(30) NOT NULL,
    "insight_type" VARCHAR(100) NOT NULL,
    "insight_data" JSONB NOT NULL,
    "confidence_score" DECIMAL(3,2),
    "generated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "expires_at" TIMESTAMPTZ,

    CONSTRAINT "user_insights_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE UNIQUE INDEX "users_email_key" ON "users"("email");

-- CreateIndex
CREATE UNIQUE INDEX "users_username_key" ON "users"("username");

-- CreateIndex
CREATE UNIQUE INDEX "user_variables_user_id_key_key" ON "user_variables"("user_id", "key");

-- CreateIndex
CREATE UNIQUE INDEX "template_reviews_template_id_user_id_key" ON "template_reviews"("template_id", "user_id");

-- CreateIndex
CREATE UNIQUE INDEX "template_favorites_template_id_user_id_key" ON "template_favorites"("template_id", "user_id");

-- CreateIndex
CREATE UNIQUE INDEX "http_cache_url_hash_key" ON "http_cache"("url_hash");

-- CreateIndex
CREATE UNIQUE INDEX "component_ratings_component_id_user_id_key" ON "component_ratings"("component_id", "user_id");

-- CreateIndex
CREATE UNIQUE INDEX "component_favorites_component_id_user_id_key" ON "component_favorites"("component_id", "user_id");

-- CreateIndex
CREATE UNIQUE INDEX "component_versions_component_id_version_key" ON "component_versions"("component_id", "version");

-- CreateIndex
CREATE UNIQUE INDEX "workspace_members_workspace_id_user_id_key" ON "workspace_members"("workspace_id", "user_id");

-- CreateIndex
CREATE UNIQUE INDEX "workspace_invitations_token_key" ON "workspace_invitations"("token");

-- CreateIndex
CREATE UNIQUE INDEX "workspace_invitations_email_key" ON "workspace_invitations"("email");

-- CreateIndex
CREATE UNIQUE INDEX "project_collaborators_project_id_user_id_key" ON "project_collaborators"("project_id", "user_id");

-- AddForeignKey
ALTER TABLE "agents" ADD CONSTRAINT "agents_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "users"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "conversations" ADD CONSTRAINT "conversations_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "users"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "conversations" ADD CONSTRAINT "conversations_agent_id_fkey" FOREIGN KEY ("agent_id") REFERENCES "agents"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "messages" ADD CONSTRAINT "messages_conversation_id_fkey" FOREIGN KEY ("conversation_id") REFERENCES "conversations"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "files" ADD CONSTRAINT "files_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "users"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "workflows" ADD CONSTRAINT "workflows_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "users"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "workflow_executions" ADD CONSTRAINT "workflow_executions_workflow_id_fkey" FOREIGN KEY ("workflow_id") REFERENCES "workflows"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "user_variables" ADD CONSTRAINT "user_variables_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "users"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "node_executions" ADD CONSTRAINT "node_executions_workflow_execution_id_fkey" FOREIGN KEY ("workflow_execution_id") REFERENCES "workflow_executions"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "node_executions" ADD CONSTRAINT "node_executions_node_id_fkey" FOREIGN KEY ("node_id") REFERENCES "nodes"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "execution_queue" ADD CONSTRAINT "execution_queue_workflow_execution_id_fkey" FOREIGN KEY ("workflow_execution_id") REFERENCES "workflow_executions"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "execution_queue" ADD CONSTRAINT "execution_queue_node_id_fkey" FOREIGN KEY ("node_id") REFERENCES "nodes"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "execution_metrics" ADD CONSTRAINT "execution_metrics_workflow_execution_id_fkey" FOREIGN KEY ("workflow_execution_id") REFERENCES "workflow_executions"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "workflow_templates" ADD CONSTRAINT "workflow_templates_author_id_fkey" FOREIGN KEY ("author_id") REFERENCES "users"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "template_reviews" ADD CONSTRAINT "template_reviews_template_id_fkey" FOREIGN KEY ("template_id") REFERENCES "workflow_templates"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "template_reviews" ADD CONSTRAINT "template_reviews_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "users"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "template_downloads" ADD CONSTRAINT "template_downloads_template_id_fkey" FOREIGN KEY ("template_id") REFERENCES "workflow_templates"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "template_downloads" ADD CONSTRAINT "template_downloads_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "users"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "template_favorites" ADD CONSTRAINT "template_favorites_template_id_fkey" FOREIGN KEY ("template_id") REFERENCES "workflow_templates"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "template_favorites" ADD CONSTRAINT "template_favorites_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "users"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "template_collections" ADD CONSTRAINT "template_collections_owner_id_fkey" FOREIGN KEY ("owner_id") REFERENCES "users"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "template_usage" ADD CONSTRAINT "template_usage_template_id_fkey" FOREIGN KEY ("template_id") REFERENCES "workflow_templates"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "template_usage" ADD CONSTRAINT "template_usage_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "users"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "template_usage" ADD CONSTRAINT "template_usage_workflow_id_fkey" FOREIGN KEY ("workflow_id") REFERENCES "workflows"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "marketplace_components" ADD CONSTRAINT "marketplace_components_author_id_fkey" FOREIGN KEY ("author_id") REFERENCES "users"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "component_ratings" ADD CONSTRAINT "component_ratings_component_id_fkey" FOREIGN KEY ("component_id") REFERENCES "marketplace_components"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "component_ratings" ADD CONSTRAINT "component_ratings_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "users"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "component_downloads" ADD CONSTRAINT "component_downloads_component_id_fkey" FOREIGN KEY ("component_id") REFERENCES "marketplace_components"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "component_downloads" ADD CONSTRAINT "component_downloads_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "users"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "component_purchases" ADD CONSTRAINT "component_purchases_component_id_fkey" FOREIGN KEY ("component_id") REFERENCES "marketplace_components"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "component_purchases" ADD CONSTRAINT "component_purchases_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "users"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "component_favorites" ADD CONSTRAINT "component_favorites_component_id_fkey" FOREIGN KEY ("component_id") REFERENCES "marketplace_components"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "component_favorites" ADD CONSTRAINT "component_favorites_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "users"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "component_versions" ADD CONSTRAINT "component_versions_component_id_fkey" FOREIGN KEY ("component_id") REFERENCES "marketplace_components"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "workspaces" ADD CONSTRAINT "workspaces_owner_id_fkey" FOREIGN KEY ("owner_id") REFERENCES "users"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "workspace_members" ADD CONSTRAINT "workspace_members_workspace_id_fkey" FOREIGN KEY ("workspace_id") REFERENCES "workspaces"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "workspace_members" ADD CONSTRAINT "workspace_members_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "users"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "workspace_invitations" ADD CONSTRAINT "workspace_invitations_workspace_id_fkey" FOREIGN KEY ("workspace_id") REFERENCES "workspaces"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "workspace_invitations" ADD CONSTRAINT "workspace_invitations_invited_by_fkey" FOREIGN KEY ("invited_by") REFERENCES "users"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "workspace_projects" ADD CONSTRAINT "workspace_projects_workspace_id_fkey" FOREIGN KEY ("workspace_id") REFERENCES "workspaces"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "workspace_projects" ADD CONSTRAINT "workspace_projects_created_by_fkey" FOREIGN KEY ("created_by") REFERENCES "users"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "project_collaborators" ADD CONSTRAINT "project_collaborators_project_id_fkey" FOREIGN KEY ("project_id") REFERENCES "workspace_projects"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "project_collaborators" ADD CONSTRAINT "project_collaborators_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "users"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "project_comments" ADD CONSTRAINT "project_comments_project_id_fkey" FOREIGN KEY ("project_id") REFERENCES "workspace_projects"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "project_comments" ADD CONSTRAINT "project_comments_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "users"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "project_comments" ADD CONSTRAINT "project_comments_parent_comment_id_fkey" FOREIGN KEY ("parent_comment_id") REFERENCES "project_comments"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "workspace_activities" ADD CONSTRAINT "workspace_activities_workspace_id_fkey" FOREIGN KEY ("workspace_id") REFERENCES "workspaces"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "workspace_activities" ADD CONSTRAINT "workspace_activities_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "users"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "project_versions" ADD CONSTRAINT "project_versions_project_id_fkey" FOREIGN KEY ("project_id") REFERENCES "workspace_projects"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "project_versions" ADD CONSTRAINT "project_versions_created_by_fkey" FOREIGN KEY ("created_by") REFERENCES "users"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "analytics_events" ADD CONSTRAINT "analytics_events_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "users"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "analytics_dashboards" ADD CONSTRAINT "analytics_dashboards_owner_id_fkey" FOREIGN KEY ("owner_id") REFERENCES "users"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "analytics_reports" ADD CONSTRAINT "analytics_reports_owner_id_fkey" FOREIGN KEY ("owner_id") REFERENCES "users"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "report_executions" ADD CONSTRAINT "report_executions_report_id_fkey" FOREIGN KEY ("report_id") REFERENCES "analytics_reports"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "analytics_alerts" ADD CONSTRAINT "analytics_alerts_owner_id_fkey" FOREIGN KEY ("owner_id") REFERENCES "users"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "analytics_exports" ADD CONSTRAINT "analytics_exports_owner_id_fkey" FOREIGN KEY ("owner_id") REFERENCES "users"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "user_behavior_metrics" ADD CONSTRAINT "user_behavior_metrics_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "users"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "user_insights" ADD CONSTRAINT "user_insights_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "users"("id") ON DELETE CASCADE ON UPDATE CASCADE;
