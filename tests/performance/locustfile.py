"""
Locust load testing script for SynapScale API endpoints
"""

import time
import json
import uuid
from locust import HttpUser, task, between, events
from locust.contrib.fasthttp import FastHttpUser
import random
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SynapScaleUser(HttpUser):
    """Simulates a user interacting with SynapScale API"""

    wait_time = between(1, 3)  # Wait 1-3 seconds between requests

    def on_start(self):
        """Setup before user starts tasks"""
        self.tenant_id = str(uuid.uuid4())
        self.workspace_id = None
        self.workflow_id = None
        self.agent_id = None
        self.auth_token = None

        # Try to authenticate first
        self.authenticate()

    def authenticate(self):
        """Attempt to authenticate user"""
        try:
            # For now, we'll test without authentication for basic load testing
            # In production, implement proper auth flow
            logger.info(f"👤 User {self.tenant_id[:8]} starting session")
        except Exception as e:
            logger.error(f"❌ Authentication failed: {e}")

    @task(10)
    def health_check(self):
        """Test health check endpoint - highest frequency"""
        with self.client.get("/health", catch_response=True) as response:
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "healthy":
                    response.success()
                else:
                    response.failure(f"Unhealthy status: {data}")
            else:
                response.failure(f"Health check failed: {response.status_code}")

    @task(5)
    def get_api_docs(self):
        """Test API documentation endpoint"""
        with self.client.get("/docs", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"API docs failed: {response.status_code}")

    @task(3)
    def test_workspaces_endpoint(self):
        """Test workspaces endpoint (should return 401 without auth)"""
        with self.client.get("/api/v1/workspaces", catch_response=True) as response:
            # We expect 401 for unauthenticated requests
            if response.status_code == 401:
                response.success()
            elif response.status_code == 200:
                # If authenticated, should return data
                response.success()
            else:
                response.failure(f"Unexpected status: {response.status_code}")

    @task(3)
    def test_workflows_endpoint(self):
        """Test workflows endpoint"""
        with self.client.get("/api/v1/workflows", catch_response=True) as response:
            if response.status_code in [200, 401, 404]:  # Expected responses
                response.success()
            else:
                response.failure(f"Unexpected status: {response.status_code}")

    @task(3)
    def test_agents_endpoint(self):
        """Test agents endpoint"""
        with self.client.get("/api/v1/agents", catch_response=True) as response:
            if response.status_code in [200, 401, 404]:  # Expected responses
                response.success()
            else:
                response.failure(f"Unexpected status: {response.status_code}")

    @task(2)
    def test_plans_endpoint(self):
        """Test plans endpoint"""
        with self.client.get("/api/v1/plans", catch_response=True) as response:
            if response.status_code in [200, 401, 404]:  # Expected responses
                response.success()
            else:
                response.failure(f"Unexpected status: {response.status_code}")

    @task(1)
    def test_large_response_endpoint(self):
        """Test endpoint that might return larger responses"""
        # Test a potential endpoint that returns more data
        endpoints_to_test = [
            "/api/v1/users",
            "/api/v1/templates",
            "/api/v1/files",
            "/api/v1/conversations",
        ]

        endpoint = random.choice(endpoints_to_test)
        with self.client.get(endpoint, catch_response=True) as response:
            if response.status_code in [200, 401, 404, 422]:  # Expected responses
                response.success()

                # Log response size for large responses
                if hasattr(response, "content") and len(response.content) > 1024:
                    logger.info(
                        f"📊 Large response from {endpoint}: {len(response.content)} bytes"
                    )
            else:
                response.failure(f"Unexpected status: {response.status_code}")


class HighLoadUser(FastHttpUser):
    """High-performance user for stress testing"""

    wait_time = between(0.1, 0.5)  # Very fast requests

    @task(20)
    def rapid_health_checks(self):
        """Rapid health check requests"""
        response = self.client.get("/health")
        if response.status_code != 200:
            logger.error(f"Health check failed: {response.status_code}")

    @task(5)
    def rapid_api_calls(self):
        """Rapid API calls to test limits"""
        endpoints = [
            "/api/v1/workspaces",
            "/api/v1/workflows",
            "/api/v1/agents",
            "/api/v1/plans",
        ]

        endpoint = random.choice(endpoints)
        response = self.client.get(endpoint)
        # Just check that server doesn't crash
        if response.status_code >= 500:
            logger.error(f"Server error on {endpoint}: {response.status_code}")


class DatabaseStressUser(HttpUser):
    """User specifically designed to stress database operations"""

    wait_time = between(0.5, 1.5)

    @task(5)
    def test_database_intensive_endpoints(self):
        """Test endpoints that are likely database-intensive"""
        # These endpoints likely involve complex queries
        db_intensive_endpoints = [
            "/api/v1/workspaces",  # Workspace queries with RLS
            "/api/v1/workflows",  # Workflow queries with joins
            "/api/v1/agents",  # Agent queries with knowledge bases
        ]

        endpoint = random.choice(db_intensive_endpoints)

        start_time = time.time()
        with self.client.get(endpoint, catch_response=True) as response:
            end_time = time.time()
            duration_ms = (end_time - start_time) * 1000

            if response.status_code in [200, 401, 404]:
                response.success()

                # Log slow database operations
                if duration_ms > 1000:  # > 1 second
                    logger.warning(
                        f"🐌 Slow DB operation: {endpoint} took {duration_ms:.0f}ms"
                    )
                elif duration_ms > 500:  # > 500ms
                    logger.info(
                        f"⚠️ Moderate DB operation: {endpoint} took {duration_ms:.0f}ms"
                    )
            else:
                response.failure(f"Unexpected status: {response.status_code}")


# Locust events for custom reporting
@events.request.add_listener
def my_request_handler(
    request_type,
    name,
    response_time,
    response_length,
    response,
    context,
    exception,
    start_time,
    url,
    **kwargs,
):
    """Custom request handler for detailed logging"""
    if exception:
        logger.error(f"❌ Request failed: {name} - {exception}")
    elif response_time > 1000:  # Log slow requests
        logger.warning(f"🐌 Slow request: {name} took {response_time:.0f}ms")


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Called when test starts"""
    logger.info("🚀 Starting SynapScale load test...")
    logger.info(f"   Target host: {environment.host}")
    logger.info(
        f"   Users: {environment.parsed_options.num_users if hasattr(environment, 'parsed_options') else 'N/A'}"
    )


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Called when test stops"""
    logger.info("✅ SynapScale load test completed")


# Test scenarios for different load patterns
class LightLoadUser(SynapScaleUser):
    """Light load simulation - normal usage"""

    wait_time = between(3, 8)


class MediumLoadUser(SynapScaleUser):
    """Medium load simulation - busy usage"""

    wait_time = between(1, 3)


class HeavyLoadUser(SynapScaleUser):
    """Heavy load simulation - peak usage"""

    wait_time = between(0.5, 2)


if __name__ == "__main__":
    # Can be run standalone for basic testing
    import os
    import sys

    # Set target host
    os.environ["LOCUST_HOST"] = "http://localhost:8000"

    print("🧪 Running basic Locust test...")
    print("Use: locust -f locustfile.py --host=http://localhost:8000")
    print("Web UI: http://localhost:8089")
