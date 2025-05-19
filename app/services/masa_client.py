"""
Masa API Client Service
Handles communication with the Masa AI API for X/Twitter data
"""
import requests
import time
import json
from typing import Dict, Any, List, Optional
from app.utils.logger import get_component_logger

logger = get_component_logger("masa_client")

# Global variables
_api_key = None
_api_url = None
_initialized = False

def initialize_masa_client(api_key: str, api_url: str) -> None:
    """Initialize the Masa API client with credentials"""
    global _api_key, _api_url, _initialized
    
    _api_key = api_key
    _api_url = api_url.rstrip("/")  # Remove trailing slash if present
    _initialized = True
    
    logger.info(f"Masa API client initialized with URL: {_api_url}")

def is_initialized() -> bool:
    """Check if the client is initialized"""
    return _initialized

def _check_initialization():
    """Check if the client is initialized and raise an exception if not"""
    if not _initialized:
        raise RuntimeError("Masa API client not initialized. Call initialize_masa_client() first.")

def _build_headers() -> Dict[str, str]:
    """Build request headers with API key"""
    _check_initialization()
    return {
        "Authorization": f"Bearer {_api_key}",
        "Content-Type": "application/json"
    }

def perform_twitter_live_search(
    query: str, 
    search_type: str = "searchbyquery", 
    max_results: int = 10,
    data_source_type: str = "twitter-scraper"
) -> Dict[str, Any]:
    """
    Perform a live search for Twitter data
    
    Args:
        query: Search query string
        search_type: Type of search (searchbyquery, searchbyfullarchive, etc.)
        max_results: Maximum number of results to return
        data_source_type: Type of data source to use
        
    Returns:
        Dictionary containing search results
    """
    _check_initialization()
    
    # Build request payload
    payload = {
        "type": data_source_type,
        "arguments": {
            "type": search_type,
            "query": query,
            "max_results": max_results
        }
    }
    
    try:
        # Submit search request
        search_url = f"{_api_url}/v1/search/live/twitter"
        response = requests.post(search_url, headers=_build_headers(), json=payload)
        response.raise_for_status()
        
        result = response.json()
        search_uuid = result.get("uuid")
        
        if not search_uuid:
            logger.error(f"No UUID returned from search request: {result}")
            raise ValueError("Invalid response from Masa API: No UUID returned")
        
        logger.info(f"Search job submitted with UUID: {search_uuid}")
        
        # Wait for job to complete (poll status endpoint)
        status_url = f"{_api_url}/v1/search/live/twitter/status/{search_uuid}"
        max_retries = 30
        retry_count = 0
        
        while retry_count < max_retries:
            status_response = requests.get(status_url, headers=_build_headers())
            status_response.raise_for_status()
            
            status_data = status_response.json()
            status = status_data.get("status")
            
            if status == "done":
                logger.info(f"Search job completed: {search_uuid}")
                break
            elif status in ["error", "failed"]:
                error_msg = status_data.get("error", "Unknown error")
                logger.error(f"Search job failed: {error_msg}")
                raise RuntimeError(f"Search job failed: {error_msg}")
            
            logger.debug(f"Job status: {status}. Waiting before retrying...")
            time.sleep(2)
            retry_count += 1
        
        if retry_count >= max_retries:
            logger.error("Search job timed out")
            raise RuntimeError("Search job timed out after maximum retries")
        
        # Fetch results
        results_url = f"{_api_url}/v1/search/live/twitter/result/{search_uuid}"
        results_response = requests.get(results_url, headers=_build_headers())
        results_response.raise_for_status()
        
        return results_response.json()
    
    except requests.exceptions.RequestException as e:
        logger.error(f"HTTP error during Twitter live search: {str(e)}")
        raise RuntimeError(f"Error communicating with Masa API: {str(e)}")
    except Exception as e:
        logger.exception(f"Error during Twitter live search: {str(e)}")
        raise

def perform_twitter_indexed_search(
    query: str,
    search_type: str = "similarity",
    keywords: Optional[List[str]] = None,
    keyword_operator: str = "and",
    max_results: int = 10
) -> Dict[str, Any]:
    """
    Perform an indexed search for Twitter data
    
    Args:
        query: Semantic search query
        search_type: Type of search (similarity, hybrid)
        keywords: Optional list of keywords to filter results
        keyword_operator: Operator to use for multiple keywords (and, or)
        max_results: Maximum number of results to return
        
    Returns:
        Dictionary containing search results
    """
    _check_initialization()
    
    # Build request payload
    payload = {
        "query": query,
        "max_results": max_results
    }
    
    # Add optional parameters if provided
    if keywords:
        payload["keywords"] = keywords
        payload["keyword_operator"] = keyword_operator
    
    try:
        # Submit search request
        search_url = f"{_api_url}/v1/search/{search_type}/twitter"
        response = requests.post(search_url, headers=_build_headers(), json=payload)
        response.raise_for_status()
        
        return response.json()
    
    except requests.exceptions.RequestException as e:
        logger.error(f"HTTP error during Twitter indexed search: {str(e)}")
        raise RuntimeError(f"Error communicating with Masa API: {str(e)}")
    except Exception as e:
        logger.exception(f"Error during Twitter indexed search: {str(e)}")
        raise

def perform_twitter_hybrid_search(
    similarity_query: str,
    text_query: str,
    similarity_weight: float = 0.7,
    text_weight: float = 0.3,
    keywords: Optional[List[str]] = None,
    keyword_operator: str = "and",
    max_results: int = 10
) -> Dict[str, Any]:
    """
    Perform a hybrid search for Twitter data
    
    Args:
        similarity_query: Semantic search query
        text_query: Full-text search query
        similarity_weight: Weight to apply to vector score (0-1)
        text_weight: Weight to apply to text score (0-1)
        keywords: Optional list of keywords to filter results
        keyword_operator: Operator to use for multiple keywords (and, or)
        max_results: Maximum number of results to return
        
    Returns:
        Dictionary containing search results
    """
    _check_initialization()
    
    # Build request payload
    payload = {
        "similarity_query": {
            "query": similarity_query,
            "weight": similarity_weight
        },
        "text_query": {
            "query": text_query,
            "weight": text_weight
        },
        "max_results": max_results
    }
    
    # Add optional parameters if provided
    if keywords:
        payload["keywords"] = keywords
        payload["keyword_operator"] = keyword_operator
    
    try:
        # Submit search request
        search_url = f"{_api_url}/v1/search/hybrid/twitter"
        response = requests.post(search_url, headers=_build_headers(), json=payload)
        response.raise_for_status()
        
        return response.json()
    
    except requests.exceptions.RequestException as e:
        logger.error(f"HTTP error during Twitter hybrid search: {str(e)}")
        raise RuntimeError(f"Error communicating with Masa API: {str(e)}")
    except Exception as e:
        logger.exception(f"Error during Twitter hybrid search: {str(e)}")
        raise 