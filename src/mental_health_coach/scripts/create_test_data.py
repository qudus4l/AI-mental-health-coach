#!/usr/bin/env python3
"""Script to create test data for the Mental Health Coach application.

This script creates a test user with a complete profile, conversations,
messages, homework assignments, and other related data.

Usage:
    python -m src.mental_health_coach.scripts.create_test_data
"""

import sys
import logging
from datetime import datetime, timedelta
import random
from typing import Dict, Any, List

from sqlalchemy.orm import Session

from src.mental_health_coach.database import SessionLocal, engine, Base
from src.mental_health_coach.models.user import User, UserProfile, SessionSchedule
from src.mental_health_coach.models.conversation import Conversation, Message, ImportantMemory
from src.mental_health_coach.models.homework import HomeworkAssignment, HomeworkStatus
from src.mental_health_coach.auth.security import get_password_hash

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_test_user(db: Session) -> User:
    """Create a test user or return existing one.
    
    Args:
        db: Database session.
        
    Returns:
        User: Created or existing test user.
    """
    # Check if test user already exists
    test_user = db.query(User).filter(User.email == "test@example.com").first()
    if test_user:
        logger.info("Test user already exists")
        return test_user
    
    # Create new test user
    hashed_password = get_password_hash("Password123!")
    test_user = User(
        email="test@example.com",
        hashed_password=hashed_password,
        first_name="Test",
        last_name="User",
        is_active=True,
        is_verified=True,
        profile_data=None
    )
    db.add(test_user)
    db.commit()
    db.refresh(test_user)
    logger.info(f"Created test user with ID {test_user.id}")
    return test_user


def create_user_profile(db: Session, user: User) -> UserProfile:
    """Create a profile for the test user.
    
    Args:
        db: Database session.
        user: User to create profile for.
        
    Returns:
        UserProfile: Created user profile.
    """
    # Check if profile already exists
    existing_profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
    if existing_profile:
        logger.info("User profile already exists")
        return existing_profile
    
    # Create new profile
    profile = UserProfile(
        user_id=user.id,
        age=30,
        location="San Francisco",
        anxiety_score=6,
        depression_score=5,
        communication_preference="text",
        session_frequency="weekly"
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    logger.info(f"Created user profile for user {user.id}")
    return profile


def create_session_schedule(db: Session, user: User) -> None:
    """Create session schedules for the test user.
    
    Args:
        db: Database session.
        user: User to create schedules for.
    """
    # Check if schedules already exist
    existing_schedules = db.query(SessionSchedule).filter(
        SessionSchedule.user_id == user.id,
        SessionSchedule.is_active == True
    ).all()
    
    if existing_schedules:
        logger.info(f"User already has {len(existing_schedules)} session schedules")
        return
    
    # Create weekly schedule on Monday at 9:00 AM
    monday_schedule = SessionSchedule(
        user_id=user.id,
        day_of_week=0,  # Monday
        hour=9,
        minute=0,
        is_active=True
    )
    
    # Create weekly schedule on Thursday at 4:30 PM
    thursday_schedule = SessionSchedule(
        user_id=user.id,
        day_of_week=3,  # Thursday
        hour=16,
        minute=30,
        is_active=True
    )
    
    db.add(monday_schedule)
    db.add(thursday_schedule)
    db.commit()
    logger.info(f"Created 2 session schedules for user {user.id}")


def create_conversations(db: Session, user: User) -> List[Conversation]:
    """Create test conversations for the user.
    
    Args:
        db: Database session.
        user: User to create conversations for.
        
    Returns:
        List[Conversation]: Created conversations.
    """
    # Check if conversations already exist
    existing_conversations = db.query(Conversation).filter(
        Conversation.user_id == user.id
    ).all()
    
    if existing_conversations:
        logger.info(f"User already has {len(existing_conversations)} conversations")
        return existing_conversations
    
    conversations = []
    
    # Create 5 conversations with varying dates
    now = datetime.utcnow()
    
    # First formal session (completed)
    conv1 = Conversation(
        user_id=user.id,
        title="Initial Assessment",
        is_formal_session=True,
        session_number=1,
        started_at=now - timedelta(days=14),
        ended_at=now - timedelta(days=14) + timedelta(hours=1),
        summary="Initial assessment of anxiety and depression symptoms. User reported feeling overwhelmed at work and having trouble sleeping. Discussed potential coping strategies and set initial goals."
    )
    
    # Second formal session (completed)
    conv2 = Conversation(
        user_id=user.id,
        title="Follow-up Session",
        is_formal_session=True,
        session_number=2,
        started_at=now - timedelta(days=7),
        ended_at=now - timedelta(days=7) + timedelta(hours=1),
        summary="Follow-up on initial goals. User reported some improvement in sleep quality after implementing bedtime routine. Continued anxiety at work, but beginning to use breathing techniques. Introduced thought challenging worksheet."
    )
    
    # Quick check-in (completed)
    conv3 = Conversation(
        user_id=user.id,
        title="Quick Check-in",
        is_formal_session=False,
        started_at=now - timedelta(days=4),
        ended_at=now - timedelta(days=4) + timedelta(minutes=15),
        summary="Brief check-in about work stressors. User feeling better after using mindfulness techniques during a difficult meeting."
    )
    
    # Third formal session (completed)
    conv4 = Conversation(
        user_id=user.id,
        title="Progress Review",
        is_formal_session=True,
        session_number=3,
        started_at=now - timedelta(days=1),
        ended_at=now - timedelta(days=1) + timedelta(hours=1),
        summary="Reviewed progress on anxiety management. User reporting significant improvement in workplace stress through mindfulness practice and cognitive restructuring. Sleep still inconsistent. Introduced progressive muscle relaxation technique."
    )
    
    # Current conversation (in progress)
    conv5 = Conversation(
        user_id=user.id,
        title="Current Session",
        is_formal_session=False,
        started_at=now - timedelta(minutes=30),
        ended_at=None,
        summary=None
    )
    
    conversations = [conv1, conv2, conv3, conv4, conv5]
    db.add_all(conversations)
    db.commit()
    
    # Refresh all conversations to get their IDs
    for conv in conversations:
        db.refresh(conv)
    
    logger.info(f"Created {len(conversations)} conversations for user {user.id}")
    return conversations


def create_messages(db: Session, conversations: List[Conversation]) -> None:
    """Create test messages for the conversations.
    
    Args:
        db: Database session.
        conversations: Conversations to create messages for.
    """
    all_messages = []
    
    # Sample conversation flows
    conversation_flows = [
        # Initial assessment conversation
        [
            {"is_from_user": False, "content": "Hello! I'm your AI mental health coach. I'm here to help you manage stress, anxiety, and other mental health challenges. How are you feeling today?"},
            {"is_from_user": True, "content": "I've been feeling pretty anxious lately, especially at work. And I'm having trouble sleeping."},
            {"is_from_user": False, "content": "I'm sorry to hear you're struggling with anxiety and sleep issues. That can be really challenging. Can you tell me more about what's happening at work that's causing anxiety?"},
            {"is_from_user": True, "content": "I have a lot of deadlines and my boss keeps adding more projects. I feel overwhelmed and can't keep up."},
            {"is_from_user": False, "content": "That sounds really stressful. It's common to feel anxious when workloads become overwhelming. Have you tried any strategies to manage the stress so far?"},
            {"is_from_user": True, "content": "I've tried making to-do lists, but they just get longer and make me more anxious."},
            {"is_from_user": False, "content": "I understand how to-do lists can sometimes add to the stress when they keep growing. Let's talk about some other strategies that might help, both for the workplace anxiety and sleep issues. Would you be open to trying some simple breathing exercises when you feel overwhelmed?"},
            {"is_from_user": True, "content": "I guess I could try that."},
            {"is_from_user": False, "content": "Great! Let's start with a basic breathing technique. When you notice anxiety rising, try this: breathe in slowly through your nose for 4 counts, hold for 2, then exhale through your mouth for 6 counts. Repeat 3-5 times. This helps activate your parasympathetic nervous system, which calms the stress response. For sleep, creating a consistent bedtime routine can help signal your body it's time to rest. Could you create a simple 15-minute routine before bed?"},
            {"is_from_user": True, "content": "I could try reading or something instead of looking at my phone."},
            {"is_from_user": False, "content": "That's an excellent idea! Screen light can interfere with melatonin production, making it harder to fall asleep. Reading a physical book is a great alternative. For our next session, I'd like you to try the breathing technique when work anxiety spikes, and create that bedtime routine without screens. We'll check in on how these strategies are working. How does that sound?"},
            {"is_from_user": True, "content": "I'll give it a try and let you know how it goes."},
            {"is_from_user": False, "content": "Perfect! I look forward to hearing about your experience. Remember, these changes take practice, so be patient with yourself. Is there anything else you'd like to discuss today?"},
            {"is_from_user": True, "content": "No, I think that's enough to start with."},
            {"is_from_user": False, "content": "Sounds good. We've covered some important ground today. To summarize: you'll practice the 4-2-6 breathing technique for work anxiety and create a screen-free bedtime routine to help with sleep. I'm here if you need to check in before our next session. Take care!"}
        ],
        
        # Follow-up session
        [
            {"is_from_user": False, "content": "Welcome back! How have you been since our last session? Were you able to try the breathing exercises and bedtime routine we discussed?"},
            {"is_from_user": True, "content": "The bedtime routine has been helping a bit. I've been reading instead of looking at my phone and I think I'm falling asleep faster. Work is still stressful though."},
            {"is_from_user": False, "content": "That's great progress with the sleep routine! Even small improvements are worth celebrating. Can you tell me more about how the breathing exercises went at work?"},
            {"is_from_user": True, "content": "I tried them a few times, but it's hard to remember when I'm stressed. When I did remember, they helped a little."},
            {"is_from_user": False, "content": "It's completely normal to forget in the moment when stress is high. The fact that you tried them and found them somewhat helpful is a good sign. Perhaps we could set some reminders? Some people find it helpful to put sticky notes in visible places or set gentle alarms on their phone."},
            {"is_from_user": True, "content": "I could put a note on my computer monitor. That might help me remember."},
            {"is_from_user": False, "content": "That's a great idea! Visual cues can be very effective. I'd also like to introduce another tool that might help with the work stress - a thought challenging worksheet. This helps identify and reframe negative thought patterns that fuel anxiety. Would you be interested in trying this?"},
            {"is_from_user": True, "content": "How does it work?"},
            {"is_from_user": False, "content": "It's a simple process: when you notice anxious thoughts, write down the situation, your automatic thought, and how it makes you feel. Then question that thought: what evidence supports it? What evidence contradicts it? Is there another way to look at the situation? Finally, write a more balanced thought. For example, if you think 'I'll never finish all this work,' you might reframe it as 'This is challenging, but I can prioritize and take it one step at a time.' Would you like to try this?"},
            {"is_from_user": True, "content": "That makes sense. I'll try it next time I'm feeling overwhelmed at work."},
            {"is_from_user": False, "content": "Excellent! For our next session, please continue with your bedtime routine, practice the breathing exercises with your new reminder, and try the thought challenging exercise at least once. How does that sound?"},
            {"is_from_user": True, "content": "That sounds doable."},
            {"is_from_user": False, "content": "Great! Is there anything else you'd like to discuss today?"},
            {"is_from_user": True, "content": "No, I think I have enough to work on for now."},
            {"is_from_user": False, "content": "Perfect. To summarize today's session: your sleep is improving with the bedtime routine, you'll add a visual reminder for breathing exercises, and you'll try the thought challenging worksheet for work stress. I'm proud of the steps you're taking. Take care, and I'll see you next time!"}
        ],
        
        # Quick check-in
        [
            {"is_from_user": True, "content": "I just wanted to check in. I had a really stressful meeting today but I used the breathing techniques and they actually helped!"},
            {"is_from_user": False, "content": "That's fantastic news! I'm so glad the breathing techniques helped during your stressful meeting. That's a real victory. Can you tell me more about how you used them and what you noticed?"},
            {"is_from_user": True, "content": "I started feeling anxious when my boss criticized part of my project. I noticed my heart racing, so I excused myself for a minute and did the breathing exercise in the hallway. When I went back in, I felt calmer and could think more clearly."},
            {"is_from_user": False, "content": "That's an excellent application of the technique! You recognized your physical symptoms, took appropriate action, and were able to regulate your emotions effectively. This is exactly how these skills are meant to work. How did the rest of the meeting go after you returned?"},
            {"is_from_user": True, "content": "Much better. I was able to explain my reasoning and even suggest some improvements to address the concerns."},
            {"is_from_user": False, "content": "That's truly impressive. You not only managed your anxiety but were able to engage constructively and professionally. This is a great example of how these coping strategies can make a real difference in everyday situations. How are you feeling about this success?"},
            {"is_from_user": True, "content": "Pretty good actually. It makes me feel like I have some control over my anxiety."},
            {"is_from_user": False, "content": "That sense of control is so important! It's empowering to know you have tools that work. This experience is also valuable evidence you can use in your thought challenging work - proof that you can handle stressful situations effectively. Would you like to discuss any other strategies for similar situations in the future?"},
            {"is_from_user": True, "content": "No, I just wanted to share this win. I need to get back to work now."},
            {"is_from_user": False, "content": "I'm really glad you shared this success! It's important to acknowledge and celebrate these wins. Keep using these techniques, and remember this positive experience when you face challenges. I'm here if you need anything else. Have a great rest of your day!"}
        ],
        
        # Progress review
        [
            {"is_from_user": False, "content": "Welcome back! It's been a week since our last formal session. How have things been going with your anxiety management and sleep?"},
            {"is_from_user": True, "content": "Work has been much better. I've been using the breathing techniques regularly and the thought challenging worksheet has really helped me put things in perspective. Sleep is still hit or miss though."},
            {"is_from_user": False, "content": "That's wonderful progress with your work anxiety! Using both the breathing techniques and thought challenging consistently shows real commitment. Can you share an example of how the thought challenging helped?"},
            {"is_from_user": True, "content": "When I got a bunch of revision requests on a project, my first thought was 'This is terrible, I did everything wrong.' After using the worksheet, I realized the revisions were actually constructive and only affected a small part of the project. My revised thought was 'Getting feedback is part of the process and helps improve the final result.'"},
            {"is_from_user": False, "content": "That's an excellent example of cognitive restructuring! You identified a distorted thought (overgeneralization and catastrophizing), examined the evidence, and created a more balanced perspective. This is exactly how the technique is meant to work. Regarding your sleep, what aspects are still challenging?"},
            {"is_from_user": True, "content": "I still wake up in the middle of the night sometimes and can't fall back asleep. My mind starts racing with all the things I need to do the next day."},
            {"is_from_user": False, "content": "That's a common sleep maintenance issue, especially when anxiety is a factor. I'd like to introduce a new technique that might help with this: Progressive Muscle Relaxation (PMR). It helps reduce physical tension and quiet the mind. Would you like to learn about this?"},
            {"is_from_user": True, "content": "Yes, I'm willing to try anything that might help."},
            {"is_from_user": False, "content": "Great! PMR involves systematically tensing and then relaxing different muscle groups throughout your body. Start at your feet and work upward. Tense each muscle group for 5-7 seconds, then release and feel the relaxation for 20-30 seconds before moving to the next group. When you wake up at night, this can help shift your focus from racing thoughts to physical sensations, promoting relaxation. Would you like me to walk you through the full sequence?"},
            {"is_from_user": True, "content": "That would be helpful, yes."},
            {"is_from_user": False, "content": "Here's the sequence: 1) Curl your toes tightly, then release. 2) Tense your foot, then release. 3) Tense your calf, then release. 4) Tense your thigh, then release. Continue with your buttocks, abdomen, chest, hands, arms, shoulders, neck, and face. When tensing your face, scrunch all your facial features toward your nose, then release. After completing the sequence, notice how your body feels. If your mind wanders to thoughts, gently bring it back to the sensation of relaxation in your body. Practice this daily and use it when you wake up at night."},
            {"is_from_user": True, "content": "I'll try this tonight. It sounds like it could be helpful."},
            {"is_from_user": False, "content": "Excellent! For our next session, please continue with your successful breathing and thought challenging practices for work anxiety, maintain your bedtime routine, and add PMR, especially when you wake during the night. Would you like to set any other specific goals?"},
            {"is_from_user": True, "content": "No, I think that's enough to focus on for now."},
            {"is_from_user": False, "content": "That sounds reasonable. To summarize today's session: You've made significant progress with work anxiety using breathing techniques and thought challenging. For sleep maintenance issues, you'll be adding Progressive Muscle Relaxation. Remember that consistency is key with these practices. I'm really impressed with your progress so far!"}
        ],
        
        # Current session
        [
            {"is_from_user": False, "content": "Hello! How are you doing today?"},
            {"is_from_user": True, "content": "I'm feeling pretty good actually. The PMR technique has been really helpful for my sleep."},
            {"is_from_user": False, "content": "That's fantastic news about the Progressive Muscle Relaxation helping your sleep! Can you tell me more about how it's been working for you?"},
            {"is_from_user": True, "content": "I've been practicing it before bed like you suggested, and I find it really relaxing. When I wake up at night, I start going through the muscle groups and often fall back asleep before I even finish."},
            {"is_from_user": False, "content": "That's excellent! It sounds like you've integrated the technique very effectively. Many people find, as you have, that they don't even need to complete the full sequence to get the benefits. The combination of physical relaxation and mental focus creates a perfect condition for sleep. How has this improved sleep been affecting other areas of your life?"}
        ]
    ]
    
    # Create messages for each conversation
    for i, conversation in enumerate(conversations):
        # Skip if conversation already has messages
        existing_messages = db.query(Message).filter(
            Message.conversation_id == conversation.id
        ).all()
        
        if existing_messages:
            logger.info(f"Conversation {conversation.id} already has {len(existing_messages)} messages")
            continue
        
        # Use conversation flow based on index
        flow_index = min(i, len(conversation_flows) - 1)
        flow = conversation_flows[flow_index]
        
        # Calculate message times
        start_time = conversation.started_at
        
        # If the conversation has ended, distribute messages evenly
        if conversation.ended_at:
            duration = (conversation.ended_at - start_time).total_seconds()
            interval = duration / len(flow)
        else:
            # For ongoing conversations, use shorter intervals
            interval = 180  # 3 minutes between messages
        
        # Create messages
        messages = []
        for j, msg_data in enumerate(flow):
            message_time = start_time + timedelta(seconds=j * interval)
            
            # Ensure message time doesn't exceed ended_at
            if conversation.ended_at and message_time > conversation.ended_at:
                message_time = conversation.ended_at - timedelta(seconds=random.randint(10, 60))
            
            message = Message(
                conversation_id=conversation.id,
                user_id=conversation.user_id if msg_data["is_from_user"] else None,
                content=msg_data["content"],
                is_from_user=msg_data["is_from_user"],
                created_at=message_time,
                is_transcript=False
            )
            messages.append(message)
        
        db.add_all(messages)
        all_messages.extend(messages)
        logger.info(f"Created {len(messages)} messages for conversation {conversation.id}")
    
    db.commit()
    logger.info(f"Created a total of {len(all_messages)} messages")


def create_important_memories(db: Session, user: User, conversations: List[Conversation]) -> None:
    """Create important memories for the test user.
    
    Args:
        db: Database session.
        user: User to create memories for.
        conversations: Conversations to link memories to.
    """
    # Check if memories already exist
    existing_memories = db.query(ImportantMemory).filter(
        ImportantMemory.user_id == user.id
    ).all()
    
    if existing_memories:
        logger.info(f"User already has {len(existing_memories)} important memories")
        return
    
    # Sample memories
    memory_data = [
        {
            "content": "User experiences significant anxiety at work, particularly related to deadlines and criticism.",
            "category": "triggers",
            "importance_score": 0.8,
            "conversation_id": conversations[0].id
        },
        {
            "content": "User has difficulty maintaining sleep, often waking up with racing thoughts about work tasks.",
            "category": "symptoms",
            "importance_score": 0.7,
            "conversation_id": conversations[0].id
        },
        {
            "content": "Breathing exercises (4-2-6 pattern) have been effective for managing acute anxiety at work.",
            "category": "coping_strategies",
            "importance_score": 0.9,
            "conversation_id": conversations[2].id
        },
        {
            "content": "User reported successfully using cognitive restructuring to reframe negative thoughts about project feedback.",
            "category": "progress",
            "importance_score": 0.85,
            "conversation_id": conversations[3].id
        },
        {
            "content": "Progressive Muscle Relaxation has been particularly effective for sleep maintenance issues.",
            "category": "coping_strategies",
            "importance_score": 0.9,
            "conversation_id": conversations[4].id
        }
    ]
    
    # Create memories
    memories = []
    for data in memory_data:
        memory = ImportantMemory(
            user_id=user.id,
            conversation_id=data["conversation_id"],
            content=data["content"],
            category=data["category"],
            importance_score=data["importance_score"],
            created_at=datetime.utcnow() - timedelta(days=random.randint(0, 14))
        )
        memories.append(memory)
    
    db.add_all(memories)
    db.commit()
    logger.info(f"Created {len(memories)} important memories for user {user.id}")


def create_homework_assignments(db: Session, user: User, conversations: List[Conversation]) -> None:
    """Create homework assignments for the test user.
    
    Args:
        db: Database session.
        user: User to create assignments for.
        conversations: Conversations to link assignments to.
    """
    # Check if assignments already exist
    existing_assignments = db.query(HomeworkAssignment).filter(
        HomeworkAssignment.user_id == user.id
    ).all()
    
    if existing_assignments:
        logger.info(f"User already has {len(existing_assignments)} homework assignments")
        return
    
    # Sample assignments
    assignment_data = [
        {
            "title": "Daily Breathing Exercise",
            "description": "Practice the 4-2-6 breathing technique at least twice daily, especially during stressful moments at work.",
            "conversation_id": conversations[0].id,
            "due_date": datetime.utcnow() - timedelta(days=7),
            "status": HomeworkStatus.COMPLETED,
            "completion_date": datetime.utcnow() - timedelta(days=8)
        },
        {
            "title": "Screen-Free Bedtime Routine",
            "description": "Establish a 15-minute routine before sleep without electronic devices. Try reading a physical book instead.",
            "conversation_id": conversations[0].id,
            "due_date": datetime.utcnow() - timedelta(days=7),
            "status": HomeworkStatus.COMPLETED,
            "completion_date": datetime.utcnow() - timedelta(days=6)
        },
        {
            "title": "Thought Challenging Worksheet",
            "description": "Complete the thought challenging worksheet for at least one anxiety-provoking situation at work.",
            "conversation_id": conversations[1].id,
            "due_date": datetime.utcnow() - timedelta(days=3),
            "status": HomeworkStatus.COMPLETED,
            "completion_date": datetime.utcnow() - timedelta(days=4)
        },
        {
            "title": "Progressive Muscle Relaxation",
            "description": "Practice PMR daily before bed and when waking during the night.",
            "conversation_id": conversations[3].id,
            "due_date": datetime.utcnow() + timedelta(days=3),
            "status": HomeworkStatus.IN_PROGRESS,
            "completion_date": None
        },
        {
            "title": "Mindfulness Journal",
            "description": "Spend 5 minutes each day writing down moments of mindfulness and how they affected your mood and anxiety levels.",
            "conversation_id": conversations[3].id,
            "due_date": datetime.utcnow() + timedelta(days=5),
            "status": HomeworkStatus.ASSIGNED,
            "completion_date": None
        }
    ]
    
    # Create assignments
    assignments = []
    for data in assignment_data:
        assignment = HomeworkAssignment(
            user_id=user.id,
            conversation_id=data["conversation_id"],
            title=data["title"],
            description=data["description"],
            due_date=data["due_date"],
            status=data["status"],
            completion_date=data["completion_date"],
            created_at=data["conversation_id"].started_at + timedelta(minutes=45)
        )
        assignments.append(assignment)
    
    db.add_all(assignments)
    db.commit()
    logger.info(f"Created {len(assignments)} homework assignments for user {user.id}")


def main() -> None:
    """Create test data for the application."""
    logger.info("Creating test data for Mental Health Coach application")
    
    # Create database session
    db = SessionLocal()
    try:
        # Create test user
        user = create_test_user(db)
        
        # Create user profile
        profile = create_user_profile(db, user)
        
        # Create session schedules
        create_session_schedule(db, user)
        
        # Create conversations
        conversations = create_conversations(db, user)
        
        # Create messages
        create_messages(db, conversations)
        
        # Create important memories
        create_important_memories(db, user, conversations)
        
        # Create homework assignments
        create_homework_assignments(db, user, conversations)
        
        logger.info("Test data creation completed successfully")
        
    except Exception as e:
        logger.error(f"Error creating test data: {str(e)}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main() 