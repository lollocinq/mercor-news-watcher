import feedparser
import json
import os
import smtplib
from email.mime.text import MIMEText

SEEN_FILE = "seen_articles.json"

def load_seen_articles():
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE, "r") as f:
            return set(json.load(f))
    return set()

def save_seen_articles(seen):
    with open(SEEN_FILE, "w") as f:
        json.dump(list(seen), f, indent=2)

def get_mercor_articles():
    url = "https://news.google.com/rss/search?q=Mercor&hl=en-US&gl=US&ceid=US:en"
    feed = feedparser.parse(url)
    return feed.entries

def send_email(new_articles):
    gmail_address = os.environ["GMAIL_ADDRESS"]
    gmail_password = os.environ["GMAIL_APP_PASSWORD"]

    body_lines = [f"- {a.title}\n  {a.link}" for a in new_articles]
    body = "New Mercor news:\n\n" + "\n\n".join(body_lines)

    msg = MIMEText(body)
    msg["Subject"] = f"Mercor News Alert: {len(new_articles)} new article(s)"
    msg["From"] = gmail_address
    msg["To"] = gmail_address

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(gmail_address, gmail_password)
        server.send_message(msg)

def main():
    seen = load_seen_articles()
    articles = get_mercor_articles()

    new_articles = [a for a in articles if a.link not in seen]

    if not new_articles:
        print("No new articles found.")
        return

    print(f"Found {len(new_articles)} new article(s). Sending email...")
    send_email(new_articles)

    for article in new_articles:
        seen.add(article.link)

    save_seen_articles(seen)
    print("Done.")

if __name__ == "__main__":
    main()
