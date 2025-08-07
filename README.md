# Mini-Fraud-Detection-App

## 🕵️‍♂️ Fraud Detection Dashboard (Mini Project)

A simple and effective **rule-based fraud detection tool** built using **Python**, **Pandas**, and **Streamlit**.
The app helps identify **potentially fraudulent transactions** and **risky users** by analyzing behavioral patterns in transaction data.

---

## 📌 Features

* ✅ Upload and analyze CSV transaction datasets
* ✅ Apply rule-based fraud detection logic
* ✅ Score transactions based on:

  * High transaction amounts
  * Night-time activity
  * Rapid repeat transactions
  * IP and device changes
  * Blacklisted merchants
  * Rounded amounts (e.g., 1000, 2000)
* ✅ Calculate **per-user risk scores**
* ✅ View flagged transactions and risky users
* ✅ Interactive filters and summary statistics
* ✅ Export flagged data as CSV

---

## 🛠 Technologies Used

* [Python 3](https://www.python.org/)
* [Pandas](https://pandas.pydata.org/)
* [Streamlit](https://streamlit.io/)

---

## 📂 How to Run

1. **Clone this repo or download the files**

2. **Set up a virtual environment (optional but recommended)**:

   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   venv\Scripts\activate     # Windows
   ```


3. **Run the app**:

   ```bash
   streamlit run FraudDetectionApp.py
   ```

4. **Upload your dataset** (e.g., `fraud_dataset.csv`) and explore the dashboard

---

## 📁 Example Dataset

A sample dataset is included (`fraud_dataset.csv`) with:

* 1,000 transactions
* 50 users
* Simulated patterns including anomalies

---

## ✅ Why This Project?

This project was built as a mini use-case to:

* Demonstrate practical fraud detection logic
* Practice real-world data analysis and dashboard building
* Prepare for fraud analytics job interviews

