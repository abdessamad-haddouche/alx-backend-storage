#!/usr/bin/env python3

'''
This module contains a function that gets the content of a webpage and caches
it
'''

import redis
import requests
from typing import Callable
from functools import wraps

cache = redis.Redis()
counter = 0


def get_page(url: str) -> str:
    '''
    This function gets the content of a webpage and caches it

    Args:
        url (str): The url of the webpage

    Returns:
        str: The content of the webpage
    '''
    cache.set(f"cached:{url}", counter)
    response = requests.get(url)
    cache.incr(f"count:{url}")
    cache.setex(f"count:{url}", 10, cache.get(f"cached:{url}"))
    return response.text
