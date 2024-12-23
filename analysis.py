import pandas as pd
import numpy as np
from datetime import datetime

def analyze_restaurant_data(user_sessions, session_orders):
    """
    Comprehensive analysis of restaurant session and order data
    """
    analysis_results = {}
    
    # 1. Order Performance Analysis
    order_analysis = session_orders.groupby('Order Status').agg({
        'Order ID': 'count',
        'Amount (USD)': ['sum', 'mean', 'median'],
        'Rating': ['mean', 'count']
    }).round(2)
    
    analysis_results['order_analysis'] = order_analysis
    
    # 2. Customer Analysis
    user_sessions['Age_Group'] = pd.cut(
        user_sessions['Age'],
        bins=[0, 25, 35, 45, 55, 100],
        labels=['18-25', '26-35', '36-45', '46-55', '55+']
    )
    
    age_analysis = user_sessions.groupby('Age_Group').agg({
        'User ID': 'count',
        'Total Orders': 'mean',
        'Session Rating': 'mean',
        'Duration (mins)': 'mean'
    }).round(2)
    
    analysis_results['age_analysis'] = age_analysis
    
    # 3. Location Analysis
    location_metrics = user_sessions.groupby('Location').agg({
        'User ID': 'nunique',
        'Total Orders': ['sum', 'mean'],
        'Session Rating': 'mean'
    }).round(2)
    
    analysis_results['location_metrics'] = location_metrics
    
    # 4. Meal Type Analysis
    meal_analysis = session_orders.groupby('Meal Type_x').agg({
        'Order ID': 'count',
        'Amount (USD)': ['sum', 'mean'],
        'Rating': 'mean'
    }).round(2)
    
    analysis_results['meal_analysis'] = meal_analysis
    
    # 5. Time Analysis
    time_analysis = session_orders.groupby('Time of Day').agg({
        'Order ID': 'count',
        'Amount (USD)': ['mean', 'sum'],
        'Rating': 'mean'
    }).round(2)
    
    analysis_results['time_analysis'] = time_analysis
    
    # 6. Session Analysis
    session_metrics = {
        'Avg Session Duration': round(user_sessions['Duration (mins)'].mean(), 2),
        'Median Session Duration': round(user_sessions['Duration (mins)'].median(), 2),
        'Avg Session Rating': round(user_sessions['Session Rating'].mean(), 2),
        'Total Unique Users': user_sessions['User ID'].nunique(),
        'Avg Orders per User': round(user_sessions['Total Orders'].mean(), 2)
    }
    
    analysis_results['session_metrics'] = session_metrics
    
    # 7. Dish Analysis
    dish_analysis = session_orders.groupby('Dish Name_x').agg({
        'Order ID': 'count',
        'Amount (USD)': ['sum', 'mean'],
        'Rating': ['mean', 'count']
    }).round(2)
    
    analysis_results['dish_analysis'] = dish_analysis
    
    return analysis_results

def generate_business_insights(analysis_results):
    """
    Generate actionable business insights from the analysis.
    """
    insights = []
    
    # 1. Revenue Insights
    meal_analysis = analysis_results['meal_analysis']
    top_meal = meal_analysis.sort_values(('Amount (USD)', 'sum'), ascending=False).index[0]
    insights.append({
        'category': 'Revenue Insights',
        'key_finding': f"Top performing meal type: {top_meal}",
        'metrics': {
            'Total Revenue': f"${meal_analysis.loc[top_meal, ('Amount (USD)', 'sum')]:,.2f}",
            'Average Order Value': f"${meal_analysis.loc[top_meal, ('Amount (USD)', 'mean')]:,.2f}",
            'Average Rating': f"{meal_analysis.loc[top_meal, ('Rating', 'mean')]:,.1f}/5"
        }
    })
    
    # Add other insights following similar structure...
    
    return insights
