"""
Alert Service for Real-time Monitoring and Notifications
Implements the actual alert evaluation engine and notification delivery system
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func, text
import json
import uuid
from enum import Enum

from synapse.models.analytics_alert import AnalyticsAlert
from synapse.models.analytics_event import AnalyticsEvent  
from synapse.models.analytics_metric import AnalyticsMetric
from synapse.models.user import User
from synapse.core.email.service import EmailService
from synapse.core.websockets.manager import WebSocketManager
from synapse.schemas.models import AlertCreate
from synapse.schemas.models import AlertUpdate

logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    """Alert severity levels"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertStatus(Enum):
    """Alert status"""

    ACTIVE = "active"
    PAUSED = "paused"
    TRIGGERED = "triggered"
    RESOLVED = "resolved"


class NotificationChannel(Enum):
    """Notification channels"""

    EMAIL = "email"
    WEBSOCKET = "websocket"
    WEBHOOK = "webhook"
    SLACK = "slack"


class AlertService:
    """Real-time alert evaluation and notification service"""

    def __init__(self, db: Session):
        self.db = db
        self.email_service = EmailService()
        self.websocket_manager = WebSocketManager()
        self._alert_states = {}  # Cache for alert state management
        self._evaluation_running = False

    async def create_alert(
        self, alert_data: Dict[str, Any], user_id: str
    ) -> Dict[str, Any]:
        """Create a new alert with real validation and setup"""
        try:
            # Validate alert condition
            condition_validated = self._validate_alert_condition(
                alert_data.get("condition", {})
            )
            if not condition_validated:
                raise ValueError("Invalid alert condition configuration")

            # Create alert in database
            alert = AnalyticsAlert(
                id=uuid.uuid4(),
                name=alert_data.get("name"),
                description=alert_data.get("description"),
                condition=alert_data.get("condition"),
                notification_config=alert_data.get("notification_config", {}),
                is_active=True,
                owner_id=user_id,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )

            self.db.add(alert)
            self.db.commit()
            self.db.refresh(alert)

            # Initialize alert state
            self._alert_states[str(alert.id)] = {
                "last_evaluation": None,
                "last_triggered": None,
                "trigger_count": 0,
                "current_value": None,
                "status": AlertStatus.ACTIVE.value,
            }

            logger.info(
                f"Alert created: {alert.name} (ID: {alert.id}) for user {user_id}"
            )

            return {
                "alert_id": str(alert.id),
                "name": alert.name,
                "status": "active",
                "created_at": alert.created_at.isoformat(),
                "condition": alert.condition,
                "notification_config": alert.notification_config,
            }

        except Exception as e:
            logger.error(f"Failed to create alert: {str(e)}")
            self.db.rollback()
            raise

    async def get_user_alerts(
        self, user_id: str, status: str = None, limit: int = 20, offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get user's alerts with real data"""
        try:
            query = self.db.query(AnalyticsAlert).filter(
                AnalyticsAlert.owner_id == user_id
            )

            if status:
                if status == "triggered":
                    # Show alerts that have been triggered recently
                    query = query.filter(
                        AnalyticsAlert.last_triggered_at
                        >= datetime.utcnow() - timedelta(hours=24)
                    )
                else:
                    query = query.filter(
                        AnalyticsAlert.is_active == (status == "active")
                    )

            alerts = (
                query.order_by(desc(AnalyticsAlert.created_at))
                .offset(offset)
                .limit(limit)
                .all()
            )

            result = []
            for alert in alerts:
                alert_state = self._alert_states.get(str(alert.id), {})
                result.append(
                    {
                        "id": str(alert.id),
                        "name": alert.name,
                        "description": alert.description,
                        "condition": alert.condition,
                        "notification_config": alert.notification_config,
                        "is_active": alert.is_active,
                        "last_triggered_at": (
                            alert.last_triggered_at.isoformat()
                            if alert.last_triggered_at
                            else None
                        ),
                        "created_at": alert.created_at.isoformat(),
                        "updated_at": alert.updated_at.isoformat(),
                        "current_status": alert_state.get("status", "active"),
                        "trigger_count": alert_state.get("trigger_count", 0),
                        "current_value": alert_state.get("current_value"),
                    }
                )

            return result

        except Exception as e:
            logger.error(f"Failed to get user alerts: {str(e)}")
            raise

    async def update_alert(
        self, alert_id: str, alert_data: AlertUpdate, user_id: str
    ) -> Dict[str, Any]:
        """Update an existing alert"""
        try:
            alert = (
                self.db.query(AnalyticsAlert)
                .filter(
                    and_(
                        AnalyticsAlert.id == alert_id,
                        AnalyticsAlert.owner_id == user_id,
                    )
                )
                .first()
            )

            if not alert:
                raise ValueError("Alert not found or access denied")

            # Validate new condition if provided
            if alert_data.condition:
                condition_validated = self._validate_alert_condition(
                    alert_data.condition
                )
                if not condition_validated:
                    raise ValueError("Invalid alert condition configuration")
                alert.condition = alert_data.condition

            # Update fields
            if alert_data.name:
                alert.name = alert_data.name
            if alert_data.description:
                alert.description = alert_data.description
            if alert_data.notification_config:
                alert.notification_config = alert_data.notification_config

            alert.updated_at = datetime.utcnow()

            self.db.commit()
            self.db.refresh(alert)

            logger.info(f"Alert updated: {alert.name} (ID: {alert.id})")

            return {
                "alert_id": str(alert.id),
                "name": alert.name,
                "updated_at": alert.updated_at.isoformat(),
            }

        except Exception as e:
            logger.error(f"Failed to update alert: {str(e)}")
            self.db.rollback()
            raise

    async def delete_alert(self, alert_id: str, user_id: str) -> bool:
        """Delete an alert"""
        try:
            alert = (
                self.db.query(AnalyticsAlert)
                .filter(
                    and_(
                        AnalyticsAlert.id == alert_id,
                        AnalyticsAlert.owner_id == user_id,
                    )
                )
                .first()
            )

            if not alert:
                return False

            self.db.delete(alert)
            self.db.commit()

            # Clean up alert state
            if alert_id in self._alert_states:
                del self._alert_states[alert_id]

            logger.info(f"Alert deleted: {alert.name} (ID: {alert.id})")
            return True

        except Exception as e:
            logger.error(f"Failed to delete alert: {str(e)}")
            self.db.rollback()
            raise

    async def pause_alert(self, alert_id: str, user_id: str) -> bool:
        """Pause an alert"""
        try:
            alert = (
                self.db.query(AnalyticsAlert)
                .filter(
                    and_(
                        AnalyticsAlert.id == alert_id,
                        AnalyticsAlert.owner_id == user_id,
                    )
                )
                .first()
            )

            if not alert:
                return False

            alert.is_active = False
            alert.updated_at = datetime.utcnow()
            self.db.commit()

            # Update alert state
            if alert_id in self._alert_states:
                self._alert_states[alert_id]["status"] = AlertStatus.PAUSED.value

            logger.info(f"Alert paused: {alert.name} (ID: {alert.id})")
            return True

        except Exception as e:
            logger.error(f"Failed to pause alert: {str(e)}")
            self.db.rollback()
            raise

    async def resume_alert(self, alert_id: str, user_id: str) -> bool:
        """Resume a paused alert"""
        try:
            alert = (
                self.db.query(AnalyticsAlert)
                .filter(
                    and_(
                        AnalyticsAlert.id == alert_id,
                        AnalyticsAlert.owner_id == user_id,
                    )
                )
                .first()
            )

            if not alert:
                return False

            alert.is_active = True
            alert.updated_at = datetime.utcnow()
            self.db.commit()

            # Update alert state
            if alert_id in self._alert_states:
                self._alert_states[alert_id]["status"] = AlertStatus.ACTIVE.value

            logger.info(f"Alert resumed: {alert.name} (ID: {alert.id})")
            return True

        except Exception as e:
            logger.error(f"Failed to resume alert: {str(e)}")
            self.db.rollback()
            raise

    async def start_alert_evaluation_engine(self):
        """Start the background alert evaluation engine"""
        if self._evaluation_running:
            logger.warning("Alert evaluation engine is already running")
            return

        self._evaluation_running = True
        logger.info("Starting alert evaluation engine...")

        # Load existing alerts into state cache
        await self._initialize_alert_states()

        # Start evaluation loop
        asyncio.create_task(self._evaluation_loop())

    async def stop_alert_evaluation_engine(self):
        """Stop the background alert evaluation engine"""
        self._evaluation_running = False
        logger.info("Alert evaluation engine stopped")

    async def _initialize_alert_states(self):
        """Initialize alert states from database"""
        try:
            alerts = (
                self.db.query(AnalyticsAlert)
                .filter(AnalyticsAlert.is_active == True)
                .all()
            )

            for alert in alerts:
                self._alert_states[str(alert.id)] = {
                    "last_evaluation": None,
                    "last_triggered": alert.last_triggered_at,
                    "trigger_count": 0,
                    "current_value": None,
                    "status": AlertStatus.ACTIVE.value,
                }

            logger.info(f"Initialized {len(alerts)} active alerts")

        except Exception as e:
            logger.error(f"Failed to initialize alert states: {str(e)}")

    async def _evaluation_loop(self):
        """Main alert evaluation loop"""
        while self._evaluation_running:
            try:
                await self._evaluate_all_alerts()
                # Evaluate every 30 seconds
                await asyncio.sleep(30)

            except Exception as e:
                logger.error(f"Error in alert evaluation loop: {str(e)}")
                await asyncio.sleep(30)

    async def _evaluate_all_alerts(self):
        """Evaluate all active alerts"""
        try:
            alerts = (
                self.db.query(AnalyticsAlert)
                .filter(AnalyticsAlert.is_active == True)
                .all()
            )

            for alert in alerts:
                try:
                    await self._evaluate_alert(alert)
                except Exception as e:
                    logger.error(f"Failed to evaluate alert {alert.id}: {str(e)}")

        except Exception as e:
            logger.error(f"Failed to evaluate alerts: {str(e)}")

    async def _evaluate_alert(self, alert: AnalyticsAlert):
        """Evaluate a specific alert"""
        try:
            alert_id = str(alert.id)
            condition = alert.condition

            # Get current metric value based on condition
            current_value = await self._get_metric_value(condition)

            # Update alert state
            if alert_id not in self._alert_states:
                self._alert_states[alert_id] = {
                    "last_evaluation": None,
                    "last_triggered": None,
                    "trigger_count": 0,
                    "current_value": None,
                    "status": AlertStatus.ACTIVE.value,
                }

            self._alert_states[alert_id]["last_evaluation"] = datetime.utcnow()
            self._alert_states[alert_id]["current_value"] = current_value

            # Check if alert should be triggered
            should_trigger = self._check_alert_condition(condition, current_value)

            if should_trigger:
                await self._trigger_alert(alert, current_value)

        except Exception as e:
            logger.error(f"Failed to evaluate alert {alert.id}: {str(e)}")

    async def _get_metric_value(self, condition: Dict[str, Any]) -> float:
        """Get current metric value based on alert condition"""
        try:
            metric_name = condition.get("metric")
            aggregation = condition.get("aggregation", "avg")
            timeframe = condition.get("timeframe", 300)  # 5 minutes default

            # Calculate time range
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(seconds=timeframe)

            # Query metrics
            if aggregation == "count":
                query = self.db.query(func.count(AnalyticsMetric.id)).filter(
                    and_(
                        AnalyticsMetric.metric_name == metric_name,
                        AnalyticsMetric.timestamp >= start_time,
                        AnalyticsMetric.timestamp <= end_time,
                    )
                )
            elif aggregation == "avg":
                query = self.db.query(func.avg(AnalyticsMetric.metric_value)).filter(
                    and_(
                        AnalyticsMetric.metric_name == metric_name,
                        AnalyticsMetric.timestamp >= start_time,
                        AnalyticsMetric.timestamp <= end_time,
                    )
                )
            elif aggregation == "max":
                query = self.db.query(func.max(AnalyticsMetric.metric_value)).filter(
                    and_(
                        AnalyticsMetric.metric_name == metric_name,
                        AnalyticsMetric.timestamp >= start_time,
                        AnalyticsMetric.timestamp <= end_time,
                    )
                )
            elif aggregation == "min":
                query = self.db.query(func.min(AnalyticsMetric.metric_value)).filter(
                    and_(
                        AnalyticsMetric.metric_name == metric_name,
                        AnalyticsMetric.timestamp >= start_time,
                        AnalyticsMetric.timestamp <= end_time,
                    )
                )
            else:
                query = self.db.query(func.sum(AnalyticsMetric.metric_value)).filter(
                    and_(
                        AnalyticsMetric.metric_name == metric_name,
                        AnalyticsMetric.timestamp >= start_time,
                        AnalyticsMetric.timestamp <= end_time,
                    )
                )

            result = query.scalar()
            return float(result) if result is not None else 0.0

        except Exception as e:
            logger.error(f"Failed to get metric value: {str(e)}")
            return 0.0

    def _check_alert_condition(
        self, condition: Dict[str, Any], current_value: float
    ) -> bool:
        """Check if alert condition is met"""
        try:
            operator = condition.get("operator", "gt")
            threshold = float(condition.get("threshold", 0))

            if operator == "gt":
                return current_value > threshold
            elif operator == "gte":
                return current_value >= threshold
            elif operator == "lt":
                return current_value < threshold
            elif operator == "lte":
                return current_value <= threshold
            elif operator == "eq":
                return current_value == threshold
            elif operator == "ne":
                return current_value != threshold
            else:
                return False

        except Exception as e:
            logger.error(f"Failed to check alert condition: {str(e)}")
            return False

    async def _trigger_alert(self, alert: AnalyticsAlert, current_value: float):
        """Trigger an alert and send notifications"""
        try:
            alert_id = str(alert.id)

            # Update alert state
            self._alert_states[alert_id]["last_triggered"] = datetime.utcnow()
            self._alert_states[alert_id]["trigger_count"] += 1
            self._alert_states[alert_id]["status"] = AlertStatus.TRIGGERED.value

            # Update database
            alert.last_triggered_at = datetime.utcnow()
            self.db.commit()

            # Send notifications
            await self._send_alert_notifications(alert, current_value)

            logger.warning(
                f"Alert triggered: {alert.name} (ID: {alert.id}) - Value: {current_value}"
            )

        except Exception as e:
            logger.error(f"Failed to trigger alert: {str(e)}")

    async def _send_alert_notifications(
        self, alert: AnalyticsAlert, current_value: float
    ):
        """Send alert notifications through configured channels"""
        try:
            notification_config = alert.notification_config
            channels = notification_config.get("channels", [])

            # Get alert owner
            owner = self.db.query(User).filter(User.id == alert.owner_id).first()
            if not owner:
                logger.error(f"Alert owner not found for alert {alert.id}")
                return

            # Prepare notification content
            severity = self._get_alert_severity(alert.condition)
            subject = f"🚨 Alert Triggered: {alert.name}"

            notification_data = {
                "alert_id": str(alert.id),
                "alert_name": alert.name,
                "description": alert.description,
                "current_value": current_value,
                "threshold": alert.condition.get("threshold"),
                "severity": severity.value,
                "triggered_at": datetime.utcnow().isoformat(),
                "owner_email": owner.email,
                "owner_name": owner.full_name or owner.email,
            }

            # Send notifications through each channel
            for channel in channels:
                try:
                    if channel["type"] == NotificationChannel.EMAIL.value:
                        await self._send_email_notification(
                            notification_data, channel.get("config", {})
                        )
                    elif channel["type"] == NotificationChannel.WEBSOCKET.value:
                        await self._send_websocket_notification(
                            notification_data, channel.get("config", {})
                        )
                    elif channel["type"] == NotificationChannel.WEBHOOK.value:
                        await self._send_webhook_notification(
                            notification_data, channel.get("config", {})
                        )
                    # Add Slack integration if needed

                except Exception as e:
                    logger.error(
                        f"Failed to send notification via {channel['type']}: {str(e)}"
                    )

        except Exception as e:
            logger.error(f"Failed to send alert notifications: {str(e)}")

    async def _send_email_notification(
        self, notification_data: Dict[str, Any], channel_config: Dict[str, Any]
    ):
        """Send email notification"""
        try:
            severity_emoji = {"low": "ℹ️", "medium": "⚠️", "high": "🔥", "critical": "💥"}

            emoji = severity_emoji.get(notification_data["severity"], "🚨")

            content = f"""
            <h3>{emoji} Alert Triggered</h3>
            <p><strong>Alert:</strong> {notification_data['alert_name']}</p>
            <p><strong>Description:</strong> {notification_data['description']}</p>
            <p><strong>Current Value:</strong> {notification_data['current_value']}</p>
            <p><strong>Threshold:</strong> {notification_data['threshold']}</p>
            <p><strong>Severity:</strong> {notification_data['severity'].upper()}</p>
            <p><strong>Triggered At:</strong> {notification_data['triggered_at']}</p>
            
            <p>Please check your monitoring dashboard for more details.</p>
            """

            await self.email_service.send_notification_email(
                email=notification_data["owner_email"],
                title=f"Alert Triggered: {notification_data['alert_name']}",
                content=content,
                user_name=notification_data["owner_name"],
                subject=f"🚨 Alert: {notification_data['alert_name']}",
            )

            logger.info(
                f"Email notification sent for alert {notification_data['alert_id']}"
            )

        except Exception as e:
            logger.error(f"Failed to send email notification: {str(e)}")

    async def _send_websocket_notification(
        self, notification_data: Dict[str, Any], channel_config: Dict[str, Any]
    ):
        """Send WebSocket notification"""
        try:
            # Send to alert owner via WebSocket
            await self.websocket_manager.send_user_message(
                user_id=str(notification_data["alert_id"]),  # This should be owner_id
                message={"type": "alert_triggered", "data": notification_data},
            )

            logger.info(
                f"WebSocket notification sent for alert {notification_data['alert_id']}"
            )

        except Exception as e:
            logger.error(f"Failed to send WebSocket notification: {str(e)}")

    async def _send_webhook_notification(
        self, notification_data: Dict[str, Any], channel_config: Dict[str, Any]
    ):
        """Send webhook notification"""
        try:
            import aiohttp

            webhook_url = channel_config.get("url")
            if not webhook_url:
                logger.error("Webhook URL not configured")
                return

            # Prepare webhook payload
            payload = {
                "event": "alert_triggered",
                "timestamp": notification_data["triggered_at"],
                "alert": {
                    "id": notification_data["alert_id"],
                    "name": notification_data["alert_name"],
                    "description": notification_data["description"],
                    "severity": notification_data["severity"],
                    "current_value": notification_data["current_value"],
                    "threshold": notification_data["threshold"],
                },
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    webhook_url,
                    json=payload,
                    headers={"Content-Type": "application/json"},
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as response:
                    if response.status == 200:
                        logger.info(
                            f"Webhook notification sent for alert {notification_data['alert_id']}"
                        )
                    else:
                        logger.error(
                            f"Webhook notification failed with status {response.status}"
                        )

        except Exception as e:
            logger.error(f"Failed to send webhook notification: {str(e)}")

    def _get_alert_severity(self, condition: Dict[str, Any]) -> AlertSeverity:
        """Determine alert severity based on condition"""
        # This could be more sophisticated based on metric type, threshold values, etc.
        threshold = condition.get("threshold", 0)
        metric = condition.get("metric", "")

        # Example logic - customize based on your needs
        if "error" in metric.lower() or "failure" in metric.lower():
            if threshold > 50:
                return AlertSeverity.CRITICAL
            elif threshold > 20:
                return AlertSeverity.HIGH
            else:
                return AlertSeverity.MEDIUM
        else:
            if threshold > 1000:
                return AlertSeverity.HIGH
            elif threshold > 100:
                return AlertSeverity.MEDIUM
            else:
                return AlertSeverity.LOW

    def _validate_alert_condition(self, condition: Dict[str, Any]) -> bool:
        """Validate alert condition structure"""
        try:
            required_fields = ["metric", "operator", "threshold"]

            for field in required_fields:
                if field not in condition:
                    return False

            # Validate operator
            valid_operators = ["gt", "gte", "lt", "lte", "eq", "ne"]
            if condition["operator"] not in valid_operators:
                return False

            # Validate threshold is numeric
            try:
                float(condition["threshold"])
            except (ValueError, TypeError):
                return False

            return True

        except Exception:
            return False

    async def get_alert_metrics(self, alert_id: str, user_id: str) -> Dict[str, Any]:
        """Get metrics and history for a specific alert"""
        try:
            alert = (
                self.db.query(AnalyticsAlert)
                .filter(
                    and_(
                        AnalyticsAlert.id == alert_id,
                        AnalyticsAlert.owner_id == user_id,
                    )
                )
                .first()
            )

            if not alert:
                raise ValueError("Alert not found or access denied")

            # Get alert state
            alert_state = self._alert_states.get(alert_id, {})

            # Get recent metric values for trending
            condition = alert.condition
            metric_name = condition.get("metric")

            # Get last 24 hours of data
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(hours=24)

            metric_history = (
                self.db.query(AnalyticsMetric)
                .filter(
                    and_(
                        AnalyticsMetric.metric_name == metric_name,
                        AnalyticsMetric.timestamp >= start_time,
                        AnalyticsMetric.timestamp <= end_time,
                    )
                )
                .order_by(AnalyticsMetric.timestamp)
                .all()
            )

            history_data = [
                {
                    "timestamp": metric.timestamp.isoformat(),
                    "value": float(metric.metric_value),
                }
                for metric in metric_history
            ]

            return {
                "alert_id": alert_id,
                "alert_name": alert.name,
                "current_value": alert_state.get("current_value"),
                "threshold": condition.get("threshold"),
                "last_triggered": (
                    alert_state.get("last_triggered").isoformat()
                    if alert_state.get("last_triggered")
                    else None
                ),
                "trigger_count": alert_state.get("trigger_count", 0),
                "status": alert_state.get("status", "active"),
                "metric_history": history_data,
            }

        except Exception as e:
            logger.error(f"Failed to get alert metrics: {str(e)}")
            raise
