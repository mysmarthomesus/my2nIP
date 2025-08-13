# Switch Hold Functionality

## Overview
The 2N IP Intercom integration now supports two different switch modes to match your hardware configuration and use case requirements.

## Switch Modes

### Toggle Mode (Default)
- **Behavior**: Switch stays ON until an explicit OFF command is sent
- **Use Case**: Doors, gates, or equipment that need to remain activated until manually deactivated
- **Commands**: 
  - Turn On: Sends switch-on command, switch remains ON
  - Turn Off: Sends switch-off command, switch turns OFF
- **State Tracking**: Integration tracks the switch state locally

### Pulse Mode (Traditional)
- **Behavior**: Momentary pulse activation (traditional intercom behavior)  
- **Use Case**: Door strikes, buzzers, or equipment that auto-resets
- **Commands**:
  - Turn On: Sends momentary pulse command
  - Turn Off: No command sent (device handles automatically)
- **State Tracking**: Switch automatically returns to OFF state

## Configuration

### During Setup
1. When adding the integration, select your preferred **Switch Mode**:
   - `Toggle (Hold until off)` - Switch stays on until off command
   - `Pulse (Momentary)` - Traditional momentary pulse behavior

### Switch Attributes
Each switch entity includes helpful attributes:
- `switch_mode`: Shows current mode (toggle/pulse)
- `switch_id`: Shows the switch number (1, 2, 3, etc.)

## Usage Examples

### Toggle Mode Example
```yaml
# automation example for toggle mode
automation:
  - alias: "Open Main Gate"
    trigger:
      platform: state
      entity_id: binary_sensor.visitor_detected
      to: 'on'
    action:
      - service: switch.turn_on
        target:
          entity_id: switch.main_gate_switch_1
      - delay: '00:00:10'  # Keep gate open for 10 seconds
      - service: switch.turn_off  # Explicitly close gate
        target:
          entity_id: switch.main_gate_switch_1
```

### Pulse Mode Example
```yaml
# automation example for pulse mode
automation:
  - alias: "Buzz Visitor In"
    trigger:
      platform: state
      entity_id: binary_sensor.doorbell_pressed
      to: 'on'
    action:
      - service: switch.turn_on  # Send momentary pulse
        target:
          entity_id: switch.front_door_switch_1
      # No need to turn off - device handles automatically
```

## Technical Details

### API Commands
- **Switch On**: `GET /api/switch/ctrl?switch=X&action=on`
- **Switch Off**: `GET /api/switch/ctrl?switch=X&action=off` (toggle mode only)

### State Management
- **Toggle Mode**: States stored in coordinator's `_switch_states` dictionary
- **Pulse Mode**: States queried from device coordinator data

### Backward Compatibility
- Existing installations continue to work without changes
- Default mode is "Toggle" for new installations
- Configuration can be updated through integration options

## Troubleshooting

### Switch Not Responding
1. Check device IP and authentication credentials
2. Verify switch number matches your 2N device configuration
3. Test switch control through the 2N web interface

### Wrong Switch Behavior
1. Check the switch mode in the entity attributes
2. Reconfigure integration with correct switch mode
3. Restart Home Assistant after configuration changes

### State Not Updating
- **Toggle Mode**: States are tracked locally and should update immediately
- **Pulse Mode**: States depend on device feedback and coordinator refresh interval
