import feedparser
import json
import os
import re
import smtplib
from datetime import datetime, timezone
from email.mime.text import MIMEText

STATUS_FILE = "status.json"

def load_status():
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

def clean_summary(raw_html):
    """Strip HTML tags from the RSS summary and trim it to a readable length."""
    text = re.sub("<[^<]+?>", "", raw_html or "")
    text = text.strip()
    return text[:200] + "..." if len(text) > 200 else text

def format_date(article):
    """Convert the feed's raw date into a clean, readable format."""
    if hasattr(article, "published_parsed") and article.published_parsed:
        return datetime(*article.published_parsed[:6]).strftime("%d %B %Y, %H:%M UTC")
    return "Date unknown"

def send_email(new_articles):
    gmail_address = os.environ["GMAIL_ADDRESS"]
    gmail_password = os.environ["GMAIL_APP_PASSWORD"]

    body_lines = []
    for a in new_articles:
        body_lines.append(
            f"- {a['title']}\n"
            f"  Date: {a['date']}\n"
            f"  {a['summary']}\n"
            f"  {a['link']}"
        )
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
    new_entries = [a for a in articles if a.link not in seen_links]

    if new_entries:
        new_articles = [
            {
                "title": a.title,
                "link": a.link,
                "date": format_date(a),
                "summary": clean_summary(a.get("summary", "")),
            }
            for a in new_entries
        ]

        print(f"Found {len(new_articles)} new article(s). Sending email...")
        send_email(new_articles)
        status["articles"].extend(new_articles)
    else:
        print("No new articles found.")

    status["last_checked"] = datetime.now(timezone.utc).isoformat()
    save_status(status)

if __name__ == "__main__":
    main()
