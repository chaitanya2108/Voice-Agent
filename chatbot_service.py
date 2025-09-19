import os
import uuid
from typing import List, Dict, Any
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from config import Config
from restaurant_data import restaurant_context
from clover_service import clover_service

class ChatbotService:
    """Service class for handling chatbot conversations with memory"""

    def __init__(self):
        """Initialize the chatbot service with Gemini and memory"""
        # Validate configuration
        Config.validate_config()

        # Initialize the Gemini model
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            api_key=Config.GEMINI_API_KEY,
            temperature=Config.CHAT_MODEL_TEMPERATURE
        )

        # Store conversation history for each session using modern approach
        self.chats_by_session_id = {}

        # Initialize restaurant context
        self.restaurant_context = restaurant_context

        # Initialize Clover service
        self.clover_service = clover_service

        # Create the prompt template
        self.prompt = self._create_prompt_template()

    def _create_prompt_template(self) -> ChatPromptTemplate:
        """Create the prompt template for restaurant assistant conversation"""

        # Define the system prompt for restaurant assistant
        system_prompt = """You are a helpful and friendly restaurant assistant for Bella Vista Ristorante, an authentic Italian restaurant. Your role is to:

1. Greet customers warmly and help them with their dining needs
2. Provide information about the restaurant, menu, hours, and policies
3. Take food orders and answer questions about menu items
4. Handle special dietary requirements and allergen information
5. Provide recommendations based on customer preferences
6. Process orders and confirm details
7. Be knowledgeable about Italian cuisine and wine pairings

Key guidelines:
- Always be polite, professional, and enthusiastic about our food
- Use the restaurant context to provide accurate information
- Ask clarifying questions when needed (party size, dietary restrictions, etc.)
- Offer suggestions and upsell when appropriate
- Confirm order details before finalizing
- Remember customer preferences and previous interactions
- If you don't know something, say so and offer to find out

Current conversation context: {context}
Current order status: {order_status}
Clover POS status: {clover_status}

Remember: You're representing Bella Vista Ristorante, so maintain our reputation for excellent service and authentic Italian hospitality."""

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
        Get a response from the restaurant assistant chatbot

        Args:
            user_input: The user's message
            session_id: Unique identifier for the conversation session

        Returns:
            Dictionary containing the response and metadata
        """
        try:
            # Process restaurant-specific commands first
            processed_input, context_update = self._process_restaurant_commands(user_input)

            # Get chat history for this session
            chat_history = self.get_chat_history(session_id)

            # Get the conversation history (limit to recent messages)
            history_messages = list(chat_history.messages)
            if len(history_messages) > Config.MAX_CONVERSATION_HISTORY * 2:  # *2 because we store both user and AI messages
                # Keep only the most recent messages
                history_messages = history_messages[-(Config.MAX_CONVERSATION_HISTORY * 2):]

            # Get current context and order status
            context_summary = self.restaurant_context.get_context_summary()
            order_status = self.restaurant_context.get_current_order()
            clover_status = "Connected" if self.clover_service.is_authenticated() else "Not connected"

            # Create the prompt with history and context
            prompt_input = {
                "input": processed_input,
                "history": history_messages,
                "context": context_summary,
                "order_status": order_status,
                "clover_status": clover_status
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
            chat_history.add_ai_message(str(response_content))

            return {
                "response": response_content,
                "session_id": session_id,
                "status": "success",
                "model": "gemini-1.5-flash",
                "context_update": context_update
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

    def _process_restaurant_commands(self, user_input: str) -> tuple:
        """Process restaurant-specific commands and return processed input and context update"""
        input_lower = user_input.lower().strip()
        context_update = None

        # Handle menu requests
        if any(keyword in input_lower for keyword in ['menu', 'food', 'dishes', 'what do you have']):
            if 'appetizer' in input_lower or 'starter' in input_lower:
                context_update = self.restaurant_context.get_menu_category('appetizers')
            elif 'pasta' in input_lower:
                context_update = self.restaurant_context.get_menu_category('pasta')
            elif 'pizza' in input_lower:
                context_update = self.restaurant_context.get_menu_category('pizza')
            elif 'main' in input_lower or 'entree' in input_lower:
                context_update = self.restaurant_context.get_menu_category('mains')
            elif 'dessert' in input_lower or 'sweet' in input_lower:
                context_update = self.restaurant_context.get_menu_category('desserts')
            elif 'drink' in input_lower or 'beverage' in input_lower or 'wine' in input_lower:
                context_update = self.restaurant_context.get_menu_category('beverages')
            else:
                context_update = self.restaurant_context.get_full_menu()

        # Handle restaurant info requests
        elif any(keyword in input_lower for keyword in ['hours', 'open', 'close', 'location', 'address', 'phone', 'contact']):
            context_update = self.restaurant_context.get_restaurant_info()

        # Handle order requests
        elif any(keyword in input_lower for keyword in ['order', 'add', 'get', 'want', 'like to have']):
            # Extract item name and quantity from input
            # This is a simplified version - in production, you'd use NLP
            words = input_lower.split()
            quantity = 1
            item_name = ""

            # Look for quantity indicators
            for i, word in enumerate(words):
                if word.isdigit():
                    quantity = int(word)
                    item_name = " ".join(words[i+1:])
                    break
                elif word in ['a', 'an', 'one']:
                    quantity = 1
                    item_name = " ".join(words[i+1:])
                    break

            if not item_name:
                item_name = user_input

            context_update = self.restaurant_context.add_to_order(item_name, quantity)

        # Handle order status requests
        elif any(keyword in input_lower for keyword in ['my order', 'current order', 'what did i order', 'order status']):
            context_update = self.restaurant_context.get_current_order()

        # Handle search requests
        elif any(keyword in input_lower for keyword in ['search', 'find', 'looking for']):
            # Extract search term
            search_terms = []
            for keyword in ['search for', 'find', 'looking for']:
                if keyword in input_lower:
                    search_terms = input_lower.split(keyword)[1].strip().split()
                    break

            if search_terms:
                search_query = " ".join(search_terms)
                context_update = self.restaurant_context.search_menu(search_query)

        # Handle payment requests
        elif any(keyword in input_lower for keyword in ['pay', 'payment', 'checkout', 'pay for', 'process payment']):
            context_update = "I can help you process your payment through our Clover POS system. Let me check if we're connected to the payment processor."
            # This will trigger payment processing in the main response logic

        # Handle order completion requests
        elif any(keyword in input_lower for keyword in ['complete order', 'finish order', 'finalize order', 'place order']):
            if self.restaurant_context.current_order:
                context_update = "I'll help you complete your order. Let me process this through our POS system."
            else:
                context_update = "Your order is empty. Would you like to add some items first?"

        return user_input, context_update

    def get_random_conversation_starter(self) -> str:
        """Get a random restaurant conversation starter"""
        starters = [
            "Welcome to Bella Vista Ristorante! How can I help you today?",
            "Hello! I'm here to help you with your dining experience. What would you like to know?",
            "Good day! Ready to explore our authentic Italian menu?",
            "Welcome! Are you looking to place an order or learn about our restaurant?",
            "Hi there! I can help you with our menu, take your order, or answer any questions about Bella Vista!",
            "Buongiorno! Welcome to our Italian kitchen. What brings you here today?",
            "Hello! I'm excited to help you discover our delicious Italian cuisine. Where shall we start?",
            "Welcome! Our wood-fired pizzas and handmade pasta are calling your name. What sounds good?",
            "Hi there! I can tell you about our specialties, help you order, or answer any questions about our restaurant.",
            "Good to see you! Our authentic Italian dishes are prepared fresh daily. What can I help you with?"
        ]

        import random
        return random.choice(starters)

    def _process_payment_request(self) -> Dict[str, Any]:
        """Process payment request and return payment information"""
        if not self.restaurant_context.current_order:
            return {
                'can_pay': False,
                'message': 'Your order is empty. Please add some items first.'
            }

        # Calculate total
        total = sum(item['price'] * item['quantity'] for item in self.restaurant_context.current_order)
        tax = total * 0.085  # 8.5% tax
        final_total = total + tax

        return {
            'can_pay': True,
            'subtotal': total,
            'tax': tax,
            'total': final_total,
            'items': len(self.restaurant_context.current_order),
            'message': f'Ready to process payment for ${final_total:.2f}'
        }

    def _process_order_completion(self) -> Dict[str, Any]:
        """Process order completion request"""
        if not self.restaurant_context.current_order:
            return {
                'can_complete': False,
                'message': 'Your order is empty. Please add some items first.'
            }

        # Calculate total
        total = sum(item['price'] * item['quantity'] for item in self.restaurant_context.current_order)
        tax = total * 0.085  # 8.5% tax
        final_total = total + tax

        return {
            'can_complete': True,
            'subtotal': total,
            'tax': tax,
            'total': final_total,
            'items': len(self.restaurant_context.current_order),
            'order_data': self.restaurant_context.current_order,
            'message': f'Order ready for completion. Total: ${final_total:.2f}'
        }

# Global chatbot service instance
chatbot_service = ChatbotService()
