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
REQUIREMENTS = ['pigpio==1.38']

_LOGGER = logging.getLogger(__name__)

# Validation of the user's configuration
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    #vol.Required(CONF_HOST): cv.string,
    #vol.Optional(CONF_USERNAME, default='admin'): cv.string,
    #vol.Optional(CONF_PASSWORD): cv.string,
})


def setup_platform(hass, config, add_devices, discovery_info=None):
    """Setup the Awesome Light platform."""
    import pigpio

    # Assign configuration variables. The configuration check takes care they are
    # present.
    ''' Set max pwm dim level, this will be translated to
        0-255 to comply with hass levels '''
    max_level = config.get('maximum_level')
    min_level = config.get('minimum_level')
    gpio_pin = config.get('gpio_pin')
    friendly_name = config.get('friendly_name')
    # Setup connection with gpio
    pi1 = pigpio.pi()


    # Add devices
    add_devices([pwmlight(friendly_name, max_level,
                         min_level, gpio_pin, pi1)])



class pwmlight(Light):
    """PWM Light"""

    def __init__(self, name, max_level,
                 min_level, gpio_pin, pi1):
        """Initialize an AwesomeLight."""
        self._name = name
        self._max_level = max_level
        self._min_level = min_level
        self._gpio_pin = gpio_pin
        self._pi1 = pi1
        self._state = None
        self._brightness = None
        self._convfactor = (max_level - min_level) / 255
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

        """Return the brightness of the light."""
        dc = self._pi1.get_PWM_frequency(self._gpio_pin)
        'Set brightness'
        #self._pi1.hardware_PWM(self._gpio_pin, 2000, ((dc - min_level) / self._fade_conv))

        return (dc - min_level) / self._fade_conv

    @property
    def is_on(self):
        """Return true if light is on."""
        return self._state

    def turn_on(self, **kwargs):
        """Instruct the light to turn on.

        You can skip the brightness part if your light does not support
        brightness control.
        """
        self._pi1.hardware_PWM(self._gpio_pin, 2000,
                               self.conv_brightness(kwargs.get(ATTR_BRIGHTNESS, 255), None))

    def turn_off(self, **kwargs):
        """Instruct the light to turn off."""
        self._pi1.hardware_PWM(self._gpio_pin, 2000, self._min_level)

    def update(self):
        """Fetch new state data for this light.

        This is the only method that should fetch new data for Home Assistant.
        """

        if self._pi1.get_PWM_frequency(self._gpio_pin) > self._min_level:
            self._state = True
        else:
            self._state = False

        self._brightness = self.conv_brightness(None,
                                                self._pi1.get_PWM_frequency(self._gpio_pin))

    def conv_brightness(self, brightness, freq):
        '''Takes the brightness and converts it to frequency'''
        if brightness is not None:
            return brightness * self._convfactor + self._min_level
        elif freq is not None:
            return (freq - self._min_level) / self._convfactor

