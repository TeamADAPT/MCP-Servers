#!/usr/bin/env python3
import logging
import requests
import json
from typing import Dict, Optional, Any, Union
from dataclasses import dataclass
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('pulsar-mcp-client')

@dataclass
class PulsarResponse:
    """Structured response from Pulsar API"""
    status_code: int
    headers: Dict[str, str]
    content: Any
    timestamp: datetime

class PulsarClientError(Exception):
    """Base exception for Pulsar client errors"""
    pass

class PulsarConnectionError(PulsarClientError):
    """Connection-related errors"""
    pass

class PulsarTimeoutError(PulsarClientError):
    """Timeout-related errors"""
    pass

class PulsarAuthenticationError(PulsarClientError):
    """Authentication-related errors"""
    pass

class PulsarClient:
    """Client for interacting with Pulsar broker"""
    
    def __init__(
        self,
        host: str = 'localhost',
        port: int = 8083,
        token: str = None,
        timeout: int = 5,
        verify_ssl: bool = False
    ):
        """Initialize Pulsar client
        
        Args:
            host: Broker hostname
            port: Admin API port
            token: JWT token for authentication
            timeout: Request timeout in seconds
            verify_ssl: Whether to verify SSL certificates
        """
        self.base_url = f'http://{host}:{port}'
        self.token = token
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        self.session = requests.Session()
        
        if token:
            self.session.headers.update({
                'Authorization': f'Bearer {token}'
            })

    def _make_request(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> PulsarResponse:
        """Make HTTP request to Pulsar API
        
        Args:
            method: HTTP method
            endpoint: API endpoint
            **kwargs: Additional request parameters
            
        Returns:
            PulsarResponse object
            
        Raises:
            PulsarConnectionError: Connection failed
            PulsarTimeoutError: Request timed out
            PulsarAuthenticationError: Authentication failed
            PulsarClientError: Other client errors
        """
        url = f'{self.base_url}{endpoint}'
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                timeout=self.timeout,
                verify=self.verify_ssl,
                stream=False,
                **kwargs
            )
            
            if response.status_code == 401:
                raise PulsarAuthenticationError('Authentication failed')
                
            response.raise_for_status()
            
            # Handle empty responses
            content = None
            if response.text:
                try:
                    content = response.json()
                except ValueError:
                    content = response.text
            
            return PulsarResponse(
                status_code=response.status_code,
                headers=dict(response.headers),
                content=content,
                timestamp=datetime.now()
            )
            
        except requests.exceptions.Timeout as e:
            logger.error(f'Request timed out: {e}')
            raise PulsarTimeoutError(f'Request timed out: {e}')
            
        except requests.exceptions.ConnectionError as e:
            logger.error(f'Connection failed: {e}')
            raise PulsarConnectionError(f'Connection failed: {e}')
            
        except requests.exceptions.RequestException as e:
            logger.error(f'Request failed: {e}')
            raise PulsarClientError(f'Request failed: {e}')

    def check_health(self) -> PulsarResponse:
        """Check broker health status"""
        return self._make_request('GET', '/admin/v2/brokers/health')

    def list_clusters(self) -> PulsarResponse:
        """List all clusters"""
        return self._make_request('GET', '/admin/v2/clusters')

    def create_topic(self, topic: str) -> PulsarResponse:
        """Create a new topic
        
        Args:
            topic: Topic name (e.g., 'test')
        """
        # Remove any persistent:// prefix if present
        topic = topic.replace('persistent://', '')
        if not topic.startswith('public/default/'):
            topic = f'public/default/{topic}'
            
        return self._make_request('PUT', f'/admin/v2/persistent/{topic}')

    def delete_topic(self, topic: str) -> PulsarResponse:
        """Delete a topic
        
        Args:
            topic: Topic name (e.g., 'test')
        """
        # Remove any persistent:// prefix if present
        topic = topic.replace('persistent://', '')
        if not topic.startswith('public/default/'):
            topic = f'public/default/{topic}'
            
        return self._make_request('DELETE', f'/admin/v2/persistent/{topic}')

    def list_topics(self, namespace: str = 'public/default') -> PulsarResponse:
        """List all topics in a namespace
        
        Args:
            namespace: Namespace (default: public/default)
        """
        return self._make_request('GET', f'/admin/v2/persistent/{namespace}')

    def get_metrics(self) -> PulsarResponse:
        """Get broker metrics"""
        return self._make_request('GET', '/metrics')

    def send_message(self, topic: str, message: str) -> PulsarResponse:
        """Send a message to a topic
        
        Args:
            topic: Topic name (e.g., 'persistent://public/default/test')
            message: Message content (string)
        """
        # Remove any persistent:// prefix if present
        topic = topic.replace('persistent://', '')
        if not topic.startswith('public/default/'):
            topic = f'public/default/{topic}'
            
        return self._make_request(
            'POST',
            f'/admin/v2/persistent/{topic}/messages',
            data=message,
            headers={'Content-Type': 'application/json'}
        )

    def consume_message(
        self,
        topic: str,
        subscription: str = 'test-sub',
        timeout: int = 5
    ) -> Optional[str]:
        """Consume a message from a topic
        
        Args:
            topic: Topic name (e.g., 'persistent://public/default/test')
            subscription: Subscription name
            timeout: Timeout in seconds
            
        Returns:
            Message content or None if no message available
        """
        # Remove any persistent:// prefix if present
        topic = topic.replace('persistent://', '')
        if not topic.startswith('public/default/'):
            topic = f'public/default/{topic}'
            
        try:
            response = self._make_request(
                'GET',
                f'/admin/v2/persistent/{topic}/subscription/{subscription}/message',
                timeout=timeout
            )
            return response.content
        except PulsarClientError as e:
            if '404' in str(e):  # No message available
                return None
            raise

    def close(self):
        """Close client session"""
        self.session.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()