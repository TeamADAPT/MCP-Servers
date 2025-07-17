#!/usr/bin/env python3
"""
Sanitize secrets from MCP configuration files before pushing to GitHub
"""
import json
import os
import shutil
import re

def sanitize_json_file(filepath, output_path):
    """Sanitize JSON file by replacing sensitive values with placeholders"""
    with open(filepath, 'r') as f:
        data = json.load(f)
    
    # Define sensitive keys to sanitize
    sensitive_keys = [
        'ANTHROPIC_API_KEY',
        'OPENAI_API_KEY',
        'PERPLEXITY_API_KEY',
        'JIRA_API_TOKEN',
        'CONFLUENCE_API_TOKEN',
        'JSM_API_TOKEN',
        'SLACK_TOKEN',
        'MONGODB_URI',
        'API_TOKEN',
        'API_KEY',
        'PASSWORD',
        'SECRET',
        'TOKEN',
        'KEY'
    ]
    
    def sanitize_value(key, value):
        """Replace sensitive values with placeholders"""
        if isinstance(value, dict):
            return {k: sanitize_value(k, v) for k, v in value.items()}
        elif isinstance(value, list):
            return [sanitize_value(key, v) for v in value]
        elif isinstance(value, str):
            # Check if the key matches sensitive patterns
            key_upper = key.upper()
            for sensitive in sensitive_keys:
                if sensitive in key_upper:
                    return f"YOUR_{sensitive}_HERE"
            
            # Check if the value looks like a credential
            if len(value) > 20 and (
                value.startswith('sk-') or 
                value.startswith('ATATT') or
                value.startswith('pplx-') or
                re.match(r'^[a-zA-Z0-9_\-]{40,}$', value)
            ):
                return "YOUR_API_KEY_HERE"
                
        return value
    
    # Sanitize the data
    sanitized_data = sanitize_value('root', data)
    
    # Write sanitized version
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(sanitized_data, f, indent=2)
    
    print(f"Sanitized {filepath} -> {output_path}")

def sanitize_shell_file(filepath, output_path):
    """Sanitize shell scripts by replacing export statements with placeholders"""
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Replace export statements with credentials
    patterns = [
        (r'export ANTHROPIC_API_KEY=YOUR-API-KEY-HERE 'export ANTHROPIC_API_KEY=YOUR-API-KEY-HERE
        (r'export OPENAI_API_KEY=YOUR-API-KEY-HERE 'export OPENAI_API_KEY=YOUR-API-KEY-HERE
        (r'export PERPLEXITY_API_KEY=YOUR-API-KEY-HERE 'export PERPLEXITY_API_KEY=YOUR-API-KEY-HERE
        (r'export JIRA_API_TOKEN=YOUR-API-TOKEN-HERE 'export JIRA_API_TOKEN=YOUR-API-TOKEN-HERE
        (r'export CONFLUENCE_API_TOKEN=YOUR-API-TOKEN-HERE 'export CONFLUENCE_API_TOKEN=YOUR-API-TOKEN-HERE
        (r'export JSM_API_TOKEN=YOUR-API-TOKEN-HERE 'export JSM_API_TOKEN=YOUR-API-TOKEN-HERE
        (r'export [A-Z_]*API_KEY=YOUR-API-KEY-HERE lambda m: f'{m.group(0).split("=")[0]}="YOUR_API_KEY_HERE"'),
        (r'export [A-Z_]*TOKEN="[^"]*"', lambda m: f'{m.group(0).split("=")[0]}="YOUR_TOKEN_HERE"'),
        (r'export [A-Z_]*SECRET="[^"]*"', lambda m: f'{m.group(0).split("=")[0]}="YOUR_SECRET_HERE"'),
    ]
    
    sanitized_content = content
    for pattern, replacement in patterns:
        if callable(replacement):
            sanitized_content = re.sub(pattern, replacement, sanitized_content)
        else:
            sanitized_content = re.sub(pattern, replacement, sanitized_content)
    
    # Write sanitized version
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        f.write(sanitized_content)
    
    # Preserve execute permissions if original had them
    if os.access(filepath, os.X_OK):
        os.chmod(output_path, os.stat(filepath).st_mode)
    
    print(f"Sanitized {filepath} -> {output_path}")

def main():
    """Main sanitization process"""
    # Create sanitized directory
    sanitized_dir = '/Threshold/TeamADAPT-mcp-servers-sanitized'
    if os.path.exists(sanitized_dir):
        shutil.rmtree(sanitized_dir)
    
    # Copy the entire repository first
    shutil.copytree('/Threshold/TeamADAPT-mcp-servers', sanitized_dir, 
                    ignore=shutil.ignore_patterns('.git', '.env', '*.log', '*venv*', 'node_modules', '__pycache__', '*.pyc', 'venv-*'),
                    symlinks=False)
    
    # Sanitize specific files
    files_to_sanitize = [
        ('claude-code-mcp-settings.json', 'json'),
        ('install.sh', 'shell'),
        ('atlassian-tricked-out/start_local.sh', 'shell'),
        ('atlassian-tricked-out/cline_mcp_settings.json', 'json'),
        ('atlassian-enterprise/cline_mcp_settings.json', 'json'),
        ('slack-mcp-server/config.json', 'json') if os.path.exists(os.path.join(sanitized_dir, 'slack-mcp-server/config.json')) else None,
    ]
    
    for file_info in files_to_sanitize:
        if file_info is None:
            continue
            
        filepath, filetype = file_info
        full_path = os.path.join('/Threshold/TeamADAPT-mcp-servers', filepath)
        output_path = os.path.join(sanitized_dir, filepath)
        
        if os.path.exists(full_path):
            if filetype == 'json':
                sanitize_json_file(full_path, output_path)
            elif filetype == 'shell':
                sanitize_shell_file(full_path, output_path)
    
    # Create .env.example file
    env_example = """# Atlassian
JIRA_URL=https://YOUR-CREDENTIALS@YOUR-DOMAIN//your-domain.atlassian.net/wiki
CONFLUENCE_USERNAME=your-email@example.com
CONFLUENCE_API_TOKEN=YOUR-API-TOKEN-HERE
JSM_URL=https://YOUR-CREDENTIALS@YOUR-DOMAIN//localhost:6379
"""
    
    with open(os.path.join(sanitized_dir, '.env.example'), 'w') as f:
        f.write(env_example)
    
    print(f"\nSanitized repository created at: {sanitized_dir}")
    print("Ready to push to GitHub!")

if __name__ == '__main__':
    main()