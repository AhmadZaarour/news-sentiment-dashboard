import requests
import sqlalchemy
from sqlalchemy import create_engine, Column, String, DateTime, Text, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
from textblob import TextBlob
from dotenv import load_dotenv

load_dotenv()

# You can use an environment variable for safety
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

# MySQL Database connection URL
DATABASE_URL = os.getenv("DATABASE_URL")

# Set up SQLAlchemy
Base = sqlalchemy.orm.declarative_base()

class NewsArticle(Base):
    __tablename__ = "news_articles"
    title = Column(String(100))
    description = Column(String(200))
    content = Column(Text)
    publishedAt = Column(DateTime)
    source = Column(String(100))
    url = Column(String(150), primary_key=True)
    sentiment_score = Column(Float)

# Set up database engine and session
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

# Create the table if it doesn't exist
Base.metadata.create_all(engine)

def fetch_news(query="AI", language="en", page_size=10):
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": query,
        "language": language,
        "pageSize": page_size,
        "sortBy": "publishedAt",
        "apiKey": NEWS_API_KEY,
    }

    response = requests.get(url, params=params)
    if response.status_code == 200:
        articles = response.json().get("articles", [])
        return articles
    else:
        print(f"Failed to fetch news: {response.status_code}")
        return []

def analyze_sentiment(text):
    # Perform sentiment analysis using TextBlob
    blob = TextBlob(text)
    return blob.sentiment.polarity  # Returns a score between -1 and 1

def save_news_to_db(articles):
    for article in articles:
        sentiment_score_val = analyze_sentiment(article["content"])
        news = NewsArticle(
            title=article["title"],
            description=article["description"],
            content=article["content"],
            publishedAt=datetime.strptime(article["publishedAt"], "%Y-%m-%dT%H:%M:%SZ"),
            source=article["source"]["name"],
            url=article["url"],
            sentiment_score=sentiment_score_val
        )
        session.add(news)
    session.commit()

if __name__ == "__main__":
    articles = fetch_news(query="AI", page_size=5)
    if articles:
        save_news_to_db(articles)
        print(f"Successfully saved {len(articles)} articles with sentiment scores to MySQL.")
    else:
        print("No articles fetched.")
