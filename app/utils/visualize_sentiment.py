import matplotlib.pyplot as plt
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from news_fetcher import NewsArticle
import os

# MySQL Database connection URL
DATABASE_URL = "mysql+pymysql://root:@localhost:3306/news_db"

# Set up database engine and session
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

def fetch_sentiment_data():
    # Fetch all articles and their sentiment scores from the database
    articles = session.query(NewsArticle).all()
    sentiments = [article.sentiment_score for article in articles]
    return sentiments

def plot_sentiment_distribution(sentiments):
    # Plotting the sentiment distribution
    plt.figure(figsize=(10, 6))
    
    # Plot histogram of sentiment scores
    plt.hist(sentiments, bins=20, color='blue', alpha=0.7)
    plt.title("Sentiment Distribution of News Articles")
    plt.xlabel("Sentiment Score")
    plt.ylabel("Number of Articles")
    plt.grid(True)
    
    # Show the plot
    plt.show()

if __name__ == "__main__":
    # Fetch sentiment data
    sentiments = fetch_sentiment_data()
    
    if sentiments:
        # Visualize the sentiment distribution
        plot_sentiment_distribution(sentiments)
    else:
        print("No sentiment data found.")
