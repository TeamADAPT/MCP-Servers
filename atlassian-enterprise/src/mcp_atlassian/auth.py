"""
Authentication and security module for MCP Atlassian.

This module provides enterprise-grade authentication and security features for 
the MCP Atlassian integration, including OAuth 2.0 support, token refresh mechanisms,
rate limiting, circuit breaker patterns, and comprehensive audit logging.
"""

import os
import json
import time
import logging
import threading
import functools
from typing import Dict, List, Optional, Any, Callable, Union, Tuple
from datetime import datetime, timedelta

import jwt
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Configure logging
logger = logging.getLogger("mcp-atlassian.auth")

# Constants
MAX_RETRY_ATTEMPTS = 5
RETRY_BACKOFF_FACTOR = 0.5
RATE_LIMIT_WINDOW = 60  # seconds
DEFAULT_RATE_LIMIT = 100  # requests per minute
CIRCUIT_BREAKER_THRESHOLD = 5  # failures
CIRCUIT_BREAKER_TIMEOUT = 60  # seconds


class CircuitBreaker:
    """
    Implements the Circuit Breaker pattern to prevent cascading failures.
    
    When the number of failures exceeds a threshold, the circuit is opened
    and all requests fail immediately without attempting to communicate with
    the service until a timeout period elapses.
    """
    
    def __init__(self, threshold: int = CIRCUIT_BREAKER_THRESHOLD, timeout: int = CIRCUIT_BREAKER_TIMEOUT):
        self.threshold = threshold
        self.timeout = timeout
        self.failures = 0
        self.state = "closed"  # closed, open, half-open
        self.last_failure_time = None
        self.lock = threading.RLock()
        
    def can_execute(self) -> bool:
        """Check if the request can be executed based on the circuit state."""
        with self.lock:
            if self.state == "closed":
                return True
            
            if self.state == "open":
                if self.last_failure_time and time.time() - self.last_failure_time >= self.timeout:
                    self.state = "half-open"
                    logger.info(f"Circuit breaker transitioning from OPEN to HALF-OPEN after timeout")
                    return True
                return False
            
            # Half-open state: allow one request to test the service
            return True
    
    def record_success(self) -> None:
        """Record a successful request, which may reset the circuit breaker."""
        with self.lock:
            if self.state == "half-open":
                self.reset()
                logger.info("Circuit breaker reset to CLOSED after successful request")
                
    def record_failure(self) -> None:
        """Record a failed request, which may open the circuit breaker."""
        with self.lock:
            self.failures += 1
            self.last_failure_time = time.time()
            
            if self.state == "closed" and self.failures >= self.threshold:
                self.state = "open"
                logger.warning(f"Circuit breaker OPENED after {self.failures} consecutive failures")
            elif self.state == "half-open":
                self.state = "open"
                logger.warning("Circuit breaker reopened after failure in HALF-OPEN state")
                
    def reset(self) -> None:
        """Reset the circuit breaker to its initial closed state."""
        with self.lock:
            self.failures = 0
            self.state = "closed"
            self.last_failure_time = None


class RateLimiter:
    """
    Implements rate limiting to prevent overloading services.
    
    Tracks request timestamps and enforces a maximum number of requests
    within a specific time window.
    """
    
    def __init__(self, limit: int = DEFAULT_RATE_LIMIT, window: int = RATE_LIMIT_WINDOW):
        self.limit = limit
        self.window = window  # seconds
        self.timestamps = []
        self.lock = threading.RLock()
        
    def can_request(self) -> bool:
        """Check if a request can be made without exceeding the rate limit."""
        with self.lock:
            current_time = time.time()
            # Remove timestamps outside the current window
            self.timestamps = [ts for ts in self.timestamps if current_time - ts <= self.window]
            
            if len(self.timestamps) < self.limit:
                self.timestamps.append(current_time)
                return True
            return False
    
    def reset(self) -> None:
        """Reset the rate limiter."""
        with self.lock:
            self.timestamps = []


class AuditLogger:
    """
    Provides comprehensive audit logging for security-sensitive operations.
    
    Logs detailed information about authentication events, access attempts, 
    and other security-relevant activities.
    """
    
    def __init__(self, log_file: Optional[str] = None):
        self.logger = logging.getLogger("mcp-atlassian.audit")
        if log_file:
            try:
                handler = logging.FileHandler(log_file)
                formatter = logging.Formatter(
                    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                )
                handler.setFormatter(formatter)
                self.logger.addHandler(handler)
            except (IOError, PermissionError) as e:
                # Fall back to console logging if file cannot be created
                console_handler = logging.StreamHandler()
                formatter = logging.Formatter(
                    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                )
                console_handler.setFormatter(formatter)
                self.logger.addHandler(console_handler)
                self.logger.warning(f"Could not create log file {log_file}: {str(e)}. Falling back to console logging.")
        self.logger.setLevel(logging.INFO)
        
    def log_auth_event(self, event_type: str, user: str, success: bool, details: Optional[Dict] = None) -> None:
        """Log an authentication-related event."""
        log_data = {
            "event_type": event_type,
            "user": user,
            "success": success,
            "timestamp": datetime.now().isoformat(),
            "details": details or {}
        }
        
        if success:
            self.logger.info(f"Auth event: {event_type} for {user}", extra=log_data)
        else:
            self.logger.warning(f"Failed auth event: {event_type} for {user}", extra=log_data)
            
    def log_api_request(self, service: str, endpoint: str, method: str, 
                       status_code: Optional[int] = None, 
                       user: Optional[str] = None,
                       details: Optional[Dict] = None) -> None:
        """Log an API request for auditing purposes."""
        log_data = {
            "service": service,
            "endpoint": endpoint,
            "method": method,
            "status_code": status_code,
            "user": user,
            "timestamp": datetime.now().isoformat(),
            "details": details or {}
        }
        
        if status_code and 400 <= status_code < 600:
            self.logger.warning(f"API request failed: {method} {endpoint}", extra=log_data)
        else:
            self.logger.info(f"API request: {method} {endpoint}", extra=log_data)
            
    def log_security_event(self, event_type: str, severity: str, details: Dict) -> None:
        """Log a security-related event."""
        log_data = {
            "event_type": event_type,
            "severity": severity,
            "timestamp": datetime.now().isoformat(),
            "details": details
        }
        
        if severity.lower() == "high":
            self.logger.critical(f"Security event: {event_type}", extra=log_data)
        elif severity.lower() == "medium":
            self.logger.error(f"Security event: {event_type}", extra=log_data)
        else:
            self.logger.warning(f"Security event: {event_type}", extra=log_data)


class TokenManager:
    """
    Manages authentication tokens, including OAuth 2.0 tokens.
    
    Handles token acquisition, storage, refresh, and validation.
    """
    
    def __init__(self, audit_logger: Optional[AuditLogger] = None):
        self.tokens = {}
        self.lock = threading.RLock()
        self.audit_logger = audit_logger or AuditLogger()
        
    def get_token(self, service: str, user_id: str) -> Optional[Dict]:
        """Get a valid token for the specified service and user."""
        with self.lock:
            key = f"{service}:{user_id}"
            token_data = self.tokens.get(key)
            
            if not token_data:
                return None
                
            # Check if token is expired or about to expire
            if "expires_at" in token_data and token_data["expires_at"] < time.time() + 300:  # 5 min buffer
                # Token is expired or about to expire, try to refresh
                if "refresh_token" in token_data:
                    new_token_data = self._refresh_token(service, token_data)
                    if new_token_data:
                        self.tokens[key] = new_token_data
                        return new_token_data
                return None
                
            return token_data
            
    def store_token(self, service: str, user_id: str, token_data: Dict) -> None:
        """Store a token for later use."""
        with self.lock:
            # Calculate expiration time if not provided
            if "expires_at" not in token_data and "expires_in" in token_data:
                token_data["expires_at"] = time.time() + token_data["expires_in"]
                
            key = f"{service}:{user_id}"
            self.tokens[key] = token_data
            self.audit_logger.log_auth_event(
                "token_stored", 
                user_id, 
                True, 
                {"service": service}
            )
            
    def revoke_token(self, service: str, user_id: str) -> bool:
        """Revoke a token for the specified service and user."""
        with self.lock:
            key = f"{service}:{user_id}"
            if key in self.tokens:
                del self.tokens[key]
                self.audit_logger.log_auth_event(
                    "token_revoked", 
                    user_id, 
                    True, 
                    {"service": service}
                )
                return True
            return False
            
    def _refresh_token(self, service: str, token_data: Dict) -> Optional[Dict]:
        """Refresh an OAuth token using the refresh token."""
        if "refresh_token" not in token_data:
            return None
            
        # Implementation depends on the specific OAuth provider
        if service == "atlassian":
            try:
                # Atlassian-specific token refresh logic
                refresh_token = token_data["refresh_token"]
                client_id = os.environ.get("ATLASSIAN_CLIENT_ID")
                client_secret = os.environ.get("ATLASSIAN_CLIENT_SECRET")
                
                if not client_id or not client_secret:
                    logger.error("Missing Atlassian OAuth credentials")
                    return None
                    
                response = requests.post(
                    "https://YOUR-CREDENTIALS@YOUR-DOMAIN/rest/api/2/project/{project_key}/issues")
            return response.json()
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Look for credentials in environment variables
            if service.lower() == "jira":
                credentials = {
                    "username": os.environ.get("JIRA_USERNAME", ""),
                    "api_token": os.environ.get("JIRA_API_TOKEN", "")
                }
            elif service.lower() == "confluence":
                credentials = {
                    "username": os.environ.get("CONFLUENCE_USERNAME", ""),
                    "api_token": os.environ.get("CONFLUENCE_API_TOKEN", "")
                }
            elif service.lower() == "bitbucket":
                credentials = {
                    "username": os.environ.get("BITBUCKET_USERNAME", ""),
                    "app_password": os.environ.get("BITBUCKET_APP_PASSWORD", "")
                }
            else:
                raise ValueError(f"Unknown service: {service}")
                
            client = auth_manager.get_service_client(service, credentials)
            return func(client, *args, **kwargs)
        return wrapper
    return decorator