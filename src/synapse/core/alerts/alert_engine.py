"""
Alert Evaluation Engine
Real-time monitoring and notification system for SynapScale
"""

import asyncio
import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func, text
from dataclasses import dataclass
from enum import Enum

from synapse.core.email.service import EmailService
from synapse.core.websockets.manager import ConnectionManager
from synapse.models.analytics import AnalyticsAlert, AnalyticsEvent, AnalyticsMetric
from synapse.models.user import User
from synapse.database import get_db

logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    """Alert severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertCondition(Enum):
    """Alert condition types"""
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    PERCENTAGE_CHANGE = "percentage_change"
    THRESHOLD_BREACH = "threshold_breach"


class NotificationChannel(Enum):
    """Available notification channels"""
    EMAIL = "email"
    WEBSOCKET = "websocket"
    WEBHOOK = "webhook"
    SLACK = "slack"


@dataclass
class AlertTrigger:
    """Represents an alert trigger event"""
    alert_id: str
    metric_name: str
    current_value: float
    threshold: float
    condition: str
    severity: AlertSeverity
    message: str
    triggered_at: datetime
    user_id: str


class AlertEvaluationEngine:
    """
    Real-time alert evaluation engine
    Monitors metrics and triggers notifications when conditions are met
    """

    def __init__(self):
        self.email_service = EmailService()
        self.websocket_manager = ConnectionManager()
        self.running = False
        self.evaluation_interval = 60  # seconds
        self.active_alerts_cache = {}
        self.last_evaluation = {}

    async def start(self):
        """Start the alert evaluation engine"""
        self.running = True
        logger.info("Alert evaluation engine started")
        
        while self.running:
            try:
                await self._evaluate_all_alerts()
                await asyncio.sleep(self.evaluation_interval)
            except Exception as e:
                logger.error(f"Error in alert evaluation loop: {e}")
                await asyncio.sleep(self.evaluation_interval)

    async def stop(self):
        """Stop the alert evaluation engine"""
        self.running = False
        logger.info("Alert evaluation engine stopped")

    async def _evaluate_all_alerts(self):
        """Evaluate all active alerts"""
        try:
            db = next(get_db())
            
            # Get all active alerts
            active_alerts = db.query(AnalyticsAlert).filter(
                AnalyticsAlert.is_active == True
            ).all()

            logger.debug(f"Evaluating {len(active_alerts)} active alerts")

            for alert in active_alerts:
                try:
                    await self._evaluate_alert(db, alert)
                except Exception as e:
                    logger.error(f"Error evaluating alert {alert.id}: {e}")

        except Exception as e:
            logger.error(f"Error getting active alerts: {e}")
        finally:
            if 'db' in locals():
                db.close()

    async def _evaluate_alert(self, db: Session, alert: AnalyticsAlert):
        """Evaluate a single alert"""
        try:
            condition = alert.condition
            metric_name = condition.get("metric_name")
            threshold = condition.get("threshold")
            condition_type = condition.get("condition")
            time_window = condition.get("time_window_minutes", 5)

            if not all([metric_name, threshold, condition_type]):
                logger.warning(f"Alert {alert.id} has incomplete condition configuration")
                return

            # Get recent metric data
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(minutes=time_window)

            current_value = await self._get_metric_value(
                db, metric_name, start_time, end_time, condition.get("aggregation", "avg")
            )

            if current_value is None:
                logger.debug(f"No metric data found for {metric_name} in alert {alert.id}")
                return

            # Evaluate condition
            should_trigger = self._evaluate_condition(
                current_value, threshold, condition_type
            )

            if should_trigger:
                await self._trigger_alert(db, alert, current_value, threshold)
            else:
                # Check if alert was previously triggered and should be resolved
                await self._check_alert_resolution(db, alert, current_value)

        except Exception as e:
            logger.error(f"Error evaluating alert {alert.id}: {e}")

    def _evaluate_condition(self, current_value: float, threshold: float, condition_type: str) -> bool:
        """Evaluate if alert condition is met"""
        if condition_type == AlertCondition.GREATER_THAN.value:
            return current_value > threshold
        elif condition_type == AlertCondition.LESS_THAN.value:
            return current_value < threshold
        elif condition_type == AlertCondition.EQUALS.value:
            return abs(current_value - threshold) < 0.001  # Float comparison
        elif condition_type == AlertCondition.NOT_EQUALS.value:
            return abs(current_value - threshold) >= 0.001
        else:
            logger.warning(f"Unknown condition type: {condition_type}")
            return False

    async def _get_metric_value(
        self, 
        db: Session, 
        metric_name: str, 
        start_time: datetime, 
        end_time: datetime,
        aggregation: str = "avg"
    ) -> Optional[float]:
        """Get aggregated metric value for the specified time window"""
        try:
            query = db.query(AnalyticsMetric).filter(
                and_(
                    AnalyticsMetric.metric_name == metric_name,
                    AnalyticsMetric.timestamp >= start_time,
                    AnalyticsMetric.timestamp <= end_time
                )
            )

            if aggregation == "avg":
                result = query.with_entities(func.avg(AnalyticsMetric.metric_value)).scalar()
            elif aggregation == "sum":
                result = query.with_entities(func.sum(AnalyticsMetric.metric_value)).scalar()
            elif aggregation == "max":
                result = query.with_entities(func.max(AnalyticsMetric.metric_value)).scalar()
            elif aggregation == "min":
                result = query.with_entities(func.min(AnalyticsMetric.metric_value)).scalar()
            elif aggregation == "count":
                result = query.count()
            else:
                result = query.with_entities(func.avg(AnalyticsMetric.metric_value)).scalar()

            return float(result) if result is not None else None

        except Exception as e:
            logger.error(f"Error getting metric value for {metric_name}: {e}")
            return None

    async def _trigger_alert(
        self, 
        db: Session, 
        alert: AnalyticsAlert, 
        current_value: float, 
        threshold: float
    ):
        """Trigger alert and send notifications"""
        try:
            # Check if alert was recently triggered (avoid spam)
            cooldown_minutes = alert.condition.get("cooldown_minutes", 15)
            
            if alert.last_triggered_at:
                time_since_last = datetime.utcnow() - alert.last_triggered_at
                if time_since_last.total_seconds() < (cooldown_minutes * 60):
                    logger.debug(f"Alert {alert.id} in cooldown period")
                    return

            # Determine severity
            severity = self._determine_severity(current_value, threshold, alert.condition)

            # Create alert trigger
            trigger = AlertTrigger(
                alert_id=str(alert.id),
                metric_name=alert.condition.get("metric_name"),
                current_value=current_value,
                threshold=threshold,
                condition=alert.condition.get("condition"),
                severity=severity,
                message=self._generate_alert_message(alert, current_value, threshold),
                triggered_at=datetime.utcnow(),
                user_id=str(alert.owner_id)
            )

            # Update alert last triggered time
            alert.last_triggered_at = datetime.utcnow()
            db.commit()

            # Send notifications
            await self._send_notifications(db, alert, trigger)

            logger.info(f"Alert {alert.id} triggered for user {alert.owner_id}")

        except Exception as e:
            logger.error(f"Error triggering alert {alert.id}: {e}")

    def _determine_severity(self, current_value: float, threshold: float, condition: Dict) -> AlertSeverity:
        """Determine alert severity based on how much the threshold is exceeded"""
        try:
            # Get severity thresholds from condition or use defaults
            severity_config = condition.get("severity", {})
            
            # Calculate how much the threshold is exceeded (as percentage)
            if threshold == 0:
                excess_percentage = 100.0
            else:
                excess_percentage = abs((current_value - threshold) / threshold) * 100

            # Determine severity based on excess percentage
            if excess_percentage >= severity_config.get("critical_threshold", 50):
                return AlertSeverity.CRITICAL
            elif excess_percentage >= severity_config.get("high_threshold", 25):
                return AlertSeverity.HIGH
            elif excess_percentage >= severity_config.get("medium_threshold", 10):
                return AlertSeverity.MEDIUM
            else:
                return AlertSeverity.LOW

        except Exception as e:
            logger.error(f"Error determining severity: {e}")
            return AlertSeverity.MEDIUM

    def _generate_alert_message(self, alert: AnalyticsAlert, current_value: float, threshold: float) -> str:
        """Generate human-readable alert message"""
        condition_type = alert.condition.get("condition")
        metric_name = alert.condition.get("metric_name")
        
        condition_text = {
            "greater_than": "exceeded",
            "less_than": "fell below",
            "equals": "equals",
            "not_equals": "does not equal"
        }.get(condition_type, "met condition for")

        return (
            f"Alert '{alert.name}': {metric_name} has {condition_text} threshold. "
            f"Current value: {current_value:.2f}, Threshold: {threshold:.2f}"
        )

    async def _send_notifications(self, db: Session, alert: AnalyticsAlert, trigger: AlertTrigger):
        """Send notifications through configured channels"""
        notification_config = alert.notification_config
        channels = notification_config.get("channels", ["email"])

        for channel in channels:
            try:
                if channel == NotificationChannel.EMAIL.value:
                    await self._send_email_notification(db, alert, trigger)
                elif channel == NotificationChannel.WEBSOCKET.value:
                    await self._send_websocket_notification(alert, trigger)
                elif channel == NotificationChannel.WEBHOOK.value:
                    await self._send_webhook_notification(alert, trigger, notification_config)
                else:
                    logger.warning(f"Unknown notification channel: {channel}")
            except Exception as e:
                logger.error(f"Error sending {channel} notification for alert {alert.id}: {e}")

    async def _send_email_notification(self, db: Session, alert: AnalyticsAlert, trigger: AlertTrigger):
        """Send email notification"""
        try:
            # Get user email
            user = db.query(User).filter(User.id == alert.owner_id).first()
            if not user or not user.email:
                logger.warning(f"No email found for user {alert.owner_id}")
                return

            subject = f"🚨 Alert Triggered: {alert.name}"
            
            content = f"""
            <div style="margin-bottom: 20px;">
                <h3>Alert Details</h3>
                <ul>
                    <li><strong>Alert Name:</strong> {alert.name}</li>
                    <li><strong>Severity:</strong> {trigger.severity.value.upper()}</li>
                    <li><strong>Metric:</strong> {trigger.metric_name}</li>
                    <li><strong>Current Value:</strong> {trigger.current_value:.2f}</li>
                    <li><strong>Threshold:</strong> {trigger.threshold:.2f}</li>
                    <li><strong>Condition:</strong> {trigger.condition}</li>
                    <li><strong>Triggered At:</strong> {trigger.triggered_at.strftime('%Y-%m-%d %H:%M:%S UTC')}</li>
                </ul>
            </div>
            <div style="margin-bottom: 20px;">
                <p><strong>Message:</strong> {trigger.message}</p>
            </div>
            <div>
                <p>Please check your dashboard for more details and take appropriate action if needed.</p>
            </div>
            """

            await self.email_service.send_notification_email(
                email=user.email,
                title="Alert Triggered",
                content=content,
                user_name=user.full_name or user.email,
                subject=subject
            )

            logger.info(f"Email notification sent for alert {alert.id} to {user.email}")

        except Exception as e:
            logger.error(f"Error sending email notification: {e}")

    async def _send_websocket_notification(self, alert: AnalyticsAlert, trigger: AlertTrigger):
        """Send real-time websocket notification"""
        try:
            notification_data = {
                "type": "alert_triggered",
                "alert_id": trigger.alert_id,
                "alert_name": alert.name,
                "severity": trigger.severity.value,
                "metric_name": trigger.metric_name,
                "current_value": trigger.current_value,
                "threshold": trigger.threshold,
                "message": trigger.message,
                "triggered_at": trigger.triggered_at.isoformat()
            }

            await self.websocket_manager.send_to_user(
                str(alert.owner_id), 
                notification_data
            )

            logger.info(f"WebSocket notification sent for alert {alert.id}")

        except Exception as e:
            logger.error(f"Error sending WebSocket notification: {e}")

    async def _send_webhook_notification(self, alert: AnalyticsAlert, trigger: AlertTrigger, config: Dict):
        """Send webhook notification"""
        try:
            import aiohttp
            
            webhook_url = config.get("webhook_url")
            if not webhook_url:
                logger.warning(f"No webhook URL configured for alert {alert.id}")
                return

            payload = {
                "alert_id": trigger.alert_id,
                "alert_name": alert.name,
                "severity": trigger.severity.value,
                "metric_name": trigger.metric_name,
                "current_value": trigger.current_value,
                "threshold": trigger.threshold,
                "condition": trigger.condition,
                "message": trigger.message,
                "triggered_at": trigger.triggered_at.isoformat(),
                "user_id": trigger.user_id
            }

            headers = {"Content-Type": "application/json"}
            
            # Add custom headers if configured
            custom_headers = config.get("webhook_headers", {})
            headers.update(custom_headers)

            async with aiohttp.ClientSession() as session:
                async with session.post(webhook_url, json=payload, headers=headers) as response:
                    if response.status == 200:
                        logger.info(f"Webhook notification sent for alert {alert.id}")
                    else:
                        logger.error(f"Webhook failed with status {response.status} for alert {alert.id}")

        except Exception as e:
            logger.error(f"Error sending webhook notification: {e}")

    async def _check_alert_resolution(self, db: Session, alert: AnalyticsAlert, current_value: float):
        """Check if a previously triggered alert should be resolved"""
        try:
            # This is a placeholder for alert resolution logic
            # You could implement logic to detect when an alert condition is no longer met
            # and send resolution notifications
            pass
        except Exception as e:
            logger.error(f"Error checking alert resolution: {e}")

    # ==================== MANUAL TESTING METHODS ====================

    async def test_alert_evaluation(self, alert_id: str) -> Dict[str, Any]:
        """Test alert evaluation for a specific alert (for debugging)"""
        try:
            db = next(get_db())
            alert = db.query(AnalyticsAlert).filter(AnalyticsAlert.id == alert_id).first()
            
            if not alert:
                return {"error": "Alert not found"}

            condition = alert.condition
            metric_name = condition.get("metric_name")
            threshold = condition.get("threshold")
            time_window = condition.get("time_window_minutes", 5)

            end_time = datetime.utcnow()
            start_time = end_time - timedelta(minutes=time_window)

            current_value = await self._get_metric_value(
                db, metric_name, start_time, end_time, condition.get("aggregation", "avg")
            )

            should_trigger = False
            if current_value is not None:
                should_trigger = self._evaluate_condition(
                    current_value, threshold, condition.get("condition")
                )

            return {
                "alert_id": alert_id,
                "alert_name": alert.name,
                "metric_name": metric_name,
                "current_value": current_value,
                "threshold": threshold,
                "condition": condition.get("condition"),
                "should_trigger": should_trigger,
                "time_window": time_window,
                "evaluation_time": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Error testing alert evaluation: {e}")
            return {"error": str(e)}
        finally:
            if 'db' in locals():
                db.close()


# Global instance
alert_engine = AlertEvaluationEngine() 