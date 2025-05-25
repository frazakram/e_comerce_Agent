import os
import json
import anthropic
import pandas as pd
import numpy as np
from dotenv import load_dotenv
from database import EcommerceDatabase
from data_analyzer import EcommerceDataAnalyzer
from report_generator import ReportGenerator

class EcommerceAgent:
    def __init__(self):
        """Initialize the E-commerce Optimization Agent."""
        # Load environment variables
        load_dotenv()
        
        # Initialize Claude client
        self.client = anthropic.Anthropic(
            api_key=os.environ.get("ANTHROPIC_API_KEY")
        )
        
        # Initialize database connection
        self.db = EcommerceDatabase()
        
        # Initialize data analyzer
        self.analyzer = EcommerceDataAnalyzer(self.db)
    
    def analyze_data(self):
        """Run data analysis on the e-commerce data."""
        print("Running initial data analysis...")
        analysis_results = self.analyzer.run_comprehensive_analysis()
        return analysis_results
    
    def enhance_with_claude(self, analysis_results):
        """Enhance analysis results with Claude's insights."""
        print("\nEnhancing analysis with Claude AI...")
        
        # Prepare a summary of the analysis results for Claude
        analysis_summary = self._prepare_analysis_summary(analysis_results)
        
        # Call Claude for enhanced insights
        message = self.client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=4000,
            temperature=0.2,
            system="You are an expert e-commerce consultant specializing in user journey optimization. "
                   "You're analyzing an e-commerce website's user journey data to provide strategic "
                   "recommendations that will improve conversion rates and customer experience. "
                   "Your insights should be data-driven, specific, actionable, and prioritized by potential impact.",
            messages=[
                {
                    "role": "user",
                    "content": f"""I'm analyzing an e-commerce website's user journey data and need your expert insights.

Here's the summary of our data analysis:

{analysis_summary}

Based on this analysis, please provide:

1. Your interpretation of the most critical issues in the user journey
2. The top 5 highest-impact recommendations for improving conversion rates and user experience
3. For each recommendation, explain why it would be effective and how to implement it
4. Identify any missing data points or analyses that would further enhance our understanding

Focus on actionable insights that directly address the friction points in the user journey."""
                }
            ]
        )
        
        claude_insights = message.content[0].text
        
        # Add Claude's insights to the analysis results
        analysis_results['claude_insights'] = claude_insights
        
        # Extract and structure the recommendations from Claude
        structured_insights = self._extract_claude_recommendations(claude_insights)
        analysis_results['claude_structured_insights'] = structured_insights
        
        return analysis_results
    
    def _prepare_analysis_summary(self, analysis_results):
        """Create a concise summary of analysis results for Claude."""
        summary = []
        
        # Conversion Funnel
        if 'conversion_funnel' in analysis_results:
            funnel = analysis_results['conversion_funnel']
            summary.append("## Conversion Funnel Analysis")
            
            if 'funnel_stages' in funnel and funnel['funnel_stages']:
                summary.append("Funnel stages drop-off rates:")
                for stage in funnel['funnel_stages']:
                    # Check if all required keys exist
                    stage_name = stage.get('stage', 'Unknown stage')
                    drop_rate = stage.get('drop_off_rate', '0%')
                    drop_count = stage.get('drop_off', 0)
                    
                    # Format the string based on whether drop_rate is already a string
                    if isinstance(drop_rate, str):
                        summary.append(f"- {stage_name}: {drop_rate} drop-off ({drop_count} users lost)")
                    else:
                        summary.append(f"- {stage_name}: {drop_rate*100:.1f}% drop-off ({drop_count} users lost)")
            
            if 'critical_dropoffs' in funnel and funnel['critical_dropoffs']:
                summary.append("\nCritical drop-off points:")
                for drop in funnel['critical_dropoffs']:
                    # Check if all required keys exist
                    stage_name = drop.get('stage', 'Unknown stage')
                    drop_rate = drop.get('drop_off_rate', '0%')
                    users_lost = drop.get('users_lost', 0)
                    
                    # Format the string based on whether drop_rate is already a string
                    if isinstance(drop_rate, str):
                        summary.append(f"- {stage_name}: {drop_rate} ({users_lost} users lost)")
                    else:
                        summary.append(f"- {stage_name}: {drop_rate*100:.1f}% ({users_lost} users lost)")
            summary.append("")
        
        # Cart Abandonment
        if 'cart_abandonment' in analysis_results:
            cart = analysis_results['cart_abandonment']
            summary.append("## Cart Abandonment Analysis")
            
            if 'abandonment_rate' in cart:
                summary.append(f"Cart abandonment rate: {cart['abandonment_rate']}")
            
            if 'average_cart_values' in cart and cart['average_cart_values']:
                summary.append("\nAverage cart values:")
                for value in cart['average_cart_values']:
                    summary.append(f"- {value['status']}: {value['avg_value']}")
            summary.append("")
        
        # Search Behavior
        if 'search_behavior' in analysis_results:
            search = analysis_results['search_behavior']
            summary.append("## Search Behavior Analysis")
            
            if 'top_searches' in search and search['top_searches']:
                summary.append("Top search queries:")
                for query in search['top_searches'][:5]:  # Top 5
                    summary.append(f"- {query['query']}: {query['count']} searches, {query['avg_results']} avg results")
            
            if 'zero_results' in search and search['zero_results']:
                summary.append("\nTop zero-result searches:")
                for query in search['zero_results'][:5]:  # Top 5
                    summary.append(f"- {query['query']}: {query['count']} searches")
            
            if 'search_conversion_rate' in search:
                summary.append(f"\nSearch to purchase conversion rate: {search['search_conversion_rate']}")
            summary.append("")
        
        # Page Effectiveness
        if 'page_effectiveness' in analysis_results:
            page = analysis_results['page_effectiveness']
            summary.append("## Page Effectiveness Analysis")
            
            if 'high_exit_pages' in page and page['high_exit_pages']:
                summary.append("High exit rate pages:")
                for p in page['high_exit_pages']:
                    summary.append(f"- {p['page_type']}: {p['exit_rate']} exit rate ({p['views']} views)")
            summary.append("")
        
        # Product Performance
        if 'product_performance' in analysis_results:
            product = analysis_results['product_performance']
            summary.append("## Product Performance Analysis")
            
            if 'top_viewed_products' in product and product['top_viewed_products']:
                summary.append("Most viewed products:")
                for p in product['top_viewed_products'][:3]:  # Top 3
                    summary.append(f"- {p['product']} ({p['category']}): {p['views']} views, {p['view_to_cart_rate']} view-to-cart rate")
            
            if 'underperforming_products' in product and product['underperforming_products']:
                summary.append("\nUnderperforming products (high views, low conversion):")
                for p in product['underperforming_products'][:3]:  # Top 3
                    summary.append(f"- {p['product']} ({p['category']}): {p['views']} views, {p['view_to_cart_rate']} view-to-cart rate")
            summary.append("")
        
        # User Segments
        if 'user_segments' in analysis_results:
            segments = analysis_results['user_segments']
            summary.append("## User Segments Analysis")
            
            if 'user_segments' in segments and segments['user_segments']:
                summary.append("Identified user segments:")
                for s in segments['user_segments']:
                    summary.append(f"- {s['segment_name']}: {s['user_count']} users, {s['conversion_rate']} conversion rate")
            
            if 'device_type_analysis' in segments and segments['device_type_analysis']:
                summary.append("\nDevice type analysis:")
                for d in segments['device_type_analysis']:
                    summary.append(f"- {d['device_type']}: {d['user_count']} users, {d['avg_conversion_rate']} avg conversion rate")
            summary.append("")
        
        return "\n".join(summary)
    
    def _extract_claude_recommendations(self, insights_text):
        """Extract and structure recommendations from Claude's response."""
        # This is a simplified extraction - in a production system,
        # you might use more robust NLP techniques or ask Claude to format its response
        # in a structured way that's easier to parse
        
        structured_insights = {
            'critical_issues': [],
            'top_recommendations': [],
            'missing_data_points': []
        }
        
        # Simple extraction based on section headers
        sections = insights_text.split('\n\n')
        current_section = None
        
        for section in sections:
            if 'critical issues' in section.lower() or 'most critical issues' in section.lower():
                current_section = 'critical_issues'
                continue
            elif 'recommendations' in section.lower() or 'top 5' in section.lower():
                current_section = 'top_recommendations'
                continue
            elif 'missing data' in section.lower():
                current_section = 'missing_data_points'
                continue
            
            if current_section and section.strip():
                # Extract numbered or bulleted items
                lines = section.split('\n')
                for line in lines:
                    line = line.strip()
                    if line and (line.startswith('-') or line.startswith('•') or 
                               (len(line) > 2 and line[0].isdigit() and line[1] in ['.',')'])):
                        structured_insights[current_section].append(line)
        
        return structured_insights
    
    def generate_report(self, analysis_results):
        """Generate a comprehensive report with insights and recommendations."""
        print("\nGenerating comprehensive report...")
        report_gen = ReportGenerator(analysis_results)
        report_gen.generate_report()
    
    def run(self):
        """Run the complete e-commerce optimization agent workflow."""
        print("E-commerce User Journey Optimization Agent")
        print("------------------------------------------\n")
        
        # Step 1: Analyze the data
        analysis_results = self.analyze_data()
        
        # Step 2: Enhance with Claude's insights
        enhanced_results = self.enhance_with_claude(analysis_results)
        
        # Step 3: Generate the report
        self.generate_report(enhanced_results)
        
        print("\nAnalysis complete! Check the 'output' directory for the full report and visualizations.")
        print("Key findings and recommendations have been provided by both quantitative analysis and Claude AI.")


if __name__ == "__main__":
    agent = EcommerceAgent()
    agent.run()
