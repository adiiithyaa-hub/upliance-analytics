import pandas as pd
import numpy as np
from google.colab import files
import io

def upload_and_read_data():
    """
    Upload single Excel file with multiple sheets and read them into pandas DataFrames
    """
    try:
        print("Please upload the Excel file containing all datasets")
        uploaded = files.upload()
        print("File uploaded successfully!")
        
        # Read the uploaded Excel file
        excel_file = io.BytesIO(list(uploaded.values())[0])
        
        # Load the required sheets
        print("Reading sheets from the Excel file...")
        user_details = pd.read_excel(excel_file, sheet_name='UserDetails.csv')
        cooking_sessions = pd.read_excel(excel_file, sheet_name='CookingSessions.csv')
        order_details = pd.read_excel(excel_file, sheet_name='OrderDetails.csv')
        print("Sheets read successfully!")
        
        return user_details, cooking_sessions, order_details

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

def clean_data(user_details, cooking_sessions, order_details):
    """
    Clean and preprocess the datasets
    """
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

def merge_data(user_details, cooking_sessions, order_details):
    """
    Merge datasets to create meaningful relationships
    """
    # Merge cooking sessions with user details
    user_sessions = pd.merge(cooking_sessions, user_details, on="User ID", how="left")
    
    # Merge order details with cooking sessions
    session_orders = pd.merge(order_details, cooking_sessions, on="Session ID", how="left")
    
    return user_sessions, session_orders
