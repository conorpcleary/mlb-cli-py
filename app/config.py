"""
Configuration module for the MLB CLI application.
Centralizes all constants and environment-specific settings.
"""

# TUI Settings
STATIC_WIDTH = 80
INITIAL_HEIGHT = 36

# Redis Settings
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 0

# Data Service Settings
LIVE_DATA_TTL = 300  # 5 minutes

# Division name mapping
DIVISION_NAMES = {
    200: "AL West",
    201: "AL East",
    202: "AL Central",
    203: "NL West",
    204: "NL East",
    205: "NL Central"
}
