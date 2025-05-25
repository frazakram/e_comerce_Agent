import pandas as pd
import numpy as np
import sqlite3
import uuid
import random
from datetime import datetime, timedelta
import os
from tqdm import tqdm
from database import EcommerceDatabase

class EcommerceDataGenerator:
    def __init__(self, num_users=500, num_sessions=1000, num_products=100, start_date='2024-01-01', end_date='2025-05-25'):
        self.num_users = num_users
        self.num_sessions = num_sessions
        self.num_products = num_products
        self.start_date = datetime.fromisoformat(start_date)
        self.end_date = datetime.fromisoformat(end_date)
        
        self.db = EcommerceDatabase()
        
        # Initialize data containers
        self.users = []
        self.sessions = []
        self.page_views = []
        self.clicks = []
        self.products = []
        self.product_views = []
        self.cart_events = []
        self.search_events = []
        self.checkout_events = []
        
        # Define common attributes
        self.device_types = ['desktop', 'mobile', 'tablet']
        self.device_weights = [0.5, 0.4, 0.1]  # probability weights
        
        self.browsers = ['Chrome', 'Safari', 'Firefox', 'Edge']
        self.browser_weights = [0.6, 0.25, 0.1, 0.05]  # probability weights
        
        self.countries = ['US', 'UK', 'Canada', 'Australia', 'Germany', 'France', 'India', 'Brazil']
        self.country_weights = [0.3, 0.15, 0.1, 0.1, 0.1, 0.1, 0.1, 0.05]  # probability weights
        
        self.referrers = ['direct', 'google', 'facebook', 'instagram', 'email', 'bing', 'twitter', 'affiliate']
        self.referrer_weights = [0.25, 0.3, 0.15, 0.1, 0.1, 0.05, 0.03, 0.02]  # probability weights
        
        self.page_types = ['homepage', 'product_listing', 'product_detail', 'cart', 'checkout', 'search_results', 'account', 'help']
        
        self.product_categories = ['electronics', 'clothing', 'home', 'beauty', 'sports', 'toys', 'books', 'food']
        
        self.element_types = ['button', 'link', 'image', 'menu', 'form', 'product_card']
        
        # Conversion probability parameters
        self.base_conversion_rate = 0.08  # 8% base conversion rate
        
        # Checkout steps
        self.checkout_steps = ['checkout_start', 'shipping_info', 'payment_info', 'review_order', 'submit_order']
        
        # Common search queries
        self.common_search_queries = [
            'shirt', 'dress', 'shoes', 'laptop', 'phone', 'tv', 'sofa', 'camera', 'watch', 'headphones',
            'jeans', 'sneakers', 'jacket', 'sweater', 'socks', 'hat', 'gloves', 'scarf', 'sunglasses',
            'tablet', 'monitor', 'keyboard', 'mouse', 'printer', 'speaker', 'coffee maker', 'blender',
            'makeup', 'skincare', 'perfume', 'shampoo', 'soap', 'toothpaste', 'deodorant',
            'basketball', 'football', 'tennis', 'yoga mat', 'weights', 'running shoes', 'bicycle',
            'action figure', 'board game', 'puzzle', 'doll', 'lego', 'card game', 'video game',
            'novel', 'cookbook', 'biography', 'self-help', 'history book', 'children\'s book',
            'chocolate', 'coffee', 'tea', 'snacks', 'pasta', 'rice', 'cereal', 'chips'
        ]
    
    def generate_users(self):
        """Generate user data."""
        print("Generating users...")
        for _ in range(self.num_users):
            user_id = str(uuid.uuid4())
            first_visit_date = self.random_date()
            device_type = random.choices(self.device_types, weights=self.device_weights)[0]
            browser = random.choices(self.browsers, weights=self.browser_weights)[0]
            country = random.choices(self.countries, weights=self.country_weights)[0]
            referrer = random.choices(self.referrers, weights=self.referrer_weights)[0]
            
            self.users.append({
                'user_id': user_id,
                'first_visit_date': first_visit_date.isoformat(),
                'device_type': device_type,
                'browser': browser,
                'country': country,
                'referrer': referrer
            })
        
        # Convert to DataFrame and insert into database
        users_df = pd.DataFrame(self.users)
        self.db.insert_data('users', users_df)
        print(f"Generated {len(self.users)} users")
    
    def generate_products(self):
        """Generate product data."""
        print("Generating products...")
        product_adjectives = ['Premium', 'Deluxe', 'Basic', 'Advanced', 'Professional', 'Compact', 'Ultra', 'Mini', 'Maxi', 'Essential']
        product_nouns = {
            'electronics': ['Smartphone', 'Laptop', 'Tablet', 'TV', 'Headphones', 'Speaker', 'Camera', 'Smartwatch', 'Monitor', 'Keyboard'],
            'clothing': ['T-shirt', 'Jeans', 'Dress', 'Jacket', 'Sweater', 'Shorts', 'Socks', 'Hat', 'Gloves', 'Shoes'],
            'home': ['Sofa', 'Chair', 'Table', 'Lamp', 'Rug', 'Curtains', 'Bed', 'Pillow', 'Vase', 'Mirror'],
            'beauty': ['Lipstick', 'Mascara', 'Moisturizer', 'Shampoo', 'Perfume', 'Soap', 'Lotion', 'Face Mask', 'Nail Polish', 'Eyeshadow'],
            'sports': ['Running Shoes', 'Yoga Mat', 'Weights', 'Bicycle', 'Tennis Racket', 'Basketball', 'Football', 'Swimsuit', 'Helmet', 'Backpack'],
            'toys': ['Action Figure', 'Doll', 'Board Game', 'Puzzle', 'LEGO Set', 'Stuffed Animal', 'Remote Control Car', 'Building Blocks', 'Card Game', 'Robot'],
            'books': ['Novel', 'Cookbook', 'Biography', 'Self-help Book', 'History Book', 'Children\'s Book', 'Comic Book', 'Art Book', 'Travel Guide', 'Dictionary'],
            'food': ['Chocolate', 'Coffee', 'Tea', 'Snacks', 'Pasta', 'Rice', 'Cereal', 'Chips', 'Cookies', 'Nuts']
        }
        
        for _ in range(self.num_products):
            product_id = str(uuid.uuid4())
            category = random.choice(self.product_categories)
            adjective = random.choice(product_adjectives)
            noun = random.choice(product_nouns[category])
            name = f"{adjective} {noun}"
            
            # Price based on category
            if category == 'electronics':
                price = round(random.uniform(50, 2000), 2)
            elif category in ['clothing', 'sports']:
                price = round(random.uniform(15, 200), 2)
            elif category == 'home':
                price = round(random.uniform(20, 500), 2)
            elif category == 'beauty':
                price = round(random.uniform(5, 100), 2)
            elif category == 'toys':
                price = round(random.uniform(10, 150), 2)
            elif category == 'books':
                price = round(random.uniform(8, 50), 2)
            elif category == 'food':
                price = round(random.uniform(3, 30), 2)
            else:
                price = round(random.uniform(10, 100), 2)
            
            # Generate a description
            description_length = random.randint(1, 3)
            description_parts = [
                f"High-quality {category} product",
                f"Perfect for everyday use",
                f"Designed with premium materials",
                f"Modern and stylish design",
                f"Durable and long-lasting",
                f"Great value for money",
                f"Customer favorite",
                f"Versatile and practical",
                f"Innovative features",
                f"Easy to use and maintain"
            ]
            description = " ".join(random.sample(description_parts, description_length))
            
            self.products.append({
                'product_id': product_id,
                'name': name,
                'category': category,
                'price': price,
                'description': description
            })
        
        # Convert to DataFrame and insert into database
        products_df = pd.DataFrame(self.products)
        self.db.insert_data('products', products_df)
        print(f"Generated {len(self.products)} products")
    
    def generate_sessions_and_events(self):
        """Generate session data and related events."""
        print("Generating sessions and events...")
        for i in tqdm(range(self.num_sessions)):
            # Select a random user
            user = random.choice(self.users)
            user_id = user['user_id']
            session_id = str(uuid.uuid4())
            
            # Session start and end times
            start_time = self.random_date()
            session_duration = timedelta(minutes=random.randint(1, 120))
            end_time = start_time + session_duration
            
            # Device and browser might change from the user's first visit
            if random.random() < 0.8:  # 80% chance to use the same device
                device_type = user['device_type']
                browser = user['browser']
            else:
                device_type = random.choices(self.device_types, weights=self.device_weights)[0]
                browser = random.choices(self.browsers, weights=self.browser_weights)[0]
            
            # Determine if this session will convert (purchase)
            # Base conversion rate adjusted by device and browser factors
            conversion_prob = self.base_conversion_rate
            if device_type == 'desktop':
                conversion_prob *= 1.2
            elif device_type == 'mobile':
                conversion_prob *= 0.9
            
            if browser == 'Chrome':
                conversion_prob *= 1.1
            elif browser == 'Safari':
                conversion_prob *= 1.05
            
            conversion_status = 'completed' if random.random() < conversion_prob else 'abandoned'
            
            self.sessions.append({
                'session_id': session_id,
                'user_id': user_id,
                'start_time': start_time.isoformat(),
                'end_time': end_time.isoformat(),
                'device_type': device_type,
                'browser': browser,
                'conversion_status': conversion_status
            })
            
            # Now generate the user journey for this session
            self.generate_user_journey(session_id, user_id, start_time, end_time, conversion_status)
        
        # Convert to DataFrame and insert into database
        sessions_df = pd.DataFrame(self.sessions)
        self.db.insert_data('sessions', sessions_df)
        
        # Insert all event data
        if self.page_views:
            page_views_df = pd.DataFrame(self.page_views)
            self.db.insert_data('page_views', page_views_df)
        
        if self.clicks:
            clicks_df = pd.DataFrame(self.clicks)
            self.db.insert_data('clicks', clicks_df)
        
        if self.product_views:
            product_views_df = pd.DataFrame(self.product_views)
            self.db.insert_data('product_views', product_views_df)
        
        if self.cart_events:
            cart_events_df = pd.DataFrame(self.cart_events)
            self.db.insert_data('cart_events', cart_events_df)
        
        if self.search_events:
            search_events_df = pd.DataFrame(self.search_events)
            self.db.insert_data('search_events', search_events_df)
        
        if self.checkout_events:
            checkout_events_df = pd.DataFrame(self.checkout_events)
            self.db.insert_data('checkout_events', checkout_events_df)
        
        print(f"Generated {len(self.sessions)} sessions with corresponding events")
    
    def generate_user_journey(self, session_id, user_id, start_time, end_time, conversion_status):
        """Generate a realistic user journey for a session."""
        current_time = start_time
        
        # Start with homepage
        self.add_page_view(session_id, user_id, current_time, 'homepage', '/index.html')
        current_time += timedelta(seconds=random.randint(5, 30))
        
        # User might perform a search
        if random.random() < 0.6:  # 60% chance to search
            search_query = random.choice(self.common_search_queries)
            results_count = random.randint(0, 50)
            self.add_search_event(session_id, user_id, current_time, search_query, results_count)
            current_time += timedelta(seconds=random.randint(2, 10))
            
            # View search results page
            self.add_page_view(session_id, user_id, current_time, 'search_results', f'/search?q={search_query}')
            current_time += timedelta(seconds=random.randint(5, 30))
            
            # Click on a search result
            self.add_click(session_id, user_id, current_time, f'/search?q={search_query}', 'product_card', 'search_result_item')
            current_time += timedelta(seconds=random.randint(1, 3))
        else:
            # Browse product categories instead
            category = random.choice(self.product_categories)
            self.add_page_view(session_id, user_id, current_time, 'product_listing', f'/categories/{category}')
            current_time += timedelta(seconds=random.randint(10, 60))
            
            # Click on a product in the listing
            self.add_click(session_id, user_id, current_time, f'/categories/{category}', 'product_card', 'product_item')
            current_time += timedelta(seconds=random.randint(1, 3))
        
        # View product details
        viewed_products = []
        products_to_view = random.randint(1, 5)  # View 1-5 products
        
        for _ in range(products_to_view):
            if current_time >= end_time:
                break
                
            product = random.choice(self.products)
            product_id = product['product_id']
            viewed_products.append(product)
            
            # Product detail page view
            self.add_page_view(session_id, user_id, current_time, 'product_detail', f'/products/{product_id}')
            current_time += timedelta(seconds=random.randint(10, 120))
            
            # Product view event
            time_spent = random.randint(10, 120)
            self.add_product_view(session_id, user_id, product_id, current_time, time_spent)
            
            # User might add to cart
            if random.random() < 0.3:  # 30% chance to add to cart
                self.add_click(session_id, user_id, current_time, f'/products/{product_id}', 'button', 'add_to_cart_btn')
                current_time += timedelta(seconds=random.randint(1, 3))
                
                quantity = random.randint(1, 3)
                self.add_cart_event(session_id, user_id, product_id, current_time, 'add_to_cart', quantity)
                current_time += timedelta(seconds=random.randint(1, 5))
        
        # Check if any products were added to cart by looking for add_to_cart events
        cart_events = [e for e in self.cart_events if e['session_id'] == session_id and e['event_type'] == 'add_to_cart']
        
        if cart_events:  # If there are items in the cart
            # View cart page
            self.add_page_view(session_id, user_id, current_time, 'cart', '/cart')
            current_time += timedelta(seconds=random.randint(10, 60))
            
            # Randomly remove some items from cart
            if random.random() < 0.2:  # 20% chance to remove items
                event_to_remove = random.choice(cart_events)
                self.add_cart_event(session_id, user_id, event_to_remove['product_id'], current_time, 'remove_from_cart', 1)
                current_time += timedelta(seconds=random.randint(1, 5))
            
            # Proceed to checkout or abandon
            checkout_probability = 0.6 if conversion_status == 'completed' else 0.3
            
            if random.random() < checkout_probability:  # Start checkout process
                self.add_click(session_id, user_id, current_time, '/cart', 'button', 'checkout_btn')
                current_time += timedelta(seconds=random.randint(1, 3))
                
                # Start checkout process
                checkout_step_index = 0
                checkout_successful = conversion_status == 'completed'
                
                # Go through checkout steps
                while checkout_step_index < len(self.checkout_steps) and current_time < end_time:
                    step = self.checkout_steps[checkout_step_index]
                    
                    # Add page view for this checkout step
                    self.add_page_view(session_id, user_id, current_time, 'checkout', f'/checkout/{step}')
                    current_time += timedelta(seconds=random.randint(30, 120))
                    
                    # Add checkout event
                    status = 'completed' if checkout_successful or checkout_step_index < len(self.checkout_steps) - 1 else 'abandoned'
                    self.add_checkout_event(session_id, user_id, current_time, step, status)
                    
                    # If this is the last step and successful, we're done
                    if checkout_step_index == len(self.checkout_steps) - 1 and checkout_successful:
                        # Add a final thank you / confirmation page
                        current_time += timedelta(seconds=random.randint(1, 3))
                        self.add_page_view(session_id, user_id, current_time, 'confirmation', '/checkout/confirmation')
                        break
                    
                    # If the user is going to abandon, they might do so at any step
                    if not checkout_successful and random.random() < 0.3:  # 30% chance to abandon at each step
                        break
                    
                    checkout_step_index += 1
                    current_time += timedelta(seconds=random.randint(5, 15))
    
    def add_page_view(self, session_id, user_id, timestamp, page_type, page_url):
        """Add a page view event."""
        view_id = str(uuid.uuid4())
        time_spent = random.randint(5, 300)  # 5-300 seconds
        exit_page = 1 if random.random() < 0.2 else 0  # 20% chance to be an exit page
        
        self.page_views.append({
            'view_id': view_id,
            'session_id': session_id,
            'user_id': user_id,
            'timestamp': timestamp.isoformat(),
            'page_type': page_type,
            'page_url': page_url,
            'time_spent_seconds': time_spent,
            'exit_page': exit_page
        })
    
    def add_click(self, session_id, user_id, timestamp, page_url, element_type, element_id):
        """Add a click event."""
        click_id = str(uuid.uuid4())
        
        self.clicks.append({
            'click_id': click_id,
            'session_id': session_id,
            'user_id': user_id,
            'page_url': page_url,
            'element_type': element_type,
            'element_id': element_id,
            'timestamp': timestamp.isoformat()
        })
    
    def add_product_view(self, session_id, user_id, product_id, timestamp, time_spent):
        """Add a product view event."""
        view_id = str(uuid.uuid4())
        
        self.product_views.append({
            'view_id': view_id,
            'session_id': session_id,
            'user_id': user_id,
            'product_id': product_id,
            'timestamp': timestamp.isoformat(),
            'time_spent_seconds': time_spent
        })
    
    def add_cart_event(self, session_id, user_id, product_id, timestamp, event_type, quantity):
        """Add a cart event (add or remove from cart)."""
        event_id = str(uuid.uuid4())
        
        self.cart_events.append({
            'event_id': event_id,
            'session_id': session_id,
            'user_id': user_id,
            'product_id': product_id,
            'event_type': event_type,
            'quantity': quantity,
            'timestamp': timestamp.isoformat()
        })
    
    def add_search_event(self, session_id, user_id, timestamp, query, results_count):
        """Add a search event."""
        search_id = str(uuid.uuid4())
        
        self.search_events.append({
            'search_id': search_id,
            'session_id': session_id,
            'user_id': user_id,
            'query': query,
            'results_count': results_count,
            'timestamp': timestamp.isoformat()
        })
    
    def add_checkout_event(self, session_id, user_id, timestamp, step, status):
        """Add a checkout event."""
        checkout_id = str(uuid.uuid4())
        
        self.checkout_events.append({
            'checkout_id': checkout_id,
            'session_id': session_id,
            'user_id': user_id,
            'step': step,
            'status': status,
            'timestamp': timestamp.isoformat()
        })
    
    def random_date(self):
        """Generate a random date between start_date and end_date."""
        time_between_dates = self.end_date - self.start_date
        days_between_dates = time_between_dates.days
        random_number_of_days = random.randrange(days_between_dates)
        random_date = self.start_date + timedelta(days=random_number_of_days)
        
        # Add random hours, minutes, seconds
        random_date = random_date.replace(
            hour=random.randint(0, 23),
            minute=random.randint(0, 59),
            second=random.randint(0, 59)
        )
        
        return random_date
    
    def generate_all_data(self):
        """Generate all data for the e-commerce database."""
        print("Starting data generation...")
        self.generate_users()
        self.generate_products()
        self.generate_sessions_and_events()
        print("Data generation complete!")


if __name__ == "__main__":
    # Check if database file exists and remove if it does
    if os.path.exists('ecommerce_data.db'):
        os.remove('ecommerce_data.db')
        print("Removed existing database file.")
    
    # Generate data
    generator = EcommerceDataGenerator(num_users=200, num_sessions=500, num_products=50)
    generator.generate_all_data()
