# Custom Device Naming Feature

## Overview
The 2N IP Intercom integration now supports custom device naming during setup. This allows you to give meaningful names to your devices, especially useful when you have multiple 2N IP Intercom devices.

## How to Use

### During Initial Setup
1. When adding the integration, you'll see a new optional field: **"Device Name"**
2. Enter a custom name for your device (e.g., "Front Door", "Main Gate", "Office Entrance")
3. If left empty, the integration will use a default name: "2N IP Intercom (IP_ADDRESS)"

### Entity Naming
All entities created by the integration will use your custom device name:

**With custom name "Front Door":**
- `Front Door Camera 1`
- `Front Door Door` 
- `Front Door Switch 1`
- `Front Door Device State`

**Without custom name (default):**
- `2N IP Intercom (192.168.1.100) Camera 1`
- `2N IP Intercom (192.168.1.100) Door`
- `2N IP Intercom (192.168.1.100) Switch 1` 
- `2N IP Intercom (192.168.1.100) Device State`

## Benefits
- **Clear identification**: Easily distinguish between multiple devices
- **Better organization**: Entities are logically grouped with meaningful names
- **User-friendly**: No more cryptic IP addresses in entity names
- **Backward compatible**: Existing installations continue to work without changes

## Example Use Cases
- **Multiple Buildings**: "Building A Entrance", "Building B Entrance"
- **Different Locations**: "Front Gate", "Back Door", "Side Entrance"
- **Functional Names**: "Visitor Intercom", "Delivery Door", "Employee Entrance"

## Technical Details
- The device name is stored in the configuration entry
- All entities (camera, switches, sensors) inherit the custom name
- Device info is updated to reflect the custom name
- Translation support included for the configuration UI
