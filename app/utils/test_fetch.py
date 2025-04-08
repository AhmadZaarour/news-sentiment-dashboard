from utils.news_fetcher import fetch_news, save_news_to_db
import json

if __name__ == "__main__":
    articles = fetch_news(query="AI", page_size=5)
    if articles:
        save_news_to_db(articles)
        print(f"Successfully saved {len(articles)} articles with sentiment scores to MySQL.")
    else:
        print("No articles fetched.")
