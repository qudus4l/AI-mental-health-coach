"""Conversation memory service using RAG for better context retrieval.

This module provides a Retrieval Augmented Generation (RAG) system
to efficiently store and retrieve relevant parts of conversation history.
"""

from typing import Dict, List, Optional, Any, Tuple
import datetime
from sqlalchemy.orm import Session
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from src.mental_health_coach.models.user import User
from src.mental_health_coach.models.conversation import Conversation, Message, ImportantMemory


class ConversationMemoryService:
    """Service for storing and retrieving conversation history using RAG.
    
    This service provides a simple vector-based retrieval system for 
    accessing relevant parts of a user's conversation history. It uses
    TF-IDF vectorization and cosine similarity for retrieval.
    
    Attributes:
        db: Database session.
        user: User to manage conversation memory for.
        vectorizer: TF-IDF vectorizer for text embedding.
    """
    
    def __init__(self, db: Session, user: User) -> None:
        """Initialize the conversation memory service.
        
        Args:
            db: Database session.
            user: User to manage conversation memory for.
        """
        self.db = db
        self.user = user
        # Initialize vectorizer with more flexible parameters to handle edge cases
        self.vectorizer = TfidfVectorizer(
            lowercase=True,
            stop_words="english",
            min_df=0.0,  # Allow terms that appear in any document (was 1)
            max_df=1.0,  # Allow terms that appear in all documents (was 0.9)
            ngram_range=(1, 2)  # Include both unigrams and bigrams for better matching
        )
        
    def index_conversations(self) -> Tuple[List[str], List[Dict[str, Any]], np.ndarray]:
        """Index all conversations for the user for efficient retrieval.
        
        This method creates vector embeddings for all messages in the user's
        conversations to enable semantic search.
        
        Returns:
            Tuple containing:
                - List of conversation chunks as strings
                - List of metadata for each chunk
                - Matrix of TF-IDF vector embeddings for each chunk
        """
        # Get all conversations for the user
        conversations = (
            self.db.query(Conversation)
            .filter(Conversation.user_id == self.user.id)
            .order_by(Conversation.started_at.asc())
            .all()
        )
        
        # Process conversations into chunks for indexing
        chunks = []
        metadata = []
        
        for conversation in conversations:
            # Get messages for this conversation
            messages = (
                self.db.query(Message)
                .filter(Message.conversation_id == conversation.id)
                .order_by(Message.created_at.asc())
                .all()
            )
            
            # Process conversation in chunks of 3 messages for better context
            for i in range(0, len(messages), 3):
                chunk_messages = messages[i:i+3]
                
                # Skip empty chunks
                if not chunk_messages:
                    continue
                
                # Create chunk text
                chunk_text = ""
                for msg in chunk_messages:
                    sender = "User" if msg.is_from_user else "Coach"
                    chunk_text += f"{sender}: {msg.content}\n"
                
                # Add chunk and metadata
                chunks.append(chunk_text)
                metadata.append({
                    "conversation_id": conversation.id,
                    "conversation_title": conversation.title,
                    "is_formal_session": conversation.is_formal_session,
                    "session_number": conversation.session_number,
                    "date": conversation.started_at.strftime("%Y-%m-%d"),
                    "first_message_id": chunk_messages[0].id if chunk_messages else None,
                    "last_message_id": chunk_messages[-1].id if chunk_messages else None,
                })
        
        # Create vector embeddings
        if not chunks:
            return [], [], np.array([])
            
        vectors = self.vectorizer.fit_transform(chunks)
        
        return chunks, metadata, vectors
    
    def store_important_memory(
        self, 
        content: str, 
        category: Optional[str] = None, 
        importance_score: float = 0.5,
        conversation_id: Optional[int] = None
    ) -> ImportantMemory:
        """Store an important memory from a conversation.
        
        Args:
            content: The content of the memory.
            category: Optional category for the memory (e.g., triggers, coping_strategies).
            importance_score: A score from 0.0 to 1.0 indicating the memory's importance.
            conversation_id: Optional ID of the conversation this memory is from.
            
        Returns:
            The created ImportantMemory object.
        """
        # Create the memory object
        memory = ImportantMemory(
            user_id=self.user.id,
            conversation_id=conversation_id,
            content=content,
            category=category,
            importance_score=importance_score,
            created_at=datetime.datetime.utcnow()
        )
        
        # Add to database
        self.db.add(memory)
        self.db.commit()
        self.db.refresh(memory)
        
        return memory
    
    def get_important_memories(
        self, 
        category: Optional[str] = None,
        limit: int = 50,
        min_importance: float = 0.0
    ) -> List[ImportantMemory]:
        """Retrieve important memories for the user.
        
        Args:
            category: Optional filter by memory category.
            limit: Maximum number of memories to retrieve.
            min_importance: Minimum importance score threshold.
            
        Returns:
            List of ImportantMemory objects.
        """
        # Build query
        query = (
            self.db.query(ImportantMemory)
            .filter(ImportantMemory.user_id == self.user.id)
            .filter(ImportantMemory.importance_score >= min_importance)
        )
        
        # Add category filter if provided
        if category:
            query = query.filter(ImportantMemory.category == category)
        
        # Get results
        memories = (
            query
            .order_by(ImportantMemory.created_at.desc())
            .limit(limit)
            .all()
        )
        
        return memories
    
    def retrieve_relevant_context(
        self, query: str, max_results: int = 5
    ) -> List[Dict[str, Any]]:
        """Retrieve the most relevant conversation chunks for a given query.
        
        Args:
            query: The query text to find relevant conversation history for.
            max_results: Maximum number of results to return.
            
        Returns:
            List of dictionaries containing relevant chunks and their metadata.
        """
        # Index conversations
        chunks, metadata, vectors = self.index_conversations()
        
        # If no conversations exist, return empty list
        if not chunks:
            return []
        
        # Vectorize the query
        query_vector = self.vectorizer.transform([query])
        
        # Calculate similarities
        similarities = cosine_similarity(query_vector, vectors).flatten()
        
        # Get top results
        top_indices = similarities.argsort()[-max_results:][::-1]
        
        # Return results
        results = []
        for idx in top_indices:
            if similarities[idx] > 0.1:  # Only include somewhat relevant results
                results.append({
                    "text": chunks[idx],
                    "metadata": metadata[idx],
                    "similarity_score": float(similarities[idx]),
                })
        
        return results
    
    def retrieve_therapeutic_timeline(self) -> List[Dict[str, Any]]:
        """Create a therapeutic timeline for the user.
        
        This method creates a chronological timeline of key therapeutic moments,
        including formal sessions, homework assignments, and important memories.
        
        Returns:
            List of dictionaries containing timeline events.
        """
        timeline = []
        
        # Add formal sessions to timeline
        formal_sessions = (
            self.db.query(Conversation)
            .filter(
                Conversation.user_id == self.user.id,
                Conversation.is_formal_session == True,
            )
            .order_by(Conversation.started_at.asc())
            .all()
        )
        
        for session in formal_sessions:
            timeline.append({
                "type": "formal_session",
                "date": session.started_at,
                "title": session.title or f"Session #{session.session_number}",
                "details": {
                    "session_number": session.session_number,
                    "conversation_id": session.id,
                    "duration_minutes": (
                        (session.ended_at - session.started_at).total_seconds() / 60
                        if session.ended_at
                        else None
                    ),
                },
            })
        
        # Add important memories to timeline
        memories = (
            self.db.query(ImportantMemory)
            .filter(ImportantMemory.user_id == self.user.id)
            .order_by(ImportantMemory.created_at.asc())
            .all()
        )
        
        for memory in memories:
            timeline.append({
                "type": "important_memory",
                "date": memory.created_at,
                "title": f"Memory: {memory.category.capitalize()}" if memory.category else "Important Memory",
                "details": {
                    "content": memory.content,
                    "category": memory.category,
                    "importance_score": memory.importance_score,
                },
            })
        
        # Add homework assignments to timeline
        from src.mental_health_coach.models.homework import HomeworkAssignment
        
        assignments = (
            self.db.query(HomeworkAssignment)
            .filter(HomeworkAssignment.user_id == self.user.id)
            .order_by(HomeworkAssignment.created_at.asc())
            .all()
        )
        
        for assignment in assignments:
            # Add assignment creation
            timeline.append({
                "type": "homework_assigned",
                "date": assignment.created_at,
                "title": f"Homework: {assignment.title}",
                "details": {
                    "homework_id": assignment.id,
                    "description": assignment.description,
                    "technique": assignment.technique,
                    "due_date": assignment.due_date,
                },
            })
            
            # Add homework completion if completed
            if assignment.is_completed and assignment.completion_date:
                timeline.append({
                    "type": "homework_completed",
                    "date": assignment.completion_date,
                    "title": f"Completed: {assignment.title}",
                    "details": {
                        "homework_id": assignment.id,
                        "completion_notes": assignment.completion_notes,
                        "days_to_complete": (
                            (assignment.completion_date - assignment.created_at).days
                        ),
                    },
                })
        
        # Sort timeline by date
        timeline.sort(key=lambda x: x["date"])
        
        return timeline
    
    def get_recent_themes(self, days: int = 30, min_occurrences: int = 2) -> List[Dict[str, Any]]:
        """Identify common themes in recent conversations.
        
        Args:
            days: Number of days to look back.
            min_occurrences: Minimum occurrences to consider a theme significant.
            
        Returns:
            List of dictionaries containing theme information.
        """
        # Get recent conversations
        cutoff_date = datetime.datetime.utcnow() - datetime.timedelta(days=days)
        
        recent_conversations = (
            self.db.query(Conversation)
            .filter(
                Conversation.user_id == self.user.id,
                Conversation.started_at >= cutoff_date,
            )
            .all()
        )
        
        # Get messages from these conversations
        conversation_ids = [c.id for c in recent_conversations]
        if not conversation_ids:
            return []
            
        messages = (
            self.db.query(Message)
            .filter(Message.conversation_id.in_(conversation_ids))
            .order_by(Message.created_at.asc())
            .all()
        )
        
        # Concatenate all user messages
        user_messages = " ".join([
            msg.content for msg in messages if msg.is_from_user
        ])
        
        # Use TF-IDF to extract important terms
        if not user_messages.strip():
            return []
            
        vectorizer = TfidfVectorizer(
            lowercase=True,
            stop_words="english",
            min_df=min_occurrences,
            max_df=0.7,
            ngram_range=(1, 2)
        )
        
        try:
            tfidf_matrix = vectorizer.fit_transform([user_messages])
            feature_names = vectorizer.get_feature_names_out()
            
            # Get scores for each term
            scores = tfidf_matrix.toarray()[0]
            
            # Create theme entries
            themes = []
            for term, score in zip(feature_names, scores):
                if score > 0.01:  # Threshold to consider significant
                    themes.append({
                        "theme": term,
                        "importance_score": float(score),
                    })
            
            # Sort by importance
            themes.sort(key=lambda x: x["importance_score"], reverse=True)
            
            return themes[:10]  # Return top 10 themes
        except ValueError:
            # Handle case where vectorizer couldn't be fitted
            return [] 