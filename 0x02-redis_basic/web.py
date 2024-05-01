#!/usr/bin/env python3
"""
Module to provide a cache decorator for web page retrieval.
"""

import requests
import redis
from typing import Callable

redis_client = redis.Redis()


def cache_decorator(func: Callable) -> Callable:
    """
    Decorator to cache the result of a function
    with a specified expiration time.
    """
    def wrapper(*args, **kwargs):
        """
        Generate a cache key based on the function name and arguments
        """
        cache_key = f"cache:{func.__name__}:{args}"

        cached_result = redis_client.get(cache_key)
        if cached_result:
            return cached_result.decode('utf-8')

        result = func(*args, **kwargs)

        redis_client.setex(cache_key, 10, result)

        return result

    return wrapper


@cache_decorator
def get_page(url: str) -> str:
    """
    Get the HTML content of a particular URL
    and cache the result with an expiration time of 10 seconds.
    """
    redis_client.incr(f"count:{url}")

    cached_data = redis_client.get(url)
    if cached_data:
        return cached_data.decode('utf-8')

    response = requests.get(url)
    html_content = response.text

    redis_client.setex(url, 10, html_content)

    return html_content
