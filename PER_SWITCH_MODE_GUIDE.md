# Per-Switch Mode Configuration Guide

The 2N IP Intercom integration now supports configuring individual switches with different modes simultaneously on the same device. This allows you to have both toggle and pulse switches operating independently.

## Overview

Starting with version 1.2.0, you can configure each switch (1-4) with its own operating mode:
- **Toggle Mode**: Switch stays ON until explicitly turned OFF (persistent state)
- **Pulse Mode**: Switch automatically turns OFF after activation (momentary pulse)

## Configuration Options

### Global Switch Mode (Legacy)
For simple setups, you can still configure all switches to use the same mode:
- During setup, select your preferred switch mode from the dropdown
- All switches will behave according to this global setting

### Per-Switch Mode Configuration
For advanced setups, individual switches can be configured with different modes in `const.py`:

```python
SWITCH_CONFIGS = {
    "door": {"name": "Door", "mode": "toggle"},
    "switch_1": {"name": "Switch 1", "mode": "toggle"},
    "switch_2": {"name": "Switch 2 (Pulse)", "mode": "pulse"},
    "switch_3": {"name": "Switch 3 (Pulse)", "mode": "pulse"},
    "switch_4": {"name": "Switch 4", "mode": "toggle"},
}
```

## Use Cases

### Mixed Mode Scenarios
1. **Main Gate + Door Strike**:
   - Switch 1 (Main Gate): `toggle` mode for controlled access
   - Switch 2 (Door Strike): `pulse` mode for quick entry

2. **Multiple Access Points**:
   - Switch 1 (Side Door): `toggle` mode for extended access
   - Switch 2 (Front Buzzer): `pulse` mode for visitor entry
   - Switch 3 (Garage Door): `toggle` mode for vehicle access
   - Switch 4 (Back Door): `pulse` mode for quick access

### Mode Behavior Details

#### Toggle Mode
- **Turn ON**: Switch activates and remains ON
- **Turn OFF**: Explicit OFF command required to deactivate
- **State Tracking**: Maintains ON/OFF state between commands
- **Best For**: Gates, doors, lights that need controlled duration

#### Pulse Mode
- **Turn ON**: Switch activates briefly then auto-deactivates
- **Turn OFF**: No effect (already OFF after pulse)
- **State Tracking**: Always returns to OFF state after activation
- **Best For**: Door strikes, buzzers, momentary activations

## Implementation Details

### Switch Entity Creation
Each configured switch is created as an individual entity:
```python
for switch_key, switch_config in SWITCH_CONFIGS.items():
    switch = TwoNIntercomSwitch(
        coordinator, 
        switch_key, 
        switch_config["name"], 
        switch_config["mode"]
    )
```

### State Management
Switches track their mode and behave accordingly:
```python
def is_on(self):
    if self._switch_mode == "pulse":
        return False  # Pulse switches are always OFF
    return self.coordinator.data.get(f"{self._switch_key}_state", False)
```

### Command Execution
Switch commands respect individual mode settings:
```python
async def async_turn_on(self):
    if self._switch_mode == "toggle":
        # Set state for toggle switches
        self.coordinator.data[f"{self._switch_key}_state"] = True
    # Send activation command for all switches
    await self._send_switch_command()
```

## Migration Guide

### From Global to Per-Switch Mode
1. **Backup**: Save your current configuration
2. **Update**: Modify `SWITCH_CONFIGS` in `const.py`
3. **Restart**: Restart Home Assistant
4. **Verify**: Check switch entities show correct modes

### Backwards Compatibility
- Existing installations continue working unchanged
- Global switch mode still available for simple setups
- Per-switch configuration overrides global settings when specified

## Troubleshooting

### Common Issues

1. **Switch Not Responding**:
   - Check network connectivity to 2N device
   - Verify switch configuration in `SWITCH_CONFIGS`
   - Review Home Assistant logs for HTTP errors

2. **Mode Not Applied**:
   - Ensure `const.py` changes are saved
   - Restart Home Assistant to reload configuration
   - Check entity attributes show correct mode

3. **State Tracking Issues**:
   - Toggle switches maintain state between commands
   - Pulse switches always show OFF state
   - Check coordinator data updates in logs

### Debug Information
Enable debug logging to troubleshoot:
```yaml
logger:
  default: info
  logs:
    custom_components.2n_ip_intercom: debug
```

## Advanced Configuration

### Custom Switch Names
Modify switch names in `SWITCH_CONFIGS`:
```python
"switch_1": {"name": "Main Entrance", "mode": "toggle"},
"switch_2": {"name": "Visitor Buzzer", "mode": "pulse"},
```

### Adding More Switches
The configuration supports up to 4 switches plus the door switch:
```python
SWITCH_CONFIGS = {
    "door": {"name": "Main Door", "mode": "toggle"},
    "switch_1": {"name": "Gate 1", "mode": "toggle"},
    "switch_2": {"name": "Buzzer", "mode": "pulse"},
    "switch_3": {"name": "Gate 2", "mode": "toggle"},
    "switch_4": {"name": "Emergency", "mode": "pulse"},
}
```

## Examples

### Home Automation Scenarios

#### Scenario 1: Apartment Building
```python
SWITCH_CONFIGS = {
    "door": {"name": "Building Entry", "mode": "toggle"},
    "switch_1": {"name": "Apartment Door", "mode": "pulse"},
    "switch_2": {"name": "Garage Gate", "mode": "toggle"},
    "switch_3": {"name": "Visitor Buzzer", "mode": "pulse"},
}
```

#### Scenario 2: Office Building
```python
SWITCH_CONFIGS = {
    "door": {"name": "Main Reception", "mode": "toggle"},
    "switch_1": {"name": "Conference Room", "mode": "pulse"},
    "switch_2": {"name": "Server Room", "mode": "toggle"},
    "switch_3": {"name": "Emergency Exit", "mode": "pulse"},
}
```

## Benefits

1. **Flexibility**: Mix toggle and pulse modes on same device
2. **Efficiency**: Each switch behaves optimally for its purpose
3. **Control**: Independent operation of different access points
4. **Compatibility**: Works with existing Home Assistant automations
5. **Simplicity**: Easy configuration through code or UI

## Version History

- **v1.2.0**: Added per-switch mode configuration
- **v1.1.0**: Added switch hold functionality
- **v1.0.0**: Initial release with basic switch support
