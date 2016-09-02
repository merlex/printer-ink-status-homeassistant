# -*- coding: utf-8 -*-
from homeassistant.const import CONF_MONITORED_CONDITIONS
from homeassistant.helpers.entity import Entity
import subprocess
__author__ = 'merlex'

# Sensor types are defined like so:
SENSOR_TYPES = {
    'status': ['Symbol', None],
    'cyan': ['Cyan', '%'],
    'magenta': ['Magenta', '%'],
    'yellow': ['Yellow', '%'],
    'black': ['Black', '%'],
}


def setup_platform(hass, config, add_devices, discovery_info=None):
    """Setup the sensor platform."""
    dev = []
    for sensor_type in config[CONF_MONITORED_CONDITIONS]:
        dev.append(InkStatusSensor(sensor_type, SENSOR_TYPES[sensor_type]))

    # add symbol as default sensor
    if len(dev) == 0:
        dev.append(InkStatusSensor("status", SENSOR_TYPES['status']))
    add_devices(dev)


class InkStatusSensor(Entity):
    """Implementation of a Epson Ink Status sensor."""

    def __init__(self, name, conf):
        """Initialize the sensor."""
        self._name = name
        self._unit_of_measurement = conf[1]
        self._state = None
        self._conf = conf

        self.update()

    @property
    def entity_id(self):
        """Return the entity ID."""
        return 'sensor.ink_status_{}'.format(self._name)

    @property
    def name(self):
        """Return the name of the sensor."""
        return 'Printer status' if self._conf[1] is None else self._conf[0]

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return self._conf[1]

    def update(self):
        """Retrieve latest state."""
        cmdpipe = subprocess.Popen("escputil -s -q --raw-device /dev/usb/lp0", stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, shell=True)
        result = {}
        for row in cmdpipe.stdout:
            if ': ' in row.decode('utf-8'):
                key, value = row.decode('utf-8').split(': ')
                result[key.strip().lower()] = value.strip()
            else:
                values = row.decode('utf-8').strip().split(' ', maxsplit=1)
                if len(values) > 1:
                    result[values[0].strip().lower()] = values[1].strip()
        if self._name in result:
            self._state = result[self._name]
        else:
            self._state = 'N/A'
