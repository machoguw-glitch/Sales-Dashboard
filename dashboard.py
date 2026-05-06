import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random

# ------------------------------
# Page configuration
st.set_page_config(page_title="Hardware Shop Sales Dashboard", layout="wide")

# ------------------------------
# Dashboard title
st.title("🔨 Hardware Shop Sales Dashboard")
st.markdown("#### 📍 Kenya | Sales Analytics 2021–2025")
st.markdown("---")

# ------------------------------
# Generate synthetic sales data (2021-2025)
@st.cache_data
def generate_sales_data():
    np.random.seed(42)
    
    # Date range: Jan 2021 to Dec 2025
    dates = pd.date_range(start="2021-01-01", end="2025-12-31", freq="D")
    
    # Product categories
    categories = {
        "Building Materials": ["Cement", "Sand", "Ballast", "Timber", "Iron Sheets"],
        "Hardware Tools": ["Hammers", "Screwdrivers", "Pliers", "Measuring Tape", "Saws"],
        "Electrical": ["Cables", "Switches", "Bulbs", "Conduit Pipes", "Breakers"],
        "Plumbing": ["Pipes", "Taps", "Valves", "Water Tanks", "Fittings"],
        "Paint & Finishes": ["Paint", "Brushes", "Rollers", "Thinner", "Putty"],
        "Steel & Metal": ["Dumuzas", "Nyumba Mabati", "Nails", "Wire Mesh", "Angle Bars"]
    }
    
    # Flatten categories for product list with grouping
    products = []
    product_category_map = {}
    for main_cat, sub_cats in categories.items():
        for sub_cat in sub_cats:
            products.append(sub_cat)
            product_category_map[sub_cat] = main_cat
    
    # Payment methods
    payment_methods = ["Cash", "M-Pesa", "Bank Transfer", "Credit"]
    
    # Generate daily sales data
    data = []
    
    for date in dates:
        year = date.year
        month = date.month
        day_of_week = date.dayofweek
        is_weekend = day_of_week >= 5
        
        # Seasonal factors: Dec peak, Jan low, weekends higher
        if month == 12:
            season_factor = 1.5  # December peak
        elif month in [1, 2]:
            season_factor = 0.7  # Jan-Feb low
        elif month in [6, 7, 8]:
            season_factor = 0.9  # Mid-year slow
        else:
            season_factor = 1.0
        
        # Growth over years (2021 to 2025)
        year_factor = 1 + (year - 2021) * 0.15  # 15% annual growth
        
        for product in products:
            # Dumuzas and Nyumba Mabati special handling (higher volume)
            if product == "Dumuzas":
                base_volume = np.random.uniform(15, 40)
                base_price = 850
            elif product == "Nyumba Mabati":
                base_volume = np.random.uniform(20, 60)
                base_price = 550
            else:
                base_volume = np.random.uniform(1, 15)
                # Price logic per product
                if product == "Cement":
                    base_price = 650
                elif product == "Timber":
                    base_price = 450
                elif product == "Paint":
                    base_price = 1200
                elif product == "Water Tanks":
                    base_price = 3500
                else:
                    base_price = np.random.uniform(100, 2000)
            
            # Volume adjusted by season, year, weekend
            volume = base_volume * season_factor * year_factor
            if is_weekend:
                volume *= 1.2
            
            volume = int(volume)
            
            # Sales amount
            sales_amount = volume * base_price
            
            # Payment method distribution
            if payment_methods[0] == "Cash":
                cash_prob = 0.4 if year <= 2022 else 0.25  # Cash declining over years
            else:
                cash_prob = 0.3
            
            payment = np.random.choice(payment_methods, p=[cash_prob, 0.45, 0.15, 0.05])
            
            data.append({
                "Date": date,
                "Year": year,
                "Month": date.strftime("%b"),
                "Quarter": f"Q{(month-1)//3 + 1}",
                "Product": product,
                "Category": product_category_map[product],
                "Volume_Sold": volume,
                "Unit_Price": round(base_price, 2),
                "Sales_Amount": round(sales_amount, 2),
                "Payment_Method": payment,
                "Payment_Type": "Cash" if payment == "Cash" else "Non-Cash",
                "Is_Weekend": is_weekend
            })
    
    df = pd.DataFrame(data)
    return df

df = generate_sales_data()

# ------------------------------
# Sidebar Filters
st.sidebar.header("🔍 Filter Dashboard")

# Date range filter
min_date = df["Date"].min()
max_date = df["Date"].max()
date_range = st.sidebar.date_input(
    "Select Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

if len(date_range) == 2:
    start_date, end_date = date_range
    filtered_df = df[(df["Date"] >= pd.to_datetime(start_date)) & (df["Date"] <= pd.to_datetime(end_date))]
else:
    filtered_df = df.copy()

# Year filter
years = st.sidebar.multiselect("Select Year(s)", sorted(df["Year"].unique()), default=sorted(df["Year"].unique()))
filtered_df = filtered_df[filtered_df["Year"].isin(years)]

# Category filter
categories = st.sidebar.multiselect("Select Product Category", df["Category"].unique(), default=df["Category"].unique())
filtered_df = filtered_df[filtered_df["Category"].isin(categories)]

# Payment type filter
payment_types = st.sidebar.multiselect("Select Payment Type", ["Cash", "Non-Cash"], default=["Cash", "Non-Cash"])
filtered_df = filtered_df[filtered_df["Payment_Type"].isin(payment_types)]

# ------------------------------
# Key Metrics
st.header("📊 Key Performance Indicators")
col1, col2, col3, col4, col5 = st.columns(5)

total_sales = filtered_df["Sales_Amount"].sum()
total_volume = filtered_df["Volume_Sold"].sum()
avg_daily_sales = filtered_df.groupby("Date")["Sales_Amount"].sum().mean()
cash_sales = filtered_df[filtered_df["Payment_Type"] == "Cash"]["Sales_Amount"].sum()
non_cash_sales = filtered_df[filtered_df["Payment_Type"] == "Non-Cash"]["Sales_Amount"].sum()

with col1:
    st.metric("💰 Total Sales", f"KES {total_sales:,.0f}")
with col2:
    st.metric("📦 Total Volume Sold", f"{total_volume:,.0f} units")
with col3:
    st.metric("📅 Avg Daily Sales", f"KES {avg_daily_sales:,.0f}")
with col4:
    cash_pct = (cash_sales / total_sales * 100) if total_sales > 0 else 0
    st.metric("💵 Cash Sales", f"KES {cash_sales:,.0f}", delta=f"{cash_pct:.1f}%")
with col5:
    non_cash_pct = (non_cash_sales / total_sales * 100) if total_sales > 0 else 0
    st.metric("📱 Non-Cash Sales", f"KES {non_cash_sales:,.0f}", delta=f"{non_cash_pct:.1f}%")

st.markdown("---")

# ------------------------------
# Tab layout
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 Sales Trends", 
    "💳 Cash vs Non-Cash", 
    "🏗️ Product Categories", 
    "🔩 Dumuzas vs Nyumba Mabati",
    "📋 Detailed Data"
])

# ==============================
# TAB 1: Sales Trends
# ==============================
with tab1:
    st.subheader("Sales Trends Over Time")
    
    # Monthly sales trend (line chart)
    monthly_sales = filtered_df.groupby(["Year", "Month"])["Sales_Amount"].sum().reset_index()
    monthly_sales["Date"] = pd.to_datetime(monthly_sales["Year"].astype(str) + "-" + monthly_sales["Month"], format="%Y-%b")
    monthly_sales = monthly_sales.sort_values("Date")
    
    fig1 = px.line(
        monthly_sales,
        x="Date",
        y="Sales_Amount",
        title="Monthly Sales Trend (KES)",
        markers=True,
        line_shape="spline"
    )
    fig1.update_layout(xaxis_title="Date", yaxis_title="Sales Amount (KES)")
    st.plotly_chart(fig1, use_container_width=True)
    
    # Yearly comparison bar chart
    col1, col2 = st.columns(2)
    
    with col1:
        yearly_sales = filtered_df.groupby("Year")["Sales_Amount"].sum().reset_index()
        fig2 = px.bar(
            yearly_sales,
            x="Year",
            y="Sales_Amount",
            title="Yearly Total Sales",
            text_auto=True,
            color="Sales_Amount",
            color_continuous_scale="Blues"
        )
        st.plotly_chart(fig2, use_container_width=True)
    
    with col2:
        yearly_volume = filtered_df.groupby("Year")["Volume_Sold"].sum().reset_index()
        fig3 = px.bar(
            yearly_volume,
            x="Year",
            y="Volume_Sold",
            title="Yearly Volume Sold (Units)",
            text_auto=True,
            color="Volume_Sold",
            color_continuous_scale="Greens"
        )
        st.plotly_chart(fig3, use_container_width=True)
    
    # Seasonal pattern (heatmap by month and year)
    st.subheader("Seasonal Sales Pattern")
    pivot_sales = filtered_df.pivot_table(
        values="Sales_Amount",
        index="Year",
        columns="Month",
        aggfunc="sum",
        fill_value=0
    )
    # Reorder months
    month_order = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    pivot_sales = pivot_sales[[m for m in month_order if m in pivot_sales.columns]]
    
    fig4 = px.imshow(
        pivot_sales,
        text_auto=True,
        aspect="auto",
        title="Sales Heatmap: Year vs Month (KES)",
        labels={"x": "Month", "y": "Year", "color": "Sales (KES)"},
        color_continuous_scale="Viridis"
    )
    st.plotly_chart(fig4, use_container_width=True)

# ==============================
# TAB 2: Cash vs Non-Cash Trends
# ==============================
with tab2:
    st.subheader("Cash vs Non-Cash Sales Analysis")
    
    # Yearly cash vs non-cash
    yearly_payment = filtered_df.groupby(["Year", "Payment_Type"])["Sales_Amount"].sum().reset_index()
    
    fig5 = px.bar(
        yearly_payment,
        x="Year",
        y="Sales_Amount",
        color="Payment_Type",
        title="Cash vs Non-Cash Sales by Year",
        barmode="group",
        color_discrete_map={"Cash": "#2ecc71", "Non-Cash": "#3498db"}
    )
    st.plotly_chart(fig5, use_container_width=True)
    
    # Stacked area chart over time
    monthly_payment = filtered_df.groupby(["Date", "Payment_Type"])["Sales_Amount"].sum().reset_index()
    monthly_payment = monthly_payment.sort_values("Date")
    
    fig6 = px.area(
        monthly_payment,
        x="Date",
        y="Sales_Amount",
        color="Payment_Type",
        title="Payment Method Trends Over Time",
        color_discrete_map={"Cash": "#2ecc71", "Non-Cash": "#3498db"},
        groupnorm=None
    )
    st.plotly_chart(fig6, use_container_width=True)
    
    # Payment method distribution pie chart (latest year)
    col1, col2 = st.columns(2)
    
    with col1:
        latest_year = filtered_df["Year"].max()
        latest_payment = filtered_df[filtered_df["Year"] == latest_year].groupby("Payment_Method")["Sales_Amount"].sum()
        fig7 = px.pie(
            values=latest_payment.values,
            names=latest_payment.index,
            title=f"Payment Method Distribution ({latest_year})",
            hole=0.3,
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        st.plotly_chart(fig7, use_container_width=True)
    
    with col2:
        # Cash vs Non-Cash trend line (percentage over years)
        yearly_payment_pct = filtered_df.groupby(["Year", "Payment_Type"])["Sales_Amount"].sum().unstack()
        yearly_payment_pct["Cash_Pct"] = yearly_payment_pct["Cash"] / (yearly_payment_pct["Cash"] + yearly_payment_pct["Non-Cash"]) * 100
        yearly_payment_pct["Non_Cash_Pct"] = 100 - yearly_payment_pct["Cash_Pct"]
        
        fig8 = px.line(
            yearly_payment_pct.reset_index(),
            x="Year",
            y=["Cash_Pct", "Non_Cash_Pct"],
            title="Payment Method Share Over Time (%)",
            markers=True,
            color_discrete_map={"Cash_Pct": "#2ecc71", "Non_Cash_Pct": "#3498db"}
        )
        st.plotly_chart(fig8, use_container_width=True)
    
    # Insight note
    st.info("💡 **Insight**: Non-cash payments (M-Pesa, Bank Transfer) have been steadily increasing, reflecting Kenya's digital payment adoption trend.")

# ==============================
# TAB 3: Product Categories Analysis
# ==============================
with tab3:
    st.subheader("Product Category Performance")
    
    # Sales by category
    category_sales = filtered_df.groupby("Category")["Sales_Amount"].sum().sort_values(ascending=False).reset_index()
    
    fig9 = px.bar(
        category_sales,
        x="Category",
        y="Sales_Amount",
        title="Total Sales by Product Category",
        text_auto=True,
        color="Sales_Amount",
        color_continuous_scale="Reds"
    )
    st.plotly_chart(fig9, use_container_width=True)
    
    # Top products by sales
    col1, col2 = st.columns(2)
    
    with col1:
        top_products = filtered_df.groupby("Product")["Sales_Amount"].sum().sort_values(ascending=False).head(10).reset_index()
        fig10 = px.bar(
            top_products,
            x="Sales_Amount",
            y="Product",
            title="Top 10 Products by Sales",
            orientation="h",
            color="Sales_Amount",
            color_continuous_scale="Viridis"
        )
        st.plotly_chart(fig10, use_container_width=True)
    
    with col2:
        top_volume = filtered_df.groupby("Product")["Volume_Sold"].sum().sort_values(ascending=False).head(10).reset_index()
        fig11 = px.bar(
            top_volume,
            x="Volume_Sold",
            y="Product",
            title="Top 10 Products by Volume Sold",
            orientation="h",
            color="Volume_Sold",
            color_continuous_scale="Blues"
        )
        st.plotly_chart(fig11, use_container_width=True)
    
    # Category performance over years
    category_yearly = filtered_df.groupby(["Year", "Category"])["Sales_Amount"].sum().reset_index()
    fig12 = px.line(
        category_yearly,
        x="Year",
        y="Sales_Amount",
        color="Category",
        title="Category Sales Trends Over Years",
        markers=True
    )
    st.plotly_chart(fig12, use_container_width=True)
    
    # Treemap of categories and products
    st.subheader("Sales Distribution: Categories & Products")
    treemap_data = filtered_df.groupby(["Category", "Product"])["Sales_Amount"].sum().reset_index()
    fig13 = px.treemap(
        treemap_data,
        path=["Category", "Product"],
        values="Sales_Amount",
        title="Treemap of Sales by Category and Product",
        color="Sales_Amount",
        color_continuous_scale="Blues"
    )
    st.plotly_chart(fig13, use_container_width=True)

# ==============================
# TAB 4: Dumuzas vs Nyumba Mabati
# ==============================
with tab4:
    st.subheader("Dumuzas vs Nyumba Mabati - Volume Analysis")
    
    # Filter only Dumuzas and Nyumba Mabati
    mabati_products = ["Dumuzas", "Nyumba Mabati"]
    mabati_df = filtered_df[filtered_df["Product"].isin(mabati_products)]
    
    if not mabati_df.empty:
        # Volume comparison over time (monthly)
        mabati_monthly = mabati_df.groupby(["Date", "Product"])["Volume_Sold"].sum().reset_index()
        mabati_monthly = mabati_monthly.sort_values("Date")
        
        fig14 = px.line(
            mabati_monthly,
            x="Date",
            y="Volume_Sold",
            color="Product",
            title="Monthly Volume Comparison: Dumuzas vs Nyumba Mabati",
            markers=True,
            color_discrete_map={"Dumuzas": "#e74c3c", "Nyumba Mabati": "#2ecc71"}
        )
        st.plotly_chart(fig14, use_container_width=True)
        
        # Yearly volume comparison
        col1, col2 = st.columns(2)
        
        with col1:
            yearly_volume_comp = mabati_df.groupby(["Year", "Product"])["Volume_Sold"].sum().reset_index()
            fig15 = px.bar(
                yearly_volume_comp,
                x="Year",
                y="Volume_Sold",
                color="Product",
                title="Yearly Volume Comparison",
                barmode="group",
                color_discrete_map={"Dumuzas": "#e74c3c", "Nyumba Mabati": "#2ecc71"},
                text_auto=True
            )
            st.plotly_chart(fig15, use_container_width=True)
        
        with col2:
            # Sales value comparison
            yearly_sales_comp = mabati_df.groupby(["Year", "Product"])["Sales_Amount"].sum().reset_index()
            fig16 = px.bar(
                yearly_sales_comp,
                x="Year",
                y="Sales_Amount",
                color="Product",
                title="Yearly Sales Value Comparison (KES)",
                barmode="group",
                color_discrete_map={"Dumuzas": "#e74c3c", "Nyumba Mabati": "#2ecc71"},
                text_auto=True
            )
            st.plotly_chart(fig16, use_container_width=True)
        
        # Volume ratio: Dumuzas vs Nyumba Mabati
        total_dumuzas = mabati_df[mabati_df["Product"] == "Dumuzas"]["Volume_Sold"].sum()
        total_nyumba = mabati_df[mabati_df["Product"] == "Nyumba Mabati"]["Volume_Sold"].sum()
        ratio = total_dumuzas / total_nyumba if total_nyumba > 0 else 0
        
        st.metric(
            "📊 Volume Ratio (Dumuzas : Nyumba Mabati)",
            f"1 : {ratio:.2f}" if ratio < 1 else f"{ratio:.2f} : 1",
            delta=f"Dumuzas: {total_dumuzas:,} units | Nyumba: {total_nyumba:,} units"
        )
        
        # Monthly comparison heatmap
        st.subheader("Monthly Volume Heatmap Comparison")
        
        # Pivot for Dumuzas
        dumuzas_pivot = mabati_df[mabati_df["Product"] == "Dumuzas"].pivot_table(
            values="Volume_Sold", index="Year", columns="Month", aggfunc="sum", fill_value=0
        )
        dumuzas_pivot = dumuzas_pivot[[m for m in month_order if m in dumuzas_pivot.columns]]
        
        fig17 = px.imshow(
            dumuzas_pivot,
            text_auto=True,
            aspect="auto",
            title="Dumuzas - Monthly Volume Heatmap",
            labels={"x": "Month", "y": "Year", "color": "Volume"},
            color_continuous_scale="Reds"
        )
        st.plotly_chart(fig17, use_container_width=True)
        
        nyumba_pivot = mabati_df[mabati_df["Product"] == "Nyumba Mabati"].pivot_table(
            values="Volume_Sold", index="Year", columns="Month", aggfunc="sum", fill_value=0
        )
        nyumba_pivot = nyumba_pivot[[m for m in month_order if m in nyumba_pivot.columns]]
        
        fig18 = px.imshow(
            nyumba_pivot,
            text_auto=True,
            aspect="auto",
            title="Nyumba Mabati - Monthly Volume Heatmap",
            labels={"x": "Month", "y": "Year", "color": "Volume"},
            color_continuous_scale="Greens"
        )
        st.plotly_chart(fig18, use_container_width=True)
        
        # Insight
        if total_dumuzas > total_nyumba:
            st.success(f"✅ **Dumuzas** is the best-selling iron sheet with {total_dumuzas:,} units sold vs {total_nyumba:,} units of Nyumba Mabati.")
        else:
            st.success(f"✅ **Nyumba Mabati** is the best-selling iron sheet with {total_nyumba:,} units sold vs {total_dumuzas:,} units of Dumuzas.")
    else:
        st.info("No data found for Dumuzas or Nyumba Mabati in the selected filters.")

# ==============================
# TAB 5: Detailed Data & Exports
# ==============================
with tab5:
    st.subheader("Detailed Sales Data")
    
    # Summary statistics
    st.subheader("Summary Statistics")
    summary_stats = filtered_df.groupby("Product").agg({
        "Sales_Amount": ["sum", "mean"],
        "Volume_Sold": ["sum", "mean"],
        "Unit_Price": "mean"
    }).round(2)
    summary_stats.columns = ["Total_Sales_KES", "Avg_Sales_KES", "Total_Volume", "Avg_Volume", "Avg_Unit_Price"]
    summary_stats = summary_stats.sort_values("Total_Sales_KES", ascending=False)
    st.dataframe(summary_stats, use_container_width=True)
    
    # Raw data table
    st.subheader("Raw Transaction Data (Sample)")
    st.dataframe(filtered_df.head(500), use_container_width=True)
    
    # Export options
    st.subheader("📎 Export Data")
    csv = filtered_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download Full Data as CSV",
        data=csv,
        file_name="hardware_sales_data.csv",
        mime="text/csv"
    )
    
    # Excel-style pivot
    st.subheader("Pivot Table: Yearly Sales by Category")
    pivot_yearly = filtered_df.pivot_table(
        values="Sales_Amount",
        index="Category",
        columns="Year",
        aggfunc="sum",
        fill_value=0
    )
    st.dataframe(pivot_yearly, use_container_width=True)

# ------------------------------
# Footer
st.markdown("---")
st.caption("📌 Hardware Shop Sales Dashboard | Data from 2021-2025 | Built with Streamlit")
