"""Redis configuration for the mcp-atlassian service."""

# Redis connection settings
REDIS_HOST = "127.0.0.1"
REDIS_PORT = 6380  # Use the correct port that's actually running
REDIS_PASSWORD = "cli-user-all-ports-037075e23a197bd1a653bcf6655bb64e"
REDIS_DB = 0

# Redis connection URL
REDIS_URL = f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"

# Redis connection options
REDIS_OPTIONS = {
    "host": REDIS_HOST,
    "port": REDIS_PORT,
    "password": REDIS_PASSWORD,
    "db": REDIS_DB,
    "retry_on_timeout": True,
    "socket_timeout": 5,
    "socket_connect_timeout": 5,
    "socket_keepalive": True,
    "health_check_interval": 30,
}
