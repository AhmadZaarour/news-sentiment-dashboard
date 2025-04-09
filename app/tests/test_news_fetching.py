import pytest
from tests.news_fetcher import analyze_sentiment, NewsArticle, Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime


@pytest.fixture

def test_analyze_sentiment_positive():
    text = "I love this product. It's amazing!"
    score = analyze_sentiment(text)
    assert score > 0

def test_analyze_sentiment_negative():
    text = "This is terrible and disappointing."
    score = analyze_sentiment(text)
    assert score < 0

def test_analyze_sentiment_neutral():
    text = "The car is red."
    score = analyze_sentiment(text)
    assert -0.1 <= score <= 0.1

def db_session():
    # Use a temporary SQLite DB in-memory for testing
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()

def test_save_article(db_session=db_session()):
    article = NewsArticle(
        title="Test News",
        description="This is a test article",
        url="http://example.com",
        publishedAt=datetime.now(),
        sentiment_score=0.5
    )
    db_session.add(article)
    db_session.commit()

    result = db_session.query(NewsArticle).filter_by(title="Test News").first()
    assert result is not None
    assert result.sentiment_score == 0.5