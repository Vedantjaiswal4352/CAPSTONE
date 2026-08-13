# analytics.py -> Analytics and monitoring module

import time 
import os
import logging
from datetime import datetime, timezone
from typing import Dict, Optional, List
from collections import defaultdict
from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger("capstone_analytics")

request_history : Dict[str, List[Dict]] = defaultdict(list)
query_cache: Dict[str, Dict] = {}

def track_request(username: str, question: str, response_time: float):
    """Track user request for analytics"""
    request_history[username].append({
        "question": question,
        "timestamp": datetime.now(timezone.utc),
        "response_time": response_time
    })
    logger.info(f"Request tracked for {username}")

def cache_query(cache_key: str, answer: str, username: str):
    """Cache query result"""
    query_cache[cache_key] = {
        "answer": answer,
        "timestamp": datetime.now(timezone.utc),
        "user": username
    }
    logger.info(f"Query cached with key: {cache_key[:30]}...")

def get_cached_query(cache_key: str)-> str:
    """Get cache query result"""
    return query_cache.get(cache_key)

def get_user_history(username: str)-> List[Dict]:
    """Get query history for user"""
    return request_history.get(username,[])

def get_analytics_summary():
    """Get comprehensive analytics summary."""
    total_queries = sum(len(queries) for queries in request_history.values())
    total_users = len(request_history)
    avg_response_time = 0

    all_time = []
    for queries in request_history.values():
        all_time.extend([q.get("response_time",0) for q in queries])
    
    if all_time:
        avg_response_time = sum(all_time) / len(all_time)
    
    return {
        "total_queries": total_queries,
        "total_users": total_users,
        "cached_queries": len(query_cache),
        "cached_size": sum(len(str(v)) for v in query_cache.values()),
        "avg_response_time": avg_response_time
    }

def clear_old_queries(max_age_seconds: int = 3600):
    """Clear cache entries older than max age"""
    now = datetime.now(timezone.utc)
    keys_to_remove = []

    for key, value in query_cache.items():
        age = (now - value["timestamp"]).total_seconds()
        if age > max_age_seconds:
            keys_to_remove.append(key)
    for key in keys_to_remove:
        del query_cache[key]
    logger.info(f"Cleared {len(keys_to_remove)} old cache entries.")