#!/usr/bin/env python3
"""Debug test script to identify switch issues."""

import asyncio
import aiohttp
import sys
import os
import json

# Add the custom component to path
component_path = os.path.join(os.path.dirname(__file__), 'custom_components', '2n_ip_intercom')
sys.path.insert(0, component_path)

async def test_switch_endpoints():
    """Test actual 2N device endpoints."""
    
    print("🔧 Testing 2N Device Switch Endpoints\n")
    
    # You'll need to update these with your actual device details
    device_config = {
        "host": "192.168.1.100",  # Update with your device IP
        "port": 80,
        "username": "admin",      # Update with your username
        "password": "2n"          # Update with your password
    }
    
    base_url = f"http://{device_config['host']}:{device_config['port']}"
    
    print(f"Testing device at: {base_url}")
    print(f"Username: {device_config['username']}")
    print(f"Password: {'*' * len(device_config['password'])}")
    print()
    
    async with aiohttp.ClientSession() as session:
        auth = aiohttp.BasicAuth(device_config['username'], device_config['password'])
        
        # Test system info first
        print("1. Testing system info endpoint...")
        try:
            async with session.get(
                f"{base_url}/api/system/info",
                auth=auth,
                ssl=False,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as resp:
                print(f"   Status: {resp.status}")
                if resp.status == 200:
                    try:
                        data = await resp.json()
                        print(f"   Device Info: {json.dumps(data, indent=2)}")
                    except:
                        content = await resp.text()
                        print(f"   Response: {content}")
                else:
                    content = await resp.text()
                    print(f"   Error: {content}")
        except Exception as e:
            print(f"   Exception: {e}")
        
        print()
        
        # Test switch control endpoints
        for switch_id in [1, 2, 3, 4]:
            print(f"2.{switch_id} Testing switch {switch_id} control...")
            
            # Test switch ON
            try:
                async with session.get(
                    f"{base_url}/api/switch/ctrl",
                    params={"switch": str(switch_id), "action": "on"},
                    auth=auth,
                    ssl=False,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    print(f"   Switch {switch_id} ON - Status: {resp.status}")
                    if resp.status != 200:
                        content = await resp.text()
                        print(f"   Error response: {content}")
                    else:
                        print(f"   ✅ Switch {switch_id} activated successfully")
            except Exception as e:
                print(f"   ❌ Switch {switch_id} ON failed: {e}")
            
            await asyncio.sleep(1)  # Wait between commands
            
        print()
        
        # Test door control
        print("3. Testing door control...")
        try:
            async with session.get(
                f"{base_url}/api/door/ctrl",
                params={"switch": "1", "action": "on"},
                auth=auth,
                ssl=False,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as resp:
                print(f"   Door control - Status: {resp.status}")
                if resp.status != 200:
                    content = await resp.text()
                    print(f"   Error response: {content}")
                else:
                    print(f"   ✅ Door control successful")
        except Exception as e:
            print(f"   ❌ Door control failed: {e}")

def test_integration_constants():
    """Test that integration constants are correct."""
    
    print("\n🔍 Testing Integration Constants")
    
    try:
        import const
        
        print(f"   DOMAIN: {const.DOMAIN}")
        print(f"   API_SWITCH_CONTROL: {const.API_SWITCH_CONTROL}")
        print(f"   API_DOOR_CONTROL: {const.API_DOOR_CONTROL}")
        print(f"   SWITCH_MODE_TOGGLE: {const.SWITCH_MODE_TOGGLE}")
        print(f"   SWITCH_MODE_PULSE: {const.SWITCH_MODE_PULSE}")
        
        print("\n   SWITCH_CONFIGS:")
        for key, config in const.SWITCH_CONFIGS.items():
            print(f"     {key}: {config}")
        
        return True
    except Exception as e:
        print(f"   ❌ Failed to load constants: {e}")
        return False

def test_integration_setup():
    """Test integration setup logic."""
    
    print("\n📦 Testing Integration Setup")
    
    try:
        # Mock configuration
        test_config = {
            "host": "192.168.1.100",
            "port": 80,
            "username": "admin",
            "password": "2n",
            "name": "Test Device",
            "switch_mode": "toggle"
        }
        
        print(f"   Mock config: {test_config}")
        
        # Test coordinator initialization logic
        base_url = f"http://{test_config['host']}:{test_config['port']}"
        device_name = test_config.get('name', f"2N IP Intercom ({test_config['host']})")
        
        print(f"   Base URL: {base_url}")
        print(f"   Device Name: {device_name}")
        
        return True
    except Exception as e:
        print(f"   ❌ Setup test failed: {e}")
        return False

async def main():
    """Run all debug tests."""
    
    print("🐛 2N IP Intercom Switch Debug Tests\n")
    print("=" * 50)
    
    # Test constants and setup
    constants_ok = test_integration_constants()
    setup_ok = test_integration_setup()
    
    if constants_ok and setup_ok:
        print("\n✅ Integration setup tests passed")
        
        print("\n" + "=" * 50)
        print("🌐 Testing Device Communication")
        print("⚠️  Update device_config in the script with your actual device details")
        print("=" * 50)
        
        # Test actual device (will fail if device not available)
        await test_switch_endpoints()
        
    else:
        print("\n❌ Integration setup issues found - fix these first")
    
    print("\n" + "=" * 50)
    print("📝 Debug Summary:")
    print("1. Check Home Assistant logs for errors")
    print("2. Verify device IP/credentials are correct")
    print("3. Test device web interface manually")
    print("4. Check network connectivity to device")
    print("5. Verify device supports the API endpoints")
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(main())
