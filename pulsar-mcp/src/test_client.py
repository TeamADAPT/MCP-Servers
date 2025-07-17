#!/usr/bin/env python3
import logging
import sys
from client import PulsarClient, PulsarClientError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('pulsar-mcp-test')

def test_client():
    """Test Pulsar client functionality"""
    
    # JWT token from environment
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJtY3AtZGV2b3BzIiwicm9sZSI6ImFkbWluIiwiaWF0IjoxNzA4Njg0MjYzLCJleHAiOjE3MTY0NjAyNjN9"
    
    # Test cases
    tests = [
        ('Health Check', lambda c: c.check_health()),
        ('List Clusters', lambda c: c.list_clusters()),
        ('List Topics', lambda c: c.list_topics()),
        ('Get Metrics', lambda c: c.get_metrics()),
        ('Create Test Topic', lambda c: c.create_topic('test-topic')),
    ]
    
    success = True
    results = []
    
    # Run tests
    with PulsarClient(token=token) as client:
        for test_name, test_func in tests:
            try:
                logger.info(f'Running test: {test_name}')
                response = test_func(client)
                
                # Format content for display
                content = response.content
                if isinstance(content, str) and len(content) > 100:
                    content = content[:100] + '...'
                
                results.append({
                    'name': test_name,
                    'status': 'SUCCESS',
                    'status_code': response.status_code,
                    'content': content
                })
                
                logger.info(f'{test_name}: SUCCESS')
                logger.info(f'Status Code: {response.status_code}')
                logger.info(f'Content: {content}')
                
            except PulsarClientError as e:
                success = False
                results.append({
                    'name': test_name,
                    'status': 'FAILED',
                    'error': str(e)
                })
                logger.error(f'{test_name}: FAILED - {e}')
    
    # Print summary
    print('\nTest Summary:')
    print('=' * 50)
    for result in results:
        status = result['status']
        name = result['name']
        if status == 'SUCCESS':
            print(f'✓ {name}')
            print(f'  Status Code: {result["status_code"]}')
            print(f'  Content: {result["content"]}')
        else:
            print(f'✗ {name}')
            print(f'  Error: {result["error"]}')
        print('-' * 50)
    
    return 0 if success else 1

if __name__ == '__main__':
    try:
        sys.exit(test_client())
    except KeyboardInterrupt:
        logger.info('Tests interrupted')
        sys.exit(130)
    except Exception as e:
        logger.error(f'Unexpected error: {e}')
        sys.exit(1)