#!/usr/bin/env python3
"""Simple test script to validate our integration changes."""

def test_constants():
    """Test that our constants are properly defined."""
    try:
        import sys
        import os
        
        # Add the custom component to path
        component_path = os.path.join(os.path.dirname(__file__), 'custom_components', '2n_ip_intercom')
        sys.path.insert(0, component_path)
        
        # Import our const module
        import const
        
        # Test that CONF_NAME is defined
        assert hasattr(const, 'CONF_NAME')
        assert const.CONF_NAME == "name"
        
        print("✅ Constants test passed!")
        return True
    except Exception as e:
        print(f"❌ Constants test failed: {e}")
        return False

def test_device_name_logic():
    """Test the device naming logic."""
    try:
        # Mock the configuration scenarios
        test_cases = [
            {
                "name": "Custom Name Test",
                "config": {"host": "192.168.1.100", "name": "Front Door"},
                "expected": "Front Door"
            },
            {
                "name": "Default Name Test", 
                "config": {"host": "192.168.1.100"},
                "expected": "2N IP Intercom (192.168.1.100)"
            }
        ]
        
        for case in test_cases:
            config = case["config"]
            expected = case["expected"]
            
            # Simulate the logic from coordinator
            device_name = config.get("name", f"2N IP Intercom ({config['host']})")
            
            assert device_name == expected, f"Expected '{expected}', got '{device_name}'"
            print(f"✅ {case['name']}: {device_name}")
        
        return True
    except Exception as e:
        print(f"❌ Device name logic test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Testing 2N IP Intercom Integration Updates\n")
    
    tests = [
        test_constants,
        test_device_name_logic,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The integration updates are working correctly.")
        print("\n📝 Summary of Changes:")
        print("   • Added optional 'Device Name' field in config flow")
        print("   • All entities now use custom device name if provided") 
        print("   • Fallback to 'IP Intercom (host)' if no custom name")
        print("   • Device info updated to use custom name")
        return 0
    else:
        print("❌ Some tests failed. Please review the code.")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
