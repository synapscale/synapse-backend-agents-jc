#!/usr/bin/env python3
"""
Test script for centralized logging system.

This script tests the complete centralized logging pipeline:
1. Application logs -> File handlers
2. Promtail collects logs
3. Loki stores logs
4. Grafana displays logs
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from pathlib import Path

# Add the src directory to the path
import sys
sys.path.append(str(Path(__file__).parent.parent / "src"))

from synapse.logger_config import get_logger


async def test_centralized_logging():
    """Test the centralized logging system."""
    
    print("🔍 Testing Centralized Logging System...")
    print("=" * 50)
    
    # Get logger instance
    logger = get_logger("test_centralized_logging")
    
    # Test different log levels with structured data
    print("\n1. Testing different log levels...")
    
    # INFO level log
    logger.logger.info(
        "Centralized logging test started",
        extra={
            "request_id": "test-req-001",
            "user_id": "test-user-123",
            "endpoint_category": "test",
            "operation": "centralized_logging_test",
            "test_type": "info_log"
        }
    )
    
    # WARNING level log
    logger.logger.warning(
        "Test warning message for centralized logging",
        extra={
            "request_id": "test-req-002",
            "error_type": "TestWarning",
            "url": "/api/v1/test",
            "method": "GET",
            "test_type": "warning_log"
        }
    )
    
    # ERROR level log
    logger.logger.error(
        "Test error message for centralized logging",
        extra={
            "request_id": "test-req-003",
            "error_type": "TestError",
            "error_count": 1,
            "traceback": "Test traceback for centralized logging",
            "test_type": "error_log"
        }
    )
    
    print("✅ Basic logging test completed")
    
    # Test LLM-specific logging
    print("\n2. Testing LLM-specific logging...")
    
    llm_logger = get_logger("synapse.services.llm_service")
    llm_logger.logger.info(
        "LLM operation test for centralized logging",
        extra={
            "request_id": "llm-req-001",
            "user_id": "test-user-123",
            "endpoint_category": "llm",
            "provider": "test_provider",
            "model": "test_model",
            "tokens_used": 150,
            "cost": 0.003,
            "operation": "llm_test"
        }
    )
    
    print("✅ LLM logging test completed")
    
    # Test system-level logging
    print("\n3. Testing system-level logging...")
    
    system_logger = get_logger("synapse.main")
    system_logger.logger.info(
        "System startup test for centralized logging",
        extra={
            "service": "synapscale",
            "environment": "test",
            "component": "main_application",
            "startup_time": time.time(),
            "operation": "system_test"
        }
    )
    
    print("✅ System logging test completed")
    
    # Test exception logging
    print("\n4. Testing exception logging...")
    
    try:
        raise ValueError("Test exception for centralized logging")
    except Exception as e:
        logger.log_error(
            e,
            context={
                "request_id": "error-req-001",
                "user_id": "test-user-123",
                "operation": "exception_test",
                "test_context": "centralized_logging_test"
            }
        )
    
    print("✅ Exception logging test completed")
    
    # Test performance logging
    print("\n5. Testing performance logging...")
    
    start_time = time.time()
    await asyncio.sleep(0.1)  # Simulate some work
    end_time = time.time()
    
    logger.logger.info(
        "Performance test completed",
        extra={
            "request_id": "perf-req-001",
            "operation": "performance_test",
            "process_time": end_time - start_time,
            "status_code": 200,
            "method": "POST",
            "url": "/api/v1/test/performance"
        }
    )
    
    print("✅ Performance logging test completed")
    
    # Check log files
    print("\n6. Checking log files...")
    
    log_dir = Path("logs")
    if log_dir.exists():
        log_files = list(log_dir.glob("*.log"))
        print(f"  Found {len(log_files)} log files:")
        for log_file in log_files:
            size = log_file.stat().st_size
            print(f"    - {log_file.name}: {size} bytes")
    else:
        print("  ⚠️  Log directory not found!")
    
    print("\n" + "=" * 50)
    print("🎉 Centralized Logging Test Completed!")
    print("\nNext steps:")
    print("1. Start Docker Compose: docker-compose -f deployment/docker/docker-compose.yml up -d")
    print("2. Check Loki: http://localhost:3100/ready")
    print("3. Check Grafana: http://localhost:3000 (admin/admin123)")
    print("4. View logs in Grafana using the SynapScale - Centralized Logs dashboard")


if __name__ == "__main__":
    asyncio.run(test_centralized_logging()) 