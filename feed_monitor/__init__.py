from redis_feed import RedisFeed

def main():
    RedisFeed.parse_args().start()

__all__ = ["RedisFeed"]