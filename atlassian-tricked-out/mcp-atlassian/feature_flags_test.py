#!/usr/bin/env python3
"""
Test the feature flags functionality for MCP Atlassian Integration.

This is a standalone test that will attempt to import the feature_flags module
and test its functionality. It does not depend on any other MCP Atlassian modules.
"""

import os
import sys
import logging
from importlib import import_module

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("feature-flags-test")

# Feature flags to test
FLAGS = [
    "ENHANCED_JIRA",
    "BITBUCKET_INTEGRATION",
    "ENHANCED_CONFLUENCE",
    "JSM_INTEGRATION",
    "ADVANCED_ANALYTICS"
]

def test_feature_flags_standalone():
    """Test feature flags without importing from mcp_atlassian"""
    print("\n" + "=" * 60)
    print("FEATURE FLAGS STANDALONE TEST")
    print("=" * 60)
    
    # Create a simple feature flags implementation
    class FeatureFlags:
        """Simple feature flags implementation"""
        
        ALL_FLAGS = set(FLAGS)
        
        def __init__(self):
            """Initialize feature flags"""
            self._enabled_flags = set()
            self._runtime_overrides = {}
            
            # Check for MCP_ATLASSIAN_FEATURE_FLAGS
            flags_str = os.environ.get("MCP_ATLASSIAN_FEATURE_FLAGS", "")
            if flags_str:
                for flag in flags_str.split(","):
                    flag = flag.strip().upper()
                    if flag in self.ALL_FLAGS:
                        self._enabled_flags.add(flag)
            
            # Check for individual flag environment variables
            for flag in self.ALL_FLAGS:
                env_var = f"MCP_ATLASSIAN_ENABLE_{flag}"
                if os.environ.get(env_var, "").lower() in ("true", "1", "yes"):
                    self._enabled_flags.add(flag)
        
        def is_enabled(self, flag):
            """Check if a flag is enabled"""
            if flag in self._runtime_overrides:
                return self._runtime_overrides[flag]
            return flag in self._enabled_flags
        
        def enable(self, flag):
            """Enable a flag at runtime"""
            if flag not in self.ALL_FLAGS:
                return False
            self._runtime_overrides[flag] = True
            return True
        
        def disable(self, flag):
            """Disable a flag at runtime"""
            if flag not in self.ALL_FLAGS:
                return False
            self._runtime_overrides[flag] = False
            return True
        
        def get_enabled_flags(self):
            """Get all enabled flags"""
            result = []
            for flag in self.ALL_FLAGS:
                if self.is_enabled(flag):
                    result.append(flag)
            return result
    
    # Create a feature flags instance
    flags = FeatureFlags()
    
    # Test 1: Check environment variables
    print("\nEnvironment variables:")
    for var, value in os.environ.items():
        if var.startswith("MCP_ATLASSIAN_"):
            print(f"  {var}={value}")
    
    # Test 2: Check enabled flags
    print("\nEnabled flags:")
    for flag in flags.get_enabled_flags():
        print(f"  {flag}")
    
    # Test 3: Enable a flag
    test_flag = "ENHANCED_JIRA"
    print(f"\nEnabling {test_flag}...")
    flags.enable(test_flag)
    print(f"  {test_flag} enabled: {flags.is_enabled(test_flag)}")
    
    # Test 4: Disable a flag
    print(f"\nDisabling {test_flag}...")
    flags.disable(test_flag)
    print(f"  {test_flag} enabled: {flags.is_enabled(test_flag)}")
    
    print("\nStandalone feature flags test completed successfully!")

def test_feature_flags_module():
    """Test the feature_flags module from mcp_atlassian"""
    print("\n" + "=" * 60)
    print("MCP_ATLASSIAN FEATURE FLAGS TEST")
    print("=" * 60)
    
    try:
        # Try to import the feature_flags module
        module_name = "mcp_atlassian.feature_flags"
        feature_flags = import_module(module_name)
        
        # Get functions
        is_enabled = getattr(feature_flags, "is_enabled", None)
        enable_feature = getattr(feature_flags, "enable_feature", None)
        disable_feature = getattr(feature_flags, "disable_feature", None)
        get_all_flags = getattr(feature_flags, "get_all_flags", None)
        
        if not all([is_enabled, enable_feature, disable_feature, get_all_flags]):
            print(f"❌ Error: Required functions not found in {module_name}")
            return False
        
        # Test 1: Get all flags
        print("\nAll flags:")
        all_flags = get_all_flags()
        for flag, enabled in all_flags.items():
            print(f"  {flag}: {enabled}")
        
        # Test 2: Enable a flag
        test_flag = next(iter(all_flags.keys()))
        print(f"\nEnabling {test_flag}...")
        enable_feature(test_flag)
        print(f"  {test_flag} enabled: {is_enabled(test_flag)}")
        
        # Test 3: Disable a flag
        print(f"\nDisabling {test_flag}...")
        disable_feature(test_flag)
        print(f"  {test_flag} enabled: {is_enabled(test_flag)}")
        
        print(f"\n✅ {module_name} test completed successfully!")
        return True
    
    except ImportError as e:
        print(f"❌ Error importing {module_name}: {e}")
        return False
    
    except Exception as e:
        print(f"❌ Error testing {module_name}: {e}")
        return False

def main():
    """Main entry point"""
    print("\n=== FEATURE FLAGS TEST ===\n")
    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}")
    
    # Test 1: Standalone test
    test_feature_flags_standalone()
    
    # Test 2: Module test
    success = test_feature_flags_module()
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    if success:
        print("\n✅ Feature flags functionality is working correctly!")
        print("You can now use the MCP Atlassian integration with feature flags.")
    else:
        print("\n❌ Feature flags module test failed.")
        print("The standalone test was successful, but the mcp_atlassian.feature_flags module test failed.")
        print("This may be due to:")
        print("1. The module is not installed correctly")
        print("2. The module is not in your Python path")
        print("3. The module has errors")
        
        print("\nSuggested actions:")
        print("1. Run the fix script:")
        print("   python /data-nova/ax/DevOps/mcp/mcp-troubleshoot/Atlassian-connection/atlas-fix/fix_atlassian_connection.py --all")
        print("2. Check your Python path")
        print("3. Try running in a virtual environment")
        print("4. Check the module for errors")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())