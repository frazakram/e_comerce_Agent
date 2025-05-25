import os
import json
import plotly
import plotly.express as px
from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from werkzeug.utils import secure_filename
from database import EcommerceDatabase
from data_analyzer import EcommerceDataAnalyzer
from generate_data import EcommerceDataGenerator
from ecommerce_agent import EcommerceAgent

app = Flask(__name__)
app.secret_key = 'ecommerce-journey-optimization-agent'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'output'

# Ensure directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

# Global variables to store analysis results
analysis_results = None
enhanced_results = None

@app.route('/')
def index():
    # Check if database exists
    db_exists = os.path.exists('ecommerce_data.db')
    return render_template('index.html', db_exists=db_exists)

@app.route('/generate-data', methods=['POST'])
def generate_data():
    try:
        num_users = int(request.form.get('num_users', 200))
        num_sessions = int(request.form.get('num_sessions', 500))
        num_products = int(request.form.get('num_products', 50))
        
        # Generate data
        generator = EcommerceDataGenerator(
            num_users=num_users,
            num_sessions=num_sessions,
            num_products=num_products
        )
        generator.generate_all_data()
        
        flash('Demo data generated successfully!', 'success')
        return redirect(url_for('index'))
    except Exception as e:
        flash(f'Error generating data: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/analyze', methods=['POST'])
def analyze():
    global analysis_results
    
    try:
        # Initialize the analyzer
        db = EcommerceDatabase()
        analyzer = EcommerceDataAnalyzer(db)
        
        # Run analysis
        analysis_results = analyzer.run_comprehensive_analysis()
        
        # Save results as JSON for the UI
        with open(os.path.join(app.config['OUTPUT_FOLDER'], 'analysis_results.json'), 'w') as f:
            # Convert any non-serializable objects to strings
            json.dump(analysis_results, f, default=lambda o: str(o), indent=2)
        
        flash('Analysis completed successfully!', 'success')
        return redirect(url_for('dashboard'))
    except Exception as e:
        flash(f'Error during analysis: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/enhance-with-claude', methods=['POST'])
def enhance_with_claude():
    global analysis_results, enhanced_results
    
    if not analysis_results:
        flash('Please run the analysis first!', 'error')
        return redirect(url_for('index'))
    
    try:
        # Initialize the agent
        agent = EcommerceAgent()
        
        # Enhance with Claude
        enhanced_results = agent.enhance_with_claude(analysis_results)
        
        # Save enhanced results
        with open(os.path.join(app.config['OUTPUT_FOLDER'], 'enhanced_results.json'), 'w') as f:
            json.dump(enhanced_results, f, default=lambda o: str(o), indent=2)
        
        flash('Analysis enhanced with Claude AI!', 'success')
        return redirect(url_for('dashboard'))
    except Exception as e:
        flash(f'Error enhancing with Claude: {str(e)}', 'error')
        return redirect(url_for('dashboard'))

@app.route('/dashboard')
def dashboard():
    global analysis_results, enhanced_results
    
    if not analysis_results:
        # Try to load from file
        try:
            with open(os.path.join(app.config['OUTPUT_FOLDER'], 'analysis_results.json'), 'r') as f:
                analysis_results = json.load(f)
        except:
            flash('No analysis results found. Please run the analysis first.', 'error')
            return redirect(url_for('index'))
    
    # Check if enhanced results exist
    has_claude_insights = False
    claude_insights = ""
    
    if enhanced_results and 'claude_insights' in enhanced_results:
        has_claude_insights = True
        claude_insights = enhanced_results['claude_insights']
    else:
        # Try to load from file
        try:
            with open(os.path.join(app.config['OUTPUT_FOLDER'], 'enhanced_results.json'), 'r') as f:
                enhanced_data = json.load(f)
                if 'claude_insights' in enhanced_data:
                    has_claude_insights = True
                    claude_insights = enhanced_data['claude_insights']
        except:
            pass
    
    # Get visualization data
    graphs = generate_dashboard_graphs(analysis_results)
    
    # Prepare recommendations
    recommendations = []
    if 'consolidated_recommendations' in analysis_results:
        recommendations = analysis_results['consolidated_recommendations']
    
    return render_template(
        'dashboard.html', 
        graphs=graphs,
        recommendations=recommendations,
        has_claude_insights=has_claude_insights,
        claude_insights=claude_insights
    )

@app.route('/report')
def view_report():
    # Check if report exists
    report_path = os.path.join(app.config['OUTPUT_FOLDER'], 'ecommerce_optimization_report.txt')
    if not os.path.exists(report_path):
        flash('Report not found. Please generate a report first.', 'error')
        return redirect(url_for('dashboard'))
    
    # Read report content
    with open(report_path, 'r') as f:
        report_content = f.read()
    
    return render_template('report.html', report_content=report_content)

@app.route('/generate-report', methods=['POST'])
def generate_report():
    global analysis_results, enhanced_results
    
    if not analysis_results:
        flash('Please run the analysis first!', 'error')
        return redirect(url_for('dashboard'))
    
    try:
        # Use the EcommerceAgent to generate the report
        agent = EcommerceAgent()
        
        # Use enhanced results if available, otherwise use regular analysis results
        results_to_use = enhanced_results if enhanced_results else analysis_results
        
        agent.generate_report(results_to_use)
        
        flash('Report generated successfully!', 'success')
        return redirect(url_for('view_report'))
    except Exception as e:
        flash(f'Error generating report: {str(e)}', 'error')
        return redirect(url_for('dashboard'))

def generate_dashboard_graphs(analysis_results):
    graphs = {}
    
    # 1. Conversion Funnel
    if 'conversion_funnel' in analysis_results and 'funnel_stages' in analysis_results['conversion_funnel']:
        funnel_data = analysis_results['conversion_funnel']['funnel_stages']
        if funnel_data:
            stages = []
            drop_rates = []
            
            for stage in funnel_data:
                stage_name = stage.get('stage', 'Unknown')
                stages.append(stage_name)
                
                # Handle drop_off_rate as string or number
                drop_rate = stage.get('drop_off_rate', '0%')
                if isinstance(drop_rate, str) and '%' in drop_rate:
                    drop_rate = float(drop_rate.strip('%'))
                elif isinstance(drop_rate, (int, float)):
                    drop_rate = drop_rate * 100
                drop_rates.append(drop_rate)
            
            fig = px.bar(
                x=stages, 
                y=drop_rates,
                title="Conversion Funnel Drop-off Rates",
                labels={"x": "Funnel Stage", "y": "Drop-off Rate (%)"},
                color=drop_rates,
                color_continuous_scale="Reds",
            )
            graphs['funnel'] = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    # 2. Page Effectiveness
    if 'page_effectiveness' in analysis_results and 'page_metrics' in analysis_results['page_effectiveness']:
        page_data = analysis_results['page_effectiveness']['page_metrics']
        if page_data:
            page_types = []
            exit_rates = []
            view_counts = []
            time_spent = []
            
            for page in page_data:
                page_types.append(page.get('page_type', 'Unknown'))
                
                # Handle exit_rate as string or number
                exit_rate = page.get('exit_rate', '0%')
                if isinstance(exit_rate, str) and '%' in exit_rate:
                    exit_rate = float(exit_rate.strip('%'))
                elif isinstance(exit_rate, (int, float)):
                    exit_rate = exit_rate * 100
                exit_rates.append(exit_rate)
                
                view_counts.append(page.get('views', 0))
                
                # Handle time_spent as string or number
                time = page.get('avg_time_spent', '0 seconds')
                if isinstance(time, str) and 'seconds' in time:
                    time = float(time.split()[0])
                time_spent.append(time)
            
            # Exit Rate chart
            fig1 = px.bar(
                x=page_types, 
                y=exit_rates,
                title="Exit Rate by Page Type",
                labels={"x": "Page Type", "y": "Exit Rate (%)"},
                color=exit_rates,
                color_continuous_scale="Reds",
            )
            graphs['exit_rates'] = json.dumps(fig1, cls=plotly.utils.PlotlyJSONEncoder)
            
            # Time Spent chart
            fig2 = px.bar(
                x=page_types, 
                y=time_spent,
                title="Average Time Spent by Page Type",
                labels={"x": "Page Type", "y": "Time (seconds)"},
                color=time_spent,
                color_continuous_scale="Blues",
            )
            graphs['time_spent'] = json.dumps(fig2, cls=plotly.utils.PlotlyJSONEncoder)
    
    # 3. Device Type Analysis
    if 'user_segments' in analysis_results and 'device_type_analysis' in analysis_results['user_segments']:
        device_data = analysis_results['user_segments']['device_type_analysis']
        if device_data:
            devices = []
            conv_rates = []
            user_counts = []
            
            for device in device_data:
                devices.append(device.get('device_type', 'Unknown'))
                
                # Handle conversion_rate as string or number
                conv_rate = device.get('avg_conversion_rate', '0%')
                if isinstance(conv_rate, str) and '%' in conv_rate:
                    conv_rate = float(conv_rate.strip('%'))
                elif isinstance(conv_rate, (int, float)):
                    conv_rate = conv_rate * 100
                conv_rates.append(conv_rate)
                
                user_counts.append(device.get('user_count', 0))
            
            fig = px.bar(
                x=devices, 
                y=conv_rates,
                title="Conversion Rate by Device Type",
                labels={"x": "Device Type", "y": "Conversion Rate (%)"},
                color=conv_rates,
                color_continuous_scale="Greens",
            )
            graphs['devices'] = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    # 4. Referrer Analysis
    if 'user_segments' in analysis_results and 'referrer_analysis' in analysis_results['user_segments']:
        referrer_data = analysis_results['user_segments']['referrer_analysis']
        if referrer_data:
            referrers = []
            conv_rates = []
            user_counts = []
            
            for ref in referrer_data:
                referrers.append(ref.get('referrer', 'Unknown'))
                
                # Handle conversion_rate as string or number
                conv_rate = ref.get('avg_conversion_rate', '0%')
                if isinstance(conv_rate, str) and '%' in conv_rate:
                    conv_rate = float(conv_rate.strip('%'))
                elif isinstance(conv_rate, (int, float)):
                    conv_rate = conv_rate * 100
                conv_rates.append(conv_rate)
                
                user_counts.append(ref.get('user_count', 0))
            
            fig = px.bar(
                x=referrers, 
                y=conv_rates,
                title="Conversion Rate by Traffic Source",
                labels={"x": "Referrer", "y": "Conversion Rate (%)"},
                color=conv_rates,
                color_continuous_scale="Purples",
            )
            graphs['referrers'] = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    return graphs

if __name__ == '__main__':
    # Development server
    app.run(debug=True, port=5002)
else:
    # Production settings when imported by WSGI server (Gunicorn)
    # Disable debug mode in production
    app.debug = False
