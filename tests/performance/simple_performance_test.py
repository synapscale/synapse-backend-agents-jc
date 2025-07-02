#!/usr/bin/env python3
"""
Simple performance tests for SynapScale database
Avoids SQLAlchemy model conflicts by using direct SQL queries
"""

import time
import statistics
import psycopg2
from psycopg2.extras import RealDictCursor
import os
import uuid
import logging
from typing import Dict, List

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SimpleDatabasePerformanceTester:
    """Simple database performance tester using direct SQL"""

    def __init__(self):
        self.connection = None
        self.test_tenant_id = str(uuid.uuid4())
        self.setup_connection()

    def setup_connection(self):
        """Setup direct database connection"""
        try:
            # Get database URL from environment
            db_url = os.getenv("DATABASE_URL")
            if not db_url:
                logger.error("DATABASE_URL not found in environment")
                raise ValueError("DATABASE_URL not configured")

            self.connection = psycopg2.connect(db_url)
            self.connection.autocommit = True
            logger.info("✅ Database connection established for performance testing")

        except Exception as e:
            logger.error(f"❌ Failed to connect to database: {e}")
            raise

    def set_tenant_context(self, tenant_id: str = None):
        """Set tenant context for RLS testing"""
        tenant_id = tenant_id or self.test_tenant_id
        with self.connection.cursor() as cursor:
            cursor.execute("SET app.current_tenant_id = %s", (tenant_id,))

    def benchmark_query(
        self, query: str, params: tuple = None, iterations: int = 100
    ) -> Dict[str, float]:
        """Execute query multiple times and measure performance"""
        times = []
        results_count = 0

        with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            # Warm-up
            cursor.execute(query, params)
            results = cursor.fetchall()
            results_count = len(results)

            # Benchmark
            for _ in range(iterations):
                start_time = time.perf_counter()
                cursor.execute(query, params)
                cursor.fetchall()
                end_time = time.perf_counter()
                times.append((end_time - start_time) * 1000)  # Convert to ms

        return {
            "mean_ms": statistics.mean(times),
            "median_ms": statistics.median(times),
            "min_ms": min(times),
            "max_ms": max(times),
            "std_dev_ms": statistics.stdev(times) if len(times) > 1 else 0,
            "iterations": iterations,
            "results_count": results_count,
        }

    def test_basic_performance(self):
        """Run comprehensive database performance tests"""
        logger.info("🚀 Starting comprehensive database performance tests...")

        results = {}

        # 1. Health Check Query
        logger.info("1️⃣ Testing basic health check...")
        results["health_check"] = self.benchmark_query(
            "SELECT 1 as health", iterations=200
        )

        # 2. Schema Information Query
        logger.info("2️⃣ Testing schema information query...")
        results["schema_info"] = self.benchmark_query(
            """
            SELECT table_name, table_type 
            FROM information_schema.tables 
            WHERE table_schema = 'synapscale_db' 
            LIMIT 10
            """,
            iterations=100,
        )

        # 3. Workspace Query with RLS
        logger.info("3️⃣ Testing workspace queries with RLS...")
        self.set_tenant_context()
        results["workspaces_rls"] = self.benchmark_query(
            """
            SELECT w.id, w.name, w.tenant_id, p.name as plan_name 
            FROM workspaces w 
            LEFT JOIN plans p ON w.plan_id = p.id 
            LIMIT 10
            """,
            iterations=50,
        )

        # 4. Complex Join Query
        logger.info("4️⃣ Testing complex join queries...")
        results["complex_join"] = self.benchmark_query(
            """
            SELECT 
                w.name as workspace_name,
                COUNT(wf.id) as workflow_count,
                COUNT(DISTINCT a.id) as agent_count
            FROM workspaces w
            LEFT JOIN workflows wf ON w.id = wf.workspace_id 
            LEFT JOIN agents a ON a.tenant_id = w.tenant_id
            WHERE w.tenant_id = %s
            GROUP BY w.id, w.name
            LIMIT 5
            """,
            (self.test_tenant_id,),
            iterations=30,
        )

        # 5. RLS Overhead Test
        logger.info("5️⃣ Testing RLS overhead...")

        # Without RLS context
        with self.connection.cursor() as cursor:
            cursor.execute("RESET app.current_tenant_id")

        results["without_rls"] = self.benchmark_query(
            "SELECT id, name FROM workspaces LIMIT 10", iterations=50
        )

        # With RLS context
        self.set_tenant_context()
        results["with_rls"] = self.benchmark_query(
            "SELECT id, name FROM workspaces LIMIT 10", iterations=50
        )

        # 6. Test various table counts
        logger.info("6️⃣ Testing table counts...")
        tables_to_test = [
            "workspaces",
            "workflows",
            "agents",
            "users",
            "plans",
            "nodes",
            "knowledge_bases",
        ]

        for table in tables_to_test:
            try:
                results[f"count_{table}"] = self.benchmark_query(
                    f"SELECT COUNT(*) FROM {table}", iterations=20
                )
            except Exception as e:
                logger.warning(f"⚠️ Failed to count {table}: {e}")

        return results

    def generate_report(self, results: Dict) -> str:
        """Generate a comprehensive performance report"""
        report = []
        report.append("=" * 80)
        report.append("🏆 SYNAPSCALE DATABASE PERFORMANCE REPORT")
        report.append("=" * 80)
        report.append("")

        # Performance Summary
        report.append("📊 PERFORMANCE SUMMARY:")
        report.append("-" * 40)

        for test_name, result in results.items():
            if isinstance(result, dict) and "mean_ms" in result:
                status = (
                    "🟢"
                    if result["mean_ms"] < 50
                    else "🟡" if result["mean_ms"] < 200 else "🔴"
                )
                report.append(
                    f"{status} {test_name.replace('_', ' ').title():<25} {result['mean_ms']:8.2f}ms avg"
                )

        report.append("")

        # RLS Overhead Analysis
        if "without_rls" in results and "with_rls" in results:
            without_rls_time = results["without_rls"]["mean_ms"]
            with_rls_time = results["with_rls"]["mean_ms"]
            overhead = ((with_rls_time - without_rls_time) / without_rls_time) * 100

            report.append("🛡️ RLS OVERHEAD ANALYSIS:")
            report.append("-" * 40)
            report.append(f"Without RLS: {without_rls_time:.2f}ms")
            report.append(f"With RLS:    {with_rls_time:.2f}ms")
            report.append(f"Overhead:    {overhead:.1f}%")

            if overhead < 25:
                report.append("✅ RLS overhead is acceptable")
            elif overhead < 50:
                report.append("⚠️ RLS overhead is moderate")
            else:
                report.append("❌ RLS overhead is high - consider optimization")

        report.append("")

        # Detailed Results
        report.append("📈 DETAILED RESULTS:")
        report.append("-" * 40)

        for test_name, result in results.items():
            if isinstance(result, dict) and "mean_ms" in result:
                report.append(f"\n{test_name.replace('_', ' ').title()}:")
                report.append(f"  Mean:    {result['mean_ms']:8.2f}ms")
                report.append(f"  Median:  {result['median_ms']:8.2f}ms")
                report.append(f"  Min:     {result['min_ms']:8.2f}ms")
                report.append(f"  Max:     {result['max_ms']:8.2f}ms")
                report.append(f"  Std Dev: {result['std_dev_ms']:8.2f}ms")
                if "results_count" in result:
                    report.append(f"  Rows:    {result['results_count']:8d}")

        report.append("")
        report.append("=" * 80)

        return "\n".join(report)

    def cleanup(self):
        """Cleanup connections"""
        if self.connection:
            self.connection.close()


def main():
    """Main performance testing function"""
    tester = SimpleDatabasePerformanceTester()

    try:
        # Run performance tests
        results = tester.test_basic_performance()

        # Generate and display report
        report = tester.generate_report(results)
        print(report)

        # Save report to file
        with open("performance_report.txt", "w") as f:
            f.write(report)

        logger.info("📝 Performance report saved to 'performance_report.txt'")

        # Return basic success metrics
        health_check_time = results.get("health_check", {}).get("mean_ms", 999)
        workspace_time = results.get("workspaces_rls", {}).get("mean_ms", 999)

        if health_check_time < 50 and workspace_time < 200:
            logger.info("✅ All performance tests passed!")
            return True
        else:
            logger.warning("⚠️ Some performance tests are slower than expected")
            return False

    except Exception as e:
        logger.error(f"❌ Performance testing failed: {e}")
        return False
    finally:
        tester.cleanup()


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
