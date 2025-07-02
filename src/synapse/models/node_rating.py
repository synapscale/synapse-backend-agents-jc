"""Node Rating Model"""

from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from synapse.database import Base


class NodeRating(Base):
    """User ratings for workflow nodes"""
    
    __tablename__ = "node_ratings"
    __table_args__ = {"schema": "synapscale_db", "extend_existing": True}

    id = Column(UUID(as_uuid=True), primary_key=True)
    node_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.nodes.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.users.id"), nullable=False)
    rating = Column(Integer, nullable=False)  # 1-5 stars
    created_at = Column(DateTime(timezone=True), nullable=True, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=True, server_default=func.now())
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.tenants.id"), nullable=True)

    # Relationships
    node = relationship("Node", back_populates="ratings")
    user = relationship("User", back_populates="node_ratings")
    tenant = relationship("Tenant", back_populates="node_ratings")

    def __str__(self):
        return f"NodeRating(node_id={self.node_id}, rating={self.rating}/5)"

    @property
    def rating_display(self):
        """Get star display for rating"""
        return "⭐" * self.rating + "☆" * (5 - self.rating)

    @property
    def is_positive(self):
        """Check if rating is positive (4-5 stars)"""
        return self.rating >= 4

    @property
    def is_negative(self):
        """Check if rating is negative (1-2 stars)"""
        return self.rating <= 2

    @property
    def is_neutral(self):
        """Check if rating is neutral (3 stars)"""
        return self.rating == 3

    def update_rating(self, new_rating):
        """Update the rating"""
        if not 1 <= new_rating <= 5:
            raise ValueError("Rating must be between 1 and 5")
        
        self.rating = new_rating
        self.updated_at = func.now()

    @classmethod
    def rate_node(cls, session, node_id, user_id, rating, tenant_id=None):
        """Rate a node (create or update existing rating)"""
        if not 1 <= rating <= 5:
            raise ValueError("Rating must be between 1 and 5")
        
        # Check if user already rated this node
        existing_rating = session.query(cls).filter(
            cls.node_id == node_id,
            cls.user_id == user_id
        ).first()
        
        if existing_rating:
            # Update existing rating
            existing_rating.update_rating(rating)
            return existing_rating
        else:
            # Create new rating
            new_rating = cls(
                node_id=node_id,
                user_id=user_id,
                rating=rating,
                tenant_id=tenant_id,
                created_at=func.now(),
                updated_at=func.now()
            )
            session.add(new_rating)
            return new_rating

    @classmethod
    def get_node_ratings(cls, session, node_id):
        """Get all ratings for a node"""
        return session.query(cls).filter(
            cls.node_id == node_id
        ).order_by(cls.created_at.desc()).all()

    @classmethod
    def get_user_ratings(cls, session, user_id, limit=50):
        """Get all ratings by a user"""
        return session.query(cls).filter(
            cls.user_id == user_id
        ).order_by(cls.updated_at.desc()).limit(limit).all()

    @classmethod
    def get_node_rating_summary(cls, session, node_id):
        """Get rating summary for a node"""
        ratings = cls.get_node_ratings(session, node_id)
        
        if not ratings:
            return {
                "total_ratings": 0,
                "average_rating": 0,
                "rating_distribution": {1: 0, 2: 0, 3: 0, 4: 0, 5: 0},
                "positive_percentage": 0,
                "negative_percentage": 0
            }
        
        total = len(ratings)
        rating_values = [r.rating for r in ratings]
        average = sum(rating_values) / total
        
        # Count distribution
        distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for rating in rating_values:
            distribution[rating] += 1
        
        # Calculate percentages
        positive_count = sum(1 for r in rating_values if r >= 4)
        negative_count = sum(1 for r in rating_values if r <= 2)
        
        return {
            "total_ratings": total,
            "average_rating": round(average, 2),
            "rating_distribution": distribution,
            "positive_percentage": round((positive_count / total) * 100, 1),
            "negative_percentage": round((negative_count / total) * 100, 1)
        }

    @classmethod
    def get_top_rated_nodes(cls, session, limit=10, min_ratings=5, tenant_id=None):
        """Get top rated nodes"""
        query = session.query(
            cls.node_id,
            func.avg(cls.rating).label('avg_rating'),
            func.count(cls.id).label('rating_count')
        ).group_by(cls.node_id).having(
            func.count(cls.id) >= min_ratings
        )
        
        if tenant_id:
            query = query.filter(cls.tenant_id == tenant_id)
        
        return query.order_by(
            func.avg(cls.rating).desc()
        ).limit(limit).all()

    @classmethod
    def get_worst_rated_nodes(cls, session, limit=10, min_ratings=5, tenant_id=None):
        """Get worst rated nodes"""
        query = session.query(
            cls.node_id,
            func.avg(cls.rating).label('avg_rating'),
            func.count(cls.id).label('rating_count')
        ).group_by(cls.node_id).having(
            func.count(cls.id) >= min_ratings
        )
        
        if tenant_id:
            query = query.filter(cls.tenant_id == tenant_id)
        
        return query.order_by(
            func.avg(cls.rating).asc()
        ).limit(limit).all()

    @classmethod
    def get_rating_trends(cls, session, node_id, days=30):
        """Get rating trends for a node"""
        from datetime import datetime, timedelta
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        ratings = session.query(cls).filter(
            cls.node_id == node_id,
            cls.created_at >= cutoff_date
        ).order_by(cls.created_at.asc()).all()
        
        if not ratings:
            return []
        
        # Group by day
        daily_ratings = {}
        for rating in ratings:
            day = rating.created_at.date()
            if day not in daily_ratings:
                daily_ratings[day] = []
            daily_ratings[day].append(rating.rating)
        
        # Calculate daily averages
        trends = []
        for day, day_ratings in sorted(daily_ratings.items()):
            avg_rating = sum(day_ratings) / len(day_ratings)
            trends.append({
                "date": day.isoformat(),
                "average_rating": round(avg_rating, 2),
                "rating_count": len(day_ratings)
            })
        
        return trends

    @classmethod
    def get_user_rating_for_node(cls, session, user_id, node_id):
        """Get user's rating for a specific node"""
        return session.query(cls).filter(
            cls.user_id == user_id,
            cls.node_id == node_id
        ).first()

    @classmethod
    def has_user_rated_node(cls, session, user_id, node_id):
        """Check if user has rated a node"""
        rating = cls.get_user_rating_for_node(session, user_id, node_id)
        return rating is not None

    @classmethod
    def delete_rating(cls, session, user_id, node_id):
        """Delete a user's rating for a node"""
        rating = cls.get_user_rating_for_node(session, user_id, node_id)
        if rating:
            session.delete(rating)
            return True
        return False

    @classmethod
    def get_rating_statistics(cls, session, tenant_id=None, days=30):
        """Get overall rating statistics"""
        from datetime import datetime, timedelta
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        query = session.query(cls).filter(cls.created_at >= cutoff_date)
        
        if tenant_id:
            query = query.filter(cls.tenant_id == tenant_id)
        
        ratings = query.all()
        
        if not ratings:
            return {}
        
        rating_values = [r.rating for r in ratings]
        
        stats = {
            "total_ratings": len(ratings),
            "average_rating": sum(rating_values) / len(ratings),
            "unique_nodes_rated": len(set(r.node_id for r in ratings)),
            "unique_users_rating": len(set(r.user_id for r in ratings)),
            "rating_distribution": {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        }
        
        # Count distribution
        for rating in rating_values:
            stats["rating_distribution"][rating] += 1
        
        # Calculate percentages
        for star in stats["rating_distribution"]:
            count = stats["rating_distribution"][star]
            stats["rating_distribution"][star] = {
                "count": count,
                "percentage": round((count / len(ratings)) * 100, 1)
            }
        
        return stats

    @classmethod
    def get_most_active_raters(cls, session, limit=10, days=30, tenant_id=None):
        """Get users who rate nodes most frequently"""
        from datetime import datetime, timedelta
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        query = session.query(
            cls.user_id,
            func.count(cls.id).label('rating_count'),
            func.avg(cls.rating).label('avg_rating_given')
        ).filter(cls.created_at >= cutoff_date)
        
        if tenant_id:
            query = query.filter(cls.tenant_id == tenant_id)
        
        return query.group_by(cls.user_id).order_by(
            func.count(cls.id).desc()
        ).limit(limit).all()
