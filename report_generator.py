import os
import json
from tabulate import tabulate
from datetime import datetime

class ReportGenerator:
    def __init__(self, analysis_results, output_dir='output'):
        """Initialize with analysis results and output directory."""
        self.analysis_results = analysis_results
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def generate_text_report(self):
        """Generate a text-based report from the analysis results."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        report = []
        
        # Report header
        report.append("E-COMMERCE USER JOURNEY OPTIMIZATION REPORT")
        report.append(f"Generated on: {timestamp}\n")
        
        # Executive Summary
        report.append("EXECUTIVE SUMMARY")
        report.append("-----------------")
        
        # Get cart abandonment rate
        if 'cart_abandonment' in self.analysis_results and 'abandonment_rate' in self.analysis_results['cart_abandonment']:
            abandonment_rate = self.analysis_results['cart_abandonment']['abandonment_rate']
            report.append(f"Cart Abandonment Rate: {abandonment_rate}")
        
        # Get funnel conversion metrics
        if 'conversion_funnel' in self.analysis_results and 'funnel_stages' in self.analysis_results['conversion_funnel']:
            stages = self.analysis_results['conversion_funnel']['funnel_stages']
            if stages:
                # Get first and last stage for overall conversion
                first_stage = stages[0]
                last_stage = stages[-1]
                # Safely access dictionary keys with get() method and provide defaults
                first_step = first_stage.get('current_step', first_stage.get('stage', 'First Step'))
                first_count = first_stage.get('current_count', first_stage.get('users', 0))
                last_step = last_stage.get('next_step', last_stage.get('stage', 'Last Step'))
                last_count = last_stage.get('next_count', last_stage.get('users', 0))
                report.append(f"Overall Funnel Conversion: From {first_step} ({first_count}) to {last_step} ({last_count})")
        
        # Get search conversion rate
        if 'search_behavior' in self.analysis_results and 'search_conversion_rate' in self.analysis_results['search_behavior']:
            search_conv_rate = self.analysis_results['search_behavior']['search_conversion_rate']
            report.append(f"Search to Purchase Conversion Rate: {search_conv_rate}\n")
        
        # Top Recommendations
        report.append("TOP RECOMMENDATIONS")
        report.append("-------------------")
        if 'consolidated_recommendations' in self.analysis_results:
            recommendations = self.analysis_results['consolidated_recommendations']
            for i, rec in enumerate(recommendations[:5], 1):  # Show top 5 recommendations
                report.append(f"{i}. {rec['area']}: {rec['suggestion']}")
        report.append("")
        
        # Detailed Analysis Sections
        
        # 1. Conversion Funnel Analysis
        report.append("1. CONVERSION FUNNEL ANALYSIS")
        report.append("-----------------------------")
        if 'conversion_funnel' in self.analysis_results:
            funnel = self.analysis_results['conversion_funnel']
            
            # Funnel Stages
            if 'funnel_stages' in funnel and funnel['funnel_stages']:
                report.append("Funnel Stage Metrics:")
                funnel_data = []
                headers = ["Stage", "Drop-off Rate", "Users Lost"]
                
                for stage in funnel['funnel_stages']:
                    funnel_data.append([stage['stage'], stage['drop_off_rate'], stage['users_lost']])
                
                report.append(tabulate(funnel_data, headers=headers, tablefmt="pipe"))
                report.append("")
            
            # Critical Drop-offs
            if 'critical_dropoffs' in funnel and funnel['critical_dropoffs']:
                report.append("Critical Drop-off Points:")
                for i, drop in enumerate(funnel['critical_dropoffs'], 1):
                    report.append(f"{i}. {drop['stage']} - {drop['drop_off_rate']} ({drop['users_lost']} users lost)")
                report.append("")
            
            # Recommendations
            if 'recommendations' in funnel and funnel['recommendations']:
                report.append("Funnel Optimization Recommendations:")
                for i, rec in enumerate(funnel['recommendations'], 1):
                    report.append(f"{i}. {rec['area']}: {rec['suggestion']}")
        report.append("")
        
        # 2. Cart Abandonment Analysis
        report.append("2. CART ABANDONMENT ANALYSIS")
        report.append("-----------------------------")
        if 'cart_abandonment' in self.analysis_results:
            cart = self.analysis_results['cart_abandonment']
            
            # Abandonment Rate
            if 'abandonment_rate' in cart:
                report.append(f"Cart Abandonment Rate: {cart['abandonment_rate']}")
            
            # Average Cart Values
            if 'average_cart_values' in cart and cart['average_cart_values']:
                report.append("\nAverage Cart Values:")
                cart_data = []
                headers = ["Status", "Average Value"]
                
                for value in cart['average_cart_values']:
                    cart_data.append([value['status'], value['avg_value']])
                
                report.append(tabulate(cart_data, headers=headers, tablefmt="pipe"))
                report.append("")
            
            # Recommendations
            if 'recommendations' in cart and cart['recommendations']:
                report.append("Cart Abandonment Recommendations:")
                for i, rec in enumerate(cart['recommendations'], 1):
                    report.append(f"{i}. {rec['area']}: {rec['suggestion']}")
        report.append("")
        
        # 3. Search Behavior Analysis
        report.append("3. SEARCH BEHAVIOR ANALYSIS")
        report.append("---------------------------")
        if 'search_behavior' in self.analysis_results:
            search = self.analysis_results['search_behavior']
            
            # Top Searches
            if 'top_searches' in search and search['top_searches']:
                report.append("Top Search Queries:")
                search_data = []
                headers = ["Query", "Count", "Average Results"]
                
                for query in search['top_searches'][:5]:  # Show top 5
                    search_data.append([query['query'], query['count'], query['avg_results']])
                
                report.append(tabulate(search_data, headers=headers, tablefmt="pipe"))
                report.append("")
            
            # Zero Results Searches
            if 'zero_results' in search and search['zero_results']:
                report.append("Top Zero-Result Searches:")
                zero_data = []
                headers = ["Query", "Count"]
                
                for query in search['zero_results'][:5]:  # Show top 5
                    zero_data.append([query['query'], query['count']])
                
                report.append(tabulate(zero_data, headers=headers, tablefmt="pipe"))
                report.append("")
            
            # Search Conversion
            if 'search_conversion_rate' in search:
                report.append(f"Search to Purchase Conversion Rate: {search['search_conversion_rate']}")
                report.append("")
            
            # Recommendations
            if 'recommendations' in search and search['recommendations']:
                report.append("Search Optimization Recommendations:")
                for i, rec in enumerate(search['recommendations'], 1):
                    report.append(f"{i}. {rec['area']}: {rec['suggestion']}")
        report.append("")
        
        # 4. Page Effectiveness Analysis
        report.append("4. PAGE EFFECTIVENESS ANALYSIS")
        report.append("------------------------------")
        if 'page_effectiveness' in self.analysis_results:
            page = self.analysis_results['page_effectiveness']
            
            # Page Metrics
            if 'page_metrics' in page and page['page_metrics']:
                report.append("Page Performance Metrics:")
                page_data = []
                headers = ["Page Type", "Views", "Avg Time Spent", "Exit Rate"]
                
                for p in page['page_metrics']:
                    page_data.append([p['page_type'], p['views'], p['avg_time_spent'], p['exit_rate']])
                
                report.append(tabulate(page_data, headers=headers, tablefmt="pipe"))
                report.append("")
            
            # High Exit Pages
            if 'high_exit_pages' in page and page['high_exit_pages']:
                report.append("High Exit Rate Pages:")
                exit_data = []
                headers = ["Page Type", "Exit Rate", "Views"]
                
                for p in page['high_exit_pages']:
                    exit_data.append([p['page_type'], p['exit_rate'], p['views']])
                
                report.append(tabulate(exit_data, headers=headers, tablefmt="pipe"))
                report.append("")
            
            # Recommendations
            if 'recommendations' in page and page['recommendations']:
                report.append("Page Optimization Recommendations:")
                for i, rec in enumerate(page['recommendations'], 1):
                    report.append(f"{i}. {rec['area']}: {rec['suggestion']}")
        report.append("")
        
        # 5. Product Performance Analysis
        report.append("5. PRODUCT PERFORMANCE ANALYSIS")
        report.append("--------------------------------")
        if 'product_performance' in self.analysis_results:
            product = self.analysis_results['product_performance']
            
            # Top Viewed Products
            if 'top_viewed_products' in product and product['top_viewed_products']:
                report.append("Most Viewed Products:")
                viewed_data = []
                headers = ["Product", "Category", "Views", "View to Cart Rate"]
                
                for p in product['top_viewed_products']:
                    viewed_data.append([p['product'], p['category'], p['views'], p['view_to_cart_rate']])
                
                report.append(tabulate(viewed_data, headers=headers, tablefmt="pipe"))
                report.append("")
            
            # Top Converting Products
            if 'top_converting_products' in product and product['top_converting_products']:
                report.append("Best Converting Products:")
                converting_data = []
                headers = ["Product", "Category", "View to Cart Rate", "Views"]
                
                for p in product['top_converting_products']:
                    converting_data.append([p['product'], p['category'], p['view_to_cart_rate'], p['views']])
                
                report.append(tabulate(converting_data, headers=headers, tablefmt="pipe"))
                report.append("")
            
            # Underperforming Products
            if 'underperforming_products' in product and product['underperforming_products']:
                report.append("Underperforming Products (High Views, Low Conversion):")
                underperforming_data = []
                headers = ["Product", "Category", "Views", "View to Cart Rate"]
                
                for p in product['underperforming_products']:
                    underperforming_data.append([p['product'], p['category'], p['views'], p['view_to_cart_rate']])
                
                report.append(tabulate(underperforming_data, headers=headers, tablefmt="pipe"))
                report.append("")
            
            # Recommendations
            if 'recommendations' in product and product['recommendations']:
                report.append("Product Optimization Recommendations:")
                for i, rec in enumerate(product['recommendations'], 1):
                    report.append(f"{i}. {rec['area']}: {rec['suggestion']}")
        report.append("")
        
        # 6. User Segments Analysis
        report.append("6. USER SEGMENTS ANALYSIS")
        report.append("-------------------------")
        if 'user_segments' in self.analysis_results:
            segments = self.analysis_results['user_segments']
            
            # User Segments
            if 'user_segments' in segments and segments['user_segments']:
                report.append("Identified User Segments:")
                segments_data = []
                headers = ["Segment", "Users", "Avg Sessions", "Avg Page Views", "Conversion Rate"]
                
                for s in segments['user_segments']:
                    segments_data.append([s['segment_name'], s['user_count'], s['avg_sessions'], 
                                         s['avg_page_views'], s['conversion_rate']])
                
                report.append(tabulate(segments_data, headers=headers, tablefmt="pipe"))
                report.append("")
            
            # Device Type Analysis
            if 'device_type_analysis' in segments and segments['device_type_analysis']:
                report.append("Device Type Analysis:")
                device_data = []
                headers = ["Device Type", "User Count", "Avg Conversion Rate"]
                
                for d in segments['device_type_analysis']:
                    device_data.append([d['device_type'], d['user_count'], d['avg_conversion_rate']])
                
                report.append(tabulate(device_data, headers=headers, tablefmt="pipe"))
                report.append("")
            
            # Referrer Analysis
            if 'referrer_analysis' in segments and segments['referrer_analysis']:
                report.append("Traffic Source Analysis:")
                referrer_data = []
                headers = ["Referrer", "User Count", "Avg Conversion Rate"]
                
                for r in segments['referrer_analysis']:
                    referrer_data.append([r['referrer'], r['user_count'], r['avg_conversion_rate']])
                
                report.append(tabulate(referrer_data, headers=headers, tablefmt="pipe"))
                report.append("")
            
            # Recommendations
            if 'recommendations' in segments and segments['recommendations']:
                report.append("User Segment Optimization Recommendations:")
                for i, rec in enumerate(segments['recommendations'], 1):
                    report.append(f"{i}. {rec['area']}: {rec['suggestion']}")
        report.append("")
        
        # Final Conclusion
        report.append("CONCLUSION AND NEXT STEPS")
        report.append("--------------------------")
        report.append("Based on the comprehensive analysis of your e-commerce user journey data, "
                     "we've identified several key areas for optimization that could significantly "
                     "improve your conversion rates and overall customer experience.")
        report.append("\nThe top priority recommendations are:")
        
        # Summarize top recommendations from all areas
        all_recommendations = []
        for key, value in self.analysis_results.items():
            if isinstance(value, dict) and 'recommendations' in value:
                all_recommendations.extend(value['recommendations'])
        
        # Sort by impact (would be better with an actual impact score)
        for i, rec in enumerate(all_recommendations[:5], 1):  # Top 5
            report.append(f"{i}. {rec['area']}: {rec['suggestion']}")
        
        report.append("\nImplementing these recommendations should lead to measurable improvements "
                     "in your key performance indicators, including conversion rate, average order value, "
                     "and customer satisfaction.")
        
        # Save the report to a file
        report_path = os.path.join(self.output_dir, 'ecommerce_optimization_report.txt')
        with open(report_path, 'w') as f:
            f.write('\n'.join(report))
        
        print(f"Text report generated and saved to {report_path}")
        return '\n'.join(report)
    
    def save_analysis_results(self):
        """Save the raw analysis results as JSON."""
        # Convert any non-serializable objects to strings
        def json_serializable(obj):
            if isinstance(obj, (datetime)):
                return obj.isoformat()
            try:
                return obj.tolist()  # For numpy arrays
            except:
                return str(obj)
        
        json_path = os.path.join(self.output_dir, 'analysis_results.json')
        with open(json_path, 'w') as f:
            json.dump(self.analysis_results, f, default=json_serializable, indent=2)
        
        print(f"Analysis results saved to {json_path}")
    
    def generate_report(self):
        """Generate all report formats."""
        self.generate_text_report()
        self.save_analysis_results()
        print("\nReport generation complete. All reports are available in the 'output' directory.")
