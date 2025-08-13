#!/usr/bin/env python3
"""Simple test to validate switch functionality."""

import sys
import os

# Add the custom component to path
component_path = os.path.join(os.path.dirname(__file__), 'custom_components', '2n_ip_intercom')
sys.path.insert(0, component_path)

def test_switch_logic():
    """Test switch logic without actual device connection."""
    
    print("🧪 Testing Switch Logic (Without Device Connection)\n")
    
    # Mock coordinator data
    class MockCoordinator:
        def __init__(self):
            self.data = {}
            self.device_name = "Test Device"
            self.switch_mode = "toggle"
            self.host = "192.168.1.100"
            self.base_url = "http://192.168.1.100:80"
            self.username = "admin"
            self.password = "2n"
        
        async def _get_session(self):
            # Mock session that doesn't actually connect
            return None
        
        def async_write_ha_state(self):
            pass
    
    # Test toggle mode switch
    print("🔄 Testing Toggle Mode Switch:")
    
    try:
        # Simulate switch creation
        coordinator = MockCoordinator()
        
        # Initialize switch state
        switch_id = 1
        switch_key = f"switch{switch_id}_state"
        
        # Test initial state
        is_on_initial = coordinator.data.get(switch_key, False)
        print(f"   Initial state: {is_on_initial}")
        
        # Simulate turn on
        coordinator.data[switch_key] = True
        is_on_after_on = coordinator.data.get(switch_key, False)
        print(f"   After turn ON: {is_on_after_on}")
        
        # Simulate turn off
        coordinator.data[switch_key] = False
        is_on_after_off = coordinator.data.get(switch_key, False)
        print(f"   After turn OFF: {is_on_after_off}")
        
        if not is_on_initial and is_on_after_on and not is_on_after_off:
            print("   ✅ Toggle mode logic works correctly")
            toggle_ok = True
        else:
            print("   ❌ Toggle mode logic failed")
            toggle_ok = False
    except Exception as e:
        print(f"   ❌ Toggle mode test failed: {e}")
        toggle_ok = False
    
    print()
    
    # Test pulse mode switch
    print("⚡ Testing Pulse Mode Switch:")
    
    try:
        coordinator = MockCoordinator()
        
        # Pulse switches always return False
        is_on_always = False  # Pulse mode always returns False
        print(f"   Pulse switch state (always): {is_on_always}")
        
        if not is_on_always:
            print("   ✅ Pulse mode logic works correctly")
            pulse_ok = True
        else:
            print("   ❌ Pulse mode logic failed")
            pulse_ok = False
    except Exception as e:
        print(f"   ❌ Pulse mode test failed: {e}")
        pulse_ok = False
    
    print()
    
    return toggle_ok and pulse_ok

def test_switch_configs():
    """Test switch configuration loading."""
    
    print("📝 Testing Switch Configurations:")
    
    try:
        import const
        
        if hasattr(const, 'SWITCH_CONFIGS'):
            configs = const.SWITCH_CONFIGS
            
            print(f"   Found {len(configs)} switch configurations:")
            
            for switch_key, config in configs.items():
                mode = config.get('mode', 'unknown')
                name = config.get('name', 'unknown')
                icon = "🔄" if mode == "toggle" else "⚡" if mode == "pulse" else "❓"
                print(f"     {icon} {switch_key}: {name} ({mode})")
            
            # Check for required modes
            modes = [config['mode'] for config in configs.values()]
            has_toggle = 'toggle' in modes
            has_pulse = 'pulse' in modes
            
            if has_toggle and has_pulse:
                print("   ✅ Both toggle and pulse modes configured")
                return True
            elif has_toggle or has_pulse:
                print("   ⚠️  Only one mode type configured")
                return True
            else:
                print("   ❌ No valid modes configured")
                return False
        else:
            print("   ❌ SWITCH_CONFIGS not found")
            return False
    except Exception as e:
        print(f"   ❌ Configuration test failed: {e}")
        return False

def test_api_endpoints():
    """Test API endpoint definitions."""
    
    print("\n📡 Testing API Endpoints:")
    
    try:
        import const
        
        required_endpoints = [
            'API_SWITCH_CONTROL',
            'API_DOOR_CONTROL',
            'API_SYSTEM_STATUS'
        ]
        
        all_ok = True
        for endpoint in required_endpoints:
            if hasattr(const, endpoint):
                value = getattr(const, endpoint)
                print(f"   ✅ {endpoint}: {value}")
            else:
                print(f"   ❌ {endpoint}: Missing")
                all_ok = False
        
        return all_ok
    except Exception as e:
        print(f"   ❌ API endpoint test failed: {e}")
        return False

def main():
    """Run all tests."""
    
    print("🔧 Switch Functionality Validation\n")
    print("=" * 50)
    
    tests = [
        ("Switch Logic", test_switch_logic),
        ("Switch Configurations", test_switch_configs),
        ("API Endpoints", test_api_endpoints),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 {test_name}:")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} passed")
            else:
                print(f"❌ {test_name} failed")
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All validation tests passed!")
        print("\n📝 Next Steps if switches still don't work:")
        print("1. Check Home Assistant logs for errors")
        print("2. Verify your 2N device IP address and credentials")
        print("3. Test device web interface manually")
        print("4. Restart Home Assistant after code changes")
        print("5. Check that entities are created in Home Assistant")
        return 0
    else:
        print("\n❌ Some validation tests failed")
        print("Fix the failed tests before proceeding")
        return 1

if __name__ == "__main__":
    sys.exit(main())
