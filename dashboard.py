import streamlit as st
import pandas as pd
import mysql.connector
import matplotlib.pyplot as plt
import seaborn as sns

#  DATABASE CONNECTION 

def get_connection():
    return mysql.connector.connect(
        host="localhost",       # change if needed 
        user="root",            # your DB username
        password="yourpassword",# your DB password
        database="laptop_rental" # your DB name
    ) 

#  FETCH DATA FROM DATABASE

def fetch_data():
    conn = get_connection()
    query_sales = "SELECT brand, model, quantity, price, sale_date FROM sales;"
    query_purchase = "SELECT brand, model, quantity, cost, purchase_date FROM purchase;"
    query_clients = "SELECT client_id, name, email, phone, rented_model, rent_date FROM clients;"

    sales_df = pd.read_sql(query_sales, conn)
    purchase_df = pd.read_sql(query_purchase, conn)
    clients_df = pd.read_sql(query_clients, conn)
    conn.close()
    return sales_df, purchase_df, clients_df

#  STREAMLIT LAYOUT
st.set_page_config(page_title="Laptop Rental Dashboard", layout="wide")

st.title("Laptop Rental Dashboard")
st.write("Monitor sales, purchases, and client records in real-time.")

# Fetch data from DB
try:
    sales_df, purchase_df, clients_df = fetch_data()
except Exception as e:
    st.error(f"Database connection error: {e}")
    st.stop()

#  METRICS SUMMARY
col1, col2, col3 = st.columns(3)
total_sales = (sales_df["quantity"] * sales_df["price"]).sum()
total_purchase = (purchase_df["quantity"] * purchase_df["cost"]).sum()
total_clients = len(clients_df)

col1.metric("Total Sales (₹)", f"{total_sales:,.2f}")
col2.metric("Total Purchase (₹)", f"{total_purchase:,.2f}")
col3.metric("Total Clients", f"{total_clients}")

#  SALES & PURCHASE GRAPHS 
st.subheader("Sales and Purchase Trends by Brand")

col4, col5 = st.columns(2)

# Sales Graph
with col4:
    sales_summary = sales_df.groupby("brand")["quantity"].sum().reset_index()
    fig, ax = plt.subplots()
    sns.barplot(x="brand", y="quantity", data=sales_summary, palette="Blues_d", ax=ax)
    ax.set_title("Sales by Brand")
    ax.set_xlabel("Brand")
    ax.set_ylabel("Units Sold")
    st.pyplot(fig)

# Purchase Graph
with col5:
    purchase_summary = purchase_df.groupby("brand")["quantity"].sum().reset_index()
    fig2, ax2 = plt.subplots()
    sns.barplot(x="brand", y="quantity", data=purchase_summary, palette="Greens_d", ax=ax2)
    ax2.set_title("Purchases by Brand")
    ax2.set_xlabel("Brand")
    ax2.set_ylabel("Units Purchased")
    st.pyplot(fig2)

#  CLIENT INFORMATION TABLE
st.subheader("Client Information")
st.dataframe(clients_df)


#  SALES vs PURCHASE OVER TIME

st.subheader("Sales vs Purchase Over Time")

sales_df["sale_date"] = pd.to_datetime(sales_df["sale_date"])
purchase_df["purchase_date"] = pd.to_datetime(purchase_df["purchase_date"])

sales_time = sales_df.groupby("sale_date")["quantity"].sum().reset_index()
purchase_time = purchase_df.groupby("purchase_date")["quantity"].sum().reset_index()

fig3, ax3 = plt.subplots(figsize=(10, 5))
sns.lineplot(x="sale_date", y="quantity", data=sales_time, label="Sales", marker="o", ax=ax3)
sns.lineplot(x="purchase_date", y="quantity", data=purchase_time, label="Purchase", marker="o", ax=ax3)
ax3.set_title("Sales vs Purchase Over Time")
ax3.set_xlabel("Date")
ax3.set_ylabel("Quantity")
st.pyplot(fig3)
