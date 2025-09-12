import os
import uuid
from typing import List, Dict, Any
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from config import Config

class ChatbotService:
    """Service class for handling chatbot conversations with memory"""

    def __init__(self):
        """Initialize the chatbot service with Gemini and memory"""
        # Validate configuration
        Config.validate_config()

        # Initialize the Gemini model
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=Config.GEMINI_API_KEY,
            temperature=Config.CHAT_MODEL_TEMPERATURE,
            max_output_tokens=1024
        )

        # Store conversation history for each session using modern approach
        self.chats_by_session_id = {}

        # Create the prompt template
        self.prompt = self._create_prompt_template()

    def _create_prompt_template(self) -> ChatPromptTemplate:
        """Create the prompt template for casual conversation"""

        # Define the system prompt for casual conversation
        system_prompt = """You are a friendly, engaging chatbot that loves to have random casual conversations.
        Your personality traits:
        - You're curious and ask interesting questions
        - You share fun facts and stories
        - You're empathetic and supportive
        - You have a good sense of humor
        - You're knowledgeable about many topics
        - You remember previous parts of the conversation
        - You're enthusiastic and positive

        Guidelines for responses:
        - Keep responses conversational and natural (2-4 sentences typically)
        - Ask follow-up questions to keep the conversation flowing
        - Share relevant personal anecdotes or fun facts when appropriate
        - Be encouraging and supportive
        - Use emojis occasionally but not excessively
        - If the user seems down, try to cheer them up
        - If they're excited about something, match their enthusiasm
        - Remember what you've talked about before in this conversation

        Always respond as if you're talking to a friend you're excited to chat with!"""

        # Create the prompt template
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{input}")
        ])

        return prompt

    def get_chat_history(self, session_id: str) -> InMemoryChatMessageHistory:
        """Get or create chat history for a session"""
        chat_history = self.chats_by_session_id.get(session_id)
        if chat_history is None:
            chat_history = InMemoryChatMessageHistory()
            self.chats_by_session_id[session_id] = chat_history
        return chat_history

    def get_response(self, user_input: str, session_id: str = "default") -> Dict[str, Any]:
        """
        Get a response from the chatbot

        Args:
            user_input: The user's message
            session_id: Unique identifier for the conversation session

        Returns:
            Dictionary containing the response and metadata
        """
        try:
            # Get chat history for this session
            chat_history = self.get_chat_history(session_id)

            # Get the conversation history (limit to recent messages)
            history_messages = list(chat_history.messages)
            if len(history_messages) > Config.MAX_CONVERSATION_HISTORY * 2:  # *2 because we store both user and AI messages
                # Keep only the most recent messages
                history_messages = history_messages[-(Config.MAX_CONVERSATION_HISTORY * 2):]

            # Create the prompt with history
            prompt_input = {
                "input": user_input,
                "history": history_messages
            }

            # Format the prompt
            formatted_prompt = self.prompt.format(**prompt_input)

            # Get response from the model
            response = self.llm.invoke(formatted_prompt)

            # Extract the content from the response
            if hasattr(response, 'content'):
                response_content = response.content
            else:
                response_content = str(response)

            # Add messages to chat history
            chat_history.add_user_message(user_input)
            chat_history.add_ai_message(response_content)

            return {
                "response": response_content,
                "session_id": session_id,
                "status": "success",
                "model": "gemini-1.5-flash"
            }

        except Exception as e:
            return {
                "response": f"I'm sorry, I encountered an error: {str(e)}. Could you try again?",
                "session_id": session_id,
                "status": "error",
                "error": str(e)
            }

    def get_conversation_history(self, session_id: str = "default") -> List[Dict[str, str]]:
        """
        Get the conversation history for a session

        Args:
            session_id: Unique identifier for the conversation session

        Returns:
            List of conversation messages
        """
        chat_history = self.get_chat_history(session_id)
        messages = chat_history.messages

        history = []
        for message in messages:
            if isinstance(message, HumanMessage):
                history.append({"role": "user", "content": message.content})
            elif isinstance(message, AIMessage):
                history.append({"role": "assistant", "content": message.content})

        return history

    def clear_conversation(self, session_id: str = "default") -> bool:
        """
        Clear conversation history for a session

        Args:
            session_id: Unique identifier for the conversation session

        Returns:
            True if successful
        """
        try:
            if session_id in self.chats_by_session_id:
                self.chats_by_session_id[session_id].clear()
            return True
        except Exception as e:
            print(f"Error clearing conversation: {e}")
            return False

    def get_random_conversation_starter(self) -> str:
        """Get a random conversation starter"""
        starters = [
            "Hey there! What's the most interesting thing that happened to you today? 😊",
            "Hi! I'm in the mood for some good conversation. What's on your mind?",
            "Hello! I was just thinking about random things. What's your favorite way to spend a lazy Sunday?",
            "Hey! I love meeting new people through chat. What's something you're passionate about?",
            "Hi there! I'm curious - if you could have dinner with anyone (living or dead), who would it be?",
            "Hello! I'm feeling chatty today. What's the last thing that made you laugh really hard?",
            "Hey! I was just wondering - what's the most random skill you wish you had?",
            "Hi there! I love learning about people. What's something unique about you that most people don't know?",
            "Hello! I'm in a great mood today. What's something that always makes you smile?",
            "Hey! I'm curious about your thoughts. What's the most underrated thing in life, in your opinion?"
        ]

        import random
        return random.choice(starters)

# Global chatbot service instance
chatbot_service = ChatbotService()
