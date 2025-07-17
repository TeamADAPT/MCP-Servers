#!/usr/bin/env python3
import logging
import sys
import time
from messaging import PulsarMessaging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('pulsar-mcp-test-messaging')

def test_messaging():
    """Test Pulsar messaging functionality"""
    
    # JWT token from environment
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJtY3AtZGV2b3BzIiwicm9sZSI6ImFkbWluIiwiaWF0IjoxNzA4Njg0MjYzLCJleHAiOjE3MTY0NjAyNjN9"
    
    # Test cases
    tests = [
        {
            'name': 'Team Channel',
            'channel': 'team',
            'subscription': 'mcp-devops-team',
            'message': {
                'type': 'test',
                'content': 'Team channel test message',
                'sender': 'Genesis',
                'priority': 'normal',
                'metadata': {
                    'team': 'mcp-devops',
                    'context': 'integration-test',
                    'correlationId': f'test-team-{int(time.time())}'
                }
            }
        },
        {
            'name': 'Alerts Channel',
            'channel': 'alerts',
            'subscription': 'mcp-devops-alerts',
            'message': {
                'type': 'test',
                'content': 'Alerts channel test message',
                'sender': 'Genesis',
                'priority': 'high',
                'metadata': {
                    'team': 'mcp-devops',
                    'context': 'integration-test',
                    'correlationId': f'test-alerts-{int(time.time())}'
                }
            }
        },
        {
            'name': 'Bridge Channel',
            'channel': 'bridge',
            'subscription': 'mcp-devops-bridge',
            'message': {
                'type': 'test',
                'content': 'Bridge channel test message',
                'sender': 'Genesis',
                'priority': 'normal',
                'metadata': {
                    'team': 'mcp-devops',
                    'context': 'integration-test',
                    'correlationId': f'test-bridge-{int(time.time())}'
                }
            }
        }
    ]
    
    success = True
    results = []
    
    # Run tests
    with PulsarMessaging(service_url='pulsar://localhost:6650', token=token) as messaging:
        for test in tests:
            try:
                logger.info(f'Testing {test["name"]}')
                
                # Send message
                messaging.send_message(
                    test['channel'],
                    test['message']['type'],
                    test['message']['content'],
                    test['message']['sender'],
                    test['message']['priority'],
                    test['message']['metadata']
                )
                
                # Receive message
                received = messaging.receive_message(
                    test['channel'],
                    test['subscription']
                )
                
                if not received:
                    raise Exception('No message received')
                
                results.append({
                    'name': test['name'],
                    'status': 'SUCCESS',
                    'sent': test['message'],
                    'received': received
                })
                
                logger.info(f'{test["name"]}: SUCCESS')
                logger.info(f'Sent: {test["message"]}')
                logger.info(f'Received: {received}')
                
            except Exception as e:
                success = False
                results.append({
                    'name': test['name'],
                    'status': 'FAILED',
                    'error': str(e)
                })
                logger.error(f'{test["name"]}: FAILED - {e}')
    
    # Print summary
    print('\nTest Summary:')
    print('=' * 50)
    for result in results:
        status = result['status']
        name = result['name']
        if status == 'SUCCESS':
            print(f'✓ {name}')
            print(f'  Sent: {result["sent"]}')
            print(f'  Received: {result["received"]}')
        else:
            print(f'✗ {name}')
            print(f'  Error: {result["error"]}')
        print('-' * 50)
    
    return 0 if success else 1

if __name__ == '__main__':
    try:
        sys.exit(test_messaging())
    except KeyboardInterrupt:
        logger.info('Tests interrupted')
        sys.exit(130)
    except Exception as e:
        logger.error(f'Unexpected error: {e}')
        sys.exit(1)
