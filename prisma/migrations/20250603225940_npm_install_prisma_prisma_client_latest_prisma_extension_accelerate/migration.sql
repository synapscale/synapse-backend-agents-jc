-- CreateTable
CREATE TABLE "users" (
    "id" TEXT NOT NULL PRIMARY KEY,
    "email" TEXT NOT NULL,
    "password_hash" TEXT NOT NULL,
    "first_name" TEXT,
    "last_name" TEXT,
    "avatar_url" TEXT,
    "is_active" BOOLEAN,
    "is_verified" BOOLEAN,
    "role" TEXT,
    "subscription_plan" TEXT,
    "preferences" TEXT,
    "created_at" DATETIME DEFAULT CURRENT_TIMESTAMP,
    "updated_at" DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- CreateTable
CREATE TABLE "conversations" (
    "id" TEXT NOT NULL PRIMARY KEY,
    "title" TEXT,
    "user_id" TEXT NOT NULL,
    "agent_id" TEXT,
    "status" TEXT,
    "context" TEXT,
    "settings" TEXT,
    "total_messages" INTEGER,
    "total_tokens" INTEGER,
    "created_at" DATETIME DEFAULT CURRENT_TIMESTAMP,
    "updated_at" DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT "conversations_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "users" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION
);

-- CreateTable
CREATE TABLE "messages" (
    "id" TEXT NOT NULL PRIMARY KEY,
    "conversation_id" TEXT NOT NULL,
    "user_id" TEXT,
    "role" TEXT NOT NULL,
    "content" TEXT NOT NULL,
    "attachments" TEXT,
    "token_count" INTEGER,
    "model_used" TEXT,
    "response_time" REAL,
    "created_at" DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT "messages_conversation_id_fkey" FOREIGN KEY ("conversation_id") REFERENCES "conversations" ("id") ON DELETE CASCADE ON UPDATE NO ACTION,
    CONSTRAINT "messages_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "users" ("id") ON DELETE SET NULL ON UPDATE NO ACTION
);

-- CreateTable
CREATE TABLE "email_verification_tokens" (
    "id" TEXT NOT NULL PRIMARY KEY,
    "user_id" TEXT NOT NULL,
    "token" TEXT NOT NULL,
    "created_at" DATETIME DEFAULT CURRENT_TIMESTAMP,
    "expires_at" DATETIME NOT NULL,
    "used_at" DATETIME,
    CONSTRAINT "email_verification_tokens_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "users" ("id") ON DELETE CASCADE ON UPDATE NO ACTION
);

-- CreateTable
CREATE TABLE "password_reset_tokens" (
    "id" TEXT NOT NULL PRIMARY KEY,
    "user_id" TEXT NOT NULL,
    "token" TEXT NOT NULL,
    "created_at" DATETIME DEFAULT CURRENT_TIMESTAMP,
    "expires_at" DATETIME NOT NULL,
    "used_at" DATETIME,
    CONSTRAINT "password_reset_tokens_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "users" ("id") ON DELETE CASCADE ON UPDATE NO ACTION
);

-- CreateTable
CREATE TABLE "refresh_tokens" (
    "id" TEXT NOT NULL PRIMARY KEY,
    "user_id" TEXT NOT NULL,
    "token" TEXT NOT NULL,
    "created_at" DATETIME DEFAULT CURRENT_TIMESTAMP,
    "expires_at" DATETIME NOT NULL,
    "revoked_at" DATETIME,
    CONSTRAINT "refresh_tokens_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "users" ("id") ON DELETE CASCADE ON UPDATE NO ACTION
);

-- CreateTable
CREATE TABLE "analytics_alerts" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "user_id" INTEGER NOT NULL,
    "name" TEXT NOT NULL,
    "condition" TEXT NOT NULL,
    "threshold" TEXT,
    "is_active" BOOLEAN,
    "created_at" DATETIME DEFAULT CURRENT_TIMESTAMP,
    "updated_at" DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- CreateTable
CREATE TABLE "analytics_dashboards" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "user_id" INTEGER NOT NULL,
    "name" TEXT NOT NULL,
    "description" TEXT,
    "layout" TEXT,
    "is_public" BOOLEAN,
    "created_at" DATETIME DEFAULT CURRENT_TIMESTAMP,
    "updated_at" DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- CreateTable
CREATE TABLE "analytics_events" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "user_id" INTEGER,
    "event_type" TEXT NOT NULL,
    "event_data" TEXT,
    "ip_address" TEXT,
    "user_agent" TEXT,
    "timestamp" DATETIME DEFAULT CURRENT_TIMESTAMP,
    "session_id" TEXT,
    "page_url" TEXT,
    "referrer" TEXT
);

-- CreateTable
CREATE TABLE "workflow_executions" (
    "id" TEXT NOT NULL PRIMARY KEY,
    "workflow_id" TEXT NOT NULL,
    "user_id" TEXT NOT NULL,
    "status" TEXT,
    "input_data" TEXT,
    "output_data" TEXT,
    "context_data" TEXT,
    "variables" TEXT,
    "started_at" DATETIME,
    "completed_at" DATETIME,
    "error_message" TEXT,
    "error_details" TEXT,
    "execution_time" REAL,
    "tokens_used" INTEGER,
    "cost_usd" REAL,
    "debug_info" TEXT,
    "tags" TEXT,
    "metadata" TEXT,
    "created_at" DATETIME DEFAULT CURRENT_TIMESTAMP,
    "updated_at" DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- CreateTable
CREATE TABLE "system_performance_metrics" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "metric_name" TEXT NOT NULL,
    "metric_value" REAL NOT NULL,
    "metric_unit" TEXT,
    "tags" TEXT,
    "recorded_at" DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- CreateTable
CREATE TABLE "report_executions" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "report_id" INTEGER NOT NULL,
    "executed_by" TEXT,
    "execution_time" REAL,
    "status" TEXT,
    "result_size" INTEGER,
    "parameters_used" TEXT,
    "created_at" DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- CreateTable
CREATE TABLE "execution_metrics" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "node_execution_id" TEXT NOT NULL,
    "metric_name" TEXT NOT NULL,
    "value_numeric" REAL,
    "value_string" TEXT,
    "value_json" TEXT,
    "tags" TEXT,
    "recorded_at" DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- CreateTable
CREATE TABLE "component_versions" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "component_id" INTEGER NOT NULL,
    "version_number" TEXT NOT NULL,
    "changelog" TEXT,
    "download_url" TEXT,
    "file_size" INTEGER,
    "checksum" TEXT,
    "compatibility_info" TEXT,
    "created_at" DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- CreateIndex
CREATE UNIQUE INDEX "ix_users_email" ON "users"("email");

-- CreateIndex
CREATE INDEX "ix_conversations_user_id" ON "conversations"("user_id");

-- CreateIndex
CREATE INDEX "ix_messages_conversation_id" ON "messages"("conversation_id");

-- CreateIndex
CREATE INDEX "ix_messages_user_id" ON "messages"("user_id");

-- CreateIndex
CREATE UNIQUE INDEX "email_verification_tokens_token_key" ON "email_verification_tokens"("token");

-- CreateIndex
CREATE INDEX "ix_email_verification_tokens_user_id" ON "email_verification_tokens"("user_id");

-- CreateIndex
CREATE UNIQUE INDEX "password_reset_tokens_token_key" ON "password_reset_tokens"("token");

-- CreateIndex
CREATE INDEX "ix_password_reset_tokens_user_id" ON "password_reset_tokens"("user_id");

-- CreateIndex
CREATE UNIQUE INDEX "refresh_tokens_token_key" ON "refresh_tokens"("token");

-- CreateIndex
CREATE INDEX "ix_refresh_tokens_user_id" ON "refresh_tokens"("user_id");

-- CreateIndex
CREATE INDEX "idx_analytics_alerts_user" ON "analytics_alerts"("user_id");

-- CreateIndex
CREATE INDEX "idx_analytics_dashboards_user" ON "analytics_dashboards"("user_id");

-- CreateIndex
CREATE INDEX "idx_analytics_events_user" ON "analytics_events"("user_id");

-- CreateIndex
CREATE INDEX "ix_workflow_executions_user_id" ON "workflow_executions"("user_id");

-- CreateIndex
CREATE INDEX "ix_workflow_executions_workflow_id" ON "workflow_executions"("workflow_id");

-- CreateIndex
CREATE INDEX "idx_system_performance_metrics_name" ON "system_performance_metrics"("metric_name");
