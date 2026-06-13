import streamlit as st
import pandas as pd

from supabase_client import supabase
from scraper import (
    scrape_techcrunch,
    scrape_anthropic,
    fetch_hackernews,
    fetch_google_ai_news,
    fetch_reddit_ai_news
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
st.caption("Automated multi-source AI news pipeline (Scraping + APIs + RSS + Social feeds)")


# ----------------------------------
# Fetch Button
# ----------------------------------
if st.button("🔄 Fetch Latest Content"):

    with st.spinner("Collecting content from all sources..."):

        try:
            scrape_techcrunch()
            scrape_anthropic()
            fetch_hackernews()
            fetch_google_ai_news()
            fetch_reddit_ai_news()

        except Exception as e:
            st.error(f"Pipeline error: {e}")

    st.success("Content collected successfully!")
    st.cache_data.clear()
    st.rerun()


# ----------------------------------
# Load Data from Supabase
# ----------------------------------
response = (
    supabase.table("articles")
    .select("*")
    .order("published_at", desc=True)
    .execute()
)

articles = response.data

# ----------------------------------
# Empty State
# ----------------------------------
if not articles:
    st.warning("No articles found in database. Click 'Fetch Latest Content'.")
    st.stop()

df = pd.DataFrame(articles)

# ----------------------------------
# Dashboard Metrics
# ----------------------------------
st.subheader("📊 Dashboard Overview")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("📰 Total Articles", len(df))

with col2:
    st.metric("📚 Sources", df["source"].nunique())

with col3:
    st.metric("🔥 Latest Batch", min(len(df), 10))

with col4:
    st.metric("🌐 Unique URLs", df["url"].nunique())


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
    search = st.text_input("Search Articles")

with col2:
    source_filter = st.selectbox(
        "Filter by Source",
        ["All"] + sorted(df["source"].unique().tolist())
    )


# Apply Filters
filtered_df = df.copy()

if search:
    filtered_df = filtered_df[
        filtered_df["title"].str.contains(search, case=False, na=False)
    ]

if source_filter != "All":
    filtered_df = filtered_df[
        filtered_df["source"] == source_filter
    ]


# ----------------------------------
# Articles Section
# ----------------------------------
st.subheader("📰 Latest Articles")

for _, row in filtered_df.iterrows():

    with st.container(border=True):

        st.markdown(f"## {row['title']}")

        col1, col2 = st.columns([3, 1])

        with col1:
            st.write(f"🏢 **Source:** {row['source']}")

        with col2:
            st.write(f"📅 {row.get('published_at', 'N/A')}")

        st.markdown(
            f"🔗 [View Original Article]({row['url']})"
        )

        st.divider()

        st.markdown("### ✍️ AI Rewritten Article")

        rewritten = row.get("rewritten_article", "")

        if rewritten:
            st.write(rewritten)
        else:
            st.warning("No rewritten article available.")

        with st.expander("📄 View Original Scraped Content"):

            original = row.get("original_content", "")

            if original:
                st.write(original)
            else:
                st.warning("No original content available.")


# ----------------------------------
# Footer
# ----------------------------------
st.divider()

st.caption(
    "Built using Python • BeautifulSoup • RSS • Hacker News API • Reddit • Supabase • Streamlit • HuggingFace LLM"
)
