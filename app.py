import streamlit as st
import pandas as pd

from supabase_client import supabase
from scraper import (
    scrape_techcrunch,
    scrape_anthropic,
    fetch_hackernews
)

# ----------------------------------
# Page Config
# ----------------------------------
st.set_page_config(
    page_title="AI & Startup Content Collector",
    page_icon="📰",
    layout="wide"
)

# ----------------------------------
# Header
# ----------------------------------
st.title("📰 AI & Startup Content Collector")
st.caption(
    "Automated data collection system using Web Scraping + API Integration"
)

# ----------------------------------
# Fetch Button
# ----------------------------------
if st.button("🔄 Fetch Latest Content"):

    with st.spinner("Collecting content from all sources..."):

        scrape_techcrunch()
        scrape_anthropic()
        fetch_hackernews()

    st.success("Content collected successfully!")
    st.rerun()

# ----------------------------------
# Load Data
# ----------------------------------
response = (
    supabase.table("articles")
    .select("*")
    .order("created_at", desc=True)
    .execute()
)

articles = response.data

if not articles:
    st.warning("No articles found in database.")
    st.stop()

df = pd.DataFrame(articles)

# ----------------------------------
# Dashboard Metrics
# ----------------------------------
st.subheader("📊 Dashboard Overview")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "📰 Total Articles",
        len(df)
    )

with col2:
    st.metric(
        "📚 Sources",
        df["source"].nunique()
    )

with col3:
    st.metric(
        "📅 Latest Records",
        min(len(df), 10)
    )

# ----------------------------------
# Source Distribution
# ----------------------------------
st.subheader("📈 Source Distribution")

source_counts = df["source"].value_counts()

st.bar_chart(source_counts)

# ----------------------------------
# Filters
# ----------------------------------
st.subheader("🔍 Search & Filter")

col1, col2 = st.columns(2)

with col1:
    search = st.text_input(
        "Search Articles"
    )

with col2:
    source_filter = st.selectbox(
        "Filter by Source",
        ["All"] + sorted(df["source"].unique().tolist())
    )

# Search Filter
if search:
    df = df[
        df["title"].str.contains(
            search,
            case=False,
            na=False
        )
    ]

# Source Filter
if source_filter != "All":
    df = df[df["source"] == source_filter]

# ----------------------------------
# Articles Section
# ----------------------------------
st.subheader("📰 Latest Articles")

for _, row in df.iterrows():

    with st.container(border=True):

        col1, col2 = st.columns([5, 1])

        with col1:

            st.markdown(
                f"### {row['title']}"
            )

            preview = (
                row["title"][:120] + "..."
                if len(row["title"]) > 120
                else row["title"]
            )

            st.write(f"📝 {preview}")

        with col2:

            st.markdown(
                f"""
                **🏢 Source**

                {row['source']}
                """
            )

        st.markdown(
            f"📅 **Collected At:** {row['created_at']}"
        )

        st.markdown(
            f"🔗 **Article Link:** [Open Article]({row['url']})"
        )

# ----------------------------------
# Footer
# ----------------------------------
st.divider()

st.caption(
    "Built using Python, BeautifulSoup, Hacker News API, Supabase and Streamlit"
)