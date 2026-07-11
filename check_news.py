import feedparser
import json
import os

SEEN_FILE = "seen_articles.json"

def load_seen_articles():
    """Load the list of article links we've already alerted on."""
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE, "r") as f:
            return set(json.load(f))
    return set()

def save_seen_articles(seen):
    """Save the updated list back to disk."""
    with open(SEEN_FILE, "w") as f:
        json.dump(list(seen), f, indent=2)

def get_mercor_articles():
    """Fetch the current Mercor news feed from Google News."""
    url = "https://news.google.com/rss/search?q=Mercor&hl=en-US&gl=US&ceid=US:en"
    feed = feedparser.parse(url)
    return feed.entries

def main():
    seen = load_seen_articles()
    articles = get_mercor_articles()

    new_articles = [a for a in articles if a.link not in seen]

    if not new_articles:
        print("No new articles found.")
        return

    print(f"Found {len(new_articles)} new article(s):")
    for article in new_articles:
        print(f"- {article.title} ({article.link})")
        seen.add(article.link)

    save_seen_articles(seen)

if __name__ == "__main__":
    main()
