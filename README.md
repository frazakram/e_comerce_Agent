# E-commerce User Journey Optimization Agent

This project implements an AI agent using the Claude model to analyze e-commerce user journey data and provide optimization recommendations. The agent identifies patterns in user behavior, detects friction points, and suggests improvements to enhance conversion rates and customer experience.

## Features

- Analysis of user click patterns
- Shopping cart abandonment insights
- Search behavior optimization
- Product page effectiveness evaluation
- Checkout flow optimization
- Personalized recommendations

## Setup

1. Clone this repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up environment variables in `.env` file with your API keys
4. Generate demo data: `python generate_data.py`
5. Run the agent: `python ecommerce_agent.py`

## Components

- `ecommerce_agent.py`: Main agent implementation using Claude API
- `database.py`: Database operations to store and retrieve user journey data
- `generate_data.py`: Script to generate realistic demo data
- `data_analyzer.py`: Analysis modules for pattern detection
- `report_generator.py`: Creates reports with insights and recommendations

## Data Schema

The user journey data includes:
- User clicks and page views
- Product interactions and cart events
- Search queries and results
- Checkout steps and completions/abandonments
- User device and session information

## Example Usage

```bash
# Generate demo data
python generate_data.py

# Run analysis and generate report
python ecommerce_agent.py
```
