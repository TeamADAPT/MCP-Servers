#!/usr/bin/env python3
"""
MCP Atlassian Connection Diagnostics

This script checks the health of your Atlassian connection and feature flags system.
It identifies and helps resolve common issues, particularly with the idna dependency.
"""

import os
import sys
import importlib.util
import subprocess
from pathlib import Path

# ANSI colors for terminal output
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BOLD = "\033[1m"
RESET = "\033[0m"

def print_header(text):
    print(f"\n{BOLD}{text}{RESET}")
    print("=" * len(text))

def print_success(text):
    print(f"{GREEN}✅ {text}{RESET}")

def print_warning(text):
    print(f"{YELLOW}⚠️ {text}{RESET}")

def print_error(text):
    print(f"{RED}❌ {text}{RESET}")

def check_module(name, file_path=None):
    """Check if a module can be imported"""
    if file_path:
        try:
            # Load module directly from file
            spec = importlib.util.spec_from_file_location(name, file_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return True, module, None
        except Exception as e:
            return False, None, str(e)
    else:
        try:
            # Try to import by name
            module = importlib.import_module(name)
            return True, module, None
        except ImportError as e:
            return False, None, str(e)
        except Exception as e:
            return False, None, str(e)

def check_idna():
    """Check if idna module is properly installed"""
    success, idna_module, error = check_module('idna')
    
    if not success:
        print_error(f"idna module is not installed: {error}")
        return False, None
    
    # Check for idna.core
    try:
        version = getattr(idna_module, '__version__', 'unknown')
        from idna.core import encode, decode
        print_success(f"idna module is properly installed (version: {version})")
        return True, version
    except ImportError:
        print_error("idna.core is missing - this is the root cause of most Atlassian connection issues")
        return False, version
    except Exception as e:
        print_error(f"Error accessing idna.core: {e}")
        return False, version

def check_feature_flags(mcp_dir):
    """Check the feature flags system"""
    feature_flags_path = os.path.join(mcp_dir, 'src', 'mcp_atlassian', 'feature_flags.py')
    
    if not os.path.exists(feature_flags_path):
        print_error(f"Feature flags module not found at {feature_flags_path}")
        return False
    
    success, ff_module, error = check_module('feature_flags', feature_flags_path)
    
    if not success:
        print_error(f"Failed to load feature flags module: {error}")
        return False
    
    # Check feature flags functionality
    try:
        # List all flags
        print("Available flags:")
        for flag in ff_module.ALL_FLAGS:
            print(f"  - {flag}")
        
        # Set an environment variable for testing
        os.environ["MCP_ATLASSIAN_FEATURE_FLAGS"] = "ENHANCED_JIRA"
        
        # Reset flags to pick up environment changes
        ff_module.reset_runtime_overrides()
        
        # Check if ENHANCED_JIRA is enabled
        if ff_module.is_enabled("ENHANCED_JIRA"):
            print_success("Feature flags system is working correctly")
            return True
        else:
            print_warning("Feature flags system loaded but not detecting environment variables")
            return False
    except Exception as e:
        print_error(f"Error testing feature flags functionality: {e}")
        return False

def check_directories():
    """Check if required directories exist"""
    dirs = {
        "Main directory": "/data-nova/ax/DevOps/mcp/mcp-troubleshoot/Atlassian-connection/mcp-atlassian",
        "Fix directory": "/data-nova/ax/DevOps/mcp/mcp-troubleshoot/Atlassian-connection/atlas-fix",
    }
    
    all_exist = True
    for name, path in dirs.items():
        if os.path.exists(path):
            print_success(f"{name} exists: {path}")
        else:
            print_error(f"{name} not found: {path}")
            all_exist = False
    
    return all_exist

def check_pip_packages():
    """Check if required pip packages are installed"""
    try:
        import pip
        import subprocess
        
        result = subprocess.run([sys.executable, "-m", "pip", "list"], 
                               capture_output=True, text=True)
        
        if result.returncode != 0:
            print_error(f"Failed to check pip packages: {result.stderr}")
            return False, {}
        
        packages = {}
        lines = result.stdout.strip().split('\n')
        # Skip the header rows
        for line in lines[2:]:
            parts = line.split()
            if parts:
                packages[parts[0].lower()] = parts[1] if len(parts) > 1 else "unknown"
        
        return True, packages
    except Exception as e:
        print_error(f"Error checking pip packages: {e}")
        return False, {}

def propose_solutions():
    """Propose solutions for common issues"""
    print_header("Recommended Solutions")
    
    print("""
1. Fix idna package issue:
   pip uninstall -y idna
   pip install idna==3.4

2. Run using a virtual environment:
   cd /data-nova/ax/DevOps/mcp/mcp-troubleshoot/Atlassian-connection/atlas-fix
   python -m venv venv-fix
   source venv-fix/bin/activate
   pip install idna==3.4 httpx requests pydantic atlassian-python-api jira

3. Configure feature flags:
   export MCP_ATLASSIAN_FEATURE_FLAGS="ENHANCED_JIRA"
   # or 
   export MCP_ATLASSIAN_ENABLE_ENHANCED_JIRA="true"

4. Run deployment script:
   cd /data-nova/ax/DevOps/mcp/mcp-troubleshoot/Atlassian-connection/atlas-fix
   ./clean_deployment_venv.sh
""")

def main():
    """Main diagnostic function"""
    print_header("MCP ATLASSIAN CONNECTION DIAGNOSTICS")
    
    # Check Python version
    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}")
    
    # Check if running in virtual environment
    in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    if in_venv:
        print_success("Running in a virtual environment")
    else:
        print_warning("Not running in a virtual environment - this may cause issues")
    
    # Check directories
    print_header("Directory Check")
    check_directories()
    
    # Check idna module
    print_header("IDNA Module Check")
    idna_ok, idna_version = check_idna()
    
    # Check for installed packages
    pip_ok, pip_packages = check_pip_packages()
    
    # Check for other Python dependencies
    print_header("Dependencies Check")
    dependencies = {
        "httpx": "httpx", 
        "requests": "requests", 
        "pydantic": "pydantic", 
        "atlassian-python-api": "atlassian_python_api", 
        "jira": "jira"
    }
    all_deps_ok = True
    
    for display_name, import_name in dependencies.items():
        success, _, error = check_module(import_name)
        
        # Special check for atlassian_python_api
        if not success and import_name == "atlassian_python_api":
            # Check if it's in pip packages
            if pip_ok and "atlassian-python-api" in pip_packages:
                print_success(f"{display_name} is installed (version: {pip_packages['atlassian-python-api']})")
                continue
        
        if success:
            print_success(f"{display_name} is installed")
        else:
            print_error(f"{display_name} is not installed: {error}")
            all_deps_ok = False
    
    # Check feature flags system
    print_header("Feature Flags Check")
    mcp_dir = "/data-nova/ax/DevOps/mcp/mcp-troubleshoot/Atlassian-connection/mcp-atlassian"
    ff_ok = check_feature_flags(mcp_dir)
    
    # Overall status
    print_header("Overall Status")
    if idna_ok and all_deps_ok and ff_ok:
        print_success("All checks passed! The MCP Atlassian connection should work correctly.")
    else:
        print_error("Some checks failed. The MCP Atlassian connection may not work correctly.")
        propose_solutions()
    
    return 0 if (idna_ok and all_deps_ok and ff_ok) else 1

if __name__ == "__main__":
    sys.exit(main())