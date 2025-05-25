import sqlite3
import os
import pandas as pd
from datetime import datetime

class EcommerceDatabase:
    def __init__(self, db_path='ecommerce_data.db'):
        """Initialize the database connection."""
        self.db_path = db_path
        self.connection = None
        self.create_tables()
    
    def connect(self):
        """Create a connection to the SQLite database."""
        self.connection = sqlite3.connect(self.db_path)
        return self.connection
    
    def close(self):
        """Close the database connection."""
        if self.connection:
            self.connection.close()
    
    def create_tables(self):
        """Create the necessary tables if they don't exist."""
        conn = self.connect()
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            first_visit_date TEXT,
            device_type TEXT,
            browser TEXT,
            country TEXT,
            referrer TEXT
        )
        ''')
        
        # Sessions table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT PRIMARY KEY,
            user_id TEXT,
            start_time TEXT,
            end_time TEXT,
            device_type TEXT,
            browser TEXT,
            conversion_status TEXT,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
        ''')
        
        # Page views table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS page_views (
            view_id TEXT PRIMARY KEY,
            session_id TEXT,
            user_id TEXT,
            timestamp TEXT,
            page_type TEXT,
            page_url TEXT,
            time_spent_seconds INTEGER,
            exit_page INTEGER,
            FOREIGN KEY (session_id) REFERENCES sessions(session_id),
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
        ''')
        
        # Clicks table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS clicks (
            click_id TEXT PRIMARY KEY,
            session_id TEXT,
            user_id TEXT,
            page_url TEXT,
            element_type TEXT,
            element_id TEXT,
            timestamp TEXT,
            FOREIGN KEY (session_id) REFERENCES sessions(session_id),
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
        ''')
        
        # Products table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            product_id TEXT PRIMARY KEY,
            name TEXT,
            category TEXT,
            price REAL,
            description TEXT
        )
        ''')
        
        # Product views table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS product_views (
            view_id TEXT PRIMARY KEY,
            session_id TEXT,
            user_id TEXT,
            product_id TEXT,
            timestamp TEXT,
            time_spent_seconds INTEGER,
            FOREIGN KEY (session_id) REFERENCES sessions(session_id),
            FOREIGN KEY (user_id) REFERENCES users(user_id),
            FOREIGN KEY (product_id) REFERENCES products(product_id)
        )
        ''')
        
        # Cart events table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS cart_events (
            event_id TEXT PRIMARY KEY,
            session_id TEXT,
            user_id TEXT,
            product_id TEXT,
            event_type TEXT,
            quantity INTEGER,
            timestamp TEXT,
            FOREIGN KEY (session_id) REFERENCES sessions(session_id),
            FOREIGN KEY (user_id) REFERENCES users(user_id),
            FOREIGN KEY (product_id) REFERENCES products(product_id)
        )
        ''')
        
        # Search events table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS search_events (
            search_id TEXT PRIMARY KEY,
            session_id TEXT,
            user_id TEXT,
            query TEXT,
            results_count INTEGER,
            timestamp TEXT,
            FOREIGN KEY (session_id) REFERENCES sessions(session_id),
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
        ''')
        
        # Checkout events table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS checkout_events (
            checkout_id TEXT PRIMARY KEY,
            session_id TEXT,
            user_id TEXT,
            step TEXT,
            status TEXT,
            timestamp TEXT,
            FOREIGN KEY (session_id) REFERENCES sessions(session_id),
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
        ''')
        
        conn.commit()
        self.close()
    
    def insert_data(self, table_name, data):
        """Insert data into the specified table."""
        conn = self.connect()
        data.to_sql(table_name, conn, if_exists='append', index=False)
        conn.commit()
        self.close()
    
    def execute_query(self, query, params=()):
        """Execute a query and return the results."""
        conn = self.connect()
        result = pd.read_sql_query(query, conn, params=params)
        self.close()
        return result
    
    def get_user_journey_data(self, user_id=None, session_id=None, limit=1000):
        """Get comprehensive user journey data for analysis."""
        conn = self.connect()
        
        query_conditions = []
        params = {}
        
        if user_id:
            query_conditions.append("u.user_id = :user_id")
            params['user_id'] = user_id
        
        if session_id:
            query_conditions.append("s.session_id = :session_id")
            params['session_id'] = session_id
        
        where_clause = ""
        if query_conditions:
            where_clause = "WHERE " + " AND ".join(query_conditions)
        
        query = f"""
        SELECT 
            u.user_id, s.session_id, s.start_time, s.end_time, s.conversion_status,
            pv.page_type, pv.page_url, pv.timestamp as page_view_time, pv.time_spent_seconds,
            c.element_type, c.element_id, c.timestamp as click_time,
            prod.product_id, prod.name as product_name, prod.category, prod.price,
            ce.event_type as cart_event, ce.quantity, ce.timestamp as cart_event_time,
            se.query as search_query, se.results_count, se.timestamp as search_time,
            che.step as checkout_step, che.status as checkout_status, che.timestamp as checkout_time
        FROM 
            users u
        LEFT JOIN 
            sessions s ON u.user_id = s.user_id
        LEFT JOIN 
            page_views pv ON s.session_id = pv.session_id
        LEFT JOIN 
            clicks c ON s.session_id = c.session_id
        LEFT JOIN 
            product_views prodv ON s.session_id = prodv.session_id
        LEFT JOIN 
            products prod ON prodv.product_id = prod.product_id
        LEFT JOIN 
            cart_events ce ON s.session_id = ce.session_id
        LEFT JOIN 
            search_events se ON s.session_id = se.session_id
        LEFT JOIN 
            checkout_events che ON s.session_id = che.session_id
        {where_clause}
        ORDER BY 
            u.user_id, s.start_time, pv.timestamp
        LIMIT :limit
        """
        
        params['limit'] = limit
        result = pd.read_sql_query(query, conn, params=params)
        self.close()
        return result
    
    def get_conversion_rates(self):
        """Calculate conversion rates by various dimensions."""
        conn = self.connect()
        
        # Overall conversion rate
        overall_query = """
        SELECT 
            COUNT(CASE WHEN conversion_status = 'completed' THEN 1 END) as completed,
            COUNT(*) as total,
            CAST(COUNT(CASE WHEN conversion_status = 'completed' THEN 1 END) AS FLOAT) / COUNT(*) as conversion_rate
        FROM 
            sessions
        """
        overall = pd.read_sql_query(overall_query, conn)
        
        # By device type
        device_query = """
        SELECT 
            device_type,
            COUNT(CASE WHEN conversion_status = 'completed' THEN 1 END) as completed,
            COUNT(*) as total,
            CAST(COUNT(CASE WHEN conversion_status = 'completed' THEN 1 END) AS FLOAT) / COUNT(*) as conversion_rate
        FROM 
            sessions
        GROUP BY 
            device_type
        ORDER BY 
            conversion_rate DESC
        """
        by_device = pd.read_sql_query(device_query, conn)
        
        # By referrer
        referrer_query = """
        SELECT 
            u.referrer,
            COUNT(CASE WHEN s.conversion_status = 'completed' THEN 1 END) as completed,
            COUNT(*) as total,
            CAST(COUNT(CASE WHEN s.conversion_status = 'completed' THEN 1 END) AS FLOAT) / COUNT(*) as conversion_rate
        FROM 
            sessions s
        JOIN
            users u ON s.user_id = u.user_id
        GROUP BY 
            u.referrer
        ORDER BY 
            conversion_rate DESC
        """
        by_referrer = pd.read_sql_query(referrer_query, conn)
        
        self.close()
        return {
            'overall': overall,
            'by_device': by_device,
            'by_referrer': by_referrer
        }
    
    def get_funnel_analysis(self):
        """Analyze the conversion funnel."""
        conn = self.connect()
        
        funnel_query = """
        WITH funnel_stages AS (
            SELECT
                s.session_id,
                MAX(CASE WHEN pv.page_type = 'homepage' THEN 1 ELSE 0 END) as homepage_view,
                MAX(CASE WHEN pv.page_type = 'product_listing' THEN 1 ELSE 0 END) as product_listing_view,
                MAX(CASE WHEN pv.page_type = 'product_detail' THEN 1 ELSE 0 END) as product_detail_view,
                MAX(CASE WHEN ce.event_type = 'add_to_cart' THEN 1 ELSE 0 END) as add_to_cart,
                MAX(CASE WHEN che.step = 'checkout_start' THEN 1 ELSE 0 END) as checkout_start,
                MAX(CASE WHEN che.step = 'shipping_info' THEN 1 ELSE 0 END) as shipping_info,
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
            SUM(shipping_info) as shipping_info_completed,
            SUM(payment_info) as payment_info_completed,
            SUM(purchase_completed) as purchases_completed
        FROM
            funnel_stages
        """
        
        funnel_data = pd.read_sql_query(funnel_query, conn)
        self.close()
        
        # Convert to step-by-step drop-off rates
        steps = funnel_data.iloc[0].tolist()
        step_names = funnel_data.columns.tolist()
        
        funnel_analysis = []
        for i in range(len(steps) - 1):
            current_step = steps[i]
            next_step = steps[i+1]
            drop_off = current_step - next_step
            if current_step > 0:
                drop_off_rate = drop_off / current_step
            else:
                drop_off_rate = 0
                
            funnel_analysis.append({
                'current_step': step_names[i],
                'next_step': step_names[i+1],
                'current_count': int(current_step),
                'next_count': int(next_step),
                'drop_off': int(drop_off),
                'drop_off_rate': float(drop_off_rate)
            })
            
        return funnel_analysis
    
    def get_cart_abandonment_data(self):
        """Analyze cart abandonment patterns."""
        conn = self.connect()
        
        query = """
        WITH cart_sessions AS (
            SELECT
                s.session_id,
                s.conversion_status,
                MAX(ce.timestamp) as last_cart_action,
                GROUP_CONCAT(p.name, ', ') as products_in_cart,
                SUM(p.price * ce.quantity) as cart_value
            FROM
                sessions s
            JOIN
                cart_events ce ON s.session_id = ce.session_id
            JOIN
                products p ON ce.product_id = p.product_id
            WHERE
                ce.event_type = 'add_to_cart'
            GROUP BY
                s.session_id
        )
        SELECT
            conversion_status,
            COUNT(*) as session_count,
            AVG(cart_value) as avg_cart_value,
            products_in_cart
        FROM
            cart_sessions
        GROUP BY
            conversion_status
        """
        
        cart_data = pd.read_sql_query(query, conn)
        self.close()
        
        return cart_data
    
    def get_search_behavior(self):
        """Analyze search behavior patterns."""
        conn = self.connect()
        
        # Top searches
        top_searches_query = """
        SELECT
            query,
            COUNT(*) as search_count,
            AVG(results_count) as avg_results
        FROM
            search_events
        GROUP BY
            query
        ORDER BY
            search_count DESC
        LIMIT 20
        """
        top_searches = pd.read_sql_query(top_searches_query, conn)
        
        # Zero results searches
        zero_results_query = """
        SELECT
            query,
            COUNT(*) as search_count
        FROM
            search_events
        WHERE
            results_count = 0
        GROUP BY
            query
        ORDER BY
            search_count DESC
        LIMIT 20
        """
        zero_results = pd.read_sql_query(zero_results_query, conn)
        
        # Search to conversion rate
        search_conversion_query = """
        SELECT
            COUNT(DISTINCT se.session_id) as sessions_with_search,
            COUNT(DISTINCT CASE WHEN s.conversion_status = 'completed' THEN se.session_id END) as converted_search_sessions,
            CAST(COUNT(DISTINCT CASE WHEN s.conversion_status = 'completed' THEN se.session_id END) AS FLOAT) / 
            COUNT(DISTINCT se.session_id) as search_conversion_rate
        FROM
            search_events se
        JOIN
            sessions s ON se.session_id = s.session_id
        """
        search_conversion = pd.read_sql_query(search_conversion_query, conn)
        
        self.close()
        
        return {
            'top_searches': top_searches,
            'zero_results': zero_results,
            'search_conversion': search_conversion
        }
    
    def get_page_effectiveness(self):
        """Analyze page effectiveness metrics."""
        conn = self.connect()
        
        query = """
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
        """
        
        page_data = pd.read_sql_query(query, conn)
        self.close()
        
        return page_data

    def get_product_performance(self):
        """Analyze product performance metrics."""
        conn = self.connect()
        
        query = """
        SELECT
            p.product_id,
            p.name,
            p.category,
            COUNT(DISTINCT pv.view_id) as view_count,
            COUNT(DISTINCT CASE WHEN ce.event_type = 'add_to_cart' THEN ce.event_id END) as add_to_cart_count,
            CAST(COUNT(DISTINCT CASE WHEN ce.event_type = 'add_to_cart' THEN ce.event_id END) AS FLOAT) / 
                NULLIF(COUNT(DISTINCT pv.view_id), 0) as view_to_cart_rate,
            COUNT(DISTINCT CASE WHEN s.conversion_status = 'completed' 
                AND ce.event_type = 'add_to_cart' THEN s.session_id END) as purchase_count,
            CAST(COUNT(DISTINCT CASE WHEN s.conversion_status = 'completed' 
                AND ce.event_type = 'add_to_cart' THEN s.session_id END) AS FLOAT) / 
                NULLIF(COUNT(DISTINCT CASE WHEN ce.event_type = 'add_to_cart' THEN ce.event_id END), 0) as cart_to_purchase_rate
        FROM
            products p
        LEFT JOIN
            product_views pv ON p.product_id = pv.product_id
        LEFT JOIN
            cart_events ce ON p.product_id = ce.product_id
        LEFT JOIN
            sessions s ON ce.session_id = s.session_id
        GROUP BY
            p.product_id
        ORDER BY
            view_count DESC
        """
        
        product_data = pd.read_sql_query(query, conn)
        self.close()
        
        return product_data
