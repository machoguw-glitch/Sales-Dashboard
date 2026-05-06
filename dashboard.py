import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime

# Page configuration
st.set_page_config(page_title="Hardware Shop Sales Dashboard", layout="wide")

# Dashboard title
st.title("🔨 Hardware Shop Sales Dashboard")
st.markdown("#### 📍 Kenya | Sales Analytics 2021–2025")
st.markdown("---")

# Generate synthetic sales data
def generate_sales_data():
    np.random.seed(42)
    
    dates = pd.date_range(start="2021-01-01", end="2025-12-31", freq="D")
    
    products = {
        "Cement": 650,
        "Dumuzas": 850,
        "Nyumba Mabati": 550,
        "Timber": 450,
        "Paint": 1200,
        "Nails": 150,
        "Pipes": 300,
        "Taps": 500,
        "Cables": 200,
        "Switches": 150
    }
    
    data = []
    
    for date in dates:
        year = date.year
        month = date.month
        
        # Seasonal factor
        if month == 12:
            season = 1.5
        elif month in [1, 2]:
            season = 0.7
        else:
            season = 1.0
        
        # Yearly growth
        growth = 1 + (year - 2021) * 0.15
        
        for product, price in products.items():
            # Base volume
            if product == "Dumuzas":
                volume = np.random.uniform(15, 40)
            elif product == "Nyumba Mabati":
                volume = np.random.uniform(20, 60)
            else:
                volume = np.random.uniform(5, 25)
            
            # Apply factors
            volume = int(volume * season * growth)
            
            # Random cash or non-cash
            if year <= 2022:
                is_cash = np.random.choice([True, False], p=[0.5, 0.5])
            else:
                is_cash = np.random.choice([True, False], p=[0.3, 0.7])
            
            sales = volume * price
            
            data.append({
                "Date": date,
                "Year": year,
                "Month": date.strftime("%b"),
                "Product": product,
                "Category": self.get_category(product),
                "Volume": volume,
                "Price": price,
                "Sales": round(sales, 2),
                "Payment_Type": "Cash" if is_cash else "Non-Cash"
            })
    
    df = pd.DataFrame(data)
    return df

def get_category(product):
    categories = {
        "Cement": "Building",
        "Dumuzas": "Roofing",
        "Nyumba Mabati": "Roofing",
        "Timber": "Building",
        "Paint": "Finishing",
        "Nails": "Hardware",
        "Pipes": "Plumbing",
        "Taps": "Plumbing",
        "Cables": "Electrical",
        "Switches": "Electrical"
    }
    return categories.get(product, "Other")

# Load data
df = generate_sales_data()

# Sidebar filters
st.sidebar.header("🔍 Filters")

years = st.sidebar.multiselect("Select Years", sorted(df["Year"].unique()), default=sorted(df["Year"].unique()))
df = df[df["Year"].isin(years)]

products = st.sidebar.multiselect("Select Products", df["Product"].unique(), default=df["Product"].unique())
df = df[df["Product"].isin(products)]

# Key Metrics
st.header("📊 Key Metrics")
col1, col2, col3, col4 = st.columns(4)

total_sales = df["Sales"].sum()
total_volume = df["Volume"].sum()
cash_sales = df[df["Payment_Type"] == "Cash"]["Sales"].sum()
non_cash_sales = df[df["Payment_Type"] == "Non-Cash"]["Sales"].sum()

with col1:
    st.metric("💰 Total Sales", f"KES {total_sales:,.0f}")
with col2:
    st.metric("📦 Total Volume", f"{total_volume:,} units")
with col3:
    st.metric("💵 Cash Sales", f"KES {cash_sales:,.0f}")
with col4:
    st.metric("📱 Non-Cash Sales", f"KES {non_cash_sales:,.0f}")

st.markdown("---")

# Tab layout
tab1, tab2, tab3, tab4 = st.tabs(["📈 Sales Trends", "💳 Cash vs Non-Cash", "🏗️ Products", "🔩 Dumuzas vs Nyumba Mabati"])

# Tab 1: Sales Trends
with tab1:
    st.subheader("Monthly Sales Trend")
    monthly = df.groupby(["Year", "Month"])["Sales"].sum().reset_index()
    fig1 = px.line(monthly, x="Month", y="Sales", color="Year", title="Monthly Sales by Year", markers=True)
    st.plotly_chart(fig1, use_container_width=True)
    
    st.subheader("Yearly Sales")
    yearly = df.groupby("Year")["Sales"].sum().reset_index()
    fig2 = px.bar(yearly, x="Year", y="Sales", title="Total Sales per Year", text_auto=True)
    st.plotly_chart(fig2, use_container_width=True)

# Tab 2: Cash vs Non-Cash
with tab2:
    st.subheader("Payment Method Trends")
    payment_year = df.groupby(["Year", "Payment_Type"])["Sales"].sum().reset_index()
    fig3 = px.bar(payment_year, x="Year", y="Sales", color="Payment_Type", title="Cash vs Non-Cash by Year", barmode="group")
    st.plotly_chart(fig3, use_container_width=True)
    
    # Payment share pie
    latest_year = df["Year"].max()
    latest_payment = df[df["Year"] == latest_year].groupby("Payment_Type")["Sales"].sum()
    fig4 = px.pie(values=latest_payment.values, names=latest_payment.index, title=f"Payment Share ({latest_year})", hole=0.3)
    st.plotly_chart(fig4, use_container_width=True)

# Tab 3: Products
with tab3:
    st.subheader("Sales by Product")
    product_sales = df.groupby("Product")["Sales"].sum().sort_values(ascending=False).reset_index()
    fig5 = px.bar(product_sales, x="Product", y="Sales", title="Total Sales per Product", color="Sales")
    st.plotly_chart(fig5, use_container_width=True)
    
    st.subheader("Category Performance")
    df["Category"] = df["Product"].apply(get_category)
    category_sales = df.groupby("Category")["Sales"].sum().reset_index()
    fig6 = px.pie(category_sales, values="Sales", names="Category", title="Sales by Category")
    st.plotly_chart(fig6, use_container_width=True)

# Tab 4: Dumuzas vs Nyumba Mabati
with tab4:
    st.subheader("Volume Comparison: Dumuzas vs Nyumba Mabati")
    
    mabati_df = df[df["Product"].isin(["Dumuzas", "Nyumba Mabati"])]
    yearly_mabati = mabati_df.groupby(["Year", "Product"])["Volume"].sum().reset_index()
    
    fig7 = px.bar(yearly_mabati, x="Year", y="Volume", color="Product", title="Yearly Volume Comparison", barmode="group")
    st.plotly_chart(fig7, use_container_width=True)
    
    # Total comparison
    dumuzas_vol = mabati_df[mabati_df["Product"] == "Dumuzas"]["Volume"].sum()
    nyumba_vol = mabati_df[mabati_df["Product"] == "Nyumba Mabati"]["Volume"].sum()
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Dumuzas Total Volume", f"{dumuzas_vol:,} units")
    with col2:
        st.metric("Nyumba Mabati Total Volume", f"{nyumba_vol:,} units")
    
    if dumuzas_vol > nyumba_vol:
        st.success(f"✅ Dumuzas is selling better with {dumuzas_vol - nyumba_vol:,} more units than Nyumba Mabati")
    else:
        st.success(f"✅ Nyumba Mabati is selling better with {nyumba_vol - dumuzas_vol:,} more units than Dumuzas")

# Data download
st.markdown("---")
st.subheader("📎 Download Data")
csv = df.to_csv(index=False).encode("utf-8")
st.download_button("Download as CSV", csv, "hardware_sales.csv", "text/csv")

# Footer
st.caption("Hardware Shop Dashboard | Data 2021-2025")



