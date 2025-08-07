

# pip install streamlit pandas
# streamlit run FraudDetectionApp.py

import streamlit as st # pyright: ignore[reportMissingImports]
import pandas as pd # pyright: ignore[reportMissingModuleSource, reportMissingImports]

st.set_page_config(page_title="Fraud Detection Dashboard", layout="wide")
st.title("🕵️‍♂️ Fraud Detection Dashboard")

# Upload file
uploaded_file = st.file_uploader("📂 Upload your fraud_dataset.csv", type=["csv"])

if not uploaded_file:
    st.warning("Please upload your fraud dataset (CSV) to view the dashboard.")
    st.stop()



df = pd.read_csv(uploaded_file, parse_dates=['Timestamp'])
df = df.sort_values(by=['UserID', 'Timestamp'])



    # -------------------- RULES -------------------- #
df['HighAmount'] = df['Amount'] > 10000
df['NightTime'] = df['Timestamp'].dt.hour < 6

    # Previous transaction timestamp
df['PrevTransaction'] = df.groupby('UserID')['Timestamp'].shift(1)
df['TimeDifference'] = (df['Timestamp'] - df['PrevTransaction']).dt.total_seconds() / 60
df['RapidTransactions'] = (df['TimeDifference'] < 10) & df['TimeDifference'].notna()

blacklisted_merchants = ['gambling_site', 'shady_merchant']
df['Blacklisted'] = df['Merchant'].isin(blacklisted_merchants)

df['RoundedAmount'] = df['Amount'] % 1000 == 0

df['PrevIP'] = df.groupby('UserID')['IPAddress'].shift(1)
df['IPChanged'] = (df['IPAddress'] != df['PrevIP']) & df['PrevIP'].notna()

df['PrevDevice'] = df.groupby('UserID')['Device'].shift(1)
df['DeviceChanged'] = (df['Device'] != df['PrevDevice']) & df['PrevDevice'].notna()



    # -------------------- SCORING -------------------- #
flag_columns = [
    'HighAmount', 'NightTime', 'RapidTransactions', 
    'Blacklisted', 'RoundedAmount', 'IPChanged', 'DeviceChanged'
    ]

risk = {
    'HighAmount': 2,
    'NightTime': 1,
    'RapidTransactions': 1,
    'Blacklisted': 2,
    'RoundedAmount': 1,
    'IPChanged': 1,
    'DeviceChanged': 1,
}

for col in flag_columns:
    df[col] = df[col].astype(int) * risk[col]

df['TransactionScore'] = df[flag_columns].sum(axis=1)


    # -------------------- USER LEVEL RISK -------------------- #
user_scores = df.groupby('UserID').agg({
    'TransactionScore': 'sum',
    'TransactionID': 'count'
}).rename(columns={'TransactionID': 'TransactionCount'})

user_scores['AvgScorePerTransaction'] = user_scores['TransactionScore'] / user_scores['TransactionCount']
user_scores['FlaggedUser'] = user_scores['TransactionScore'] >= 5

df = df.merge(user_scores, on='UserID', how='left')


    # -------------------- DASHBOARD -------------------- #
st.subheader("📊 Dashboard Summary")
col1, col2, col3 = st.columns(3)
col1.metric("Total Transactions", len(df))
col2.metric("Flagged Transactions", (df['TransactionScore'] >= 3).sum())
col3.metric("Flagged Users", user_scores['FlaggedUser'].sum())

    # Filter
st.subheader("🔍 Flagged Transactions")
min_score = st.slider("Minimum Transaction Score to show", 0, int(df['TransactionScore'].max()), 3)
filtered = df[df['TransactionScore'] >= min_score]

st.dataframe(
    filtered[[
        'TransactionID', 'UserID', 'Amount', 'Timestamp', 
        'Location', 'Merchant', 'TransactionScore'
    ] + flag_columns], 
    use_container_width=True
)

    # User risk scores
st.subheader("👤 User-Level Risk Scores")
st.dataframe(user_scores.sort_values('TransactionScore', ascending=False), use_container_width=True)

    # Download
st.subheader("📥 Export")
st.download_button(
    label="Download Filtered Transactions as CSV",
    data=filtered.to_csv(index=False),
    file_name="flagged_transactions.csv",
    mime="text/csv"
)
