import pandas as pd
import numpy as np
# Set non-interactive backend for matplotlib to avoid thread issues
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from sklearn.cluster import KMeans
from database import EcommerceDatabase
from tabulate import tabulate
import os

class EcommerceDataAnalyzer:
    def __init__(self, db=None):
        """Initialize the analyzer with a database connection."""
        self.db = db if db else EcommerceDatabase()
        
        # Create output directory for visualizations
        os.makedirs('output', exist_ok=True)
    
    def analyze_conversion_funnel(self):
        """Analyze the conversion funnel to identify drop-off points."""
        funnel_data = self.db.get_funnel_analysis()
        
        insights = {
            'funnel_stages': [],
            'critical_dropoffs': [],
            'recommendations': []
        }
        
        # Sort stages by drop-off rate
        sorted_stages = sorted(funnel_data, key=lambda x: x['drop_off_rate'], reverse=True)
        
        # Prepare data for visualization
        # Safely access current_step or use alternatives like 'stage' if available
        stages = []
        for stage in funnel_data:
            stage_name = stage.get('current_step', stage.get('stage', f'Stage {len(stages)+1}'))
            stages.append(stage_name)
        counts = []
        for stage in funnel_data:
            count = stage.get('current_count', stage.get('count', 0))
            counts.append(count)
        
        # Create visualization
        plt.figure(figsize=(12, 6))
        plt.bar(stages, counts)
        plt.title('Conversion Funnel')
        plt.xlabel('Funnel Stage')
        plt.ylabel('Number of Users')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig('output/conversion_funnel.png')
        
        # Add insights
        for stage in funnel_data:
            insights['funnel_stages'].append({
                'stage': f"{stage.get('current_step', stage.get('stage', 'Unknown'))} → {stage.get('next_step', 'Next Stage')}",
                'drop_off_rate': f"{stage.get('drop_off_rate', 0)*100:.1f}%" if not isinstance(stage.get('drop_off_rate'), str) else stage.get('drop_off_rate'),
                'users_lost': stage.get('drop_off', 0)
            })
            
            # Identify critical drop-offs (more than 50%)
            # Safely check drop_off_rate with a default of 0
            drop_rate = stage.get('drop_off_rate', 0)
            if isinstance(drop_rate, str):
                try:
                    # Try to convert percentage string to float for comparison
                    drop_rate = float(drop_rate.strip('%')) / 100
                except:
                    drop_rate = 0
                    
            if drop_rate > 0.5:
                insights['critical_dropoffs'].append({
                    'stage': f"{stage.get('current_step', stage.get('stage', 'Unknown'))} → {stage.get('next_step', 'Next Stage')}",
                    'drop_off_rate': f"{drop_rate*100:.1f}%" if not isinstance(stage.get('drop_off_rate'), str) else stage.get('drop_off_rate'),
                    'users_lost': stage.get('drop_off', 0)
                })
                
                # Generate specific recommendations based on the stage
                current_step = stage.get('current_step', stage.get('stage', ''))
                next_step = stage.get('next_step', '')
                
                if current_step and 'checkout' in current_step:
                    insights['recommendations'].append({
                        'area': f"{current_step} optimization",
                        'suggestion': "Simplify the checkout process by reducing form fields and adding progress indicators"
                    })
                elif current_step and next_step and 'product_detail' in current_step and 'add_to_cart' in next_step:
                    insights['recommendations'].append({
                        'area': "Product page optimization",
                        'suggestion': "Enhance product pages with better images, clearer descriptions, and more prominent add-to-cart buttons"
                    })
                elif current_step and next_step and 'add_to_cart' in current_step and 'checkout' in next_step:
                    insights['recommendations'].append({
                        'area': "Cart to checkout transition",
                        'suggestion': "Add trust signals, clear shipping information, and guest checkout options"
                    })
        
        return insights
    
    def analyze_cart_abandonment(self):
        """Analyze cart abandonment patterns."""
        cart_data = self.db.get_cart_abandonment_data()
        
        insights = {
            'abandonment_rate': 0,
            'average_cart_values': [],
            'common_abandoned_products': [],
            'recommendations': []
        }
        
        # Calculate abandonment rate
        completed = cart_data[cart_data['conversion_status'] == 'completed']['session_count'].sum()
        abandoned = cart_data[cart_data['conversion_status'] == 'abandoned']['session_count'].sum()
        total = completed + abandoned
        
        if total > 0:
            abandonment_rate = abandoned / total
            insights['abandonment_rate'] = f"{abandonment_rate*100:.1f}%"
        
        # Average cart values
        for status, group in cart_data.groupby('conversion_status'):
            insights['average_cart_values'].append({
                'status': status,
                'avg_value': f"${group['avg_cart_value'].mean():.2f}"
            })
        
        # Recommendations based on cart values
        if 'completed' in cart_data['conversion_status'].values and 'abandoned' in cart_data['conversion_status'].values:
            completed_avg = cart_data[cart_data['conversion_status'] == 'completed']['avg_cart_value'].mean()
            abandoned_avg = cart_data[cart_data['conversion_status'] == 'abandoned']['avg_cart_value'].mean()
            
            if abandoned_avg > completed_avg * 1.2:  # Abandoned carts are 20% higher in value
                insights['recommendations'].append({
                    'area': "High-value cart recovery",
                    'suggestion': "Implement targeted cart recovery emails with special incentives for high-value abandoned carts"
                })
            
            insights['recommendations'].append({
                'area': "Checkout friction",
                'suggestion': "Reduce checkout friction by implementing a progress indicator, guest checkout, and multiple payment options"
            })
            
            insights['recommendations'].append({
                'area': "Trust signals",
                'suggestion': "Add trust signals such as secure payment icons, money-back guarantees, and customer reviews on the checkout page"
            })
        
        # Create visualization
        if not cart_data.empty and 'avg_cart_value' in cart_data.columns and 'conversion_status' in cart_data.columns:
            plt.figure(figsize=(10, 6))
            sns.barplot(x='conversion_status', y='avg_cart_value', data=cart_data)
            plt.title('Average Cart Value by Conversion Status')
            plt.xlabel('Conversion Status')
            plt.ylabel('Average Cart Value ($)')
            plt.savefig('output/cart_abandonment.png')
        
        return insights
    
    def analyze_search_behavior(self):
        """Analyze search behavior patterns."""
        search_data = self.db.get_search_behavior()
        
        insights = {
            'top_searches': [],
            'zero_results': [],
            'search_conversion_rate': 0,
            'recommendations': []
        }
        
        # Top searches
        if not search_data['top_searches'].empty:
            top_searches = search_data['top_searches'].head(10)
            for _, row in top_searches.iterrows():
                insights['top_searches'].append({
                    'query': row['query'],
                    'count': row['search_count'],
                    'avg_results': row['avg_results']
                })
        
        # Zero results searches
        if not search_data['zero_results'].empty:
            zero_results = search_data['zero_results'].head(10)
            for _, row in zero_results.iterrows():
                insights['zero_results'].append({
                    'query': row['query'],
                    'count': row['search_count']
                })
        
        # Search conversion rate
        if not search_data['search_conversion'].empty:
            search_conversion_rate = search_data['search_conversion']['search_conversion_rate'].iloc[0]
            insights['search_conversion_rate'] = f"{search_conversion_rate*100:.1f}%"
        
        # Recommendations based on search behavior
        if insights['zero_results']:
            insights['recommendations'].append({
                'area': "Zero-result searches",
                'suggestion': "Add synonyms, correct misspellings, and suggest related products for common zero-result searches"
            })
        
        insights['recommendations'].append({
            'area': "Search functionality",
            'suggestion': "Implement autocomplete, search suggestions, and filters to improve the search experience"
        })
        
        insights['recommendations'].append({
            'area': "Search results page",
            'suggestion': "Optimize search results page with better sorting, filtering, and product information"
        })
        
        # Create visualization for top searches
        if not search_data['top_searches'].empty:
            top_5_searches = search_data['top_searches'].head(5)
            plt.figure(figsize=(10, 6))
            sns.barplot(x='query', y='search_count', data=top_5_searches)
            plt.title('Top 5 Search Queries')
            plt.xlabel('Query')
            plt.ylabel('Search Count')
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.savefig('output/top_searches.png')
        
        return insights
    
    def analyze_page_effectiveness(self):
        """Analyze page effectiveness metrics."""
        page_data = self.db.get_page_effectiveness()
        
        insights = {
            'page_metrics': [],
            'high_exit_pages': [],
            'recommendations': []
        }
        
        # Page metrics
        if not page_data.empty:
            for _, row in page_data.iterrows():
                insights['page_metrics'].append({
                    'page_type': row['page_type'],
                    'views': row['view_count'],
                    'avg_time_spent': f"{row['avg_time_spent']:.1f} seconds",
                    'exit_rate': f"{row['exit_rate']*100:.1f}%"
                })
        
        # High exit pages (exit rate > 40%)
        high_exit_pages = page_data[page_data['exit_rate'] > 0.4]
        for _, row in high_exit_pages.iterrows():
            insights['high_exit_pages'].append({
                'page_type': row['page_type'],
                'exit_rate': f"{row['exit_rate']*100:.1f}%",
                'views': row['view_count']
            })
        
        # Recommendations based on page effectiveness
        for page in insights['high_exit_pages']:
            page_type = page['page_type']
            if page_type == 'product_detail':
                insights['recommendations'].append({
                    'area': "Product detail page optimization",
                    'suggestion': "Enhance product details with better images, clearer descriptions, and more prominent call-to-action buttons"
                })
            elif page_type == 'checkout':
                insights['recommendations'].append({
                    'area': "Checkout optimization",
                    'suggestion': "Simplify the checkout process, add progress indicators, and ensure clear error messages"
                })
            elif page_type == 'cart':
                insights['recommendations'].append({
                    'area': "Cart page optimization",
                    'suggestion': "Add related products, clear shipping information, and streamline the path to checkout"
                })
            elif page_type == 'search_results':
                insights['recommendations'].append({
                    'area': "Search results optimization",
                    'suggestion': "Improve relevance ranking, add filtering options, and enhance product cards"
                })
        
        # Create visualization
        if not page_data.empty:
            plt.figure(figsize=(12, 6))
            sns.barplot(x='page_type', y='exit_rate', data=page_data)
            plt.title('Exit Rate by Page Type')
            plt.xlabel('Page Type')
            plt.ylabel('Exit Rate')
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.savefig('output/exit_rates.png')
        
        return insights
    
    def analyze_product_performance(self):
        """Analyze product performance metrics."""
        product_data = self.db.get_product_performance()
        
        insights = {
            'top_viewed_products': [],
            'top_converting_products': [],
            'underperforming_products': [],
            'recommendations': []
        }
        
        if not product_data.empty:
            # Top viewed products
            top_viewed = product_data.sort_values('view_count', ascending=False).head(5)
            for _, row in top_viewed.iterrows():
                insights['top_viewed_products'].append({
                    'product': row['name'],
                    'category': row['category'],
                    'views': row['view_count'],
                    'view_to_cart_rate': f"{row['view_to_cart_rate']*100:.1f}%" if pd.notna(row['view_to_cart_rate']) else "0.0%"
                })
            
            # Top converting products (view to cart)
            top_converting = product_data.sort_values('view_to_cart_rate', ascending=False).head(5)
            for _, row in top_converting.iterrows():
                if pd.notna(row['view_to_cart_rate']) and row['view_count'] > 10:  # Only include products with sufficient views
                    insights['top_converting_products'].append({
                        'product': row['name'],
                        'category': row['category'],
                        'view_to_cart_rate': f"{row['view_to_cart_rate']*100:.1f}%" if pd.notna(row['view_to_cart_rate']) else "0.0%",
                        'views': row['view_count']
                    })
            
            # Underperforming products (high views, low conversion)
            underperforming = product_data[
                (product_data['view_count'] > product_data['view_count'].quantile(0.75)) & 
                (product_data['view_to_cart_rate'] < product_data['view_to_cart_rate'].quantile(0.25))
            ].head(5)
            
            for _, row in underperforming.iterrows():
                insights['underperforming_products'].append({
                    'product': row['name'],
                    'category': row['category'],
                    'views': row['view_count'],
                    'view_to_cart_rate': f"{row['view_to_cart_rate']*100:.1f}%" if pd.notna(row['view_to_cart_rate']) else "0.0%"
                })
            
            # Recommendations based on product performance
            if insights['underperforming_products']:
                insights['recommendations'].append({
                    'area': "Underperforming products",
                    'suggestion': "Review product pages for high-traffic but low-converting products; improve descriptions, images, and pricing"
                })
            
            insights['recommendations'].append({
                'area': "Product page optimization",
                'suggestion': "Apply successful elements from high-converting product pages to other products"
            })
            
            # Create visualization
            top_products = product_data.sort_values('view_count', ascending=False).head(10)
            plt.figure(figsize=(14, 7))
            bars = plt.bar(top_products['name'], top_products['view_count'])
            plt.title('Top 10 Viewed Products')
            plt.xlabel('Product')
            plt.ylabel('View Count')
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            
            # Add conversion rate as text on top of bars
            for i, bar in enumerate(bars):
                height = bar.get_height()
                view_to_cart = top_products.iloc[i]['view_to_cart_rate']
                if pd.notna(view_to_cart):
                    plt.text(bar.get_x() + bar.get_width()/2., height + 5,
                            f'{view_to_cart*100:.1f}%',
                            ha='center', va='bottom', rotation=0)
            
            plt.savefig('output/product_performance.png')
        
        return insights
    
    def analyze_user_segments(self):
        """Analyze user segments and behavior patterns."""
        # Get user journey data for clustering
        user_data = self.db.execute_query("""
        SELECT 
            u.user_id, 
            u.device_type, 
            u.browser, 
            u.country, 
            u.referrer,
            COUNT(DISTINCT s.session_id) as session_count,
            AVG(pv.time_spent_seconds) as avg_time_spent,
            COUNT(DISTINCT pv.view_id) as page_view_count,
            COUNT(DISTINCT c.click_id) as click_count,
            COUNT(DISTINCT ce.event_id) as cart_event_count,
            COUNT(DISTINCT se.search_id) as search_count,
            SUM(CASE WHEN s.conversion_status = 'completed' THEN 1 ELSE 0 END) as completed_purchases,
            COUNT(DISTINCT s.session_id) as total_sessions,
            CAST(SUM(CASE WHEN s.conversion_status = 'completed' THEN 1 ELSE 0 END) AS FLOAT) / 
                COUNT(DISTINCT s.session_id) as conversion_rate
        FROM 
            users u
        LEFT JOIN 
            sessions s ON u.user_id = s.user_id
        LEFT JOIN 
            page_views pv ON s.session_id = pv.session_id
        LEFT JOIN 
            clicks c ON s.session_id = c.session_id
        LEFT JOIN 
            cart_events ce ON s.session_id = ce.session_id
        LEFT JOIN 
            search_events se ON s.session_id = se.session_id
        GROUP BY 
            u.user_id
        HAVING
            session_count > 0
        """)
        
        insights = {
            'user_segments': [],
            'device_type_analysis': [],
            'referrer_analysis': [],
            'recommendations': []
        }
        
        # Device type analysis
        device_analysis = user_data.groupby('device_type').agg({
            'user_id': 'count',
            'conversion_rate': 'mean'
        }).reset_index()
        
        device_analysis = device_analysis.rename(columns={'user_id': 'user_count'})
        
        for _, row in device_analysis.iterrows():
            insights['device_type_analysis'].append({
                'device_type': row['device_type'],
                'user_count': row['user_count'],
                'avg_conversion_rate': f"{row['conversion_rate']*100:.1f}%" if pd.notna(row['conversion_rate']) else "0.0%"
            })
        
        # Referrer analysis
        referrer_analysis = user_data.groupby('referrer').agg({
            'user_id': 'count',
            'conversion_rate': 'mean'
        }).reset_index()
        
        referrer_analysis = referrer_analysis.rename(columns={'user_id': 'user_count'})
        
        for _, row in referrer_analysis.iterrows():
            insights['referrer_analysis'].append({
                'referrer': row['referrer'],
                'user_count': row['user_count'],
                'avg_conversion_rate': f"{row['conversion_rate']*100:.1f}%" if pd.notna(row['conversion_rate']) else "0.0%"
            })
        
        # Clustering for user segments
        if len(user_data) > 10:  # Only perform clustering with sufficient data
            # Select features for clustering
            features = ['session_count', 'avg_time_spent', 'page_view_count', 'click_count', 
                       'cart_event_count', 'search_count', 'conversion_rate']
            
            # Handle missing values
            X = user_data[features].fillna(0)
            
            # Normalize data
            from sklearn.preprocessing import StandardScaler
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            
            # Determine optimal number of clusters (simplified)
            n_clusters = min(3, len(X) // 20 + 1)  # Simple heuristic, at least 20 users per cluster
            
            # Apply K-means clustering
            kmeans = KMeans(n_clusters=n_clusters, random_state=42)
            user_data['cluster'] = kmeans.fit_predict(X_scaled)
            
            # Analyze clusters
            cluster_analysis = user_data.groupby('cluster').agg({
                'user_id': 'count',
                'session_count': 'mean',
                'avg_time_spent': 'mean',
                'page_view_count': 'mean',
                'cart_event_count': 'mean',
                'search_count': 'mean',
                'conversion_rate': 'mean'
            }).reset_index()
            
            for _, row in cluster_analysis.iterrows():
                cluster_id = int(row['cluster'])
                
                # Determine segment name based on key characteristics
                if row['conversion_rate'] > 0.2:  # High converters
                    segment_name = "High-Value Shoppers"
                elif row['search_count'] > cluster_analysis['search_count'].mean() * 1.5:  # Search-heavy users
                    segment_name = "Research-Oriented Browsers"
                elif row['session_count'] < 2 and row['conversion_rate'] < 0.05:  # One-time visitors with low conversion
                    segment_name = "One-Time Visitors"
                elif row['cart_event_count'] > 0 and row['conversion_rate'] < 0.1:  # Cart abandoners
                    segment_name = "Cart Abandoners"
                else:
                    segment_name = f"Segment {cluster_id + 1}"
                
                insights['user_segments'].append({
                    'segment_name': segment_name,
                    'user_count': int(row['user_id']),
                    'avg_sessions': f"{row['session_count']:.1f}",
                    'avg_page_views': f"{row['page_view_count']:.1f}",
                    'avg_time_spent': f"{row['avg_time_spent']:.1f} seconds",
                    'avg_searches': f"{row['search_count']:.1f}",
                    'avg_cart_events': f"{row['cart_event_count']:.1f}",
                    'conversion_rate': f"{row['conversion_rate']*100:.1f}%" if pd.notna(row['conversion_rate']) else "0.0%"
                })
                
                # Generate segment-specific recommendations
                if segment_name == "High-Value Shoppers":
                    insights['recommendations'].append({
                        'area': "Loyalty program",
                        'suggestion': "Implement a loyalty program to reward and retain high-value customers"
                    })
                elif segment_name == "Research-Oriented Browsers":
                    insights['recommendations'].append({
                        'area': "Enhanced search and filtering",
                        'suggestion': "Improve search capabilities with better filters, comparison tools, and detailed product information"
                    })
                elif segment_name == "One-Time Visitors":
                    insights['recommendations'].append({
                        'area': "First-time visitor experience",
                        'suggestion': "Optimize the landing page experience with clearer value propositions and guided browsing options"
                    })
                elif segment_name == "Cart Abandoners":
                    insights['recommendations'].append({
                        'area': "Cart abandonment recovery",
                        'suggestion': "Implement cart abandonment emails with incentives and simplify the checkout process"
                    })
        
        # Device-specific recommendations
        if insights['device_type_analysis']:
            lowest_device = min(insights['device_type_analysis'], key=lambda x: float(x['avg_conversion_rate'].strip('%')))
            
            if lowest_device['device_type'] == 'mobile':
                insights['recommendations'].append({
                    'area': "Mobile optimization",
                    'suggestion': "Improve mobile user experience with faster page loads, simplified navigation, and mobile-friendly checkout"
                })
            elif lowest_device['device_type'] == 'tablet':
                insights['recommendations'].append({
                    'area': "Tablet optimization",
                    'suggestion': "Optimize layouts and interaction elements for tablet users"
                })
        
        # Referrer-specific recommendations
        if insights['referrer_analysis']:
            # Find top referrer by user count
            top_referrer = max(insights['referrer_analysis'], key=lambda x: x['user_count'])
            
            if top_referrer['referrer'] in ['google', 'bing']:
                insights['recommendations'].append({
                    'area': "Search engine optimization",
                    'suggestion': "Enhance SEO strategy to improve organic search traffic quality and conversion rate"
                })
            elif top_referrer['referrer'] in ['facebook', 'instagram', 'twitter']:
                insights['recommendations'].append({
                    'area': "Social media integration",
                    'suggestion': "Strengthen social proof elements and integrate social sharing to improve conversion from social media traffic"
                })
            elif top_referrer['referrer'] == 'email':
                insights['recommendations'].append({
                    'area': "Email marketing optimization",
                    'suggestion': "Segment email campaigns and personalize landing pages for email traffic"
                })
        
        # Create visualization for user segments
        if 'cluster' in user_data.columns and len(insights['user_segments']) > 0:
            # Plot conversion rate by segment
            segment_df = pd.DataFrame(insights['user_segments'])
            segment_df['conversion_rate_num'] = segment_df['conversion_rate'].str.rstrip('%').astype(float)
            
            plt.figure(figsize=(10, 6))
            sns.barplot(x='segment_name', y='conversion_rate_num', data=segment_df)
            plt.title('Conversion Rate by User Segment')
            plt.xlabel('Segment')
            plt.ylabel('Conversion Rate (%)')
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.savefig('output/user_segments.png')
        
        return insights
    
    def run_comprehensive_analysis(self):
        """Run all analyses and compile a comprehensive report."""
        print("Running comprehensive e-commerce journey analysis...")
        
        analysis_results = {
            'conversion_funnel': self.analyze_conversion_funnel(),
            'cart_abandonment': self.analyze_cart_abandonment(),
            'search_behavior': self.analyze_search_behavior(),
            'page_effectiveness': self.analyze_page_effectiveness(),
            'product_performance': self.analyze_product_performance(),
            'user_segments': self.analyze_user_segments()
        }
        
        # Compile all recommendations
        all_recommendations = []
        for analysis_type, results in analysis_results.items():
            if 'recommendations' in results:
                for rec in results['recommendations']:
                    rec['analysis_type'] = analysis_type
                    all_recommendations.append(rec)
        
        # Deduplicate recommendations
        unique_recommendations = []
        seen_areas = set()
        
        for rec in all_recommendations:
            if rec['area'] not in seen_areas:
                seen_areas.add(rec['area'])
                unique_recommendations.append(rec)
        
        analysis_results['consolidated_recommendations'] = unique_recommendations
        
        print("Analysis complete. Results and visualizations available in the 'output' directory.")
        return analysis_results
