import streamlit as st
import pandas as pd

st.set_page_config(page_title="Fraud Detection Dashboard", layout="wide")
st.title("🕵️‍♂️ Fraud Detection Dashboard")

# Upload file
uploaded_file = st.file_uploader("📂 Upload your fraud_dataset.csv", type=["csv"])

if not uploaded_file:
    st.warning("Please upload your fraud dataset (CSV) to view the dashboard.")
    st.stop()

if uploaded_file:
    df = pd.read_csv(uploaded_file, parse_dates=['Timestamp'])
    
    # Debug: Show data structure
    st.write("Data Preview:", df.head())
    st.write("Columns in data:", df.columns.tolist())
    
    # -------------------- RULES -------------------- #
    df['HighAmount'] = df['Amount'] > 10000
    df['NightTime'] = df['Timestamp'].dt.hour < 6  # Transactions between midnight-6am

    # Time between transactions
    df['PrevTransaction'] = df.groupby('UserID')['Timestamp'].shift(1)
    df['TimeDifference'] = (df['Timestamp'] - df['PrevTransaction']).dt.total_seconds() / 60
    df['RapidTransactions'] = (df['TimeDifference'] < 10) & df['TimeDifference'].notna()

    # Merchant checks
    blacklisted_merchants = ['gambling_site', 'shady_merchant', 'fraudulent_store']  # Add your actual blacklisted merchants
    df['Blacklisted'] = df['Merchant'].isin(blacklisted_merchants)

    # Amount patterns
    df['RoundedAmount'] = df['Amount'] % 1000 == 0  # Exact thousand amounts
    
    # Device/IP changes
    df['PrevIP'] = df.groupby('UserID')['IPAddress'].shift(1)
    df['IPChanged'] = (df['IPAddress'] != df['PrevIP']) & df['PrevIP'].notna()
    
    df['PrevDevice'] = df.groupby('UserID')['Device'].shift(1)
    df['DeviceChanged'] = (df['Device'] != df['PrevDevice']) & df['PrevDevice'].notna()

    # -------------------- SCORING -------------------- #
    flag_columns = [
        'HighAmount', 'NightTime', 'RapidTransactions', 
        'Blacklisted', 'RoundedAmount', 'IPChanged', 'DeviceChanged'
    ]
    
    # Verify all flag columns exist
    available_flags = [col for col in flag_columns if col in df.columns]
    st.write("Available fraud flags:", available_flags)

    risk_weights = {
        'HighAmount': 2,
        'NightTime': 1,
        'RapidTransactions': 1,
        'Blacklisted': 3,  # Higher weight for blacklisted merchants
        'RoundedAmount': 1,
        'IPChanged': 1,
        'DeviceChanged': 1,
    }

    # Calculate weighted scores
    for col in available_flags:
        df[col+'_Score'] = df[col].astype(int) * risk_weights.get(col, 0)
    
    df['TransactionScore'] = df[[col+'_Score' for col in available_flags]].sum(axis=1)

    # -------------------- USER LEVEL RISK -------------------- #
    user_scores = df.groupby('UserID').agg({
        'TransactionScore': 'sum',
        'TransactionID': 'count'
    }).rename(columns={'TransactionID': 'TransactionCount'})

    user_scores['AvgScorePerTransaction'] = user_scores['TransactionScore'] / user_scores['TransactionCount']
    user_scores['FlaggedUser'] = user_scores['TransactionScore'] >= 5  # Threshold for user flagging

    # -------------------- DASHBOARD -------------------- #
    st.subheader("📊 Dashboard Summary")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Transactions", len(df))
    col2.metric("Flagged Transactions", (df['TransactionScore'] >= 3).sum())  # Transactions scoring ≥3
    col3.metric("Flagged Users", user_scores['FlaggedUser'].sum())

    st.subheader("🔍 Flagged Transactions")
    min_score = st.slider("Minimum Risk Score", 0, int(df['TransactionScore'].max()), 3)
    flagged_df = df[df['TransactionScore'] >= min_score].sort_values('TransactionScore', ascending=False)
    
    st.dataframe(
        flagged_df[['TransactionID', 'UserID', 'Amount', 'Timestamp', 
                   'Location', 'Merchant', 'TransactionScore'] + available_flags],
        use_container_width=True,
        height=400
    )

    st.subheader("👤 High-Risk Users")
    st.dataframe(
        user_scores.sort_values('TransactionScore', ascending=False),
        use_container_width=True
    )

    # Export
    st.subheader("📥 Export Results")
    st.download_button(
        "Download Flagged Transactions",
        flagged_df.to_csv(index=False),
        "flagged_transactions.csv",
        "text/csv"
    )
