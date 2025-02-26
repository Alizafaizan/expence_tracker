import streamlit as st
import pandas as pd
import datetime
import plotly.express as px
from fpdf2 import FPDF   # For generating PDFs

# Initialize session state for expense tracking
if 'transactions' not in st.session_state:
    st.session_state.transactions = pd.DataFrame(columns=['Date', 'Type', 'Category', 'Amount'])

# App Title with Styling
st.markdown("""
    <h1 style='text-align: center; color: #4CAF50;'>💰 Daily Expense Tracker</h1>
""", unsafe_allow_html=True)

# Sidebar for adding transactions
st.sidebar.header("➕ Add a New Transaction")
date = st.sidebar.date_input("📅 Date", datetime.date.today())
type_ = st.sidebar.radio("🔄 Type", ["Income", "Expense"], horizontal=True)
category = st.sidebar.selectbox("📂 Category", ["Food", "Transport", "Shopping", "Rent", "Salary", "Entertainment", "Healthcare", "Bills", "Other"])
amount = st.sidebar.number_input("💵 Amount", min_value=0.0, format="%.2f")
add_button = st.sidebar.button("✅ Add Transaction")

if add_button and amount > 0:
    new_data = pd.DataFrame([[date, type_, category, amount]], columns=['Date', 'Type', 'Category', 'Amount'])
    st.session_state.transactions = pd.concat([st.session_state.transactions, new_data], ignore_index=True)
    st.sidebar.success("Transaction Added!")

# Display Transactions with Improved UI
st.subheader("📋 Transaction History")
st.dataframe(
    st.session_state.transactions.style.set_properties(**{
        'background-color': '#ffffff',  # White background
        'color': '#000000',  # Black font color
        'border-color': 'black'
    })
)

# Summary Metrics with Cards
st.subheader("📊 Summary")
income = st.session_state.transactions[st.session_state.transactions['Type'] == "Income"]['Amount'].sum()
expense = st.session_state.transactions[st.session_state.transactions['Type'] == "Expense"]['Amount'].sum()
balance = income - expense

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("💰 Total Income", f"${income:.2f}")
with col2:
    st.metric("💸 Total Expense", f"${expense:.2f}")
with col3:
    st.metric("💳 Balance", f"${balance:.2f}", delta=balance)

# Pie Chart of Expenses
st.subheader("📌 Expense Breakdown")
expense_data = st.session_state.transactions[st.session_state.transactions['Type'] == "Expense"]
if not expense_data.empty:
    fig = px.pie(expense_data, names='Category', values='Amount', title='Category-wise Expenses', color_discrete_sequence=px.colors.sequential.RdBu)
    st.plotly_chart(fig)
else:
    st.info("No expenses recorded yet.")

# Monthly Filter
st.subheader("📅 Filter Transactions by Month")
selected_month = st.selectbox("Select Month", options=pd.to_datetime(st.session_state.transactions['Date']).dt.strftime('%Y-%m').unique(), index=0 if not st.session_state.transactions.empty else None)
if selected_month:
    filtered_data = st.session_state.transactions[pd.to_datetime(st.session_state.transactions['Date']).dt.strftime('%Y-%m') == selected_month]
    st.dataframe(filtered_data)

# Export Data Button for CSV
if not st.session_state.transactions.empty:
    csv = st.session_state.transactions.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Transactions (CSV)",
        data=csv,
        file_name="transactions.csv",
        mime="text/csv",
        key='download-csv'
    )

# Export Data Button for PDF
if not st.session_state.transactions.empty:
    def create_pdf(df):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Transaction History", ln=True, align="C")
        pdf.ln(10)
        
        # Add table headers
        pdf.set_font("Arial", size=10, style='B')
        pdf.cell(40, 10, "Date", border=1)
        pdf.cell(40, 10, "Type", border=1)
        pdf.cell(40, 10, "Category", border=1)
        pdf.cell(40, 10, "Amount", border=1)
        pdf.ln()
        
        # Add table rows
        pdf.set_font("Arial", size=10)
        for index, row in df.iterrows():
            pdf.cell(40, 10, str(row['Date']), border=1)
            pdf.cell(40, 10, row['Type'], border=1)
            pdf.cell(40, 10, row['Category'], border=1)
            pdf.cell(40, 10, f"${row['Amount']:.2f}", border=1)
            pdf.ln()
        
        return pdf.output(dest='S').encode('latin1')

    pdf_data = create_pdf(st.session_state.transactions)
    st.download_button(
        label="📥 Download Transactions (PDF)",
        data=pdf_data,
        file_name="transactions.pdf",
        mime="application/pdf",
        key='download-pdf'
    )
    