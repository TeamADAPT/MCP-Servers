#!/usr/bin/env python3
'''
Validate MCP Atlassian Integration

This script validates the MCP Atlassian integration by checking for required
dependencies and modules.
'''

import sys
import os
import importlib.util
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("mcp-atlassian-validation")

def check_module(name, package=None):
    '''Check if a module can be imported'''
    try:
        if package:
            name = f"{package}.{name}"
        spec = importlib.util.find_spec(name)
        return spec is not None, None
    except ImportError as e:
        return False, str(e)
    except Exception as e:
        return False, str(e)

def check_dependency(name):
    '''Check if a dependency is installed'''
    return check_module(name)

def main():
    '''Main entry point'''
    print("\n" + "=" * 60)
    print("MCP ATLASSIAN INTEGRATION VALIDATION")
    print("=" * 60)
    
    # Check Python version
    print(f"\nPython version: {sys.version}")
    print(f"Python executable: {sys.executable}")
    
    # Check for virtual environment
    in_venv = hasattr(sys, 'real_prefix') or hasattr(sys, 'base_prefix')
    print(f"Running in virtual environment: {'Yes' if in_venv else 'No'}")
    
    # Check for required dependencies
    print("\n" + "-" * 40)
    print("DEPENDENCIES")
    print("-" * 40)
    
    dependencies = [
        "httpx",
        "requests",
        "idna",
        "pydantic",
        "atlassian-python-api",
        "jira",
    ]
    
    all_deps_ok = True
    
    for dep in dependencies:
        available, error = check_dependency(dep)
        status = "✅ Available" if available else "❌ Not available"
        print(f"{dep}: {status}")
        if error:
            print(f"  Error: {error}")
        if not available:
            all_deps_ok = False
    
    # Check for MCP Atlassian modules
    print("\n" + "-" * 40)
    print("MCP ATLASSIAN MODULES")
    print("-" * 40)
    
    modules = [
        "config",
        "jira",
        "confluence",
        "server",
        "enhanced_jira",
        "feature_flags",
        "server_enhanced_jira",
    ]
    
    all_modules_ok = True
    
    for module in modules:
        available, error = check_module(module, package="mcp_atlassian")
        status = "✅ Available" if available else "❌ Not available"
        print(f"{module}: {status}")
        if error:
            print(f"  Error: {error}")
        if not available:
            all_modules_ok = False
    
    # Check environment variables
    print("\n" + "-" * 40)
    print("ENVIRONMENT VARIABLES")
    print("-" * 40)
    
    mcp_vars = {k: v for k, v in os.environ.items() if k.startswith("MCP_")}
    
    if mcp_vars:
        for var, value in mcp_vars.items():
            print(f"{var}={value}")
    else:
        print("No MCP environment variables found.")
    
    # Check for idna issue
    print("\n" + "-" * 40)
    print("IDNA MODULE CHECK")
    print("-" * 40)
    
    try:
        import idna
        print(f"idna version: {idna.__version__}")
        try:
            from idna.core import encode, decode
            print("idna.core modules: ✅ Available")
            idna_ok = True
        except ImportError:
            print("idna.core modules: ❌ Not available")
            idna_ok = False
    except ImportError:
        print("idna module: ❌ Not available")
        idna_ok = False
    
    # Overall status
    print("\n" + "=" * 60)
    print("VALIDATION RESULTS")
    print("=" * 60)
    
    all_ok = all_deps_ok and all_modules_ok and idna_ok
    
    if all_ok:
        print("\n✅ All checks passed! The MCP Atlassian integration should work correctly.")
    else:
        print("\n❌ Some checks failed. The MCP Atlassian integration may not work correctly.")
        
        if not all_deps_ok:
            print("\nDependency Issues:")
            print("1. Install missing dependencies:")
            print("   pip install httpx requests idna==3.4 pydantic atlassian-python-api jira")
            print("2. If you're having issues with idna, try:")
            print("   pip uninstall -y idna")
            print("   pip install idna==3.4")
        
        if not all_modules_ok:
            print("\nModule Issues:")
            print("1. Make sure the MCP Atlassian package is installed and in your Python path")
            print("2. Check that all required files are present")
            print("3. Try running the deployment script again")
        
        if not idna_ok:
            print("\nIDNA Issue:")
            print("1. Try reinstalling idna:")
            print("   pip uninstall -y idna")
            print("   pip install idna==3.4")
            print("2. Create a new virtual environment:")
            print("   python -m venv venv")
            print("   source venv/bin/activate")
            print("   pip install httpx requests idna==3.4 pydantic atlassian-python-api jira")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
