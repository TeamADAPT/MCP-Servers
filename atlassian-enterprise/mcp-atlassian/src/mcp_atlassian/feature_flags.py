"""Feature Flag System for MCP Atlassian Integration.

This module provides a feature flag system to enable or disable specific
features in the MCP Atlassian integration. This allows for gradual enablement
of features in production.

Features can be enabled or disabled using environment variables, a config file, or at runtime.
The precedence order is:
1. Runtime toggle (highest priority)
2. Environment variable
3. Config file (if exists)
4. Default values (lowest priority)
"""

import os
import json
import logging
import time
from typing import Dict, Any, Optional, List, Set
from pathlib import Path

# Configure logging
logger = logging.getLogger("mcp-atlassian")

# Default feature flags - all disabled by default
DEFAULT_FLAGS = {
    # Core features
    "enhanced_jira": False,
    "enhanced_confluence": False,
    
    # JSM features
    "jsm": False,
    "jsm_approvals": False,
    "jsm_forms": False,
    "jsm_knowledge_base": False,
    "jsm_queue": False,
    
    # Bitbucket features
    "bitbucket": False,
    "bitbucket_integration": False,
    "bitbucket_pipeline": False,
    
    # Enhanced Confluence features
    "space_management": False,
    "template_management": False,
    "content_management": False,
    
    # Enterprise features
    "enterprise": False,
    "analytics": False,
    "ai_capabilities": False,
    "marketplace_integration": False,
}

# Feature dependencies - flags that will be auto-enabled when a parent feature is enabled
FEATURE_DEPENDENCIES = {
    "enhanced_jira": [],
    "enhanced_confluence": ["space_management", "template_management", "content_management"],
    "jsm": ["jsm_approvals", "jsm_forms", "jsm_knowledge_base", "jsm_queue"],
    "bitbucket": ["bitbucket_integration", "bitbucket_pipeline"],
    "enterprise": ["analytics", "ai_capabilities", "marketplace_integration"]
}

# Feature flag state
_feature_flags: Dict[str, bool] = {}
_runtime_overrides: Dict[str, bool] = {}
_last_config_check_time = 0
_config_file_path = os.getenv("FEATURE_FLAGS_CONFIG", "/etc/mcp-atlassian/feature_flags.json")


def _load_from_config_file() -> Dict[str, bool]:
    """Load feature flags from config file if it exists.
    
    Returns:
        Dict[str, bool]: Dictionary of feature flags from config file
    """
    if not os.path.exists(_config_file_path):
        return {}
    
    try:
        with open(_config_file_path, "r") as f:
            config = json.load(f)
        
        # Validate and filter config
        valid_flags = {}
        for flag_name, enabled in config.items():
            if flag_name in DEFAULT_FLAGS:
                if isinstance(enabled, bool):
                    valid_flags[flag_name] = enabled
                else:
                    logger.warning(f"Invalid value for feature flag '{flag_name}' in config file: {enabled}")
            else:
                logger.warning(f"Unknown feature flag '{flag_name}' in config file")
        
        return valid_flags
    except Exception as e:
        logger.error(f"Error loading feature flags from config file: {e}")
        return {}


def _check_config_file_changes():
    """Check if config file has changed and reload if needed."""
    global _last_config_check_time
    
    # Only check every 60 seconds
    current_time = time.time()
    if current_time - _last_config_check_time < 60:
        return
    
    _last_config_check_time = current_time
    
    if not os.path.exists(_config_file_path):
        return
    
    try:
        file_mtime = os.path.getmtime(_config_file_path)
        if file_mtime > _last_config_check_time:
            logger.info("Feature flags config file has changed, reloading")
            initialize_flags(reload=True)
    except Exception as e:
        logger.error(f"Error checking config file changes: {e}")


def _resolve_dependencies(enabled_flags: Set[str]) -> Set[str]:
    """Resolve dependencies for enabled flags.
    
    Args:
        enabled_flags: Set of initially enabled flags
        
    Returns:
        Set[str]: Set of all flags that should be enabled
    """
    result = enabled_flags.copy()
    
    # Process dependencies
    for flag_name in enabled_flags:
        if flag_name in FEATURE_DEPENDENCIES:
            for dependency in FEATURE_DEPENDENCIES[flag_name]:
                result.add(dependency)
                logger.debug(f"Auto-enabling dependency '{dependency}' for '{flag_name}'")
    
    return result


def initialize_flags(reload: bool = False) -> None:
    """Initialize feature flags from environment variables, config file, or defaults.
    
    Args:
        reload: Whether to force a reload of all flags
    """
    global _feature_flags
    
    if _feature_flags and not reload:
        return
    
    # Start with default flags
    _feature_flags = DEFAULT_FLAGS.copy()
    
    # Load from config file if it exists
    config_flags = _load_from_config_file()
    _feature_flags.update(config_flags)
    
    # Override with environment variables
    env_enabled_flags = set()
    for flag_name in _feature_flags:
        env_var_name = f"ENABLE_{flag_name.upper()}"
        if os.getenv(env_var_name, "").lower() in ["true", "1", "yes"]:
            _feature_flags[flag_name] = True
            env_enabled_flags.add(flag_name)
            logger.info(f"Feature flag {flag_name} enabled from environment")
    
    # Resolve dependencies for environment-enabled flags
    auto_enabled = _resolve_dependencies(env_enabled_flags)
    for flag_name in auto_enabled:
        if flag_name in _feature_flags and flag_name not in env_enabled_flags:
            _feature_flags[flag_name] = True
            logger.info(f"Feature flag {flag_name} auto-enabled as dependency")
    
    # Apply runtime overrides
    for flag_name, enabled in _runtime_overrides.items():
        if flag_name in _feature_flags:
            _feature_flags[flag_name] = enabled
    
    # Log the final state
    enabled_flags = [name for name, enabled in _feature_flags.items() if enabled]
    logger.info(f"Feature flags initialized. Enabled flags: {', '.join(enabled_flags) if enabled_flags else 'None'}")


def is_enabled(feature_name: str) -> bool:
    """Check if a feature is enabled.
    
    Args:
        feature_name: The name of the feature to check
        
    Returns:
        bool: True if the feature is enabled, False otherwise
    """
    if not _feature_flags:
        initialize_flags()
    else:
        # Periodically check for config file changes
        _check_config_file_changes()
    
    if feature_name not in _feature_flags:
        logger.warning(f"Unknown feature flag '{feature_name}', defaulting to disabled")
        return False
    
    return _feature_flags[feature_name]


def enable_feature(feature_name: str) -> bool:
    """Enable a feature at runtime.
    
    Args:
        feature_name: The name of the feature to enable
        
    Returns:
        bool: True if the feature was enabled, False if it doesn't exist
    """
    if not _feature_flags:
        initialize_flags()
    
    if feature_name not in _feature_flags:
        logger.warning(f"Cannot enable unknown feature '{feature_name}'")
        return False
    
    # Set runtime override
    _runtime_overrides[feature_name] = True
    _feature_flags[feature_name] = True
    
    # Auto-enable dependencies
    if feature_name in FEATURE_DEPENDENCIES:
        for dependency in FEATURE_DEPENDENCIES[feature_name]:
            if dependency in _feature_flags:
                _runtime_overrides[dependency] = True
                _feature_flags[dependency] = True
                logger.info(f"Feature '{dependency}' auto-enabled as dependency of '{feature_name}'")
    
    logger.info(f"Feature '{feature_name}' enabled at runtime")
    return True


def disable_feature(feature_name: str) -> bool:
    """Disable a feature at runtime.
    
    Args:
        feature_name: The name of the feature to disable
        
    Returns:
        bool: True if the feature was disabled, False if it doesn't exist
    """
    if not _feature_flags:
        initialize_flags()
    
    if feature_name not in _feature_flags:
        logger.warning(f"Cannot disable unknown feature '{feature_name}'")
        return False
    
    # Check if this feature is a dependency for other enabled features
    dependent_features = []
    for parent, dependencies in FEATURE_DEPENDENCIES.items():
        if feature_name in dependencies and is_enabled(parent):
            dependent_features.append(parent)
    
    if dependent_features:
        logger.warning(f"Cannot disable feature '{feature_name}' as it is a dependency for: {', '.join(dependent_features)}")
        return False
    
    # Set runtime override
    _runtime_overrides[feature_name] = False
    _feature_flags[feature_name] = False
    
    logger.info(f"Feature '{feature_name}' disabled at runtime")
    return True


def get_all_flags() -> Dict[str, bool]:
    """Get all feature flags and their states.
    
    Returns:
        Dict[str, bool]: Dictionary of all feature flags and their states
    """
    if not _feature_flags:
        initialize_flags()
    else:
        # Periodically check for config file changes
        _check_config_file_changes()
    
    return _feature_flags.copy()


def get_feature_groups() -> Dict[str, List[str]]:
    """Get all feature flags organized by feature groups.
    
    Returns:
        Dict[str, List[str]]: Dictionary of feature groups and their flags
    """
    feature_groups = {
        "core": ["enhanced_jira", "enhanced_confluence"],
        "jira": ["enhanced_jira"],
        "confluence": ["enhanced_confluence", "space_management", "template_management", "content_management"],
        "jsm": ["jsm", "jsm_approvals", "jsm_forms", "jsm_knowledge_base", "jsm_queue"],
        "bitbucket": ["bitbucket", "bitbucket_integration", "bitbucket_pipeline"],
        "enterprise": ["enterprise", "analytics", "ai_capabilities", "marketplace_integration"]
    }
    
    return feature_groups


def reset_runtime_overrides() -> None:
    """Reset all runtime overrides, reverting to config file and environment settings."""
    global _runtime_overrides
    
    _runtime_overrides = {}
    initialize_flags(reload=True)
    
    logger.info("Runtime feature flag overrides have been reset")


def save_current_flags_to_config() -> bool:
    """Save current feature flag state to config file.
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Make sure config directory exists
        config_dir = os.path.dirname(_config_file_path)
        if config_dir and not os.path.exists(config_dir):
            os.makedirs(config_dir)
        
        with open(_config_file_path, "w") as f:
            json.dump(_feature_flags, f, indent=2)
        
        logger.info(f"Feature flags saved to config file: {_config_file_path}")
        return True
    except Exception as e:
        logger.error(f"Error saving feature flags to config file: {e}")
        return False


# Initialize flags when module is loaded
initialize_flags()