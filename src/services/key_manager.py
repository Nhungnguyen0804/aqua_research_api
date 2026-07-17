# xoay vòng key  

from itertools import cycle

from src.config import API_KEYS

key_cycle = cycle(API_KEYS)

def get_next_key() -> ():
    return next(key_cycle)