

!pip install plotly openpyxl

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from google.colab import files
import io

def upload_and_read_data():
    try:
        print("Please upload the Excel file containing all datasets")
        uploaded = files.upload()
        print("File uploaded successfully!")

        excel_file = io.BytesIO(list(uploaded.values())[0])

        print("Reading sheets from the Excel file...")
        user_details = pd.read_excel(excel_file, sheet_name='UserDetails.csv')
        cooking_sessions = pd.read_excel(excel_file, sheet_name='CookingSessions.csv')
        order_details = pd.read_excel(excel_file, sheet_name='OrderDetails.csv')
        print("Sheets read successfully!")

        return user_details, cooking_sessions, order_details

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
user_details, cooking_sessions, order_details = upload_and_read_data()

def clean_data(user_details, cooking_sessions, order_details):
    # Clean UserDetails
    user_details['Registration Date'] = pd.to_datetime(user_details['Registration Date'])
    user_details['Age'] = user_details['Age'].fillna(user_details['Age'].median())
    user_details = user_details.dropna(subset=['User ID'])

    # Clean CookingSessions
    cooking_sessions['Session Start'] = pd.to_datetime(cooking_sessions['Session Start'], errors='coerce')
    cooking_sessions['Session End'] = pd.to_datetime(cooking_sessions['Session End'], errors='coerce')
    cooking_sessions['Duration (mins)'] = cooking_sessions['Duration (mins)'].fillna(0).astype(int)
    cooking_sessions = cooking_sessions.dropna(subset=['User ID', 'Dish Name'])

    # Clean OrderDetails
    order_details['Order Date'] = pd.to_datetime(order_details['Order Date'])
    order_details['Amount (USD)'] = order_details['Amount (USD)'].fillna(0).astype(float)
    order_details = order_details.dropna(subset=['User ID', 'Order ID'])

    print("\nDataset Dimensions:")
    print(f"UserDetails: {user_details.shape}")
    print(f"CookingSessions: {cooking_sessions.shape}")
    print(f"OrderDetails: {order_details.shape}")

    return user_details, cooking_sessions, order_details

user_details, cooking_sessions, order_details = clean_data(user_details, cooking_sessions, order_details)

def merge_data(user_details, cooking_sessions, order_details):
    # Merge cooking sessions with user details
    user_sessions = pd.merge(cooking_sessions, user_details, on="User ID", how="left")

    # Merge order details with cooking sessions
    session_orders = pd.merge(order_details, cooking_sessions, on="Session ID", how="left")

    return user_sessions, session_orders
user_sessions, session_orders = merge_data(user_details, cooking_sessions, order_details)
print("\nMerged Datasets:")
print(f"User Sessions: {user_sessions.shape}")
print(f"Session Orders: {session_orders.shape}")
print("Columns in user_sessions:", user_sessions.columns)
print("Columns in session_orders:", session_orders.columns)

import pandas as pd
import numpy as np
from datetime import datetime

def analyze_restaurant_data(user_sessions, session_orders):
    analysis_results = {}

    # 1. Order Performance Analysis
    print("\n=== Order Performance Analysis ===")

    order_analysis = session_orders.groupby('Order Status').agg({
        'Order ID': 'count',
        'Amount (USD)': ['sum', 'mean', 'median'],
        'Rating': ['mean', 'count']
    }).round(2)

    print("\nOrder Status Summary:")
    print(order_analysis)
    analysis_results['order_analysis'] = order_analysis

    # 2. Customer Analysis
    print("\n=== Customer Analysis ===")

    # Age demographics
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

    print("\nAge Demographics:")
    print(age_analysis)
    analysis_results['age_analysis'] = age_analysis

    # 3. Location Analysis
    print("\n=== Location Analysis ===")

    location_metrics = user_sessions.groupby('Location').agg({
        'User ID': 'nunique',
        'Total Orders': ['sum', 'mean'],
        'Session Rating': 'mean'
    }).round(2)

    print("\nLocation Performance:")
    print(location_metrics.sort_values(('Total Orders', 'sum'), ascending=False).head())
    analysis_results['location_metrics'] = location_metrics

    # 4. Meal Type Performance
    print("\n=== Meal Type Analysis ===")

    meal_analysis = session_orders.groupby('Meal Type_x').agg({
        'Order ID': 'count',
        'Amount (USD)': ['sum', 'mean'],
        'Rating': 'mean'
    }).round(2)

    print("\nMeal Type Performance:")
    print(meal_analysis)
    analysis_results['meal_analysis'] = meal_analysis

    # 5. Time Analysis
    print("\n=== Time Analysis ===")

    time_analysis = session_orders.groupby('Time of Day').agg({
        'Order ID': 'count',
        'Amount (USD)': ['mean', 'sum'],
        'Rating': 'mean'
    }).round(2)

    print("\nTime of Day Performance:")
    print(time_analysis)
    analysis_results['time_analysis'] = time_analysis

    # 6. Session Analysis
    print("\n=== Session Analysis ===")

    session_metrics = {
    'Avg Session Duration': round(user_sessions['Duration (mins)'].mean(), 2), # Changed this line
    'Median Session Duration': round(user_sessions['Duration (mins)'].median(), 2), # Changed this line
    'Avg Session Rating': round(user_sessions['Session Rating'].mean(), 2), # Changed this line
    'Total Unique Users': user_sessions['User ID'].nunique(),
    'Avg Orders per User': round(user_sessions['Total Orders'].mean(), 2) # Changed this line
}

    print("\nSession Metrics:")
    for metric, value in session_metrics.items():
        print(f"{metric}: {value}")
    analysis_results['session_metrics'] = session_metrics

    # 7. Dish Performance
    print("\n=== Dish Analysis ===")

    dish_analysis = session_orders.groupby('Dish Name_x').agg({
        'Order ID': 'count',
        'Amount (USD)': ['sum', 'mean'],
        'Rating': ['mean', 'count']
    }).round(2)

    print("\nTop Dishes by Revenue:")
    print(dish_analysis.sort_values(('Amount (USD)', 'sum'), ascending=False).head())
    analysis_results['dish_analysis'] = dish_analysis

    return analysis_results
results = analyze_restaurant_data(user_sessions, session_orders)

def generate_business_insights(analysis_results):
    """
    Generate actionable business insights from the analysis.
    """
    print("\n=== Key Business Insights ===")

    # 1. Revenue Insights
    meal_analysis = analysis_results['meal_analysis']
    top_meal = meal_analysis.sort_values(('Amount (USD)', 'sum'), ascending=False).index[0]
    print(f"\n1. Revenue Insights:")
    print(f"- Top performing meal type: {top_meal}")
    print(f"  * Total Revenue: ${meal_analysis.loc[top_meal, ('Amount (USD)', 'sum')]:,.2f}")
    print(f"  * Average Order Value: ${meal_analysis.loc[top_meal, ('Amount (USD)', 'mean')]:,.2f}")
    print(f"  * Average Rating: {meal_analysis.loc[top_meal, ('Rating', 'mean')]:,.1f}/5")

    # 2. Customer Demographics
    age_analysis = analysis_results['age_analysis']
    most_active_age = age_analysis['Total Orders'].idxmax()
    print(f"\n2. Customer Demographics:")
    print(f"- Most active age group: {most_active_age}")
    print(f"  * Average orders: {age_analysis.loc[most_active_age, 'Total Orders']:.1f}")
    print(f"  * Average session rating: {age_analysis.loc[most_active_age, 'Session Rating']:.1f}/5")

    # 3. Operational Insights
    time_analysis = analysis_results['time_analysis']
    peak_time = time_analysis['Order ID'].idxmax()
    print(f"\n3. Operational Insights:")
    print(f"- Peak ordering time: {peak_time}")
    avg_order_value = time_analysis.loc[peak_time, ('Amount (USD)', 'mean')]
    avg_order_value = avg_order_value.item() if isinstance(avg_order_value, pd.Series) else avg_order_value
    print(f"  * Average order value: ${avg_order_value:,.2f}")

    avg_rating = time_analysis.loc[peak_time, ('Rating', 'mean')]
    avg_rating = avg_rating.item() if isinstance(avg_rating, pd.Series) else avg_rating
    print(f"  * Average rating: {avg_rating:,.1f}/5")

    # 4. Location Performance
    location_metrics = analysis_results['location_metrics']
    top_location = location_metrics.sort_values(('Total Orders', 'sum'), ascending=False).index[0]
    print(f"\n4. Location Performance:")
    print(f"- Top performing location: {top_location}")
    print(f"  * Total orders: {location_metrics.loc[top_location, ('Total Orders', 'sum')]:,.0f}")
    print(f"  * Average rating: {location_metrics.loc[top_location, ('Session Rating', 'mean')]:,.1f}/5")

    # 5. Session Insights
    session_metrics = analysis_results['session_metrics']
    print(f"\n5. Session Insights:")
    print(f"- Average session duration: {session_metrics['Avg Session Duration']:.1f} minutes")
    print(f"- Average session rating: {session_metrics['Avg Session Rating']:.1f}/5")
    print(f"- Average orders per user: {session_metrics['Avg Orders per User']:.1f}")

    # 6. Key Recommendations
    print("\n6. Key Recommendations:")

    # Menu optimization
    dish_analysis = analysis_results['dish_analysis']
    required_columns = [('Rating', 'mean'), ('Order ID', 'count')]
    if all(col in dish_analysis.columns for col in required_columns):
        low_performing_dishes = dish_analysis[
            (dish_analysis[('Rating', 'mean')] < dish_analysis[('Rating', 'mean')].median()) &
            (dish_analysis[('Order ID', 'count')] < dish_analysis[('Order ID', 'count')].median())
        ]

        print("Menu Optimization:")
        if len(low_performing_dishes) > 0:
            print("- Consider reviewing these low-performing dishes:")
            for dish in low_performing_dishes.index[:3]:
                print(f"  * {dish}")
        else:
            print("- No low-performing dishes were identified.")
    else:
        print("- Dish analysis data is missing required columns. Cannot generate menu recommendations.")

    # Customer engagement
    print("\nCustomer Engagement:")
    print("- Focus marketing on age groups with lower engagement.")
    print("- Consider loyalty programs to increase average orders per user.")
    print("- Investigate locations with lower ratings for improvement opportunities.")
results = analyze_restaurant_data(user_sessions, session_orders)
generate_business_insights(results)

import plotly.express as px
import plotly.graph_objects as go

def plot_order_performance(order_analysis):
    fig = px.bar(order_analysis.reset_index(),
                 x='Order Status',
                 y=('Order ID', 'count'),
                 color='Order Status',
                 title='Order Performance by Status',
                 labels={'y': 'Number of Orders'})
    fig.show()
plot_order_performance(results['order_analysis'])

# Visualization 2: Age Demographics Analysis
def plot_age_demographics(age_analysis):
    fig = px.pie(age_analysis.reset_index(),
                 values='User ID',
                 names='Age_Group',
                 title='User Age Demographics')
    fig.show()
plot_age_demographics(results['age_analysis'])

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

# Call analyze_restaurant_data to get results and assign to 'results'
results = analyze_restaurant_data(user_sessions, session_orders)
# Use 'results' to access the 'dish_analysis' data for plotting
dishes_plot = plot_top_dishes(results['dish_analysis'])
dishes_plot.show()

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
duration_plot = plot_duration_vs_rating(user_sessions)
duration_plot.show()

def visualize_revenue_patterns(analysis_results):
    """
    Create visualizations for revenue-related insights.
    """
    # Revenue by Time and Meal Type
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
    fig.show()

# Call analyze_restaurant_data to get results and assign to 'results'
results = analyze_restaurant_data(user_sessions, session_orders)
# Pass 'results' to visualize_revenue_patterns
visualize_revenue_patterns(results) # This line was changed

def visualize_menu_performance(session_orders):
    """
    Create visualizations for menu performance insights.
    """
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            'Top 5 Dishes by Revenue',
            'Rating Distribution by Meal Type',
            'Average Order Value by Meal Type',
            'Order Volume by Time of Day'
        )
    )

    # Top Dishes
    dish_metrics = session_orders.groupby('Dish Name_x').agg({
        'Amount (USD)': 'sum',
        'Rating': 'mean'
    }).sort_values('Amount (USD)', ascending=False)

    fig.add_trace(
        go.Bar(
            x=dish_metrics.head()['Amount (USD)'],
            y=dish_metrics.head().index,
            orientation='h',
            name='Revenue'
        ),
        row=1, col=1
    )

    # Ratings by Meal Type
    meal_ratings = session_orders.groupby('Meal Type_x')['Rating'].mean()
    fig.add_trace(
        go.Bar(
            x=meal_ratings.index,
            y=meal_ratings.values,
            name='Avg Rating'
        ),
        row=1, col=2
    )

    # Average Order Value
    avg_order = session_orders.groupby('Meal Type_x')['Amount (USD)'].mean()
    fig.add_trace(
        go.Bar(
            x=avg_order.index,
            y=avg_order.values,
            name='Avg Order Value'
        ),
        row=2, col=1
    )

    # Order Volume by Time
    time_orders = session_orders.groupby('Time of Day')['Order ID'].count()
    fig.add_trace(
        go.Scatter(
            x=time_orders.index,
            y=time_orders.values,
            mode='lines+markers',
            name='Order Volume'
        ),
        row=2, col=2
    )

    fig.update_layout(height=1000, title_text="Menu Performance Analysis")
    fig.show()
print("\n4. Menu Performance")
visualize_menu_performance(session_orders)

def visualize_customer_insights(user_sessions):
    """
    Create visualizations for customer behavior insights.
    """
    fig = make_subplots(
        rows=2, cols=2,
        specs=[[{"type": "pie"}, {"type": "bar"}],
               [{"type": "histogram"}, {"type": "xy"}]], # Define subplot types here
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
        go.Pie(
            labels=age_counts.index,
            values=age_counts.values,
            name='Age Groups'
        ),
        row=1, col=1
    )

    # Average Duration by Age
    avg_duration = user_sessions.groupby('Age_Group')['Duration (mins)'].mean()
    fig.add_trace(
        go.Bar(
            x=avg_duration.index,
            y=avg_duration.values,
            name='Avg Duration'
        ),
        row=1, col=2
    )

    # Rating Distribution
    fig.add_trace(
        go.Histogram(
            x=user_sessions['Session Rating'],
            nbinsx=10,
            name='Ratings'
        ),
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
    fig.show()
print("\n2. Customer Insights")
visualize_customer_insights(user_sessions)

def visualize_location_performance(user_sessions):
    """
    Create visualizations for location-based insights.
    """
    # Location Performance Overview
    location_metrics = user_sessions.groupby('Location').agg({
        'User ID': 'nunique',
        'Total Orders': ['sum', 'mean'],
        'Session Rating': 'mean'
    }).round(2)

    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=(
            'Orders and Ratings by Location',
            'Average Orders per User by Location'
        ),
        specs=[[{"secondary_y": True}], [{"secondary_y": False}]]
    )

    # Orders and Ratings
    fig.add_trace(
        go.Bar(
            x=location_metrics.index,
            y=location_metrics[('Total Orders', 'sum')],
            name='Total Orders'
        ),
        row=1, col=1
    )

    fig.add_trace(
        go.Scatter(
            x=location_metrics.index,
            y=location_metrics[('Session Rating', 'mean')],
            name='Avg Rating',
            mode='lines+markers'
        ),
        row=1, col=1,
        secondary_y=True
    )

    # Average Orders per User
    fig.add_trace(
        go.Bar(
            x=location_metrics.index,
            y=location_metrics[('Total Orders', 'mean')],
            name='Avg Orders/User'
        ),
        row=2, col=1
    )

    fig.update_layout(height=800, title_text="Location Performance Analysis")
    fig.show()
print("\n3. Location Performance")
visualize_location_performance(user_sessions)
