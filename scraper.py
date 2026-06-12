import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone
from supabase_client import supabase
import re



def clean_title(title):
    title = re.sub(r"\b\w{3}\s\d{1,2},\s\d{4}", "", title)
    title = re.sub(r"\s+", " ", title).strip()
    return title



def generate_summary(title):
    if not title:
        return ""
    return title[:120] + "..."



def normalize_article(article, fallback_source="unknown"):
    return {
        "title": clean_title(article.get("title", "")),
        "url": article.get("url", ""),
        "source": article.get("source", fallback_source),
        "published_at": article.get(
            "published_at",
            datetime.now(timezone.utc).isoformat()
        ),
        "summary": article.get("summary", "")
    }



def save_articles(articles):
    inserted = 0
    skipped = 0

    for article in articles:
        try:
            existing = (
                supabase.table("articles")
                .select("id")
                .eq("url", article["url"])
                .execute()
            )

            if existing.data:
                skipped += 1
                print(f"⚠️ Skipped duplicate: {article['title']}")
                continue

            supabase.table("articles").insert(article).execute()

            inserted += 1
            print(f"✅ Inserted: {article['title']}")

        except Exception as e:
            print(f"❌ Error inserting article: {e}")

    return inserted, skipped



def scrape_techcrunch():
    url = "https://techcrunch.com"
    headers = {"User-Agent": "Mozilla/5.0"}

    response = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(response.text, "html.parser")

    articles = []
    seen_urls = set()

    links = soup.find_all("a", href=True)

    for link_tag in links:
        title = link_tag.get_text(strip=True)
        link = link_tag["href"]

        if not title or len(title) < 30:
            continue

        if not link.startswith("https://techcrunch.com/"):
            continue

        if "/author/" in link or "/tag/" in link:
            continue

        if "logo" in title.lower():
            continue

        if link in seen_urls:
            continue

        seen_urls.add(link)

        articles.append({
            "title": title,
            "url": link,
            "source": "TechCrunch",
            "published_at": datetime.now(timezone.utc).isoformat(),
            "summary": generate_summary(title)
        })

    cleaned = [normalize_article(a, "TechCrunch") for a in articles]
    inserted, skipped = save_articles(cleaned[:10])

    print("\n=== TechCrunch ===")
    print(f"Inserted: {inserted}")
    print(f"Skipped: {skipped}")
    print(f"Total Found: {len(cleaned)}")

    return cleaned



def scrape_anthropic():
    url = "https://www.anthropic.com/news"
    headers = {"User-Agent": "Mozilla/5.0"}

    response = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(response.text, "html.parser")

    articles = []
    seen_urls = set()

    links = soup.find_all("a", href=True)

    for link_tag in links:
        title = link_tag.get_text(strip=True)
        link = link_tag.get("href", "")

        if not title or len(title) < 20:
            continue

        if not link:
            continue

        if link.startswith("/"):
            link = "https://www.anthropic.com" + link

        if not link.startswith("https://www.anthropic.com"):
            continue

        if link in seen_urls:
            continue

        seen_urls.add(link)

        articles.append({
            "title": title,
            "url": link,
            "source": "Anthropic",
            "published_at": datetime.now(timezone.utc).isoformat(),
            "summary": generate_summary(title)
        })

    cleaned = [normalize_article(a, "Anthropic") for a in articles]
    inserted, skipped = save_articles(cleaned[:10])

    print("\n=== Anthropic ===")
    print(f"Inserted: {inserted}")
    print(f"Skipped: {skipped}")
    print(f"Total Found: {len(cleaned)}")

    return cleaned



def fetch_hackernews():
    articles = []

    try:
        ids_url = "https://hacker-news.firebaseio.com/v0/topstories.json"
        story_ids = requests.get(ids_url, timeout=10).json()

        for story_id in story_ids[:10]:
            item_url = f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
            item = requests.get(item_url, timeout=10).json()

            if not item:
                continue

            title = item.get("title")
            if not title:
                continue

            url = item.get(
                "url",
                f"https://news.ycombinator.com/item?id={story_id}"
            )

            articles.append({
                "title": title,
                "url": url,
                "source": "HackerNews",
                "published_at": datetime.now(timezone.utc).isoformat(),
                "summary": generate_summary(title)
            })

        cleaned = [normalize_article(a, "HackerNews") for a in articles]
        inserted, skipped = save_articles(cleaned)

        print("\n=== Hacker News ===")
        print(f"Inserted: {inserted}")
        print(f"Skipped: {skipped}")
        print(f"Total Found: {len(cleaned)}")

        return cleaned

    except Exception as e:
        print(f"❌ Hacker News Error: {e}")
        return []



def run_all_sources():
    print("\n🚀 Starting Automated Data Collection Pipeline\n")

    print("Collecting from TechCrunch...")
    scrape_techcrunch()

    print("\nCollecting from Anthropic...")
    scrape_anthropic()

    print("\nCollecting from Hacker News...")
    fetch_hackernews()

    print("\n✅ Pipeline Completed")


if __name__ == "__main__":
    run_all_sources()
