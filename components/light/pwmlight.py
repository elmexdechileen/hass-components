"""
Support for dimmable lights controlled with the RPI PWM
"""

import logging

import voluptuous as vol

# Import the device class from the component that you want to support
from homeassistant.components.light import ATTR_BRIGHTNESS, Light, PLATFORM_SCHEMA
from homeassistant.const import CONF_HOST, CONF_USERNAME, CONF_PASSWORD
import homeassistant.helpers.config_validation as cv

# Home Assistant depends on 3rd party packages for API specific code.
REQUIREMENTS = ['pwmlight==0.2']

_LOGGER = logging.getLogger(__name__)

# Validation of the user's configuration
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    #vol.Required(CONF_HOST): cv.string,
    #vol.Optional(CONF_USERNAME, default='admin'): cv.string,
    #vol.Optional(CONF_PASSWORD): cv.string,
})


def setup_platform(hass, config, add_devices, discovery_info=None):
    """Setup the Awesome Light platform."""
    import pwmlight as pl

    # Assign configuration variables. The configuration check takes care they are
    # present.
    ''' Set max pwm dim level, this will be translated to
        0-255 to comply with hass levels '''
    max_level = config.get('maximum_level')
    min_level = config.get('minimum_level')
    gpio_pin = config.get('gpio_pin')
    friendly_name = config.get('friendly_name')

    # Add devices
    add_devices([PwmLight(pl.pwmlight(gpio_pin, min_level,
                         max_level, friendly_name))])



class PwmLight(Light):
    """Representation of an Awesome Light."""

    def __init__(self, light):
        """Initialize an AwesomeLight."""
        self._light = light
        self._name = self._light.name
        self._state = None
        self._brightness = None

    @property
    def name(self):
        """Return the display name of this light."""
        return self._name

    @property
    def brightness(self):
        """Return the brightness of the light.

        This method is optional. Removing it indicates to Home Assistant
        that brightness is not supported for this light.
        """
        return self._brightness

    @property
    def is_on(self):
        """Return true if light is on."""
        return self._state

    def turn_on(self, **kwargs):
        """Instruct the light to turn on.

        You can skip the brightness part if your light does not support
        brightness control.
        """
        self._light.setBrightness(kwargs.get(ATTR_BRIGHTNESS, 255))
        self._light.turnOn()

    def turn_off(self, **kwargs):
        """Instruct the light to turn off."""
        self._light.turnOff()

    def update(self):
        """Fetch new state data for this light.

        This is the only method that should fetch new data for Home Assistant.
        """
        self._light.update()
        self._state = self._light.getState()
        self._brightness = self._light.brightness