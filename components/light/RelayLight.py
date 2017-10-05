import logging

import voluptuous as vol

# Import the device class from the component that you want to support
from homeassistant.components.light import ATTR_BRIGHTNESS, Light, PLATFORM_SCHEMA
from homeassistant.const import CONF_HOST, CONF_PORT
import homeassistant.helpers.config_validation as cv

# Home Assistant depends on 3rd party packages for API specific code.
REQUIREMENTS = ['lanrelay==0.8']

_LOGGER = logging.getLogger(__name__)

# Validation of the user's configuration
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_HOST): cv.string,
})


def setup_platform(hass, config, add_devices, discovery_info=None):
    """Setup the Awesome Light platform."""
    import lanrelay.lanrelay as ar

    # Assign configuration variables. The configuration check takes care they are
    # present.
    host = config.get('relay_controller_address')
    if not host:
        _LOGGER.error(
            "The required parameter 'relay_controller_address'"
            " was not found in config"
        )
        return False

    nrelay = config.get('number_relays')
    if not host:
        _LOGGER.error(
            "The required parameter 'number_relays'"
            " was not found in config"
        )
        return False

    port = config.get('relay_controller_port')
    if not host:
        _LOGGER.error(
            "The required parameter 'relay_controller_port'"
            " was not found in config"
        )
        return False

    rl = ar.EightChanRelay(host, port, nrelay)

    # Verify that passed in configuration works
    if not rl:
        _LOGGER.error("Could not connect to relay")
        return False

    # Add devices
    add_devices(RelayLight(relay) for relay in rl.relays)



class RelayLight(Light):
    """Representation of a relay light"""

    def __init__(self, light):
        """Initialize a relay light."""
        self._light = light
        self._name = light.name
        self._state = None

    @property
    def name(self):
        """Return the display name of this light."""
        return self._name

    @property
    def is_on(self):
        """Return true if light is on."""
        return self._state

    def turn_on(self, **kwargs):
        """Instruct the light to turn on."""
        self._light.turnOn()

    def turn_off(self, **kwargs):
        """Instruct the light to turn off."""
        self._light.turnOff()

    def update(self):
        """Fetch new state data for this light.

        This is the only method that should fetch new data for Home Assistant.
        """
        self._state =  self._light.getStatus()
