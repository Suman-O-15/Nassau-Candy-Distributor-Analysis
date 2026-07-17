import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Page config
st.set_page_config(page_title="Nassau Candy Distributor", layout="wide")

# Load data
@st.cache_data
@st.cache_data
def load_data():
    # Works both locally and on Streamlit Cloud
    possible_paths = [
        "../data/Nassau_Candy_Distributor.csv",
        "data/Nassau_Candy_Distributor.csv",
        "../data/Nassau Candy Distributor.csv",
        "data/Nassau Candy Distributor.csv",
    ]
    
    df = None
    for path in possible_paths:
        try:
            df = pd.read_csv(path)
            break
        except:
            continue
    
    if df is None:
        st.error("Dataset not found!")
        st.stop()

    df['Order Date'] = pd.to_datetime(df['Order Date'], dayfirst=True)
    df['Ship Date'] = pd.to_datetime(df['Ship Date'], dayfirst=True)
    df['Lead Time'] = (df['Ship Date'] - df['Order Date']).dt.days

    def get_factory(pid):
        if 'CHO-MIL' in pid or 'CHO-NUT' in pid or 'CHO-SCR' in pid:
            return "Lot's O' Nuts"
        elif 'CHO-TRI' in pid or 'CHO-FUD' in pid:
            return "Wicked Choccy's"
        elif pid.startswith('SUG'):
            return "Sugar Shack"
        elif 'GOB' in pid or 'LIC' in pid or 'GUM' in pid:
            return "Secret Factory"
        else:
            return "The Other Factory"

    df['Factory'] = df['Product ID'].apply(get_factory)
    df['Route'] = df['Factory'] + " → " + df['State/Province']
    return df

df = load_data()

# Title
st.title("🍬 Nassau Candy Distributor")
st.subheader("Factory-to-Customer Shipping Route Efficiency Analysis")
st.markdown("---")

# Sidebar filters
st.sidebar.header("🔍 Filters")
regions = st.sidebar.multiselect("Select Region", df['Region'].unique(), default=df['Region'].unique())
ship_modes = st.sidebar.multiselect("Select Ship Mode", df['Ship Mode'].unique(), default=df['Ship Mode'].unique())

filtered_df = df[(df['Region'].isin(regions)) & (df['Ship Mode'].isin(ship_modes))]

# KPI Cards
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Shipments", f"{len(filtered_df):,}")
col2.metric("Avg Lead Time", f"{filtered_df['Lead Time'].mean():.0f} days")
col3.metric("Min Lead Time", f"{filtered_df['Lead Time'].min():.0f} days")
col4.metric("Max Lead Time", f"{filtered_df['Lead Time'].max():.0f} days")

st.markdown("---")

# Charts Row 1
col1, col2 = st.columns(2)

with col1:
    st.subheader("📦 Avg Lead Time by Ship Mode")
    fig, ax = plt.subplots(figsize=(8, 4))
    data = filtered_df.groupby('Ship Mode')['Lead Time'].mean().sort_values()
    ax.barh(data.index, data.values, color='steelblue')
    ax.set_xlabel("Days")
    st.pyplot(fig)

with col2:
    st.subheader("🌍 Avg Lead Time by Region")
    fig, ax = plt.subplots(figsize=(8, 4))
    data = filtered_df.groupby('Region')['Lead Time'].mean().sort_values()
    ax.bar(data.index, data.values, color='coral')
    ax.set_ylabel("Days")
    st.pyplot(fig)

# Charts Row 2
col1, col2 = st.columns(2)

with col1:
    st.subheader("🏭 Top 10 Most Efficient Routes")
    route_stats = filtered_df.groupby('Route')['Lead Time'].mean().sort_values().head(10)
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.barh(route_stats.index, route_stats.values, color='green')
    ax.invert_yaxis()
    ax.set_xlabel("Avg Lead Time (Days)")
    st.pyplot(fig)

with col2:
    st.subheader("⚠️ Top 10 Least Efficient Routes")
    route_stats2 = filtered_df.groupby('Route')['Lead Time'].mean().sort_values(ascending=False).head(10)
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.barh(route_stats2.index, route_stats2.values, color='red')
    ax.invert_yaxis()
    ax.set_xlabel("Avg Lead Time (Days)")
    st.pyplot(fig)

st.markdown("---")
st.subheader("📊 Raw Data")
st.dataframe(filtered_df.head(100))