# 2N IP Intercom for Home Assistant

This custom component integrates the 2N IP Intercom via its HTTP API into Home Assistant. It supports both sensor and switch platforms.

## Features

- **Sensor**: Polls the intercom status every 30 seconds.
- **Switch**: Allows control of a switch function (if supported by the device).

## Installation
HACS
Add https://github.com/mysmarthomesus/my2nIP as a custom repository
Download my2nIP through the regular explore & download prompt
Restart Homeassistant

1. Place the custom component folder under your Home Assistant configuration directory:
   
   ```
   <config>/custom_components/2n_ip_intercom
   ```

2. Restart Home Assistant.

## Configuration

You can set up the integration via the Home Assistant UI. When prompted, input the following:

- **Host**: The IP address or hostname of your 2N IP Intercom device.
- **Port**: The port used by the device (default is 80).
- **Username** (optional): Your device username, if any.
- **Password** (optional): Your device password, if any.

## Files

- `manifest.json`: Integration metadata.
- `__init__.py`: Setup code for the integration, forwarding sensor and switch platforms.
- `config_flow.py`: Configuration flow for the integration.
- `const.py`: Constants used in the integration.
- `sensor.py`: Sensor platform implementation.

## Further Customization

You may extend the integration to add additional platforms or customize behavior according to your needs. Refer to the [2N IP Intercom HTTP API Documentation](https://wiki.2n.com/hip/hapi/latest/en/2-popis-protokolu-http-api/) for more details.

## License

Provide your license information here.

## Code Owners

- @mysmarthomesus
