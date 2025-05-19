"""
NLP Service for KOL Sentiment MCP
Provides natural language processing capabilities
"""
import nltk
from textblob import TextBlob
import re
from typing import Dict, Any, List, Tuple
from app.utils.logger import get_component_logger

logger = get_component_logger("nlp_service")

# Global variables
_initialized = False

def initialize_nlp() -> None:
    """Initialize NLP components"""
    global _initialized
    
    try:
        # Download required NLTK data
        nltk.download('punkt', quiet=True)
        nltk.download('stopwords', quiet=True)
        nltk.download('wordnet', quiet=True)
        
        _initialized = True
        logger.info("NLP service initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize NLP service: {str(e)}")
        raise

def _check_initialization():
    """Check if NLP service is initialized"""
    if not _initialized:
        raise RuntimeError("NLP service not initialized. Call initialize_nlp() first.")

def analyze_sentiment(text: str) -> Dict[str, Any]:
    """
    Analyze sentiment of a text
    
    Args:
        text: The text to analyze
        
    Returns:
        Dictionary with sentiment analysis results
    """
    _check_initialization()
    
    try:
        # Clean the text
        clean_text = re.sub(r'http\S+', '', text)  # Remove URLs
        clean_text = re.sub(r'@\w+', '', clean_text)  # Remove mentions
        clean_text = re.sub(r'#\w+', '', clean_text)  # Remove hashtags
        
        # Analyze sentiment with TextBlob
        blob = TextBlob(clean_text)
        polarity = blob.sentiment.polarity
        subjectivity = blob.sentiment.subjectivity
        
        # Determine sentiment label
        if polarity > 0.1:
            sentiment = "positive"
        elif polarity < -0.1:
            sentiment = "negative"
        else:
            sentiment = "neutral"
        
        return {
            "sentiment": sentiment,
            "polarity": polarity,
            "subjectivity": subjectivity,
            "text": text
        }
    except Exception as e:
        logger.error(f"Error analyzing sentiment: {str(e)}")
        return {
            "sentiment": "unknown",
            "polarity": 0,
            "subjectivity": 0,
            "text": text,
            "error": str(e)
        }

def extract_topics(text: str, max_topics: int = 5) -> List[str]:
    """
    Extract main topics from text
    
    Args:
        text: The text to analyze
        max_topics: Maximum number of topics to extract
        
    Returns:
        List of topics
    """
    _check_initialization()
    
    try:
        # Clean the text
        clean_text = re.sub(r'http\S+', '', text)  # Remove URLs
        clean_text = re.sub(r'@\w+', '', clean_text)  # Remove mentions
        
        # Extract hashtags
        hashtags = re.findall(r'#(\w+)', text)
        
        # Tokenize the text
        blob = TextBlob(clean_text)
        
        # Extract noun phrases as potential topics
        noun_phrases = list(blob.noun_phrases)
        
        # Combine hashtags and noun phrases, prioritizing hashtags
        topics = hashtags + [np for np in noun_phrases if np not in hashtags]
        
        # Return the top topics
        return topics[:max_topics]
    except Exception as e:
        logger.error(f"Error extracting topics: {str(e)}")
        return []

def batch_analyze_sentiment(texts: List[str]) -> List[Dict[str, Any]]:
    """
    Analyze sentiment for a batch of texts
    
    Args:
        texts: List of texts to analyze
        
    Returns:
        List of sentiment analysis results
    """
    return [analyze_sentiment(text) for text in texts]

def classify_sentiment_distribution(sentiments: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Classify sentiment distribution from a list of sentiment analysis results
    
    Args:
        sentiments: List of sentiment analysis results
        
    Returns:
        Dictionary with sentiment distribution stats
    """
    if not sentiments:
        return {
            "positive": 0,
            "neutral": 0,
            "negative": 0,
            "positive_percentage": 0,
            "neutral_percentage": 0,
            "negative_percentage": 0,
            "average_polarity": 0,
            "average_subjectivity": 0
        }
    
    positive_count = sum(1 for s in sentiments if s["sentiment"] == "positive")
    neutral_count = sum(1 for s in sentiments if s["sentiment"] == "neutral")
    negative_count = sum(1 for s in sentiments if s["sentiment"] == "negative")
    total = len(sentiments)
    
    avg_polarity = sum(s["polarity"] for s in sentiments) / total
    avg_subjectivity = sum(s["subjectivity"] for s in sentiments) / total
    
    return {
        "positive": positive_count,
        "neutral": neutral_count,
        "negative": negative_count,
        "positive_percentage": (positive_count / total) * 100 if total > 0 else 0,
        "neutral_percentage": (neutral_count / total) * 100 if total > 0 else 0,
        "negative_percentage": (negative_count / total) * 100 if total > 0 else 0,
        "average_polarity": avg_polarity,
        "average_subjectivity": avg_subjectivity
    } 