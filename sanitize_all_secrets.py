#!/usr/bin/env python3
"""
Comprehensive sanitization script to remove all secrets from repository
"""
import os
import re
import json

def sanitize_file(filepath):
    """Sanitize secrets from a file"""
    try:
        with open(filepath, 'r') as f:
            content = f.read()
    except:
        return  # Skip binary files
    
    original = content
    
    # Replace API keys and tokens with more comprehensive patterns
    patterns = [
        # Anthropic API key
        (r'sk-ant-api03-[A-Za-z0-9\-_]+', 'sk-ant-api03-YOUR-ANTHROPIC-KEY-HERE'),
        # OpenAI API key
        (r'sk-proj-[A-Za-z0-9\-_]+', 'sk-proj-YOUR-OPENAI-KEY-HERE'),
        # Perplexity API key
        (r'pplx-[A-Za-z0-9]+', 'pplx-YOUR-PERPLEXITY-KEY-HERE-PERPLEXITY-KEY-HERE-PERPLEXITY-KEY-HERE'),
        # Atlassian API token (comprehensive pattern)
        (r'ATATT3xFfGF0[A-Za-z0-9\-_/+=]+', 'YOUR-ATLASSIAN-API-TOKEN-HERE'),
        # Generic API key patterns in JSON
        (r'"api_key":\s*"[^"]+', '"api_key": "YOUR-API-KEY-HERE"apiKey":\s*"[^"]+', '"apiKey": "YOUR-API-KEY-HERE"API_KEY":\s*"[^"]+', '"API_KEY": "YOUR-API-KEY-HERE"API_TOKEN":\s*"[^"]+', '"API_TOKEN": "YOUR-API-TOKEN-HERE"JIRA_API_TOKEN":\s*"ATATT[^"]+', '"JIRA_API_TOKEN": "YOUR_JIRA_API_TOKEN_HERE'),
        (r'"CONFLUENCE_API_TOKEN":\s*"ATATT[^"]+', '"CONFLUENCE_API_TOKEN": "YOUR_CONFLUENCE_API_TOKEN_HERE'),
        (r'"JSM_API_TOKEN":\s*"ATATT[^"]+', '"JSM_API_TOKEN": "YOUR_JSM_API_TOKEN_HERE'),
        # Shell script patterns
        (r'export JIRA_API_TOKEN=YOUR-API-TOKEN-HERE 'export JIRA_API_TOKEN=YOUR-API-TOKEN-HERE
        (r'export CONFLUENCE_API_TOKEN=YOUR-API-TOKEN-HERE 'export CONFLUENCE_API_TOKEN=YOUR-API-TOKEN-HERE
        (r'export JSM_API_TOKEN=YOUR-API-TOKEN-HERE 'export JSM_API_TOKEN=YOUR-API-TOKEN-HERE
        (r'API_KEY=YOUR-API-KEY-HERE 'API_KEY=YOUR-API-KEY-HERE
        (r'API_TOKEN=YOUR-API-TOKEN-HERE 'API_TOKEN=YOUR-API-TOKEN-HERE
        # URL patterns with embedded tokens
        (r'https://YOUR-CREDENTIALS@YOUR-DOMAIN/]+', 'https://YOUR-CREDENTIALS@YOUR-DOMAIN/Threshold/TeamADAPT-mcp-servers')
    
    print("🔍 Searching for and sanitizing secrets...")
    
    # First pass - sanitize all files
    count = find_and_sanitize_all()
    print(f"\n✅ Sanitized {count} files")
    
    # Double check for any remaining secrets
    print("\n🔍 Double-checking for remaining secrets...")
    
    remaining_secrets = []
    for root, dirs, files in os.walk('.'):
        if '.git' in root or 'node_modules' in root or 'venv' in root:
            continue
            
        for file in files:
            filepath = os.path.join(root, file)
            try:
                with open(filepath, 'r') as f:
                    content = f.read()
                    if 'ATATT3xFfGF0' in content or 'sk-ant-api03-' in content or 'sk-proj-' in content:
                        remaining_secrets.append(filepath)
            except:
                continue
    
    if remaining_secrets:
        print(f"\n⚠️  Found {len(remaining_secrets)} files still containing secrets:")
        for f in remaining_secrets:
            print(f"  - {f}")
        
        # Second pass on remaining files
        print("\n🔄 Running second sanitization pass...")
        for filepath in remaining_secrets:
            sanitize_file(filepath)
    else:
        print("\n✅ No remaining secrets found!")
    
    print("\n🎉 Sanitization complete! Repository is ready to push.")

if __name__ == "__main__":
    main()