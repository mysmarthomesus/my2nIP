"""Constants for the 2N IP Intercom integration."""
DOMAIN = "2n_ip_intercom"

DEFAULT_PORT = 80
DEFAULT_USERNAME = "admin"
DEFAULT_PASSWORD = "2n"

# Configuration keys
CONF_NAME = "name"

# API endpoints
API_SYSTEM_STATUS = "/api/system/info"
API_SWITCH_CONTROL = "/api/switch/ctrl"
API_DOOR_CONTROL = "/api/door/ctrl"

# Available controls
CONTROL_TYPES = {
    "switch": API_SWITCH_CONTROL,
    "door": API_DOOR_CONTROL,
}

ATTR_DEVICE_ID = "device_id"
ATTR_CONTROL_TYPE = "control_type"
