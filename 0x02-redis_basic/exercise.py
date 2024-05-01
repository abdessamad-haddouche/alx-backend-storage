#!/usr/bin/env python3

'''
This module contains the Cache class
'''

from typing import Any, Callable, Optional, Union
from uuid import uuid4
from functools import wraps
import redis


def call_history(method: Callable) -> Callable:
    '''
    decorator that stores the history of inputs and outputs for a function

    Args:
        method (Callable): a function that takes any number of arguments

    Returns:
        Callable: a function that returns the original function
    '''

    inp = method.__qualname__ + ':inputs'
    outp = method.__qualname__ + ':outputs'

    @wraps(method)
    def wrapper(self, *args, **kwargs) -> Any:
        '''
        wrapper function that stores the history of inputs and outputs

        Args:
            self (Any): the class instance
            *args: any number of arguments
            **kwargs: any number of keyword arguments

        Returns:
            Any: the result of the original function
        '''
        self._redis.rpush(inp, str(args))
        result = method(self, *args)
        self._redis.rpush(outp, result)
        return result
    return wrapper


def count_calls(method: Callable) -> Callable:
    '''
    decorator that increments the count for a function key every time the
    function is called

    Args:
        method (Callable): a function that takes any number of arguments

    Returns:
        Callable: a function that returns the original function
    '''
    key = method.__qualname__
    # print("qualified name", key) // Cache.store

    @wraps(method)
    def wrapper(self, *args, **kwargs) -> Any:
        '''
        wrapper function that increments the count for a function key

        Args:
            self (Any): the class instance

        Returns:
            Any: the result of the original function
        '''
        self._redis.incr(key)
        return method(self, *args, **kwargs)
    return wrapper


def replay(method: Callable) -> None:
    '''
    displays the history of inputs and outputs of a function

    Args:
        method (Callable): a function that takes any number of arguments

    Returns:
        None
    '''
    key = method.__qualname__
    all_data = redis.Redis()
    history = all_data.get(key).decode("utf-8")
    print("{} was called {} times:".format(key, history))
    inps = all_data.lrange(key + ":inputs", 0, -1)
    outps = all_data.lrange(key + ":outputs", 0, -1)
    for key, value in zip(inps, outps):
        print(f"{key}(*{key.decode('utf-8')}) -> {value.decode('utf-8')}")


class Cache:
    '''
    Cache class that stores instances of the Redis client

    Attributes:
        _redis (Redis): an instance of the Redis client

    Methods:
        store(self, data: Union[str, bytes, int, float]) -> str:
        takes a data argument and returns a string
        generates a random key using uuid from stored input data
        stores the input data in Redis using the random key'''
    def __init__(self):
        '''
        initializes an instance of the Redis client
        '''
        self._redis = redis.Redis()
        self._redis.flushdb()

    @count_calls
    @call_history
    def store(self, data: Union[str, bytes, int, float]) -> str:
        '''
        takes a data argument and returns a string

        Args:
            data (Union[str, bytes, int, float]): a string, bytes, int

        Returns:
            str: a random key generated using uuid from stored input data
        '''
        k = str(uuid4())
        self._redis.mset({k: data})
        # print(self._redis.get(key))
        return k

    def get(
            self, key: str, fn: Optional[Callable] = None
            ) -> Union[str, bytes, int, float]:
        '''
        retrieves the data stored in Redis

        Args:
            key (str): a string key
            fn (Optional[Callable]): a function that takes a byte argument

        Returns:
            Union[str, bytes, int, float]: the data stored in Redis
        '''
        _bytes = self._redis.get(key)
        return fn(_bytes) if fn else _bytes

    def get_str(self, key: str) -> str:
        '''
        parametize get with str

        Args:
            key (str): a string key

        Returns:
            str: the data stored in Redis
        '''
        return self.get(key, str)

    def get_int(self, key: str) -> int:
        '''
        parametize get with int
        '''
        return self.get(key, int)
