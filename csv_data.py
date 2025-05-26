import os
import pandas as pd
import sqlite3

def export_database_to_csv(db_path='ecommerce_data.db', output_dir='exported_data'):
    """Export all tables from the SQLite database to CSV files."""
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Connect to the database
    conn = sqlite3.connect(db_path)
    
    # Get list of tables
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    # Export each table to CSV
    for table in tables:
        table_name = table[0]
        print(f"Exporting {table_name} to CSV...")
        
        # Skip sqlite_sequence table
        if table_name == 'sqlite_sequence':
            continue
        
        # Read the table into a pandas DataFrame
        df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
        
        # Save to CSV
        csv_path = os.path.join(output_dir, f"{table_name}.csv")
        df.to_csv(csv_path, index=False)
        print(f"  Saved {len(df)} rows to {csv_path}")
    
    # Create a combined user journey file
    print("Creating combined user journey data...")
    query = """
    SELECT 
        u.user_id, s.session_id, s.start_time, s.end_time, s.conversion_status,
        u.device_type, u.browser, u.country, u.referrer,
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
    ORDER BY 
        u.user_id, s.start_time, pv.timestamp
    LIMIT 10000
    """
    
    combined_data = pd.read_sql_query(query, conn)
    combined_csv_path = os.path.join(output_dir, "combined_user_journey.csv")
    combined_data.to_csv(combined_csv_path, index=False)
    print(f"  Saved {len(combined_data)} rows to {combined_csv_path}")
    
    # Also create a simplified combined view (just the key attributes)
    print("Creating simplified overview data...")
    simplified_query = """
    SELECT 
        u.user_id, 
        u.device_type, 
        u.browser, 
        u.country,
        u.referrer,
        COUNT(DISTINCT s.session_id) as session_count,
        COUNT(DISTINCT pv.view_id) as page_views,
        COUNT(DISTINCT c.click_id) as clicks,
        COUNT(DISTINCT prodv.view_id) as product_views,
        COUNT(DISTINCT CASE WHEN ce.event_type = 'add_to_cart' THEN ce.event_id END) as add_to_cart_events,
        COUNT(DISTINCT se.search_id) as searches,
        COUNT(DISTINCT CASE WHEN che.step = 'submit_order' AND che.status = 'completed' THEN che.checkout_id END) as completed_purchases
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
        cart_events ce ON s.session_id = ce.session_id
    LEFT JOIN 
        search_events se ON s.session_id = se.session_id
    LEFT JOIN 
        checkout_events che ON s.session_id = che.session_id
    GROUP BY
        u.user_id
    """
    
    simplified_data = pd.read_sql_query(simplified_query, conn)
    simplified_csv_path = os.path.join(output_dir, "user_summary.csv")
    simplified_data.to_csv(simplified_csv_path, index=False)
    print(f"  Saved {len(simplified_data)} rows to {simplified_csv_path}")
    
    # Close the connection
    conn.close()
    
    print(f"Export complete! All data exported to {output_dir}/ directory")
    print(f"You can find the following files:")
    print(f"  - Individual table data in separate CSV files")
    print(f"  - Complete user journey data in {combined_csv_path}")
    print(f"  - Simplified user summary in {simplified_csv_path}")

if __name__ == "__main__":
    export_database_to_csv()