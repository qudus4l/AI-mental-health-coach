"""Dashboard service for user progress tracking.

This module provides functionality for generating dashboard data and metrics
related to user progress in therapy.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple

from sqlalchemy import func
from sqlalchemy.orm import Session

from src.mental_health_coach.models.user import User
from src.mental_health_coach.models.conversation import Conversation, Message
from src.mental_health_coach.models.homework import HomeworkAssignment, HomeworkProgressNote


class DashboardService:
    """Service for generating dashboard data for users.
    
    This service aggregates data from various sources to provide insights
    into user progress and engagement with the mental health coach.
    
    Attributes:
        db: Database session.
        user: User to generate dashboard data for.
    """
    
    def __init__(self, db: Session, user: User) -> None:
        """Initialize the dashboard service.
        
        Args:
            db: Database session.
            user: User to generate dashboard data for.
        """
        self.db = db
        self.user = user
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get comprehensive dashboard data for the user.
        
        Returns:
            Dict[str, Any]: Dashboard data including session stats, homework stats,
                            engagement metrics, and progress over time.
        """
        # Get data from various sources
        session_stats = self.get_session_stats()
        homework_stats = self.get_homework_stats()
        engagement_metrics = self.get_engagement_metrics()
        progress_over_time = self.get_progress_over_time()
        upcoming_sessions = self.get_upcoming_sessions()
        
        # Combine into a single dashboard object
        dashboard_data = {
            "session_stats": session_stats,
            "homework_stats": homework_stats,
            "engagement_metrics": engagement_metrics,
            "progress_over_time": progress_over_time,
            "upcoming_sessions": upcoming_sessions,
            "last_updated": datetime.utcnow(),
        }
        
        return dashboard_data
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get statistics about user therapy sessions.
        
        Returns:
            Dict[str, Any]: Session statistics including total sessions,
                           session frequency, average duration, etc.
        """
        # Count total formal sessions
        total_sessions = (
            self.db.query(func.count(Conversation.id))
            .filter(
                Conversation.user_id == self.user.id,
                Conversation.is_formal_session == True,
                Conversation.ended_at != None,
            )
            .scalar() or 0
        )
        
        # Calculate average messages per session
        session_message_counts = (
            self.db.query(
                Conversation.id,
                func.count(Message.id).label("message_count"),
            )
            .join(Message, Conversation.id == Message.conversation_id)
            .filter(
                Conversation.user_id == self.user.id,
                Conversation.is_formal_session == True,
                Conversation.ended_at != None,
            )
            .group_by(Conversation.id)
            .all()
        )
        
        avg_messages_per_session = 0
        if session_message_counts:
            avg_messages_per_session = sum(count for _, count in session_message_counts) / len(session_message_counts)
        
        # Calculate average session duration
        session_durations = []
        sessions_with_duration = (
            self.db.query(Conversation)
            .filter(
                Conversation.user_id == self.user.id,
                Conversation.is_formal_session == True,
                Conversation.ended_at != None,
            )
            .all()
        )
        
        for session in sessions_with_duration:
            if session.started_at and session.ended_at:
                duration = (session.ended_at - session.started_at).total_seconds() / 60  # minutes
                session_durations.append(duration)
        
        avg_session_duration = 0
        if session_durations:
            avg_session_duration = sum(session_durations) / len(session_durations)
        
        # Get session frequency (sessions per week)
        four_weeks_ago = datetime.utcnow() - timedelta(days=28)
        recent_session_count = (
            self.db.query(func.count(Conversation.id))
            .filter(
                Conversation.user_id == self.user.id,
                Conversation.is_formal_session == True,
                Conversation.started_at >= four_weeks_ago,
            )
            .scalar() or 0
        )
        
        sessions_per_week = recent_session_count / 4
        
        return {
            "total_sessions": total_sessions,
            "sessions_per_week": sessions_per_week,
            "avg_messages_per_session": avg_messages_per_session,
            "avg_session_duration_minutes": avg_session_duration,
            "last_session_date": self._get_last_session_date(),
        }
    
    def get_homework_stats(self) -> Dict[str, Any]:
        """Get statistics about user homework assignments.
        
        Returns:
            Dict[str, Any]: Homework statistics including completion rate,
                           overdue assignments, current assignments, etc.
        """
        # Count total homework assignments
        total_assignments = (
            self.db.query(func.count(HomeworkAssignment.id))
            .filter(HomeworkAssignment.user_id == self.user.id)
            .scalar() or 0
        )
        
        # Count completed assignments
        completed_assignments = (
            self.db.query(func.count(HomeworkAssignment.id))
            .filter(
                HomeworkAssignment.user_id == self.user.id,
                HomeworkAssignment.is_completed == True,
            )
            .scalar() or 0
        )
        
        # Calculate completion rate
        completion_rate = 0
        if total_assignments > 0:
            completion_rate = (completed_assignments / total_assignments) * 100
        
        # Get current (incomplete and not overdue) assignments
        now = datetime.utcnow()
        current_assignments = (
            self.db.query(func.count(HomeworkAssignment.id))
            .filter(
                HomeworkAssignment.user_id == self.user.id,
                HomeworkAssignment.is_completed == False,
                HomeworkAssignment.due_date > now,
            )
            .scalar() or 0
        )
        
        # Get overdue assignments
        overdue_assignments = (
            self.db.query(func.count(HomeworkAssignment.id))
            .filter(
                HomeworkAssignment.user_id == self.user.id,
                HomeworkAssignment.is_completed == False,
                HomeworkAssignment.due_date <= now,
            )
            .scalar() or 0
        )
        
        # Calculate average time to complete
        completion_times = []
        completed_homework = (
            self.db.query(HomeworkAssignment)
            .filter(
                HomeworkAssignment.user_id == self.user.id,
                HomeworkAssignment.is_completed == True,
                HomeworkAssignment.completion_date != None,
            )
            .all()
        )
        
        for hw in completed_homework:
            if hw.created_at and hw.completion_date:
                time_to_complete = (hw.completion_date - hw.created_at).total_seconds() / (60 * 60 * 24)  # days
                completion_times.append(time_to_complete)
        
        avg_time_to_complete = 0
        if completion_times:
            avg_time_to_complete = sum(completion_times) / len(completion_times)
        
        return {
            "total_assignments": total_assignments,
            "completed_assignments": completed_assignments,
            "completion_rate": completion_rate,
            "current_assignments": current_assignments,
            "overdue_assignments": overdue_assignments,
            "avg_days_to_complete": avg_time_to_complete,
        }
    
    def get_engagement_metrics(self) -> Dict[str, Any]:
        """Get metrics related to user engagement with the platform.
        
        Returns:
            Dict[str, Any]: Engagement metrics including conversation frequency,
                           response times, total messages, etc.
        """
        # Count total conversations
        total_conversations = (
            self.db.query(func.count(Conversation.id))
            .filter(Conversation.user_id == self.user.id)
            .scalar() or 0
        )
        
        # Count total messages
        total_messages = (
            self.db.query(func.count(Message.id))
            .join(Conversation, Message.conversation_id == Conversation.id)
            .filter(Conversation.user_id == self.user.id)
            .scalar() or 0
        )
        
        # Count user messages
        user_messages = (
            self.db.query(func.count(Message.id))
            .join(Conversation, Message.conversation_id == Conversation.id)
            .filter(
                Conversation.user_id == self.user.id,
                Message.is_from_user == True,
            )
            .scalar() or 0
        )
        
        # Calculate average messages per day over the last 30 days
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_messages = (
            self.db.query(func.count(Message.id))
            .join(Conversation, Message.conversation_id == Conversation.id)
            .filter(
                Conversation.user_id == self.user.id,
                Message.created_at >= thirty_days_ago,
            )
            .scalar() or 0
        )
        
        messages_per_day = recent_messages / 30
        
        return {
            "total_conversations": total_conversations,
            "total_messages": total_messages,
            "user_messages": user_messages,
            "coach_messages": total_messages - user_messages,
            "messages_per_day": messages_per_day,
            "days_since_last_conversation": self._days_since_last_activity(),
        }
    
    def get_progress_over_time(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get time-series data showing user progress over time.
        
        Returns:
            Dict[str, List[Dict[str, Any]]]: Time-series data for various metrics.
        """
        # This would typically involve more complex queries and data processing
        # For now, we'll return a simplified version with weekly data points
        
        # Get homework completion by week
        now = datetime.utcnow()
        weeks_data = []
        
        for i in range(4):  # Last 4 weeks
            week_start = now - timedelta(days=now.weekday(), weeks=i)
            week_end = week_start + timedelta(days=6)
            
            # Format dates for display
            week_label = f"{week_start.strftime('%b %d')} - {week_end.strftime('%b %d')}"
            
            # Count completed homework for this week
            completed_hw = (
                self.db.query(func.count(HomeworkAssignment.id))
                .filter(
                    HomeworkAssignment.user_id == self.user.id,
                    HomeworkAssignment.is_completed == True,
                    HomeworkAssignment.completion_date >= week_start,
                    HomeworkAssignment.completion_date <= week_end,
                )
                .scalar() or 0
            )
            
            # Count conversations for this week
            conversations = (
                self.db.query(func.count(Conversation.id))
                .filter(
                    Conversation.user_id == self.user.id,
                    Conversation.started_at >= week_start,
                    Conversation.started_at <= week_end,
                )
                .scalar() or 0
            )
            
            weeks_data.append({
                "week": week_label,
                "completed_homework": completed_hw,
                "conversations": conversations,
            })
        
        # Reverse to show oldest to newest
        weeks_data.reverse()
        
        return {
            "weekly_data": weeks_data,
        }
    
    def get_upcoming_sessions(self) -> List[Dict[str, Any]]:
        """Get upcoming scheduled therapy sessions.
        
        Returns:
            List[Dict[str, Any]]: List of upcoming sessions with date and time.
        """
        from src.mental_health_coach.models.user import SessionSchedule
        
        # Get all active session schedules
        schedules = (
            self.db.query(SessionSchedule)
            .filter(
                SessionSchedule.user_id == self.user.id,
                SessionSchedule.is_active == True,
            )
            .all()
        )
        
        # Convert schedules to upcoming sessions
        upcoming_sessions = []
        
        if schedules:
            today = datetime.utcnow().date()
            weekday = today.weekday()  # 0 = Monday, 6 = Sunday
            
            for schedule in schedules:
                # Calculate days until next occurrence
                days_until = (schedule.day_of_week - weekday) % 7
                
                # If it's the same day but the time has passed, add 7 days
                if days_until == 0:
                    now = datetime.utcnow()
                    if (now.hour > schedule.hour or 
                        (now.hour == schedule.hour and now.minute >= schedule.minute)):
                        days_until = 7
                
                next_date = today + timedelta(days=days_until)
                next_datetime = datetime.combine(
                    next_date,
                    datetime.min.time(),
                ) + timedelta(hours=schedule.hour, minutes=schedule.minute)
                
                day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
                day_name = day_names[schedule.day_of_week]
                
                upcoming_sessions.append({
                    "day": day_name,
                    "time": f"{schedule.hour:02d}:{schedule.minute:02d}",
                    "next_session": next_datetime,
                    "days_until": days_until,
                })
        
        # Sort by next occurrence
        upcoming_sessions.sort(key=lambda x: x["next_session"])
        
        return upcoming_sessions
    
    def _get_last_session_date(self) -> Optional[datetime]:
        """Get the date of the user's last formal therapy session.
        
        Returns:
            Optional[datetime]: Date of the last session, or None if no sessions exist.
        """
        last_session = (
            self.db.query(Conversation)
            .filter(
                Conversation.user_id == self.user.id,
                Conversation.is_formal_session == True,
                Conversation.ended_at != None,
            )
            .order_by(Conversation.ended_at.desc())
            .first()
        )
        
        if last_session and last_session.ended_at:
            return last_session.ended_at
        
        return None
    
    def _days_since_last_activity(self) -> int:
        """Calculate days since the user's last activity.
        
        Returns:
            int: Number of days since last activity, or 0 if activity today.
        """
        # Find most recent message from user
        last_message = (
            self.db.query(Message)
            .join(Conversation, Message.conversation_id == Conversation.id)
            .filter(
                Conversation.user_id == self.user.id,
                Message.is_from_user == True,
            )
            .order_by(Message.created_at.desc())
            .first()
        )
        
        if not last_message or not last_message.created_at:
            return 0
        
        # Calculate days since last message
        now = datetime.utcnow()
        delta = now - last_message.created_at
        return delta.days 