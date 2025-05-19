"""
KOL Action Handlers
"""
from typing import Dict, Any, List
from model_context_protocol import MCPRequest
from app.utils.logger import get_component_logger
from app.services.masa_client import (
    perform_twitter_live_search,
    perform_twitter_indexed_search,
    perform_twitter_hybrid_search
)
from app.services.nlp_service import (
    analyze_sentiment,
    extract_topics,
    batch_analyze_sentiment,
    classify_sentiment_distribution
)
from flask import current_app

logger = get_component_logger("kol_actions")

def handle_kol_action(request: MCPRequest) -> Dict[str, Any]:
    """Route KOL actions to their appropriate handlers"""
    action = request.action
    params = request.params or {}
    
    logger.info(f"Processing KOL action: {action}")
    
    try:
        if action == "kol.search":
            return search_kol_content(params)
        elif action == "kol.sentiment":
            return analyze_kol_sentiment(params)
        elif action == "kol.topics":
            return extract_kol_topics(params)
        elif action == "kol.insights":
            return analyze_kol_insights(params)
        elif action == "kol.trends":
            return get_kol_trends(params)
        else:
            logger.error(f"Unknown KOL action: {action}")
            raise ValueError(f"Unknown KOL action: {action}")
    except Exception as e:
        logger.error(f"Error processing KOL action {action}: {str(e)}")
        return {
            "error": str(e),
            "action": action,
            "success": False
        }


def search_kol_content(params: Dict[str, Any]) -> Dict[str, Any]:
    """Search for KOL content on social media"""
    if 'query' not in params:
        raise ValueError("Missing required parameter: query")
    
    query = params['query']
    search_type = params.get('search_type', 'indexed')
    max_results = int(params.get('max_results', current_app.config.get('DEFAULT_MAX_RESULTS', 10)))
    max_results = min(max(1, max_results), 100)
    
    keywords = params.get('keywords', [])
    kol_username = params.get('kol_username')
    
    if kol_username:
        if search_type == 'live':
            query = f"from:{kol_username} {query}"
        else:
            if not isinstance(keywords, list):
                keywords = [keywords]
            keywords.append(f"@{kol_username}")
    
    if search_type == 'live':
        results = perform_twitter_live_search(
            query=query,
            search_type="searchbyquery",
            max_results=max_results
        )
    elif search_type == 'indexed':
        results = perform_twitter_indexed_search(
            query=query,
            search_type="similarity",
            keywords=keywords if keywords else None,
            keyword_operator=params.get('keyword_operator', 'and'),
            max_results=max_results
        )
    elif search_type == 'hybrid':
        text_query = params.get('text_query', query)
        results = perform_twitter_hybrid_search(
            similarity_query=query,
            text_query=text_query,
            similarity_weight=float(params.get('similarity_weight', 0.7)),
            text_weight=float(params.get('text_weight', 0.3)),
            keywords=keywords if keywords else None,
            keyword_operator=params.get('keyword_operator', 'and'),
            max_results=max_results
        )
    else:
        raise ValueError(f"Invalid search_type: {search_type}")
    
    return {
        "query": query,
        "search_type": search_type,
        "max_results": max_results,
        "kol_username": kol_username,
        "results": results,
        "result_count": len(results) if isinstance(results, list) else "unknown"
    }


def analyze_kol_sentiment(params: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze sentiment of KOL content"""
    if 'text' in params:
        text = params['text']
        sentiment_result = analyze_sentiment(text)
        return {
            "text": text,
            "sentiment": sentiment_result,
            "single_analysis": True
        }
    elif 'query' in params:
        search_params = {
            'query': params['query'],
            'search_type': params.get('search_type', 'indexed'),
            'max_results': params.get('max_results', current_app.config.get('DEFAULT_MAX_RESULTS', 10)),
            'keywords': params.get('keywords', []),
            'kol_username': params.get('kol_username')
        }
        
        search_results = search_kol_content(search_params)
        results = search_results.get('results', [])
        if not isinstance(results, list):
            raise ValueError(f"Unexpected search results format: {type(results)}")
        
        texts = [result.get('Content', '') for result in results if 'Content' in result]
        sentiment_results = batch_analyze_sentiment(texts)
        sentiment_distribution = classify_sentiment_distribution(sentiment_results)
        
        return {
            "query": params['query'],
            "kol_username": params.get('kol_username'),
            "sentiment_results": sentiment_results,
            "sentiment_distribution": sentiment_distribution,
            "result_count": len(texts),
            "single_analysis": False
        }
    else:
        raise ValueError("Missing required parameter: either 'text' or 'query' must be provided")


def extract_kol_topics(params: Dict[str, Any]) -> Dict[str, Any]:
    """Extract topics from KOL content"""
    max_topics = int(params.get('max_topics', 5))
    
    if 'text' in params:
        text = params['text']
        topics = extract_topics(text, max_topics=max_topics)
        return {
            "text": text,
            "topics": topics,
            "topic_count": len(topics),
            "single_analysis": True
        }
    elif 'query' in params:
        search_params = {
            'query': params['query'],
            'search_type': params.get('search_type', 'indexed'),
            'max_results': params.get('max_results', current_app.config.get('DEFAULT_MAX_RESULTS', 10)),
            'keywords': params.get('keywords', []),
            'kol_username': params.get('kol_username')
        }
        
        search_results = search_kol_content(search_params)
        results = search_results.get('results', [])
        if not isinstance(results, list):
            raise ValueError(f"Unexpected search results format: {type(results)}")
        
        texts = [result.get('Content', '') for result in results if 'Content' in result]
        all_topics = []
        for text in texts:
            all_topics.extend(extract_topics(text, max_topics=max_topics))
        
        topic_counts = {}
        for topic in all_topics:
            topic_counts[topic] = topic_counts.get(topic, 0) + 1
        
        sorted_topics = sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)
        
        return {
            "query": params['query'],
            "kol_username": params.get('kol_username'),
            "top_topics": sorted_topics[:max_topics],
            "all_topics": topic_counts,
            "result_count": len(texts),
            "single_analysis": False
        }
    else:
        raise ValueError("Missing required parameter: either 'text' or 'query' must be provided")


def analyze_kol_insights(params: Dict[str, Any]) -> Dict[str, Any]:
    """Get comprehensive sentiment analysis about a KOL"""
    if 'username' not in params:
        raise ValueError("Missing required parameter: username")
    
    username = params['username']
    query = params.get('query', '')
    search_type = params.get('search_type', 'indexed')
    max_results = int(params.get('max_results', current_app.config.get('DEFAULT_MAX_RESULTS', 20)))
    
    search_params = {
        'query': query,
        'search_type': search_type,
        'max_results': max_results,
        'kol_username': username
    }
    
    search_results = search_kol_content(search_params)
    results = search_results.get('results', [])
    if not isinstance(results, list):
        raise ValueError(f"Unexpected search results format: {type(results)}")
    
    texts = [result.get('Content', '') for result in results if 'Content' in result]
    
    if not texts:
        return {
            "username": username,
            "query": query,
            "error": "No content found for this KOL",
            "success": False
        }
    
    sentiment_results = batch_analyze_sentiment(texts)
    sentiment_distribution = classify_sentiment_distribution(sentiment_results)
    
    all_topics = []
    for text in texts:
        all_topics.extend(extract_topics(text, max_topics=10))
    
    topic_counts = {}
    for topic in all_topics:
        topic_counts[topic] = topic_counts.get(topic, 0) + 1
    
    sorted_topics = sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)
    top_topics = sorted_topics[:10]
    
    return {
        "username": username,
        "query": query,
        "content_count": len(texts),
        "sentiment_distribution": sentiment_distribution,
        "top_topics": top_topics,
        "recent_content": [
            {
                "text": result.get('Content', ''),
                "sentiment": analyze_sentiment(result.get('Content', '')),
                "topics": extract_topics(result.get('Content', ''), max_topics=3)
            }
            for result in results[:5]
        ],
        "success": True
    }


def get_kol_trends(params: Dict[str, Any]) -> Dict[str, Any]:
    """Get trending topics among multiple KOLs"""
    if 'usernames' not in params:
        raise ValueError("Missing required parameter: usernames")
    
    usernames = params['usernames']
    if not isinstance(usernames, list):
        usernames = [usernames]
    
    if not usernames:
        raise ValueError("Empty usernames list")
    
    query = params.get('query', '')
    search_type = params.get('search_type', 'indexed')
    max_results_per_kol = int(params.get('max_results_per_kol', 10))
    max_trends = int(params.get('max_trends', 10))
    
    all_topics = []
    all_sentiments = []
    kol_results = {}
    
    for username in usernames:
        try:
            search_params = {
                'query': query,
                'search_type': search_type,
                'max_results': max_results_per_kol,
                'kol_username': username
            }
            
            search_results = search_kol_content(search_params)
            results = search_results.get('results', [])
            if not isinstance(results, list):
                logger.warning(f"Unexpected search results format for {username}: {type(results)}")
                continue
            
            texts = [result.get('Content', '') for result in results if 'Content' in result]
            
            if not texts:
                logger.warning(f"No content found for KOL: {username}")
                kol_results[username] = {
                    "content_count": 0,
                    "error": "No content found"
                }
                continue
            
            sentiment_results = batch_analyze_sentiment(texts)
            sentiment_distribution = classify_sentiment_distribution(sentiment_results)
            
            kol_topics = []
            for text in texts:
                kol_topics.extend(extract_topics(text, max_topics=5))
            
            kol_results[username] = {
                "content_count": len(texts),
                "topics": kol_topics,
                "sentiment_distribution": sentiment_distribution
            }
            
            all_topics.extend(kol_topics)
            all_sentiments.extend(sentiment_results)
            
        except Exception as e:
            logger.error(f"Error analyzing KOL {username}: {str(e)}")
            kol_results[username] = {
                "error": str(e)
            }
    
    topic_counts = {}
    for topic in all_topics:
        topic_counts[topic] = topic_counts.get(topic, 0) + 1
    
    sorted_topics = sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)
    top_trends = sorted_topics[:max_trends]
    
    overall_sentiment = classify_sentiment_distribution(all_sentiments)
    
    return {
        "usernames": usernames,
        "query": query,
        "top_trends": top_trends,
        "kol_count": len(usernames),
        "analyzed_count": sum(1 for k, v in kol_results.items() if "error" not in v),
        "overall_sentiment": overall_sentiment,
        "kol_results": kol_results,
        "success": True
    } 