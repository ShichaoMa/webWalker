from redis_feed import RedisFeed
import sys
import os
sys.path.insert(0, os.getcwd())

def main():
    RedisFeed.parse_args().start()

__all__ = ["RedisFeed", "main"]