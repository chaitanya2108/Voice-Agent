"""
Restaurant Data and Context Management
Contains all restaurant information, menu, and context protocols
"""

from datetime import datetime, time
from typing import Dict, List, Optional, Any
import json

class RestaurantContext:
    """Manages restaurant context and conversation state"""

    def __init__(self):
        self.restaurant_info = {
            "name": "Bella Vista Ristorante",
            "tagline": "Authentic Italian Cuisine Since 1985",
            "address": "123 Main Street, Downtown",
            "phone": "(555) 123-4567",
            "email": "info@bellavista.com",
            "website": "www.bellavista.com",
            "hours": {
                "monday": "11:00 AM - 10:00 PM",
                "tuesday": "11:00 AM - 10:00 PM",
                "wednesday": "11:00 AM - 10:00 PM",
                "thursday": "11:00 AM - 10:00 PM",
                "friday": "11:00 AM - 11:00 PM",
                "saturday": "10:00 AM - 11:00 PM",
                "sunday": "10:00 AM - 9:00 PM"
            },
            "specialties": [
                "Wood-fired pizzas",
                "Fresh handmade pasta",
                "Authentic Italian desserts",
                "Extensive wine selection"
            ],
            "policies": {
                "reservations": "Recommended for parties of 4 or more",
                "dress_code": "Smart casual",
                "parking": "Valet parking available",
                "delivery": "Available within 5 miles",
                "takeout": "Available for all menu items"
            }
        }

        self.menu = {
            "appetizers": [
                {"name": "Bruschetta Classica", "price": 12.99, "description": "Toasted bread with fresh tomatoes, basil, and garlic", "allergens": ["gluten"]},
                {"name": "Antipasto Misto", "price": 18.99, "description": "Selection of cured meats, cheeses, and olives", "allergens": ["dairy"]},
                {"name": "Calamari Fritti", "price": 15.99, "description": "Crispy fried squid with marinara sauce", "allergens": ["seafood", "gluten"]},
                {"name": "Caprese Salad", "price": 14.99, "description": "Fresh mozzarella, tomatoes, and basil drizzled with balsamic", "allergens": ["dairy"]}
            ],
            "pasta": [
                {"name": "Spaghetti Carbonara", "price": 19.99, "description": "Classic Roman pasta with eggs, pancetta, and pecorino cheese", "allergens": ["gluten", "dairy", "eggs"]},
                {"name": "Fettuccine Alfredo", "price": 18.99, "description": "Creamy fettuccine with parmesan and butter", "allergens": ["gluten", "dairy"]},
                {"name": "Penne Arrabbiata", "price": 17.99, "description": "Spicy penne in tomato sauce with garlic and red peppers", "allergens": ["gluten"]},
                {"name": "Ravioli di Ricotta", "price": 21.99, "description": "Homemade ravioli filled with ricotta and spinach", "allergens": ["gluten", "dairy", "eggs"]}
            ],
            "pizza": [
                {"name": "Margherita", "price": 16.99, "description": "Classic pizza with tomato, mozzarella, and fresh basil", "allergens": ["gluten", "dairy"]},
                {"name": "Quattro Stagioni", "price": 22.99, "description": "Four seasons pizza with artichokes, mushrooms, prosciutto, and olives", "allergens": ["gluten", "dairy"]},
                {"name": "Diavola", "price": 20.99, "description": "Spicy pizza with tomato, mozzarella, and spicy salami", "allergens": ["gluten", "dairy"]},
                {"name": "Vegetariana", "price": 19.99, "description": "Vegetable pizza with bell peppers, mushrooms, and zucchini", "allergens": ["gluten", "dairy"]}
            ],
            "mains": [
                {"name": "Osso Buco", "price": 32.99, "description": "Braised veal shanks with risotto milanese", "allergens": ["gluten", "dairy"]},
                {"name": "Chicken Parmigiana", "price": 24.99, "description": "Breaded chicken breast with marinara and mozzarella", "allergens": ["gluten", "dairy", "eggs"]},
                {"name": "Salmon al Limone", "price": 28.99, "description": "Pan-seared salmon with lemon butter sauce", "allergens": ["seafood", "dairy"]},
                {"name": "Eggplant Parmigiana", "price": 22.99, "description": "Breaded eggplant with marinara and mozzarella", "allergens": ["gluten", "dairy", "eggs"]}
            ],
            "desserts": [
                {"name": "Tiramisu", "price": 8.99, "description": "Classic Italian dessert with coffee and mascarpone", "allergens": ["dairy", "eggs", "gluten"]},
                {"name": "Cannoli", "price": 7.99, "description": "Crispy shells filled with sweet ricotta", "allergens": ["dairy", "gluten"]},
                {"name": "Gelato", "price": 6.99, "description": "Three scoops of house-made gelato", "allergens": ["dairy"]},
                {"name": "Panna Cotta", "price": 7.99, "description": "Vanilla custard with berry compote", "allergens": ["dairy"]}
            ],
            "beverages": [
                {"name": "House Wine (Glass)", "price": 8.99, "description": "Red or white wine selection", "allergens": []},
                {"name": "Italian Soda", "price": 4.99, "description": "Choice of flavors: lemon, orange, or cherry", "allergens": []},
                {"name": "Espresso", "price": 3.99, "description": "Traditional Italian coffee", "allergens": []},
                {"name": "Cappuccino", "price": 4.99, "description": "Espresso with steamed milk foam", "allergens": ["dairy"]}
            ]
        }

        self.current_order = []
        self.customer_info = {}
        self.conversation_context = {
            "stage": "greeting",  # greeting, taking_order, confirming_order, payment, completed
            "last_mentioned_items": [],
            "dietary_restrictions": [],
            "party_size": None,
            "preferred_dining_time": None
        }

    def get_restaurant_info(self) -> str:
        """Get formatted restaurant information"""
        info = f"""
Welcome to {self.restaurant_info['name']}!
{self.restaurant_info['tagline']}

📍 {self.restaurant_info['address']}
📞 {self.restaurant_info['phone']}
🌐 {self.restaurant_info['website']}

Hours:
{self._format_hours()}

Our Specialties:
{', '.join(self.restaurant_info['specialties'])}

Policies:
• {self.restaurant_info['policies']['reservations']}
• {self.restaurant_info['policies']['dress_code']}
• {self.restaurant_info['policies']['parking']}
• {self.restaurant_info['policies']['delivery']}
• {self.restaurant_info['policies']['takeout']}
        """
        return info.strip()

    def _format_hours(self) -> str:
        """Format restaurant hours"""
        hours_text = ""
        for day, hours in self.restaurant_info['hours'].items():
            hours_text += f"• {day.capitalize()}: {hours}\n"
        return hours_text.strip()

    def get_menu_category(self, category: str) -> str:
        """Get formatted menu for a specific category"""
        if category not in self.menu:
            return f"Sorry, we don't have a '{category}' category. Our categories are: {', '.join(self.menu.keys())}"

        items = self.menu[category]
        menu_text = f"\n{category.upper()}:\n"

        NO_ALLERGENS_TEXT = " (No allergens)"
        for item in items:
            allergens = f" (Contains: {', '.join(item['allergens'])})" if item['allergens'] else NO_ALLERGENS_TEXT
            menu_text += f"• {item['name']} - ${item['price']:.2f}\n  {item['description']}{allergens}\n\n"

        return menu_text.strip()

    def get_full_menu(self) -> str:
        """Get complete menu"""
        menu_text = "Our Complete Menu:\n"
        NO_ALLERGENS_TEXT = " (No allergens)"
        for category, items in self.menu.items():
            menu_text += f"\n{category.upper()}:\n"
            for item in items:
                allergens = f" (Contains: {', '.join(item['allergens'])})" if item['allergens'] else NO_ALLERGENS_TEXT
                menu_text += f"• {item['name']} - ${item['price']:.2f}\n  {item['description']}{allergens}\n"
        return menu_text

    def search_menu(self, query: str) -> str:
        """Search menu items by name or description"""
        query_lower = query.lower()
        results = []

        for category, items in self.menu.items():
            for item in items:
                if (query_lower in item['name'].lower() or
                    query_lower in item['description'].lower()):
                    results.append((category, item))

        if not results:
            return f"Sorry, I couldn't find any items matching '{query}'. Would you like to see our full menu?"

        result_text = f"Here are items matching '{query}':\n"
        NO_ALLERGENS_TEXT = " (No allergens)"
        for category, item in results:
            allergens = f" (Contains: {', '.join(item['allergens'])})" if item['allergens'] else NO_ALLERGENS_TEXT
            result_text += f"• {item['name']} - ${item['price']:.2f} ({category})\n  {item['description']}{allergens}\n\n"

        return result_text.strip()

    def add_to_order(self, item_name: str, quantity: int = 1, special_requests: str = "") -> str:
        """Add item to current order"""
        # Find the item in the menu
        item = None
        category = None
        for cat, items in self.menu.items():
            for menu_item in items:
                if item_name.lower() in menu_item['name'].lower():
                    item = menu_item
                    category = cat
                    break
            if item:
                break

        if not item:
            return f"Sorry, I couldn't find '{item_name}' on our menu. Would you like to see our menu or try a different item?"

        # Add to order
        order_item = {
            "name": item['name'],
            "price": item['price'],
            "quantity": quantity,
            "special_requests": special_requests,
            "category": category
        }

        self.current_order.append(order_item)
        self.conversation_context['stage'] = 'taking_order'

        return f"Added {quantity}x {item['name']} to your order. Anything else I can help you with?"

    def get_current_order(self) -> str:
        """Get formatted current order"""
        if not self.current_order:
            return "Your order is currently empty. Would you like to see our menu?"

        order_text = "Your Current Order:\n"
        total = 0

        for i, item in enumerate(self.current_order, 1):
            item_total = item['price'] * item['quantity']
            total += item_total
            order_text += f"{i}. {item['name']} x{item['quantity']} - ${item_total:.2f}\n"
            if item['special_requests']:
                order_text += f"   Special requests: {item['special_requests']}\n"

        # Add tax (8.5%)
        tax = total * 0.085
        final_total = total + tax

        order_text += f"\nSubtotal: ${total:.2f}\n"
        order_text += f"Tax (8.5%): ${tax:.2f}\n"
        order_text += f"Total: ${final_total:.2f}"

        return order_text

    def clear_order(self):
        """Clear current order"""
        self.current_order = []
        self.conversation_context['stage'] = 'greeting'

    def set_customer_info(self, name: str = "", phone: str = "", email: str = ""):
        """Set customer information"""
        if name:
            self.customer_info['name'] = name
        if phone:
            self.customer_info['phone'] = phone
        if email:
            self.customer_info['email'] = email

    def get_context_summary(self) -> str:
        """Get current conversation context summary"""
        context = f"Conversation Stage: {self.conversation_context['stage']}\n"
        context += f"Order Items: {len(self.current_order)}\n"
        if self.customer_info:
            context += f"Customer: {self.customer_info.get('name', 'Not provided')}\n"
        return context

# Global restaurant context instance
restaurant_context = RestaurantContext()
