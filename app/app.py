from flask import Flask, render_template, request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from utils.news_fetcher import NewsArticle
import json
from collections import defaultdict
from datetime import datetime

import os

app = Flask(__name__)

# MySQL Database connection URL
DATABASE_URL = "mysql+pymysql://root:@localhost:3306/news_db"

# Set up database engine and session
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

@app.route('/')
def index():
    # Get filters from query params
    sentiment_filter = request.args.get('sentiment')
    keyword_filter = request.args.get('keyword', '').lower()

    # Base query
    query = session.query(NewsArticle)

    # Apply sentiment filtering
    if sentiment_filter:
        if sentiment_filter == 'positive':
            query = query.filter(NewsArticle.sentiment_score > 0.1)
        elif sentiment_filter == 'negative':
            query = query.filter(NewsArticle.sentiment_score < -0.1)
        elif sentiment_filter == 'neutral':
            query = query.filter(NewsArticle.sentiment_score.between(-0.1, 0.1))

    # Apply keyword filtering
    if keyword_filter:
        query = query.filter(
            (NewsArticle.title.ilike(f"%{keyword_filter}%")) |
            (NewsArticle.description.ilike(f"%{keyword_filter}%"))
        )

    # Fetch results
    articles = query.all()

    # Prepare table
    news_data = [{
        'title': a.title,
        'description': a.description,
        'publishedAt': a.publishedAt,
        'sentiment_score': a.sentiment_score
    } for a in articles]

    # Sentiment counts for filtered set
    sentiment_counts = {'positive': 0, 'neutral': 0, 'negative': 0}
    for article in articles:
        score = article.sentiment_score
        if score > 0.1:
            sentiment_counts['positive'] += 1
        elif score < -0.1:
            sentiment_counts['negative'] += 1
        else:
            sentiment_counts['neutral'] += 1

    # Time series for filtered data
    daily_scores = defaultdict(list)
    for article in articles:
        if article.publishedAt:
            date_str = article.publishedAt.strftime('%Y-%m-%d')
            daily_scores[date_str].append(article.sentiment_score)

    daily_avg_sentiment = {
        date: sum(scores) / len(scores)
        for date, scores in daily_scores.items()
    }

    sorted_dates = sorted(daily_avg_sentiment.keys())
    sentiment_trend = {
        'dates': sorted_dates,
        'scores': [daily_avg_sentiment[date] for date in sorted_dates]
    }

    return render_template(
        'index.html',
        news_data=news_data,
        sentiment_counts=sentiment_counts,
        sentiment_trend=json.dumps(sentiment_trend)
    )


if __name__ == '__main__':
    app.run(debug=True)
