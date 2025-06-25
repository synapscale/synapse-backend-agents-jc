# SynapScale Centralized Logging System

## Overview

The SynapScale centralized logging system provides comprehensive log aggregation, analysis, and monitoring using a modern observability stack. This system collects logs from all application components and makes them searchable and analyzable through a unified interface.

## Architecture

### Components

1. **Application Logs** - Structured JSON logs from the FastAPI application
2. **Loki** - Log aggregation and storage system (Grafana Labs)
3. **Promtail** - Log collector that ships logs to Loki
4. **Grafana** - Visualization and dashboarding for log analysis
5. **File Handlers** - Rotating log files for different log categories

### Log Flow

```
FastAPI App → Structured Logs → File Handlers → Promtail → Loki → Grafana
```

## Features

### ✅ Structured Logging
- JSON-formatted logs with consistent schema
- Request correlation IDs for tracing
- User context and operation metadata
- Error tracking with stack traces
- Performance metrics logging

### ✅ Log Categorization
- **Main Application Logs** (`synapse.log`) - All application events
- **Error Logs** (`synapse_errors.log`) - Critical errors and exceptions
- **System Logs** (`system.log`) - Infrastructure and startup events
- **LLM Operations** (`llm_operations.log`) - AI/ML specific operations

### ✅ Centralized Collection
- Promtail automatically discovers and ships logs
- Docker container log collection
- File-based log collection
- Real-time log streaming

### ✅ Advanced Querying
- LogQL query language (similar to PromQL)
- Full-text search across all logs
- Time-based filtering and aggregation
- Label-based filtering and grouping

### ✅ Visualization & Monitoring
- Pre-built Grafana dashboards
- Real-time log streaming
- Error rate monitoring
- Performance analytics
- Custom alerting rules

## Quick Start

### 1. Start the Logging Stack

```bash
# Start all services including Loki, Promtail, and Grafana
docker-compose -f deployment/docker/docker-compose.yml up -d

# Check service health
curl http://localhost:3100/ready  # Loki
curl http://localhost:9080/ready  # Promtail
```

### 2. Access Grafana

- URL: http://localhost:3000
- Username: admin
- Password: admin123

### 3. Test the System

```bash
# Run the logging test script
python scripts/test_centralized_logging.py

# Generate some application logs
python -m uvicorn src.synapse.main:app --reload
```

### 4. View Logs in Grafana

1. Navigate to "Explore" in Grafana
2. Select "Loki" as the data source
3. Use LogQL queries to explore logs:

```logql
# All application logs
{job="synapscale-app-logs"}

# Error logs only
{job="synapscale-app-logs"} |= "ERROR"

# LLM operations
{job="synapscale-app-logs"} | json | endpoint_category="llm"

# Logs for specific user
{job="synapscale-app-logs"} | json | user_id="user-123"

# Recent errors with context
{job="synapscale-app-logs"} |= "ERROR" | json | __error__=""
```

## Configuration

### Environment Variables

```bash
# Enable centralized logging
ENABLE_CENTRALIZED_LOGGING=true
LOKI_URL=http://localhost:3100
LOG_RETENTION_DAYS=7
ENABLE_LOG_FILE_OUTPUT=true
LOG_DIRECTORY=logs

# Log levels and formatting
LOG_LEVEL=INFO
LOG_FORMAT=json
```

### Log Structure

All logs follow this JSON structure:

```json
{
  "timestamp": "2024-01-15T10:30:00.123456Z",
  "level": "INFO",
  "logger": "synapse.services.llm_service",
  "message": "LLM request completed successfully",
  "module": "llm_service",
  "function": "generate_response",
  "line": 142,
  "request_id": "req_abc123",
  "user_id": "user_456",
  "endpoint_category": "llm",
  "url": "/api/v1/llm/generate",
  "method": "POST",
  "status_code": 200,
  "process_time": 1.234,
  "provider": "openai",
  "model": "gpt-4",
  "tokens_used": 150,
  "cost": 0.003
}
```

## Log Categories

### 1. Application Logs (`synapse.log`)
- All application events and operations
- Request/response logging
- Business logic events
- User actions and workflows

### 2. Error Logs (`synapse_errors.log`)
- Exceptions and stack traces
- Critical system errors
- Failed operations
- Security incidents

### 3. System Logs (`system.log`)
- Application startup/shutdown
- Configuration changes
- Database connections
- Middleware operations

### 4. LLM Operations (`llm_operations.log`)
- AI/ML model requests
- Token usage and costs
- Provider interactions
- Model performance metrics

## Dashboards

### SynapScale - Centralized Logs Dashboard

Pre-built dashboard includes:

1. **Log Volume by Level** - Timeline of log levels
2. **Error Rate Gauge** - Current error rate monitoring
3. **Log Volume by Module** - Activity by application module
4. **Application Logs Panel** - Real-time log streaming
5. **Top Error Types** - Most frequent error categories
6. **Most Active Endpoints** - API usage analytics

### Custom Dashboards

Create custom dashboards for:
- User activity monitoring
- Performance analytics
- Security event tracking
- Business metrics

## Querying Examples

### Basic Queries

```logql
# All logs from the last hour
{job="synapscale-app-logs"}

# Filter by log level
{job="synapscale-app-logs"} |= "level=\"ERROR\""

# Filter by module
{job="synapscale-app-logs"} | json | module="llm_service"
```

### Advanced Queries

```logql
# Error rate over time
rate({job="synapscale-app-logs"} |= "ERROR" [5m])

# Top error types
topk(10, sum by (error_type) (count_over_time({job="synapscale-app-logs"} | json | error_type != "" [1h])))

# Average response time by endpoint
avg_over_time({job="synapscale-app-logs"} | json | process_time > 0 | unwrap process_time [5m]) by (url)

# User activity
{job="synapscale-app-logs"} | json | user_id="user-123" | line_format "{{.timestamp}} {{.level}} {{.message}}"
```

### Performance Queries

```logql
# Slow requests (>2 seconds)
{job="synapscale-app-logs"} | json | process_time > 2

# LLM cost tracking
sum(sum_over_time({job="synapscale-app-logs"} | json | cost > 0 | unwrap cost [1h])) by (provider)

# Request volume by endpoint
sum(rate({job="synapscale-app-logs"} | json | url != "" [5m])) by (url)
```

## Alerting

### Recommended Alerts

1. **High Error Rate**
   ```logql
   rate({job="synapscale-app-logs"} |= "ERROR" [5m]) > 0.1
   ```

2. **Slow Response Times**
   ```logql
   avg_over_time({job="synapscale-app-logs"} | json | process_time > 0 | unwrap process_time [5m]) > 5
   ```

3. **LLM Cost Spike**
   ```logql
   sum(rate({job="synapscale-app-logs"} | json | cost > 0 | unwrap cost [5m])) > 1.0
   ```

4. **Authentication Failures**
   ```logql
   rate({job="synapscale-app-logs"} |= "AuthenticationError" [5m]) > 0.05
   ```

## Retention and Storage

### Log Retention
- **Default**: 7 days (configurable)
- **Error logs**: 30 days
- **System logs**: 14 days
- **LLM operations**: 7 days

### Storage Management
- Automatic log rotation (10MB files)
- Compressed backups
- Configurable retention policies
- Storage usage monitoring

## Troubleshooting

### Common Issues

1. **Logs not appearing in Loki**
   - Check Promtail logs: `docker logs promtail-container`
   - Verify log file permissions
   - Check Loki connectivity

2. **High memory usage**
   - Adjust log retention settings
   - Increase Loki memory limits
   - Optimize log volume

3. **Query performance issues**
   - Use time range filters
   - Add label filters early in queries
   - Avoid full-text search on large datasets

### Health Checks

```bash
# Check Loki health
curl http://localhost:3100/ready

# Check Promtail health
curl http://localhost:9080/ready

# Check log file creation
ls -la logs/

# Test log ingestion
tail -f logs/synapse.log
```

## Best Practices

### 1. Structured Logging
- Always use structured JSON logs
- Include correlation IDs
- Add relevant context fields
- Use consistent field names

### 2. Log Levels
- **DEBUG**: Detailed diagnostic information
- **INFO**: General operational messages
- **WARNING**: Warning conditions
- **ERROR**: Error conditions requiring attention

### 3. Performance
- Avoid logging sensitive data
- Use appropriate log levels
- Include timing information
- Batch log writes when possible

### 4. Security
- Never log passwords or tokens
- Sanitize user input in logs
- Use secure log transmission
- Implement log access controls

## Integration

### With Existing Systems

1. **Prometheus Metrics**: Correlate logs with metrics
2. **Distributed Tracing**: Link logs to trace spans
3. **Alertmanager**: Route log-based alerts
4. **External SIEMs**: Export logs for security analysis

### API Integration

Access logs programmatically:

```python
import requests

# Query Loki API
response = requests.get(
    "http://localhost:3100/loki/api/v1/query_range",
    params={
        "query": '{job="synapscale-app-logs"}',
        "start": "2024-01-15T00:00:00Z",
        "end": "2024-01-15T23:59:59Z"
    }
)
```

## Maintenance

### Regular Tasks

1. **Monitor storage usage**
2. **Review retention policies**
3. **Update dashboards**
4. **Test alert rules**
5. **Backup configurations**

### Scaling Considerations

- Horizontal scaling for Loki
- Load balancing for Promtail
- Index optimization
- Query performance tuning

## Support

For issues and questions:
1. Check service logs
2. Review configuration
3. Test connectivity
4. Consult Grafana/Loki documentation
5. Contact the development team

---

**Last Updated**: 2024-01-15
**Version**: 1.0.0 