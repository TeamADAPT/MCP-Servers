#!/usr/bin/env python3
import json
import logging
import pulsar
from datetime import datetime
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('pulsar-mcp-messaging')

class PulsarMessaging:
    """Client for Pulsar messaging operations"""
    
    def __init__(
        self,
        service_url: str = 'pulsar://localhost:6650',
        token: str = None
    ):
        """Initialize Pulsar messaging client
        
        Args:
            service_url: Pulsar service URL
            token: JWT token for authentication
        """
        self.service_url = service_url
        self.token = token
        self.client = pulsar.Client(
            service_url,
            authentication=pulsar.AuthenticationToken(token) if token else None
        )
        self.producers = {}
        self.consumers = {}
        
        # Standard channels
        self.channels = {
            'team': 'persistent://public/default/team.mcp-devops.communication',
            'alerts': 'persistent://public/default/team.mcp-devops.channel.alerts',
            'bridge': 'persistent://public/default/teams.pulsar.mcp-devops.bridge'
        }

    def create_message(
        self,
        message_type: str,
        content: str,
        sender: str,
        priority: str = 'normal',
        metadata: Optional[Dict[str, str]] = None
    ) -> str:
        """Create a formatted message
        
        Args:
            message_type: Type of message
            content: Message content
            sender: Nova name of sender
            priority: Message priority (low, normal, high)
            metadata: Optional metadata dictionary
            
        Returns:
            JSON-encoded message string
        """
        message = {
            'type': message_type,
            'content': content,
            'sender': sender,
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'priority': priority,
            'metadata': metadata or {
                'team': 'mcp-devops',
                'context': 'integration'
            }
        }
        return json.dumps(message)

    def get_producer(self, topic: str) -> pulsar.Producer:
        """Get or create a producer for a topic
        
        Args:
            topic: Topic name
            
        Returns:
            Pulsar producer
        """
        if topic not in self.producers:
            self.producers[topic] = self.client.create_producer(topic)
        return self.producers[topic]

    def get_consumer(
        self,
        topic: str,
        subscription: str
    ) -> pulsar.Consumer:
        """Get or create a consumer for a topic
        
        Args:
            topic: Topic name
            subscription: Subscription name
            
        Returns:
            Pulsar consumer
        """
        key = f'{topic}:{subscription}'
        if key not in self.consumers:
            self.consumers[key] = self.client.subscribe(
                topic,
                subscription
            )
        return self.consumers[key]

    def send_message(
        self,
        channel: str,
        message_type: str,
        content: str,
        sender: str,
        priority: str = 'normal',
        metadata: Optional[Dict[str, str]] = None
    ) -> None:
        """Send a message to a channel
        
        Args:
            channel: Channel name (team, alerts, bridge)
            message_type: Type of message
            content: Message content
            sender: Nova name of sender
            priority: Message priority
            metadata: Optional metadata
        """
        topic = self.channels.get(channel)
        if not topic:
            raise ValueError(f'Unknown channel: {channel}')
            
        message = self.create_message(
            message_type,
            content,
            sender,
            priority,
            metadata
        )
        
        producer = self.get_producer(topic)
        producer.send(message.encode('utf-8'))
        
        logger.info(f'Message sent to {channel}: {message}')

    def receive_message(
        self,
        channel: str,
        subscription: str,
        timeout_ms: int = 5000
    ) -> Optional[Dict[str, Any]]:
        """Receive a message from a channel
        
        Args:
            channel: Channel name (team, alerts, bridge)
            subscription: Subscription name
            timeout_ms: Receive timeout in milliseconds
            
        Returns:
            Decoded message or None if no message available
        """
        topic = self.channels.get(channel)
        if not topic:
            raise ValueError(f'Unknown channel: {channel}')
            
        consumer = self.get_consumer(topic, subscription)
        
        try:
            msg = consumer.receive(timeout_millis=timeout_ms)
            message = json.loads(msg.data().decode('utf-8'))
            consumer.acknowledge(msg)
            
            logger.info(f'Message received from {channel}: {message}')
            return message
            
        except Exception as e:
            if 'timeout' not in str(e).lower():
                logger.error(f'Error receiving message: {e}')
            return None

    def close(self):
        """Close all producers, consumers and client"""
        for producer in self.producers.values():
            producer.close()
        for consumer in self.consumers.values():
            consumer.close()
        self.client.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()