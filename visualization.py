import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def plot_order_performance(order_analysis):
    """
    Create bar chart showing order performance by status
    """
    fig = px.bar(
        order_analysis.reset_index(), 
        x='Order Status', 
        y=('Order ID', 'count'), 
        color='Order Status',
        title='Order Performance by Status',
        labels={'y': 'Number of Orders'}
    )
    return fig

def plot_age_demographics(age_analysis):
    """
    Create pie chart showing user age demographics
    """
    fig = px.pie(
        age_analysis.reset_index(), 
        values='User ID',
        names='Age_Group',
        title='User Age Demographics'
    )
    return fig

def plot_top_dishes(dish_analysis):
    """
    Create bar chart showing top 5 dishes by revenue
    """
    top_5_dishes = dish_analysis.nlargest(5, ('Amount (USD)', 'sum'))
    fig = px.bar(
        x=top_5_dishes.index,
        y=top_5_dishes[('Amount (USD)', 'sum')],
        title='Top 5 Dishes by Revenue',
        labels={'x': 'Dish Name', 'y': 'Revenue (USD)'}
    )
    fig.update_traces(texttemplate='%{y:.2f}', textposition='auto')
    fig.update_layout(height=500)
    return fig

def plot_duration_vs_rating(user_sessions):
    """
    Create scatter plot showing relationship between session duration and rating
    """
    fig = px.scatter(
        user_sessions,
        x='Duration (mins)',
        y='Session Rating',
        color='Age_Group',
        title='Session Duration vs Rating by Age Group',
        labels={
            'Duration (mins)': 'Session Duration (minutes)',
            'Session Rating': 'Rating',
            'Age_Group': 'Age Group'
        }
    )
    fig.update_layout(height=500)
    return fig

def visualize_revenue_patterns(analysis_results):
    """
    Create subplot with revenue patterns
    """
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('Daily Revenue Pattern', 'Revenue by Meal Type')
    )
    
    # Daily Pattern
    time_data = analysis_results['time_analysis']
    fig.add_trace(
        go.Scatter(
            x=time_data.index,
            y=time_data[('Amount (USD)', 'sum')],
            mode='lines+markers',
            name='Revenue'
        ),
        row=1, col=1
    )
    
    # Meal Type Revenue
    meal_data = analysis_results['meal_analysis']
    fig.add_trace(
        go.Bar(
            x=meal_data.index,
            y=meal_data[('Amount (USD)', 'sum')],
            name='Revenue by Meal',
            text=meal_data[('Amount (USD)', 'sum')].round(2),
            textposition='auto'
        ),
        row=1, col=2
    )
    
    fig.update_layout(height=500, title_text="Revenue Patterns")
    return fig

def visualize_customer_insights(user_sessions):
    """
    Create comprehensive customer insights dashboard
    """
    fig = make_subplots(
        rows=2, cols=2,
        specs=[[{"type": "pie"}, {"type": "bar"}],
               [{"type": "histogram"}, {"type": "xy"}]],
        subplot_titles=(
            'Age Group Distribution',
            'Average Session Duration by Age',
            'Rating Distribution',
            'Session Duration vs Rating'
        )
    )
    
    # Age Distribution
    age_counts = user_sessions['Age_Group'].value_counts()
    fig.add_trace(
        go.Pie(labels=age_counts.index, values=age_counts.values, name='Age Groups'),
        row=1, col=1
    )
    
    # Average Duration by Age
    avg_duration = user_sessions.groupby('Age_Group')['Duration (mins)'].mean()
    fig.add_trace(
        go.Bar(x=avg_duration.index, y=avg_duration.values, name='Avg Duration'),
        row=1, col=2
    )
    
    # Rating Distribution
    fig.add_trace(
        go.Histogram(x=user_sessions['Session Rating'], nbinsx=10, name='Ratings'),
        row=2, col=1
    )
    
    # Duration vs Rating
    fig.add_trace(
        go.Scatter(
            x=user_sessions['Duration (mins)'],
            y=user_sessions['Session Rating'],
            mode='markers',
            name='Duration vs Rating',
            opacity=0.6
        ),
        row=2, col=2
    )
    
    fig.update_layout(height=800, title_text="Customer Behavior Insights")
    return fig
