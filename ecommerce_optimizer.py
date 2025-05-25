import os
import json
import sqlite3
import uuid
import random
from datetime import datetime, timedelta

# Create a simple database and generate demo data
def setup_database():
    print("Setting up database...")
    # Remove existing database if it exists
    if os.path.exists('ecommerce_data.db'):
        os.remove('ecommerce_data.db')
        print("Removed existing database file.")
    
    # Create a new database
    conn = sqlite3.connect('ecommerce_data.db')
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''
    CREATE TABLE users (
        user_id TEXT PRIMARY KEY,
        device_type TEXT,
        referrer TEXT
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE sessions (
        session_id TEXT PRIMARY KEY,
        user_id TEXT,
        start_time TEXT,
        conversion_status TEXT,
        FOREIGN KEY (user_id) REFERENCES users(user_id)
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE page_views (
        view_id TEXT PRIMARY KEY,
        session_id TEXT,
        page_type TEXT,
        time_spent_seconds INTEGER,
        exit_page INTEGER,
        FOREIGN KEY (session_id) REFERENCES sessions(session_id)
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE product_views (
        view_id TEXT PRIMARY KEY,
        session_id TEXT,
        product_id TEXT,
        time_spent_seconds INTEGER,
        FOREIGN KEY (session_id) REFERENCES sessions(session_id)
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE cart_events (
        event_id TEXT PRIMARY KEY,
        session_id TEXT,
        product_id TEXT,
        event_type TEXT,
        FOREIGN KEY (session_id) REFERENCES sessions(session_id)
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE checkout_events (
        checkout_id TEXT PRIMARY KEY,
        session_id TEXT,
        step TEXT,
        status TEXT,
        FOREIGN KEY (session_id) REFERENCES sessions(session_id)
    )
    ''')
    
    conn.commit()
    print("Database schema created.")
    
    # Generate demo data
    print("Generating demo data...")
    
    # Common attributes
    device_types = ['desktop', 'mobile', 'tablet']
    device_weights = [0.5, 0.4, 0.1]  # probability weights
    
    referrers = ['direct', 'google', 'facebook', 'email']
    referrer_weights = [0.3, 0.4, 0.2, 0.1]  # probability weights
    
    page_types = ['homepage', 'product_listing', 'product_detail', 'cart', 'checkout']
    
    # Generate users
    users = []
    for i in range(100):
        user_id = str(uuid.uuid4())
        device_type = random.choices(device_types, weights=device_weights)[0]
        referrer = random.choices(referrers, weights=referrer_weights)[0]
        
        users.append((user_id, device_type, referrer))
    
    cursor.executemany('INSERT INTO users VALUES (?, ?, ?)', users)
    print(f"Generated {len(users)} users.")
    
    # Generate sessions and events
    sessions = []
    page_views = []
    product_views = []
    cart_events = []
    checkout_events = []
    
    for user_id, _, _ in users:
        # Each user has 1-3 sessions
        for _ in range(random.randint(1, 3)):
            session_id = str(uuid.uuid4())
            
            # 20% conversion rate
            conversion_status = 'completed' if random.random() < 0.2 else 'abandoned'
            start_time = datetime.now() - timedelta(days=random.randint(1, 30))
            
            sessions.append((session_id, user_id, start_time.isoformat(), conversion_status))
            
            # Generate page views for this session
            for page_type in page_types[:random.randint(1, len(page_types))]:
                view_id = str(uuid.uuid4())
                time_spent = random.randint(5, 300)  # 5-300 seconds
                exit_page = 1 if random.random() < 0.2 else 0  # 20% chance to be an exit page
                
                page_views.append((view_id, session_id, page_type, time_spent, exit_page))
            
            # Some sessions have product views
            if random.random() < 0.7:  # 70% chance
                for _ in range(random.randint(1, 3)):
                    view_id = str(uuid.uuid4())
                    product_id = f"product_{random.randint(1, 50)}"
                    time_spent = random.randint(10, 180)  # 10-180 seconds
                    
                    product_views.append((view_id, session_id, product_id, time_spent))
                
                # Some sessions have cart events
                if random.random() < 0.5:  # 50% chance
                    event_id = str(uuid.uuid4())
                    product_id = f"product_{random.randint(1, 50)}"
                    event_type = 'add_to_cart'
                    
                    cart_events.append((event_id, session_id, product_id, event_type))
                    
                    # Some sessions have checkout events
                    if random.random() < 0.4:  # 40% chance
                        checkout_steps = ['checkout_start', 'shipping_info', 'payment_info', 'review_order']
                        
                        for step in checkout_steps[:random.randint(1, len(checkout_steps))]:
                            checkout_id = str(uuid.uuid4())
                            status = 'completed' if conversion_status == 'completed' or random.random() < 0.7 else 'abandoned'
                            
                            checkout_events.append((checkout_id, session_id, step, status))
    
    cursor.executemany('INSERT INTO sessions VALUES (?, ?, ?, ?)', sessions)
    cursor.executemany('INSERT INTO page_views VALUES (?, ?, ?, ?, ?)', page_views)
    cursor.executemany('INSERT INTO product_views VALUES (?, ?, ?, ?)', product_views)
    cursor.executemany('INSERT INTO cart_events VALUES (?, ?, ?, ?)', cart_events)
    cursor.executemany('INSERT INTO checkout_events VALUES (?, ?, ?, ?)', checkout_events)
    
    conn.commit()
    conn.close()
    
    print(f"Generated {len(sessions)} sessions with corresponding events.")
    print(f"Generated {len(page_views)} page views.")
    print(f"Generated {len(product_views)} product views.")
    print(f"Generated {len(cart_events)} cart events.")
    print(f"Generated {len(checkout_events)} checkout events.")
    print("\nDemo data generation complete!")

# Analyze the e-commerce user journey data
def analyze_data():
    print("\nAnalyzing e-commerce user journey data...")
    conn = sqlite3.connect('ecommerce_data.db')
    cursor = conn.cursor()
    
    # 1. Calculate conversion rate
    cursor.execute("""
    SELECT 
        COUNT(*) as total_sessions,
        SUM(CASE WHEN conversion_status = 'completed' THEN 1 ELSE 0 END) as completed_sessions,
        CAST(SUM(CASE WHEN conversion_status = 'completed' THEN 1 ELSE 0 END) AS FLOAT) / COUNT(*) as conversion_rate
    FROM 
        sessions
    """)
    
    total, completed, conv_rate = cursor.fetchone()
    print(f"\nOverall conversion rate: {conv_rate*100:.2f}% ({completed}/{total} sessions)")
    
    # 2. Device type analysis
    cursor.execute("""
    SELECT 
        u.device_type,
        COUNT(*) as total_sessions,
        SUM(CASE WHEN s.conversion_status = 'completed' THEN 1 ELSE 0 END) as completed_sessions,
        CAST(SUM(CASE WHEN s.conversion_status = 'completed' THEN 1 ELSE 0 END) AS FLOAT) / COUNT(*) as conversion_rate
    FROM 
        sessions s
    JOIN
        users u ON s.user_id = u.user_id
    GROUP BY
        u.device_type
    ORDER BY
        conversion_rate DESC
    """)
    
    print("\nConversion rate by device type:")
    print("{:<10} {:<15} {:<20} {:<15}".format("Device", "Total Sessions", "Completed Sessions", "Conversion Rate"))
    print("-" * 65)
    
    for device, total, completed, rate in cursor.fetchall():
        print("{:<10} {:<15} {:<20} {:<15.2f}%".format(device, total, completed, rate*100))
    
    # 3. Referrer analysis
    cursor.execute("""
    SELECT 
        u.referrer,
        COUNT(*) as total_sessions,
        SUM(CASE WHEN s.conversion_status = 'completed' THEN 1 ELSE 0 END) as completed_sessions,
        CAST(SUM(CASE WHEN s.conversion_status = 'completed' THEN 1 ELSE 0 END) AS FLOAT) / COUNT(*) as conversion_rate
    FROM 
        sessions s
    JOIN
        users u ON s.user_id = u.user_id
    GROUP BY
        u.referrer
    ORDER BY
        conversion_rate DESC
    """)
    
    print("\nConversion rate by referrer:")
    print("{:<10} {:<15} {:<20} {:<15}".format("Referrer", "Total Sessions", "Completed Sessions", "Conversion Rate"))
    print("-" * 65)
    
    for referrer, total, completed, rate in cursor.fetchall():
        print("{:<10} {:<15} {:<20} {:<15.2f}%".format(referrer, total, completed, rate*100))
    
    # 4. Page effectiveness analysis
    cursor.execute("""
    SELECT
        page_type,
        COUNT(*) as view_count,
        AVG(time_spent_seconds) as avg_time_spent,
        SUM(exit_page) as exit_count,
        CAST(SUM(exit_page) AS FLOAT) / COUNT(*) as exit_rate
    FROM
        page_views
    GROUP BY
        page_type
    ORDER BY
        view_count DESC
    """)
    
    print("\nPage effectiveness:")
    print("{:<15} {:<10} {:<20} {:<10} {:<10}".format("Page Type", "Views", "Avg Time (sec)", "Exits", "Exit Rate"))
    print("-" * 70)
    
    for page_type, views, avg_time, exits, exit_rate in cursor.fetchall():
        print("{:<15} {:<10} {:<20.1f} {:<10} {:<10.2f}%".format(
            page_type, views, avg_time, exits, exit_rate*100))
    
    # 5. Funnel analysis
    cursor.execute("""
    WITH funnel_stages AS (
        SELECT
            s.session_id,
            MAX(CASE WHEN pv.page_type = 'homepage' THEN 1 ELSE 0 END) as homepage_view,
            MAX(CASE WHEN pv.page_type = 'product_listing' THEN 1 ELSE 0 END) as product_listing_view,
            MAX(CASE WHEN pv.page_type = 'product_detail' THEN 1 ELSE 0 END) as product_detail_view,
            MAX(CASE WHEN ce.event_type = 'add_to_cart' THEN 1 ELSE 0 END) as add_to_cart,
            MAX(CASE WHEN che.step = 'checkout_start' THEN 1 ELSE 0 END) as checkout_start,
            MAX(CASE WHEN che.step = 'payment_info' THEN 1 ELSE 0 END) as payment_info,
            MAX(CASE WHEN s.conversion_status = 'completed' THEN 1 ELSE 0 END) as purchase_completed
        FROM
            sessions s
        LEFT JOIN
            page_views pv ON s.session_id = pv.session_id
        LEFT JOIN
            cart_events ce ON s.session_id = ce.session_id
        LEFT JOIN
            checkout_events che ON s.session_id = che.session_id
        GROUP BY
            s.session_id
    )
    SELECT
        SUM(homepage_view) as homepage_views,
        SUM(product_listing_view) as product_listing_views,
        SUM(product_detail_view) as product_detail_views,
        SUM(add_to_cart) as add_to_cart_events,
        SUM(checkout_start) as checkout_starts,
        SUM(payment_info) as payment_info_completed,
        SUM(purchase_completed) as purchases_completed
    FROM
        funnel_stages
    """)
    
    funnel_data = cursor.fetchone()
    funnel_stages = ['Homepage', 'Product Listing', 'Product Detail', 
                    'Add to Cart', 'Checkout Start', 'Payment Info', 'Purchase']
    
    print("\nConversion funnel:")
    print("{:<20} {:<10} {:<15}".format("Stage", "Count", "Drop-off Rate"))
    print("-" * 50)
    
    for i in range(len(funnel_data) - 1):
        current = funnel_data[i]
        next_step = funnel_data[i+1]
        drop_off = current - next_step
        drop_off_rate = (drop_off / current) * 100 if current > 0 else 0
        
        print("{:<20} {:<10} {:<15.2f}%".format(
            funnel_stages[i], current, drop_off_rate))
    
    # Final conversion
    print("{:<20} {:<10}".format(funnel_stages[-1], funnel_data[-1]))
    
    conn.close()
    print("\nAnalysis complete!")

# Generate a report with AI-based recommendations
def generate_report():
    print("\nGenerating optimization recommendations...")
    
    # In a production environment, this would call Claude API
    # Here we'll provide static recommendations based on common patterns
    
    recommendations = [
        {"area": "Mobile Experience", 
         "issue": "Lower conversion rates on mobile devices",
         "recommendation": "Optimize the mobile checkout experience with simplified forms and mobile-friendly payment options"},
        
        {"area": "Checkout Process", 
         "issue": "High drop-off between checkout start and payment info",
         "recommendation": "Reduce form fields, add progress indicators, and provide guest checkout option"},
        
        {"area": "Product Pages", 
         "issue": "Users viewing product details but not adding to cart",
         "recommendation": "Enhance product pages with better images, clearer descriptions, and more prominent call-to-action buttons"},
        
        {"area": "Cart Abandonment", 
         "issue": "Users adding products to cart but not starting checkout",
         "recommendation": "Add trust signals, clear shipping information, and implement cart abandonment recovery emails"},
        
        {"area": "Search Functionality", 
         "issue": "Users performing searches but not finding relevant products",
         "recommendation": "Improve search algorithms, add search suggestions, and ensure zero-result searches show alternative products"}
    ]
    
    print("\nTop Recommendations for Optimizing User Journey:")
    print("-" * 100)
    
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. {rec['area']}: {rec['recommendation']}")
        print(f"   Issue: {rec['issue']}")
        print()
    
    print("Implementing these recommendations should lead to measurable improvements")
    print("in your key performance indicators, including conversion rate, average order value,")
    print("and customer satisfaction.")

# Main function to run the complete flow
def main():
    print("E-commerce User Journey Optimization Agent")
    print("------------------------------------------\n")
    
    # Step 1: Set up database and generate demo data
    setup_database()
    
    # Step 2: Analyze the data
    analyze_data()
    
    # Step 3: Generate recommendations
    generate_report()
    
    print("\nAnalysis complete! In a production environment, this agent would:")
    print("1. Connect to your actual e-commerce database")
    print("2. Perform more sophisticated analysis using machine learning")
    print("3. Generate personalized recommendations using Claude AI")
    print("4. Create visualizations of key metrics")
    print("5. Continuously monitor performance and suggest improvements")

if __name__ == "__main__":
    main()
