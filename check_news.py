name: Check Mercor News

on:
  schedule:
    - cron: "0 */3 * * *"
  workflow_dispatch:

jobs:
  check-news:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Run news check
        env:
          GMAIL_ADDRESS: ${{ secrets.GMAIL_ADDRESS }}
          GMAIL_APP_PASSWORD: ${{ secrets.GMAIL_APP_PASSWORD }}
        run: python check_news.py

      - name: Commit updated seen list
        run: |
          git config user.name "github-actions"
          git config user.email "actions@github.com"
          git add seen_articles.json
          git diff --staged --quiet || git commit -m "Update seen articles"
          git push
