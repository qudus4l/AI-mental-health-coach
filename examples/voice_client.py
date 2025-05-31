#!/usr/bin/env python
"""Example client for the voice conversation API.

This script demonstrates how to use the voice conversation API
to interact with the AI mental health coach using voice.
"""

import os
import sys
import json
import asyncio
import logging
import argparse
import websockets
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class VoiceClient:
    """Client for interacting with the voice conversation API.
    
    This class provides methods to interact with the AI mental health coach
    using voice through the WebSocket API.
    
    Attributes:
        base_url: Base URL for the API.
        auth_token: Authentication token.
        user_id: User ID.
        conversation_id: ID of the current conversation.
        websocket: WebSocket connection.
    """
    
    def __init__(self, base_url: str, auth_token: str, user_id: int) -> None:
        """Initialize the voice client.
        
        Args:
            base_url: Base URL for the API.
            auth_token: Authentication token.
            user_id: User ID.
        """
        self.base_url = base_url
        self.auth_token = auth_token
        self.user_id = user_id
        self.conversation_id: Optional[int] = None
        self.websocket = None
    
    async def start_conversation(self, is_formal_session: bool = False, title: Optional[str] = None) -> int:
        """Start a new conversation.
        
        Args:
            is_formal_session: Whether this is a formal therapy session.
            title: Optional title for the conversation.
            
        Returns:
            int: ID of the created conversation.
        """
        import aiohttp
        
        url = f"{self.base_url}/api/voice/conversations"
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        data = {
            "is_formal_session": is_formal_session,
            "title": title or "Voice conversation",
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data, headers=headers) as response:
                if response.status != 201:
                    raise Exception(f"Failed to start conversation: {await response.text()}")
                
                result = await response.json()
                self.conversation_id = result["id"]
                logger.info(f"Started conversation with ID: {self.conversation_id}")
                return self.conversation_id
    
    async def end_conversation(self) -> None:
        """End the current conversation."""
        if not self.conversation_id:
            logger.warning("No active conversation to end")
            return
        
        import aiohttp
        
        url = f"{self.base_url}/api/voice/conversations/{self.conversation_id}/end"
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers) as response:
                if response.status != 200:
                    raise Exception(f"Failed to end conversation: {await response.text()}")
                
                logger.info(f"Ended conversation with ID: {self.conversation_id}")
                self.conversation_id = None
    
    async def connect_websocket(self) -> None:
        """Connect to the WebSocket for real-time communication."""
        url = f"{self.base_url.replace('http', 'ws')}/api/voice/ws/{self.user_id}"
        self.websocket = await websockets.connect(url)
        logger.info("Connected to WebSocket")
    
    async def start_listening(self) -> None:
        """Start listening for voice input."""
        if not self.websocket:
            raise Exception("WebSocket not connected")
        
        await self.websocket.send(json.dumps({"command": "start_listening"}))
        logger.info("Started listening")
    
    async def stop_listening(self) -> None:
        """Stop listening for voice input."""
        if not self.websocket:
            raise Exception("WebSocket not connected")
        
        await self.websocket.send(json.dumps({"command": "stop_listening"}))
        logger.info("Stopped listening")
    
    async def send_text_message(self, message: str) -> None:
        """Send a text message.
        
        Args:
            message: The message to send.
        """
        if not self.websocket:
            raise Exception("WebSocket not connected")
        
        await self.websocket.send(json.dumps({"command": "send_text", "message": message}))
        logger.info(f"Sent message: {message}")
    
    async def stop_speaking(self) -> None:
        """Stop the AI coach from speaking."""
        if not self.websocket:
            raise Exception("WebSocket not connected")
        
        await self.websocket.send(json.dumps({"command": "stop_speaking"}))
        logger.info("Stopped speaking")
    
    async def receive_messages(self) -> None:
        """Receive and handle messages from the WebSocket."""
        if not self.websocket:
            raise Exception("WebSocket not connected")
        
        try:
            while True:
                message = await self.websocket.recv()
                data = json.loads(message)
                
                if "error" in data:
                    logger.error(f"Error from server: {data['error']}")
                    continue
                
                message_type = data.get("type")
                
                if message_type == "transcription":
                    logger.info(f"Transcription: {data['message']}")
                
                elif message_type == "response":
                    logger.info(f"AI Response: {data['message']}")
                
                elif message_type == "status":
                    logger.info(f"Status: {data['status']}")
                
                else:
                    logger.info(f"Unknown message: {message}")
        
        except websockets.exceptions.ConnectionClosed:
            logger.info("WebSocket connection closed")
    
    async def disconnect(self) -> None:
        """Disconnect from the WebSocket."""
        if self.websocket:
            await self.websocket.close()
            logger.info("Disconnected from WebSocket")
            self.websocket = None


async def interactive_session(client: VoiceClient) -> None:
    """Run an interactive session with the AI coach.
    
    Args:
        client: Voice client instance.
    """
    try:
        # Start a conversation
        await client.start_conversation(title="Interactive voice session")
        
        # Connect to the WebSocket
        await client.connect_websocket()
        
        # Start a task to receive messages
        receive_task = asyncio.create_task(client.receive_messages())
        
        print("\nInteractive session with AI Mental Health Coach")
        print("----------------------------------------------")
        print("Commands:")
        print("  listen        - Start listening for voice input")
        print("  stop          - Stop listening")
        print("  text [message] - Send a text message")
        print("  quiet         - Stop the AI coach from speaking")
        print("  exit          - End the session")
        print("----------------------------------------------\n")
        
        while True:
            command = await asyncio.get_event_loop().run_in_executor(None, input, "> ")
            
            if command == "listen":
                await client.start_listening()
            
            elif command == "stop":
                await client.stop_listening()
            
            elif command.startswith("text "):
                message = command[5:]
                await client.send_text_message(message)
            
            elif command == "quiet":
                await client.stop_speaking()
            
            elif command == "exit":
                break
            
            else:
                print("Unknown command")
        
        # Cancel the receive task
        receive_task.cancel()
        try:
            await receive_task
        except asyncio.CancelledError:
            pass
        
        # End the conversation and disconnect
        await client.end_conversation()
        await client.disconnect()
    
    except Exception as e:
        logger.error(f"Error in interactive session: {e}", exc_info=True)
        # Ensure we clean up
        await client.end_conversation()
        await client.disconnect()


def main() -> None:
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description="Voice client for the AI mental health coach")
    parser.add_argument("--url", default="http://localhost:8000", help="Base URL for the API")
    parser.add_argument("--token", required=True, help="Authentication token")
    parser.add_argument("--user-id", required=True, type=int, help="User ID")
    
    args = parser.parse_args()
    
    # Create a voice client
    client = VoiceClient(args.url, args.token, args.user_id)
    
    # Run an interactive session
    asyncio.run(interactive_session(client))


if __name__ == "__main__":
    main() 