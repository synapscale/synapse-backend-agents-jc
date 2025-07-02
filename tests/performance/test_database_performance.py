import pytest
import time
import statistics
from typing import List, Dict, Any
import psycopg2
from psycopg2.extras import RealDictCursor
import logging
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from src.synapse.database import SessionLocal, get_database_config
from src.synapse.models.workspace import Workspace
from src.synapse.models.workflow import Workflow
from src.synapse.models.agent import Agent
from src.synapse.models.user import User
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabasePerformanceTester:
    """Classe para testes de performance do banco de dados"""

    def __init__(self):
        self.connection = None
        self.test_tenant_id = str(uuid.uuid4())
        self.setup_database_connection()

    def setup_database_connection(self):
        """Setup direct database connection for performance testing"""
        try:
            # Get database config from environment or settings
            db_config = get_database_config()
            db_url = db_config.get("url")

            if not db_url:
                # Fallback to environment variables
                db_url = os.getenv("DATABASE_URL")

            if db_url:
                self.connection = psycopg2.connect(db_url)
            else:
                # Fallback to individual parameters
                self.connection = psycopg2.connect(
                    host=os.getenv("DATABASE_HOST", "localhost"),
                    port=os.getenv("DATABASE_PORT", "5432"),
                    database=os.getenv("DATABASE_NAME", "postgres"),
                    user=os.getenv("DATABASE_USER", "postgres"),
                    password=os.getenv("DATABASE_PASSWORD", ""),
                )

            self.connection.autocommit = True
            logger.info(
                "✅ Conexão direta com banco estabelecida para testes de performance"
            )
        except Exception as e:
            logger.error(f"❌ Erro ao conectar com banco: {e}")
            raise

    def set_tenant_context(self, tenant_id: str = None):
        """Set tenant context for RLS testing"""
        tenant_id = tenant_id or self.test_tenant_id
        with self.connection.cursor() as cursor:
            cursor.execute("SET app.current_tenant_id = %s", (tenant_id,))
            logger.info(f"🏷️ Contexto de tenant definido: {tenant_id}")

    def execute_query_benchmark(
        self, query: str, params: tuple = None, iterations: int = 100
    ) -> Dict[str, float]:
        """Execute query multiple times and measure performance"""
        times = []

        with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            # Warm-up query
            cursor.execute(query, params)
            cursor.fetchall()

            # Actual benchmarking
            for i in range(iterations):
                start_time = time.perf_counter()
                cursor.execute(query, params)
                results = cursor.fetchall()
                end_time = time.perf_counter()

                times.append((end_time - start_time) * 1000)  # Convert to ms

        return {
            "mean_ms": statistics.mean(times),
            "median_ms": statistics.median(times),
            "min_ms": min(times),
            "max_ms": max(times),
            "std_dev": statistics.stdev(times) if len(times) > 1 else 0,
            "iterations": iterations,
            "total_results": len(results) if "results" in locals() else 0,
        }

    def cleanup(self):
        """Cleanup test data and connections"""
        if self.connection:
            self.connection.close()


@pytest.fixture
def perf_tester():
    """Fixture para tester de performance"""
    tester = DatabasePerformanceTester()
    yield tester
    tester.cleanup()


class TestDatabasePerformance:
    """Testes de performance do banco de dados"""

    @pytest.mark.benchmark
    def test_health_check_query_performance(self, perf_tester, benchmark):
        """Test performance of basic health check query"""

        def health_check():
            return perf_tester.execute_query_benchmark(
                "SELECT 1 as health_check", iterations=50
            )

        result = benchmark(health_check)
        logger.info(f"🏥 Health Check Performance: {result['mean_ms']:.2f}ms avg")

        # Assert performance criteria
        assert (
            result["mean_ms"] < 10
        ), f"Health check too slow: {result['mean_ms']:.2f}ms"

    @pytest.mark.benchmark
    def test_workspaces_with_rls_performance(self, perf_tester, benchmark):
        """Test performance of workspace queries with RLS enabled"""
        perf_tester.set_tenant_context()

        def workspace_query():
            return perf_tester.execute_query_benchmark(
                """
                SELECT w.id, w.name, w.tenant_id, p.name as plan_name 
                FROM workspaces w 
                LEFT JOIN plans p ON w.plan_id = p.id 
                WHERE w.tenant_id = %s 
                LIMIT 10
                """,
                (perf_tester.test_tenant_id,),
                iterations=50,
            )

        result = benchmark(workspace_query)
        logger.info(
            f"🏢 Workspace RLS Query Performance: {result['mean_ms']:.2f}ms avg"
        )

        # Assert performance criteria
        assert (
            result["mean_ms"] < 100
        ), f"Workspace query too slow: {result['mean_ms']:.2f}ms"

    @pytest.mark.benchmark
    def test_workflows_with_rls_performance(self, perf_tester, benchmark):
        """Test performance of workflow queries with RLS enabled"""
        perf_tester.set_tenant_context()

        def workflow_query():
            return perf_tester.execute_query_benchmark(
                """
                SELECT w.id, w.name, w.tenant_id, w.workspace_id, 
                       COUNT(n.id) as node_count
                FROM workflows w 
                LEFT JOIN nodes n ON w.id = n.workflow_id 
                WHERE w.tenant_id = %s 
                GROUP BY w.id, w.name, w.tenant_id, w.workspace_id
                LIMIT 10
                """,
                (perf_tester.test_tenant_id,),
                iterations=50,
            )

        result = benchmark(workflow_query)
        logger.info(f"⚡ Workflow RLS Query Performance: {result['mean_ms']:.2f}ms avg")

        # Assert performance criteria
        assert (
            result["mean_ms"] < 150
        ), f"Workflow query too slow: {result['mean_ms']:.2f}ms"

    @pytest.mark.benchmark
    def test_agents_with_rls_performance(self, perf_tester, benchmark):
        """Test performance of agent queries with RLS enabled"""
        perf_tester.set_tenant_context()

        def agent_query():
            return perf_tester.execute_query_benchmark(
                """
                SELECT a.id, a.name, a.tenant_id, a.agent_type,
                       COUNT(kb.id) as knowledge_base_count
                FROM agents a 
                LEFT JOIN knowledge_bases kb ON a.id = kb.agent_id 
                WHERE a.tenant_id = %s 
                GROUP BY a.id, a.name, a.tenant_id, a.agent_type
                LIMIT 10
                """,
                (perf_tester.test_tenant_id,),
                iterations=50,
            )

        result = benchmark(agent_query)
        logger.info(f"🤖 Agent RLS Query Performance: {result['mean_ms']:.2f}ms avg")

        # Assert performance criteria
        assert (
            result["mean_ms"] < 150
        ), f"Agent query too slow: {result['mean_ms']:.2f}ms"

    @pytest.mark.benchmark
    def test_complex_join_performance(self, perf_tester, benchmark):
        """Test performance of complex joins across multi-tenant tables"""
        perf_tester.set_tenant_context()

        def complex_query():
            return perf_tester.execute_query_benchmark(
                """
                SELECT 
                    w.name as workspace_name,
                    wf.name as workflow_name,
                    a.name as agent_name,
                    COUNT(n.id) as node_count,
                    COUNT(kb.id) as knowledge_base_count
                FROM workspaces w
                JOIN workflows wf ON w.id = wf.workspace_id 
                LEFT JOIN agents a ON a.tenant_id = w.tenant_id
                LEFT JOIN nodes n ON wf.id = n.workflow_id
                LEFT JOIN knowledge_bases kb ON a.id = kb.agent_id
                WHERE w.tenant_id = %s 
                  AND wf.tenant_id = %s
                GROUP BY w.id, w.name, wf.id, wf.name, a.id, a.name
                LIMIT 5
                """,
                (perf_tester.test_tenant_id, perf_tester.test_tenant_id),
                iterations=30,
            )

        result = benchmark(complex_query)
        logger.info(f"🔗 Complex Join Performance: {result['mean_ms']:.2f}ms avg")

        # Assert performance criteria
        assert (
            result["mean_ms"] < 300
        ), f"Complex join too slow: {result['mean_ms']:.2f}ms"

    @pytest.mark.benchmark
    def test_rls_overhead_comparison(self, perf_tester, benchmark):
        """Compare performance with and without RLS context"""

        def without_rls():
            # Test without setting tenant context (should use fallback)
            with perf_tester.connection.cursor() as cursor:
                cursor.execute("RESET app.current_tenant_id")

            return perf_tester.execute_query_benchmark(
                "SELECT id, name FROM workspaces LIMIT 10", iterations=30
            )

        def with_rls():
            # Test with tenant context
            perf_tester.set_tenant_context()
            return perf_tester.execute_query_benchmark(
                "SELECT id, name FROM workspaces LIMIT 10", iterations=30
            )

        result_without = benchmark.pedantic(without_rls, iterations=1, rounds=5)
        result_with = benchmark.pedantic(with_rls, iterations=1, rounds=5)

        # Calculate overhead
        overhead_pct = (
            (result_with["mean_ms"] - result_without["mean_ms"])
            / result_without["mean_ms"]
        ) * 100

        logger.info(f"🛡️ RLS Overhead: {overhead_pct:.1f}%")
        logger.info(f"   - Without RLS: {result_without['mean_ms']:.2f}ms")
        logger.info(f"   - With RLS: {result_with['mean_ms']:.2f}ms")

        # Assert overhead is acceptable (< 50%)
        assert overhead_pct < 50, f"RLS overhead too high: {overhead_pct:.1f}%"

    @pytest.mark.benchmark
    def test_tenant_isolation_performance(self, perf_tester, benchmark):
        """Test performance of tenant isolation queries"""

        def tenant_isolation_test():
            # Test queries that should return different results for different tenants
            tenant1 = str(uuid.uuid4())
            tenant2 = str(uuid.uuid4())

            results = {}

            # Test tenant 1
            perf_tester.set_tenant_context(tenant1)
            results["tenant1"] = perf_tester.execute_query_benchmark(
                "SELECT COUNT(*) FROM workspaces", iterations=20
            )

            # Test tenant 2
            perf_tester.set_tenant_context(tenant2)
            results["tenant2"] = perf_tester.execute_query_benchmark(
                "SELECT COUNT(*) FROM workspaces", iterations=20
            )

            return results

        result = benchmark(tenant_isolation_test)

        logger.info(f"🔒 Tenant Isolation Performance:")
        logger.info(f"   - Tenant 1: {result['tenant1']['mean_ms']:.2f}ms avg")
        logger.info(f"   - Tenant 2: {result['tenant2']['mean_ms']:.2f}ms avg")

        # Both should be fast
        assert result["tenant1"]["mean_ms"] < 50, "Tenant 1 queries too slow"
        assert result["tenant2"]["mean_ms"] < 50, "Tenant 2 queries too slow"


if __name__ == "__main__":
    # Run basic performance tests
    tester = DatabasePerformanceTester()

    print("🚀 Executando testes básicos de performance...")

    # Health check
    result = tester.execute_query_benchmark("SELECT 1", iterations=100)
    print(f"Health Check: {result['mean_ms']:.2f}ms avg")

    # Workspace query
    tester.set_tenant_context()
    result = tester.execute_query_benchmark(
        "SELECT id, name FROM workspaces LIMIT 10", iterations=50
    )
    print(f"Workspace Query: {result['mean_ms']:.2f}ms avg")

    tester.cleanup()
    print("✅ Testes básicos concluídos")
