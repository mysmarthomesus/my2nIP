#!/usr/bin/env python3
"""Test script to validate the 2N IP Intercom integration."""

import sys
import os

# Add the custom_components path to sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'custom_components'))

def test_imports():
    """Test that all modules can be imported."""
    try:
        from 2n_ip_intercom import const
        from 2n_ip_intercom import coordinator
        from 2n_ip_intercom import config_flow
        from 2n_ip_intercom import camera
        from 2n_ip_intercom import switch
        from 2n_ip_intercom import sensor
        print("✅ All imports successful!")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_config_schema():
    """Test the config flow schema."""
    try:
        from custom_components.two_n_ip_intercom.config_flow import ConfigFlow
        from custom_components.two_n_ip_intercom.const import CONF_NAME
        from homeassistant.const import CONF_HOST, CONF_PORT, CONF_USERNAME, CONF_PASSWORD
        
        # Test that CONF_NAME is properly defined
        assert CONF_NAME == "name"
        print("✅ Configuration constants defined correctly!")
        return True
    except Exception as e:
        print(f"❌ Config schema test failed: {e}")
        return False

def test_coordinator_device_name():
    """Test that coordinator handles device names correctly."""
    try:
        from custom_components.two_n_ip_intercom.coordinator import TwoNIntercomDataUpdateCoordinator
        from custom_components.two_n_ip_intercom.const import CONF_NAME
        from homeassistant.const import CONF_HOST
        
        # Mock HomeAssistant object for testing
        class MockHass:
            pass
        
        # Test with custom name
        config_with_name = {
            CONF_HOST: "192.168.1.100",
            CONF_NAME: "Front Door Intercom"
        }
        hass_mock = MockHass()
        coordinator = TwoNIntercomDataUpdateCoordinator(hass_mock, config_with_name)
        assert coordinator.device_name == "Front Door Intercom"
        
        # Test without custom name (default)
        config_without_name = {
            CONF_HOST: "192.168.1.100"
        }
        coordinator2 = TwoNIntercomDataUpdateCoordinator(hass_mock, config_without_name)
        assert coordinator2.device_name == "2N IP Intercom (192.168.1.100)"
        
        print("✅ Coordinator device naming works correctly!")
        return True
    except Exception as e:
        print(f"❌ Coordinator test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Testing 2N IP Intercom Integration\n")
    
    tests = [
        test_imports,
        test_config_schema,
        test_coordinator_device_name,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The integration is ready to use.")
        return 0
    else:
        print("❌ Some tests failed. Please review the code.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
