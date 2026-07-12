import feedparser
import json
import os
import smtplib
from datetime import datetime, timezone
from email.mime.text import MIMEText

STATUS_FILE = "status.json"

def load_status():
    """Load last check time and all articles alerted on so far."""
    if os.path.exists(STATUS_FILE):
        with open(STATUS_FILE, "r") as f:
            return json.load(f)
    return {"last_checked": None, "articles": []}

def save_status(status):
    with open(STATUS_FILE, "w") as f:
        json.dump(status, f, indent=2)

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
    status = load_status()
    seen_links = {a["link"] for a in status["articles"]}

    articles = get_mercor_articles()
    new_articles = [a for a in articles if a.link not in seen_links]

    if new_articles:
        print(f"Found {len(new_articles)} new article(s). Sending email...")
        send_email(new_articles)
        for article in new_articles:
            status["articles"].append({
                "title": article.title,
                "link": article.link,
            })
    else:
        print("No new articles found.")

    # Always update the timestamp, even with nothing new, so the status
    # page proves the automation is actually alive and checking.
    status["last_checked"] = datetime.now(timezone.utc).isoformat()
    save_status(status)

if __name__ == "__main__":
    main()
