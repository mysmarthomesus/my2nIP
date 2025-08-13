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

# Available controls
CONTROL_TYPES = {
    "switch": API_SWITCH_CONTROL,
    "door": API_DOOR_CONTROL,
}

ATTR_DEVICE_ID = "device_id"
ATTR_CONTROL_TYPE = "control_type"
