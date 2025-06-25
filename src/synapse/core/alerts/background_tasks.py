"""
Background Task Manager for Alert System
Manages long-running tasks like alert evaluation and metric aggregation
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Optional
from datetime import datetime, timedelta

from synapse.core.alerts.alert_engine import alert_engine

logger = logging.getLogger(__name__)


class BackgroundTaskManager:
    """
    Manages background tasks for the alert system
    """

    def __init__(self):
        self.tasks = {}
        self.running = False

    async def start_all_tasks(self):
        """Start all background tasks"""
        if self.running:
            logger.warning("Background tasks already running")
            return

        self.running = True
        logger.info("Starting background tasks")

        try:
            # Start alert evaluation engine
            self.tasks["alert_engine"] = asyncio.create_task(
                self._run_alert_engine(), name="alert_engine"
            )

            # Start metric aggregation task
            self.tasks["metric_aggregation"] = asyncio.create_task(
                self._run_metric_aggregation(), name="metric_aggregation"
            )

            # Start cleanup task
            self.tasks["cleanup"] = asyncio.create_task(
                self._run_cleanup_task(), name="cleanup"
            )

            logger.info(f"Started {len(self.tasks)} background tasks")

        except Exception as e:
            logger.error(f"Error starting background tasks: {e}")
            await self.stop_all_tasks()

    async def stop_all_tasks(self):
        """Stop all background tasks"""
        if not self.running:
            return

        logger.info("Stopping background tasks")
        self.running = False

        # Stop alert engine first
        await alert_engine.stop()

        # Cancel all tasks
        for task_name, task in self.tasks.items():
            if not task.done():
                logger.info(f"Cancelling task: {task_name}")
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    logger.info(f"Task {task_name} cancelled")

        self.tasks.clear()
        logger.info("All background tasks stopped")

    async def restart_task(self, task_name: str):
        """Restart a specific task"""
        if task_name in self.tasks:
            task = self.tasks[task_name]
            if not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass

        # Restart the task
        if task_name == "alert_engine":
            self.tasks[task_name] = asyncio.create_task(
                self._run_alert_engine(), name=task_name
            )
        elif task_name == "metric_aggregation":
            self.tasks[task_name] = asyncio.create_task(
                self._run_metric_aggregation(), name=task_name
            )
        elif task_name == "cleanup":
            self.tasks[task_name] = asyncio.create_task(
                self._run_cleanup_task(), name=task_name
            )

        logger.info(f"Restarted task: {task_name}")

    async def get_task_status(self) -> dict:
        """Get status of all background tasks"""
        status = {
            "running": self.running,
            "tasks": {}
        }

        for task_name, task in self.tasks.items():
            status["tasks"][task_name] = {
                "done": task.done(),
                "cancelled": task.cancelled(),
                "exception": str(task.exception()) if task.done() and task.exception() else None
            }

        return status

    async def _run_alert_engine(self):
        """Run the alert evaluation engine"""
        try:
            logger.info("Starting alert evaluation engine")
            await alert_engine.start()
        except asyncio.CancelledError:
            logger.info("Alert engine task cancelled")
            raise
        except Exception as e:
            logger.error(f"Alert engine task failed: {e}")
            # Auto-restart after delay
            await asyncio.sleep(30)
            if self.running:
                await self.restart_task("alert_engine")

    async def _run_metric_aggregation(self):
        """Run metric aggregation task"""
        logger.info("Starting metric aggregation task")
        
        while self.running:
            try:
                await self._aggregate_metrics()
                await asyncio.sleep(300)  # Run every 5 minutes
            except asyncio.CancelledError:
                logger.info("Metric aggregation task cancelled")
                raise
            except Exception as e:
                logger.error(f"Error in metric aggregation: {e}")
                await asyncio.sleep(60)  # Wait before retry

    async def _run_cleanup_task(self):
        """Run cleanup task for old data"""
        logger.info("Starting cleanup task")
        
        while self.running:
            try:
                await self._cleanup_old_data()
                await asyncio.sleep(3600)  # Run every hour
            except asyncio.CancelledError:
                logger.info("Cleanup task cancelled")
                raise
            except Exception as e:
                logger.error(f"Error in cleanup task: {e}")
                await asyncio.sleep(300)  # Wait before retry

    async def _aggregate_metrics(self):
        """Aggregate metrics for better performance"""
        try:
            from synapse.database import get_db
            from synapse.models.analytics import AnalyticsEvent, AnalyticsMetric
            from sqlalchemy import func, text
            
            db = next(get_db())
            
            # Aggregate events into metrics every 5 minutes
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(minutes=5)
            
            # Count error events
            error_count = db.query(AnalyticsEvent).filter(
                AnalyticsEvent.event_type == "error_occurred",
                AnalyticsEvent.timestamp >= start_time,
                AnalyticsEvent.timestamp < end_time
            ).count()
            
            if error_count > 0:
                error_metric = AnalyticsMetric(
                    metric_name="error_count",
                    metric_value=error_count,
                    dimensions={"aggregation_period": "5min"},
                    timestamp=end_time
                )
                db.add(error_metric)
            
            # Count page views
            page_view_count = db.query(AnalyticsEvent).filter(
                AnalyticsEvent.event_type == "page_view",
                AnalyticsEvent.timestamp >= start_time,
                AnalyticsEvent.timestamp < end_time
            ).count()
            
            if page_view_count > 0:
                page_view_metric = AnalyticsMetric(
                    metric_name="page_view_count",
                    metric_value=page_view_count,
                    dimensions={"aggregation_period": "5min"},
                    timestamp=end_time
                )
                db.add(page_view_metric)
            
            # Calculate average response time (if available in properties)
            response_times = db.query(AnalyticsEvent.properties).filter(
                AnalyticsEvent.event_type == "performance_metric",
                AnalyticsEvent.timestamp >= start_time,
                AnalyticsEvent.timestamp < end_time,
                AnalyticsEvent.properties.contains({"response_time": 1})  # Check if contains response_time
            ).all()
            
            if response_times:
                total_time = 0
                count = 0
                for event in response_times:
                    if isinstance(event.properties, dict) and "response_time" in event.properties:
                        total_time += float(event.properties["response_time"])
                        count += 1
                
                if count > 0:
                    avg_response_time = total_time / count
                    response_metric = AnalyticsMetric(
                        metric_name="avg_response_time",
                        metric_value=avg_response_time,
                        dimensions={"aggregation_period": "5min"},
                        timestamp=end_time
                    )
                    db.add(response_metric)
            
            db.commit()
            logger.debug(f"Aggregated metrics for period {start_time} to {end_time}")
            
        except Exception as e:
            logger.error(f"Error aggregating metrics: {e}")
        finally:
            if 'db' in locals():
                db.close()

    async def _cleanup_old_data(self):
        """Clean up old analytics data"""
        try:
            from synapse.database import get_db
            from synapse.models.analytics import AnalyticsEvent, AnalyticsMetric
            
            db = next(get_db())
            
            # Delete events older than 90 days
            cutoff_date = datetime.utcnow() - timedelta(days=90)
            
            deleted_events = db.query(AnalyticsEvent).filter(
                AnalyticsEvent.timestamp < cutoff_date
            ).delete(synchronize_session=False)
            
            # Delete metrics older than 180 days
            metrics_cutoff = datetime.utcnow() - timedelta(days=180)
            
            deleted_metrics = db.query(AnalyticsMetric).filter(
                AnalyticsMetric.timestamp < metrics_cutoff
            ).delete(synchronize_session=False)
            
            db.commit()
            
            if deleted_events > 0 or deleted_metrics > 0:
                logger.info(f"Cleaned up {deleted_events} old events and {deleted_metrics} old metrics")
            
        except Exception as e:
            logger.error(f"Error cleaning up old data: {e}")
        finally:
            if 'db' in locals():
                db.close()


# Global instance
background_task_manager = BackgroundTaskManager()


@asynccontextmanager
async def lifespan_manager():
    """Context manager for application lifespan"""
    try:
        # Start background tasks
        await background_task_manager.start_all_tasks()
        yield
    finally:
        # Stop background tasks
        await background_task_manager.stop_all_tasks() 