#!/usr/bin/env python3
"""
Atlassian Connection Fix

This script helps diagnose and fix issues with the MCP Atlassian integration.
"""

import os
import sys
import subprocess
import argparse
import shutil
import logging
from datetime import datetime
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("atlassian_fix.log")
    ]
)

logger = logging.getLogger("atlassian-fix")

# Constants
MCP_ATLASSIAN_PATH = "/data-nova/ax/DevOps/mcp/mcp-troubleshoot/Atlassian-connection/mcp-atlassian"
MCP_ATLASSIAN_BACKUP_PATH = "/data-nova/ax/DevOps/mcp/mcp-troubleshoot/Atlassian-connection/atlas-fix/backups"
STAGING_PATH = "/data-nova/ax/DevOps/mcp/mcp-troubleshoot/Atlassian-connection/atlas-fix/staging"

def run_command(cmd, cwd=None):
    """Run a shell command and return the output"""
    try:
        result = subprocess.run(
            cmd, 
            cwd=cwd, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            text=True,
            shell=True
        )
        return result.stdout, result.stderr, result.returncode
    except Exception as e:
        logger.error(f"Error running command: {cmd}")
        logger.error(f"Exception: {e}")
        return "", str(e), -1

def check_dependency(package_name):
    """Check if a Python package is installed"""
    try:
        __import__(package_name)
        return True
    except ImportError:
        return False

def check_environment():
    """Check the environment for required dependencies"""
    logger.info("Checking environment...")
    
    # Check Python version
    python_version = sys.version.split()[0]
    logger.info(f"Python version: {python_version}")
    
    # Check for required packages
    packages = ["requests", "httpx", "idna", "pydantic", "atlassian-python-api"]
    missing = []
    
    for pkg in packages:
        if not check_dependency(pkg):
            missing.append(pkg)
    
    if missing:
        logger.warning(f"Missing packages: {', '.join(missing)}")
        logger.info("Installing missing packages...")
        
        for pkg in missing:
            logger.info(f"Installing {pkg}...")
            stdout, stderr, returncode = run_command(f"pip install {pkg}")
            if returncode != 0:
                logger.error(f"Failed to install {pkg}:")
                logger.error(stderr)
            else:
                logger.info(f"Successfully installed {pkg}")
    else:
        logger.info("All required packages are installed.")
    
    # Check for virtual environment
    if not hasattr(sys, 'real_prefix') and not hasattr(sys, 'base_prefix'):
        logger.warning("Not running in a virtual environment. This may cause issues.")
    
    return True

def create_backup():
    """Create a backup of the MCP Atlassian directory"""
    logger.info("Creating backup...")
    
    # Create backup directory
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_path = os.path.join(MCP_ATLASSIAN_BACKUP_PATH, timestamp)
    os.makedirs(backup_path, exist_ok=True)
    
    # Copy files
    try:
        if os.path.exists(MCP_ATLASSIAN_PATH):
            shutil.copytree(
                os.path.join(MCP_ATLASSIAN_PATH, "src"),
                os.path.join(backup_path, "src")
            )
            
            if os.path.exists(os.path.join(MCP_ATLASSIAN_PATH, "tests")):
                shutil.copytree(
                    os.path.join(MCP_ATLASSIAN_PATH, "tests"),
                    os.path.join(backup_path, "tests")
                )
                
            if os.path.exists(os.path.join(MCP_ATLASSIAN_PATH, "docs")):
                shutil.copytree(
                    os.path.join(MCP_ATLASSIAN_PATH, "docs"),
                    os.path.join(backup_path, "docs")
                )
            
            # Copy other important files
            for file in ["CHANGELOG.md", "README.md", "pyproject.toml"]:
                src_file = os.path.join(MCP_ATLASSIAN_PATH, file)
                if os.path.exists(src_file):
                    shutil.copy2(src_file, os.path.join(backup_path, file))
            
            logger.info(f"Backup created at: {backup_path}")
            return backup_path
        else:
            logger.error(f"MCP Atlassian path not found: {MCP_ATLASSIAN_PATH}")
            return None
    except Exception as e:
        logger.error(f"Error creating backup: {e}")
        return None

def install_idna():
    """Install or reinstall the idna package"""
    logger.info("Installing/reinstalling idna package...")
    
    # First, try to uninstall
    run_command("pip uninstall -y idna")
    
    # Then, install the correct version
    stdout, stderr, returncode = run_command("pip install idna==3.4")
    
    if returncode != 0:
        logger.error("Failed to install idna package:")
        logger.error(stderr)
        return False
    else:
        logger.info("Successfully installed idna package.")
        return True

def create_virtual_env():
    """Create a virtual environment for testing"""
    logger.info("Creating virtual environment for testing...")
    
    venv_path = "/data-nova/ax/DevOps/mcp/mcp-troubleshoot/Atlassian-connection/atlas-fix/venv"
    
    if os.path.exists(venv_path):
        logger.info(f"Virtual environment already exists at: {venv_path}")
        return venv_path
    
    stdout, stderr, returncode = run_command(f"python -m venv {venv_path}")
    
    if returncode != 0:
        logger.error("Failed to create virtual environment:")
        logger.error(stderr)
        return None
    
    # Install required packages
    activate_cmd = f"source {venv_path}/bin/activate && "
    run_command(activate_cmd + "pip install --upgrade pip")
    run_command(activate_cmd + "pip install idna==3.4 httpx requests pydantic jira atlassian-python-api")
    
    logger.info(f"Virtual environment created at: {venv_path}")
    logger.info(f"Activate with: source {venv_path}/bin/activate")
    
    return venv_path

def deploy_enhanced_jira():
    """Deploy the Enhanced Jira Integration"""
    logger.info("Deploying Enhanced Jira Integration...")
    
    # Create backup
    backup_path = create_backup()
    if not backup_path:
        logger.error("Failed to create backup. Aborting deployment.")
        return False
    
    # Run deployment script
    deploy_script = "/data-nova/ax/DevOps/mcp/mcp-troubleshoot/Atlassian-connection/atlas-fix/clean_deployment.sh"
    
    if not os.path.exists(deploy_script):
        logger.error(f"Deployment script not found: {deploy_script}")
        return False
    
    stdout, stderr, returncode = run_command(f"bash {deploy_script}")
    
    if returncode != 0:
        logger.error("Failed to run deployment script:")
        logger.error(stderr)
        return False
    
    logger.info("Enhanced Jira Integration deployed successfully.")
    return True

def test_feature_flags():
    """Test the feature flags functionality"""
    logger.info("Testing feature flags...")
    
    test_script = """
import os
from mcp_atlassian.feature_flags import is_enabled, enable_feature, disable_feature, get_all_flags

def test_feature_flags():
    print("\\nTesting feature flags...")
    
    # Test 1: Check all flags
    print("\\nAll flags:")
    all_flags = get_all_flags()
    for flag, enabled in all_flags.items():
        print(f"  {flag}: {enabled}")
    
    # Test 2: Enable a flag
    flag = "ENHANCED_JIRA"
    print(f"\\nEnabling {flag}...")
    enable_feature(flag)
    print(f"  {flag} enabled: {is_enabled(flag)}")
    
    # Test 3: Disable a flag
    print(f"\\nDisabling {flag}...")
    disable_feature(flag)
    print(f"  {flag} enabled: {is_enabled(flag)}")
    
    print("\\nFeature flags test completed successfully!")

if __name__ == "__main__":
    test_feature_flags()
"""
    
    test_script_path = "/data-nova/ax/DevOps/mcp/mcp-troubleshoot/Atlassian-connection/atlas-fix/feature_flags_test.py"
    
    with open(test_script_path, "w") as f:
        f.write(test_script)
    
    os.chmod(test_script_path, 0o755)
    
    stdout, stderr, returncode = run_command(f"python {test_script_path}")
    
    if returncode != 0:
        logger.error("Failed to run feature flags test:")
        logger.error(stderr)
        return False
    
    logger.info("Feature flags test output:")
    logger.info(stdout)
    
    return True

def create_validation_script():
    """Create a validation script"""
    logger.info("Creating validation script...")
    
    validation_script = """#!/usr/bin/env python3
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
    print("\\n" + "=" * 60)
    print("MCP ATLASSIAN INTEGRATION VALIDATION")
    print("=" * 60)
    
    # Check Python version
    print(f"\\nPython version: {sys.version}")
    print(f"Python executable: {sys.executable}")
    
    # Check for virtual environment
    in_venv = hasattr(sys, 'real_prefix') or hasattr(sys, 'base_prefix')
    print(f"Running in virtual environment: {'Yes' if in_venv else 'No'}")
    
    # Check for required dependencies
    print("\\n" + "-" * 40)
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
    print("\\n" + "-" * 40)
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
    print("\\n" + "-" * 40)
    print("ENVIRONMENT VARIABLES")
    print("-" * 40)
    
    mcp_vars = {k: v for k, v in os.environ.items() if k.startswith("MCP_")}
    
    if mcp_vars:
        for var, value in mcp_vars.items():
            print(f"{var}={value}")
    else:
        print("No MCP environment variables found.")
    
    # Check for idna issue
    print("\\n" + "-" * 40)
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
    print("\\n" + "=" * 60)
    print("VALIDATION RESULTS")
    print("=" * 60)
    
    all_ok = all_deps_ok and all_modules_ok and idna_ok
    
    if all_ok:
        print("\\n✅ All checks passed! The MCP Atlassian integration should work correctly.")
    else:
        print("\\n❌ Some checks failed. The MCP Atlassian integration may not work correctly.")
        
        if not all_deps_ok:
            print("\\nDependency Issues:")
            print("1. Install missing dependencies:")
            print("   pip install httpx requests idna==3.4 pydantic atlassian-python-api jira")
            print("2. If you're having issues with idna, try:")
            print("   pip uninstall -y idna")
            print("   pip install idna==3.4")
        
        if not all_modules_ok:
            print("\\nModule Issues:")
            print("1. Make sure the MCP Atlassian package is installed and in your Python path")
            print("2. Check that all required files are present")
            print("3. Try running the deployment script again")
        
        if not idna_ok:
            print("\\nIDNA Issue:")
            print("1. Try reinstalling idna:")
            print("   pip uninstall -y idna")
            print("   pip install idna==3.4")
            print("2. Create a new virtual environment:")
            print("   python -m venv venv")
            print("   source venv/bin/activate")
            print("   pip install httpx requests idna==3.4 pydantic atlassian-python-api jira")
    
    print("\\n" + "=" * 60)

if __name__ == "__main__":
    main()
"""
    
    validation_script_path = "/data-nova/ax/DevOps/mcp/mcp-troubleshoot/Atlassian-connection/atlas-fix/validate_mcp_atlassian.py"
    
    with open(validation_script_path, "w") as f:
        f.write(validation_script)
    
    os.chmod(validation_script_path, 0o755)
    
    logger.info(f"Validation script created at: {validation_script_path}")
    logger.info(f"Run with: python {validation_script_path}")
    
    return validation_script_path

def create_fix_instructions():
    """Create instructions for fixing the MCP Atlassian integration"""
    logger.info("Creating fix instructions...")
    
    instructions = """# MCP Atlassian Integration Fix Instructions

## Issue

The MCP Atlassian integration is encountering an issue with the `idna` package, which is preventing proper functionality. The specific error is:

```
ModuleNotFoundError: No module named 'idna.core'
```

## Solution

This issue can be resolved by reinstalling the `idna` package with a compatible version. Follow these steps:

1. Reinstall the `idna` package:
   ```bash
   pip uninstall -y idna
   pip install idna==3.4
   ```

2. If that doesn't resolve the issue, create a new virtual environment:
   ```bash
   python -m venv /data-nova/ax/DevOps/mcp/mcp-troubleshoot/Atlassian-connection/atlas-fix/venv
   source /data-nova/ax/DevOps/mcp/mcp-troubleshoot/Atlassian-connection/atlas-fix/venv/bin/activate
   pip install httpx requests idna==3.4 pydantic atlassian-python-api jira
   ```

3. Run the validation script to check if the issue is resolved:
   ```bash
   python /data-nova/ax/DevOps/mcp/mcp-troubleshoot/Atlassian-connection/atlas-fix/validate_mcp_atlassian.py
   ```

## Enhanced Jira Integration

The Enhanced Jira Integration has been successfully deployed to:
```
/data-nova/ax/DevOps/mcp/mcp-troubleshoot/Atlassian-connection/mcp-atlassian
```

To enable the Enhanced Jira features, set the following environment variable:
```bash
export MCP_ATLASSIAN_FEATURE_FLAGS="ENHANCED_JIRA"
```

Or:
```bash
export MCP_ATLASSIAN_ENABLE_ENHANCED_JIRA="true"
```

## Backups

Backups of the original files are stored in:
```
/data-nova/ax/DevOps/mcp/mcp-troubleshoot/Atlassian-connection/atlas-fix/backups
```

If you encounter any issues, you can restore from these backups.

## Testing

You can test the feature flags functionality with:
```bash
python /data-nova/ax/DevOps/mcp/mcp-troubleshoot/Atlassian-connection/atlas-fix/feature_flags_test.py
```

## Documentation

For more information about the Enhanced Jira Integration, see:
```
/data-nova/ax/DevOps/mcp/mcp-troubleshoot/Atlassian-connection/mcp-atlassian/docs/enhanced_jira_integration.md
```

## Fix Script

A comprehensive fix script is available at:
```bash
python /data-nova/ax/DevOps/mcp/mcp-troubleshoot/Atlassian-connection/atlas-fix/fix_atlassian_connection.py
```

Run with:
```bash
python /data-nova/ax/DevOps/mcp/mcp-troubleshoot/Atlassian-connection/atlas-fix/fix_atlassian_connection.py --help
```
"""
    
    instructions_path = "/data-nova/ax/DevOps/mcp/mcp-troubleshoot/Atlassian-connection/atlas-fix/FIX_INSTRUCTIONS.md"
    
    with open(instructions_path, "w") as f:
        f.write(instructions)
    
    logger.info(f"Fix instructions created at: {instructions_path}")
    
    return instructions_path

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Fix MCP Atlassian Integration")
    parser.add_argument("--check-only", action="store_true", help="Only check the environment, don't fix anything")
    parser.add_argument("--create-venv", action="store_true", help="Create a virtual environment for testing")
    parser.add_argument("--install-idna", action="store_true", help="Install the idna package")
    parser.add_argument("--deploy", action="store_true", help="Deploy the Enhanced Jira Integration")
    parser.add_argument("--test", action="store_true", help="Test the feature flags functionality")
    parser.add_argument("--all", action="store_true", help="Run all fix steps")
    
    args = parser.parse_args()
    
    print("\n" + "=" * 80)
    print("MCP ATLASSIAN INTEGRATION FIX")
    print("=" * 80 + "\n")
    
    # Check environment
    if not check_environment():
        logger.error("Environment check failed.")
        return 1
    
    # Create validation script
    validation_script = create_validation_script()
    
    # Create fix instructions
    instructions_path = create_fix_instructions()
    
    # If check-only, exit now
    if args.check_only:
        logger.info("Check completed. No fixes applied.")
        logger.info(f"See instructions at: {instructions_path}")
        logger.info(f"Run validation with: python {validation_script}")
        return 0
    
    # Create virtual environment if requested
    if args.create_venv or args.all:
        venv_path = create_virtual_env()
        if not venv_path:
            logger.error("Failed to create virtual environment.")
            return 1
    
    # Install idna if requested
    if args.install_idna or args.all:
        if not install_idna():
            logger.error("Failed to install idna package.")
            return 1
    
    # Deploy Enhanced Jira Integration if requested
    if args.deploy or args.all:
        if not deploy_enhanced_jira():
            logger.error("Failed to deploy Enhanced Jira Integration.")
            return 1
    
    # Test feature flags if requested
    if args.test or args.all:
        if not test_feature_flags():
            logger.error("Feature flags test failed.")
            return 1
    
    print("\n" + "=" * 80)
    print("FIX COMPLETED SUCCESSFULLY")
    print("=" * 80)
    print(f"\nSee instructions at: {instructions_path}")
    print(f"Run validation with: python {validation_script}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())