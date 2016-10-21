# Redis host information
REDIS_HOST = '127.0.0.1'
REDIS_PORT = 6379

CUSTOM_REDIS = True

# logging setup
LOG_LEVEL = 'INFO'
LOG_STDOUT = True
LOG_JSON = True
LOG_DIR = "logs"
LOG_MAX_BYTES = '10MB'
LOG_BACKUPS = 5

TO_KAFKA = False
KAFKA_HOSTS = '127.0.0.1:9092'
