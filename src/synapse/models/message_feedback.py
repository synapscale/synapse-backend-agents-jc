"""Message Feedback Model"""

from sqlalchemy import Column, String, Text, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from synapse.database import Base


class MessageFeedback(Base):
    """User feedback on LLM messages"""
    
    __tablename__ = "message_feedbacks"
    __table_args__ = {"schema": "synapscale_db"}

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    message_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.llms_messages.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.users.id"), nullable=False)
    rating_type = Column(String(20), nullable=False)  # thumbs_up, thumbs_down, star_rating, etc.
    rating_value = Column(Integer, nullable=True)  # 1-5 for star ratings, null for thumbs
    feedback_text = Column(Text, nullable=True)
    feedback_category = Column(String(50), nullable=True)  # accuracy, helpfulness, clarity, etc.
    improvement_suggestions = Column(Text, nullable=True)
    is_public = Column(Boolean, nullable=True, server_default="false")
    feedback_metadata = Column("feedback_metadata", JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.tenants.id"), nullable=True)

    # Relationships
    message = relationship("Message", back_populates="feedbacks")
    user = relationship("User", back_populates="message_feedbacks")
    tenant = relationship("Tenant", back_populates="message_feedbacks")

    def __str__(self):
        return f"MessageFeedback(message_id={self.message_id}, rating={self.rating_type})"

    @property
    def is_positive(self):
        """Check if feedback is positive"""
        if self.rating_type == "thumbs_up":
            return True
        elif self.rating_type == "thumbs_down":
            return False
        elif self.rating_type == "star_rating" and self.rating_value:
            return self.rating_value >= 4
        return None

    @property
    def rating_display(self):
        """Get human-readable rating display"""
        if self.rating_type == "thumbs_up":
            return "👍 Positive"
        elif self.rating_type == "thumbs_down":
            return "👎 Negative"
        elif self.rating_type == "star_rating" and self.rating_value:
            return f"⭐ {self.rating_value}/5"
        return self.rating_type

    def update_feedback(self, rating_value=None, feedback_text=None, category=None):
        """Update feedback details"""
        if rating_value is not None:
            self.rating_value = rating_value
        if feedback_text is not None:
            self.feedback_text = feedback_text
        if category is not None:
            self.feedback_category = category
        self.updated_at = func.now()

    @classmethod
    def get_message_feedback_summary(cls, session, message_id):
        """Get feedback summary for a message"""
        feedbacks = session.query(cls).filter(cls.message_id == message_id).all()
        
        if not feedbacks:
            return {"total": 0}
        
        positive = sum(1 for f in feedbacks if f.is_positive)
        negative = sum(1 for f in feedbacks if f.is_positive is False)
        neutral = len(feedbacks) - positive - negative
        
        avg_rating = None
        star_ratings = [f.rating_value for f in feedbacks if f.rating_type == "star_rating" and f.rating_value]
        if star_ratings:
            avg_rating = sum(star_ratings) / len(star_ratings)
        
        return {
            "total": len(feedbacks),
            "positive": positive,
            "negative": negative,
            "neutral": neutral,
            "average_rating": avg_rating
        }
