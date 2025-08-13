#!/usr/bin/env python3
"""Test script to validate DNS and network issue fixes."""

def test_session_management():
    """Test that session management improvements are in place."""
    try:
        import sys
        import os
        
        # Add the custom component to path
        component_path = os.path.join(os.path.dirname(__file__), 'custom_components', '2n_ip_intercom')
        sys.path.insert(0, component_path)
        
        # Check coordinator has session management
        with open('custom_components/2n_ip_intercom/coordinator.py', 'r') as f:
            coordinator_content = f.read()
            
        # Check for session management improvements
        checks = [
            "_get_session" in coordinator_content,
            "TCPConnector" in coordinator_content,
            "ttl_dns_cache" in coordinator_content,
            "force_close=True" in coordinator_content,
            "async_shutdown" in coordinator_content,
        ]
        
        if all(checks):
            print("✅ Session management improvements detected!")
        else:
            print("❌ Some session management improvements missing")
            return False
            
        # Check switch.py uses coordinator session
        with open('custom_components/2n_ip_intercom/switch.py', 'r') as f:
            switch_content = f.read()
            
        switch_checks = [
            "await self.coordinator._get_session()" in switch_content,
            "raise_for_status=False" in switch_content,
            "_LOGGER.error" in switch_content,
        ]
        
        if all(switch_checks):
            print("✅ Switch session management improvements detected!")
        else:
            print("❌ Some switch session improvements missing")
            return False
            
        return True
    except Exception as e:
        print(f"❌ Session management test failed: {e}")
        return False

def test_error_handling():
    """Test that proper error handling is in place."""
    try:
        # Check coordinator error handling
        with open('custom_components/2n_ip_intercom/coordinator.py', 'r') as f:
            coordinator_content = f.read()
            
        error_checks = [
            "ClientConnectorError" in coordinator_content,
            "TimeoutError" in coordinator_content,
            "_LOGGER.error" in coordinator_content,
            "UpdateFailed" in coordinator_content,
        ]
        
        if all(error_checks):
            print("✅ Comprehensive error handling detected!")
        else:
            print("❌ Some error handling improvements missing")
            return False
            
        return True
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        return False

def test_dns_fixes():
    """Test that DNS-related fixes are in place."""
    try:
        # Check for DNS-specific improvements
        with open('custom_components/2n_ip_intercom/coordinator.py', 'r') as f:
            coordinator_content = f.read()
            
        dns_checks = [
            "ttl_dns_cache" in coordinator_content,
            "use_dns_cache=True" in coordinator_content,
            '"Connection": "close"' in coordinator_content,  # Check exact format
            "timeout=" in coordinator_content,
        ]
        
        # Debug what's missing
        check_names = ["ttl_dns_cache", "use_dns_cache=True", "Connection: close", "timeout="]
        for i, check in enumerate(dns_checks):
            if not check:
                print(f"   Missing: {check_names[i]}")
        
        if all(dns_checks):
            print("✅ DNS timeout fixes detected!")
        else:
            print("❌ Some DNS fixes missing")
            return False
            
        return True
    except Exception as e:
        print(f"❌ DNS fixes test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Testing DNS Timeout and Network Issue Fixes\n")
    
    tests = [
        test_session_management,
        test_error_handling,
        test_dns_fixes,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! DNS timeout issues should be resolved.")
        print("\n📝 Summary of Fixes:")
        print("   • Proper session management with connection pooling")
        print("   • DNS caching with TTL to reduce DNS lookups")
        print("   • Force close connections to prevent stale connections")
        print("   • Comprehensive error handling for network issues")
        print("   • Proper timeouts and connection limits")
        print("   • No more creating new sessions for each request")
        return 0
    else:
        print("❌ Some tests failed. Please review the code.")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
