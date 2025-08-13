"""Constants for the 2N IP Intercom integration."""
DOMAIN = "2n_ip_intercom"

DEFAULT_PORT = 80
DEFAULT_USERNAME = "admin"
DEFAULT_PASSWORD = "2n"

# Configuration keys
CONF_NAME = "name"
CONF_SWITCH_MODE = "switch_mode"

# API endpoints
API_SYSTEM_STATUS = "/api/system/info"
API_SWITCH_CONTROL = "/api/switch/ctrl"
API_DOOR_CONTROL = "/api/door/ctrl"
API_CAMERA_SNAPSHOT = "/api/camera/snapshot"

# Switch control modes
SWITCH_MODE_PULSE = "pulse"  # Traditional momentary pulse
SWITCH_MODE_TOGGLE = "toggle"  # Hold until off command

# Default switch mode
DEFAULT_SWITCH_MODE = SWITCH_MODE_TOGGLE

# Switch configurations - can be customized per installation
SWITCH_CONFIGS = {
    "door": {"mode": SWITCH_MODE_TOGGLE, "name": "Door"},
    "switch_1": {"mode": SWITCH_MODE_TOGGLE, "name": "Switch 1"},
    "switch_2": {"mode": SWITCH_MODE_PULSE, "name": "Switch 2 (Pulse)"},
    "switch_3": {"mode": SWITCH_MODE_PULSE, "name": "Switch 3 (Pulse)"},
    "switch_4": {"mode": SWITCH_MODE_TOGGLE, "name": "Switch 4"},
}

# Available controls
CONTROL_TYPES = {
    "switch": API_SWITCH_CONTROL,
    "door": API_DOOR_CONTROL,
}

ATTR_DEVICE_ID = "device_id"
ATTR_CONTROL_TYPE = "control_type"
