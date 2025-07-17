"""Tests for the feature_flags module."""

import os
import pytest
from unittest import mock

from src.mcp_atlassian.feature_flags import (
    initialize_flags,
    is_enabled,
    enable_feature,
    disable_feature,
    get_all_flags,
    DEFAULT_FLAGS,
    _feature_flags,
)


@pytest.fixture
def reset_feature_flags():
    """Reset feature flags to their default state before each test."""
    global _feature_flags
    _feature_flags.clear()
    # Clear any environment variables that might affect tests
    for key in list(os.environ.keys()):
        if key.startswith("ENABLE_"):
            del os.environ[key]
    yield
    # Clean up after tests
    _feature_flags.clear()


def test_initialize_flags_defaults(reset_feature_flags):
    """Test that initialize_flags sets default values correctly."""
    initialize_flags()
    assert _feature_flags == DEFAULT_FLAGS


def test_initialize_flags_from_env(reset_feature_flags):
    """Test that initialize_flags reads from environment variables."""
    with mock.patch.dict(os.environ, {"ENABLE_JSM": "true", "ENABLE_BITBUCKET": "1"}):
        initialize_flags()
        assert _feature_flags["jsm"] is True
        assert _feature_flags["bitbucket"] is True
        assert _feature_flags["enhanced_jira"] is False  # Default unchanged


def test_is_enabled(reset_feature_flags):
    """Test that is_enabled returns the correct flag value."""
    initialize_flags()
    assert is_enabled("jsm") is False
    
    _feature_flags["jsm"] = True
    assert is_enabled("jsm") is True


def test_is_enabled_unknown_feature(reset_feature_flags):
    """Test that is_enabled handles unknown features gracefully."""
    initialize_flags()
    assert is_enabled("nonexistent_feature") is False


def test_enable_feature(reset_feature_flags):
    """Test enabling a feature."""
    initialize_flags()
    assert _feature_flags["jsm"] is False
    
    result = enable_feature("jsm")
    assert result is True
    assert _feature_flags["jsm"] is True


def test_enable_unknown_feature(reset_feature_flags):
    """Test enabling an unknown feature."""
    initialize_flags()
    result = enable_feature("nonexistent_feature")
    assert result is False


def test_disable_feature(reset_feature_flags):
    """Test disabling a feature."""
    initialize_flags()
    _feature_flags["jsm"] = True
    
    result = disable_feature("jsm")
    assert result is True
    assert _feature_flags["jsm"] is False


def test_disable_unknown_feature(reset_feature_flags):
    """Test disabling an unknown feature."""
    initialize_flags()
    result = disable_feature("nonexistent_feature")
    assert result is False


def test_get_all_flags(reset_feature_flags):
    """Test getting all feature flags."""
    initialize_flags()
    flags = get_all_flags()
    assert flags == DEFAULT_FLAGS
    
    # Ensure we get a copy, not the original
    flags["jsm"] = True
    assert _feature_flags["jsm"] is False