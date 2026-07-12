import feedparser
import json
import os
import re
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
    """Fetch the current Mercor news feed from Google News."""
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
    """Send a cheese-themed HTML email listing the new articles."""
    gmail_address = os.environ["GMAIL_ADDRESS"]
    gmail_password = os.environ["GMAIL_APP_PASSWORD"]

    article_blocks = ""
    for a in new_articles:
        article_blocks += f"""
        <div style="background:#FFF8DC; border:2px solid #F4C430; border-radius:12px;
                    padding:16px; margin-bottom:16px;">
          <a href="{a['link']}" style="font-size:16px; font-weight:bold; color:#B8860B;
             text-decoration:none;">🧀 {a['title']}</a>
          <div style="color:#8B6508; font-size:12px; margin-top:4px;">{a['date']}</div>
          <div style="color:#4A3B00; font-size:14px; margin-top:8px;">{a['summary']}</div>
        </div>
        """

    html_body = f"""
    <html>
      <body style="background:#FFFBEA; font-family:Georgia, serif; padding:20px;">
        <h1 style="color:#D2691E;">🧀 Mercor News Watcher</h1>
        <p style="color:#8B6508;">Gouda news! {len(new_articles)} fresh article(s) just came out of the press.</p>
        {article_blocks}
        <p style="color:#B8860B; font-size:12px; margin-top:20px;">That's brie-lliant. Catch you next time it melts.</p>
      </body>
    </html>
    """

    msg = MIMEText(html_body, "html")
    msg["Subject"] = f"🧀 Mercor News Alert: {len(new_articles)} new article(s)"
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

    # Always update the timestamp, even with nothing new, so the status
    # page proves the automation is actually alive and checking.
    status["last_checked"] = datetime.now(timezone.utc).isoformat()
    save_status(status)

if __name__ == "__main__":
    main()
