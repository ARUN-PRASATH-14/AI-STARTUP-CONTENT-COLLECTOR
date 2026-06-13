import os
import re
import requests
import feedparser

from bs4 import BeautifulSoup
from datetime import datetime, timezone
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

from supabase_client import supabase


# -----------------------------
# Load Environment
# -----------------------------
load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")

hf_client = InferenceClient(
    api_key=HF_TOKEN
)


# -----------------------------
# Clean Title
# -----------------------------
def clean_title(title):
    title = re.sub(r"\b\w{3}\s\d{1,2},\s\d{4}", "", title)
    title = re.sub(r"\s+", " ", title).strip()
    return title


# -----------------------------
# Extract Article Content
# -----------------------------
def extract_article_content(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}

        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        paragraphs = soup.find_all("p")

        content = "\n".join(
            p.get_text(strip=True) for p in paragraphs
        )

        return content[:8000]

    except Exception as e:
        print(f"❌ Content extraction error: {e}")
        return ""


# -----------------------------
# AI Rewrite
# -----------------------------
def rewrite_article(content):
    try:
        if not content:
            return ""

        prompt = f"""
Rewrite this into a professional news article.

Rules:
- No markdown
- No bullet points
- No headings
- Human written style
- Journalistic tone

CONTENT:
{content[:3000]}
"""

        response = hf_client.chat.completions.create(
            model="Qwen/Qwen2.5-72B-Instruct",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=700
        )

        article = response.choices[0].message.content

        return article.replace("#", "").replace("*", "").strip()

    except Exception as e:
        print(f"❌ Rewrite error: {e}")
        return ""


# -----------------------------
# Normalize
# -----------------------------
def normalize_article(article, fallback_source="unknown"):
    return {
        "title": clean_title(article.get("title", "")),
        "url": article.get("url", ""),
        "source": article.get("source", fallback_source),
        "published_at": article.get(
            "published_at",
            datetime.now(timezone.utc).isoformat()
        ),
        "original_content": article.get("original_content", ""),
        "rewritten_article": article.get("rewritten_article", "")
    }


# -----------------------------
# Save to Supabase
# -----------------------------
def save_articles(articles):
    inserted = 0
    skipped = 0

    for article in articles:
        try:
            existing = supabase.table("articles") \
                .select("id") \
                .eq("url", article["url"]) \
                .execute()

            if existing.data:
                skipped += 1
                print(f"⚠️ Skipped duplicate: {article['title']}")
                continue

            supabase.table("articles").insert(article).execute()

            inserted += 1
            print(f"✅ Inserted: {article['title']}")

        except Exception as e:
            print(f"❌ Insert error: {e}")

    return inserted, skipped


# =============================
# TECHCRUNCH
# =============================
def scrape_techcrunch():
    url = "https://techcrunch.com"

    try:
        print("\nCollecting from TechCrunch...")

        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
        soup = BeautifulSoup(response.text, "html.parser")

        articles = []
        seen = set()

        for link in soup.find_all("a", href=True):

            if len(articles) >= 1:
                break

            title = link.get_text(strip=True)
            url = link["href"]

            if not title or len(title) < 30:
                continue

            if not url.startswith("https://techcrunch.com"):
                continue

            if url in seen:
                continue

            seen.add(url)

            print(f"🔍 Processing: {title}")

            content = extract_article_content(url)
            if len(content) < 300:
                continue

            rewritten = rewrite_article(content)

            articles.append({
                "title": title,
                "url": url,
                "source": "TechCrunch",
                "published_at": datetime.now(timezone.utc).isoformat(),
                "original_content": content,
                "rewritten_article": rewritten
            })

        cleaned = [normalize_article(a, "TechCrunch") for a in articles]

        save_articles(cleaned)

        return cleaned

    except Exception as e:
        print(f"❌ TechCrunch error: {e}")
        return []


# =============================
# ANTHROPIC
# =============================
def scrape_anthropic():
    url = "https://www.anthropic.com/news"

    try:
        print("\nCollecting from Anthropic...")

        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
        soup = BeautifulSoup(response.text, "html.parser")

        articles = []
        seen = set()

        for link in soup.find_all("a", href=True):

            if len(articles) >= 1:
                break

            title = link.get_text(strip=True)
            url = link.get("href", "")

            if not title or len(title) < 20:
                continue

            if url.startswith("/"):
                url = "https://www.anthropic.com" + url

            if not url.startswith("https://www.anthropic.com"):
                continue

            if url in seen:
                continue

            seen.add(url)

            print(f"🔍 Processing: {title}")

            content = extract_article_content(url)
            if len(content) < 300:
                continue

            rewritten = rewrite_article(content)

            articles.append({
                "title": title,
                "url": url,
                "source": "Anthropic",
                "published_at": datetime.now(timezone.utc).isoformat(),
                "original_content": content,
                "rewritten_article": rewritten
            })

        cleaned = [normalize_article(a, "Anthropic") for a in articles]

        save_articles(cleaned)

        return cleaned

    except Exception as e:
        print(f"❌ Anthropic error: {e}")
        return []


# =============================
# HACKERNEWS
# =============================
def fetch_hackernews():
    articles = []

    keywords = [
        "ai", "artificial intelligence", "llm",
        "openai", "anthropic", "chatgpt",
        "gemini", "claude", "machine learning"
    ]

    try:
        print("\nCollecting from HackerNews...")

        ids = requests.get(
            "https://hacker-news.firebaseio.com/v0/topstories.json"
        ).json()

        for story_id in ids[:30]:

            item = requests.get(
                f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
            ).json()

            if not item:
                continue

            title = item.get("title", "")

            if not any(k in title.lower() for k in keywords):
                continue

            url = item.get("url", f"https://news.ycombinator.com/item?id={story_id}")

            print(f"🔍 Processing HackerNews: {title}")

            content = extract_article_content(url)
            if len(content) < 300:
                continue

            rewritten = rewrite_article(content)

            articles.append({
                "title": title,
                "url": url,
                "source": "HackerNews",
                "published_at": datetime.now(timezone.utc).isoformat(),
                "original_content": content,
                "rewritten_article": rewritten
            })

            if len(articles) >= 3:
                break

        cleaned = [normalize_article(a, "HackerNews") for a in articles]

        save_articles(cleaned)

        return cleaned

    except Exception as e:
        print(f"❌ HackerNews error: {e}")
        return []


# =============================
# GOOGLE NEWS
# =============================
def fetch_google_ai_news():
    articles = []

    try:
        print("\nCollecting from Google News...")

        rss = "https://news.google.com/rss/search?q=artificial+intelligence&hl=en-IN&gl=IN&ceid=IN:en"
        feed = feedparser.parse(rss)

        for entry in feed.entries[:10]:

            title = entry.title
            url = entry.link

            print(f"🔍 Processing Google News: {title}")

            content = extract_article_content(url)
            if len(content) < 300:
                continue

            rewritten = rewrite_article(content)

            articles.append({
                "title": title,
                "url": url,
                "source": "Google News",
                "published_at": datetime.now(timezone.utc).isoformat(),
                "original_content": content,
                "rewritten_article": rewritten
            })

        cleaned = [normalize_article(a, "Google News") for a in articles]

        save_articles(cleaned)

        return cleaned

    except Exception as e:
        print(f"❌ Google News error: {e}")
        return []


# =============================
# REDDIT AI NEWS
# =============================
def fetch_reddit_ai_news():
    articles = []

    try:
        print("\nCollecting from Reddit...")

        subreddits = [
            "MachineLearning",
            "ArtificialInteligence",
            "singularity",
            "OpenAI"
        ]

        for sub in subreddits:

            feed = feedparser.parse(f"https://www.reddit.com/r/{sub}/.rss")

            for entry in feed.entries[:3]:

                title = entry.title
                url = entry.link

                print(f"🔍 Processing Reddit: {title}")

                content = extract_article_content(url)
                if len(content) < 200:
                    continue

                rewritten = rewrite_article(content)

                articles.append({
                    "title": title,
                    "url": url,
                    "source": f"Reddit {sub}",
                    "published_at": datetime.now(timezone.utc).isoformat(),
                    "original_content": content,
                    "rewritten_article": rewritten
                })

                if len(articles) >= 5:
                    break

        cleaned = [normalize_article(a, "Reddit") for a in articles]

        save_articles(cleaned)

        return cleaned

    except Exception as e:
        print(f"❌ Reddit error: {e}")
        return []


# =============================
# RUN ALL SOURCES
# =============================
def run_all_sources():

    print("\n🚀 Starting Full AI News Pipeline\n")

    scrape_techcrunch()
    scrape_anthropic()
    fetch_hackernews()
    fetch_google_ai_news()
    fetch_reddit_ai_news()

    print("\n✅ Pipeline Completed")


if __name__ == "__main__":
    run_all_sources()
