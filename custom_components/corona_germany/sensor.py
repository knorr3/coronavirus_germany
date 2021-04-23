"""Coronavirus Germany sensor platform."""
from datetime import timedelta
import logging
import re
import json
from typing import Any, Callable, Dict, Optional

import async_timeout

from homeassistant import config_entries, core
from homeassistant.helpers import aiohttp_client
from homeassistant.components.sensor import PLATFORM_SCHEMA
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.typing import (
    ConfigType,
    DiscoveryInfoType,
    HomeAssistantType,
)
import voluptuous as vol

from .const import (
    CONF_COUNTY,
    ATTR_CASES,
    ATTR_DEATHS,
    ATTR_INCIDENCE,

    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)
# Time between updating data
SCAN_INTERVAL = timedelta(minutes=10)

COUNTY_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_COUNTY): cv.string,
    }
)

async def async_setup_entry(
    hass: core.HomeAssistant,
    config_entry: config_entries.ConfigEntry,
    async_add_entities,
):
    """Setup sensors from a config entry created in the integrations UI."""
    config = hass.data[DOMAIN][config_entry.entry_id]
    # Update our config to include new repos and remove those that have been removed.
    if config_entry.options:
        config.update(config_entry.options)
    sensors = [CoronaSensor(config[CONF_COUNTY], hass)]
    async_add_entities(sensors, update_before_add=True)


async def async_setup_platform(
    hass: HomeAssistantType,
    config: ConfigType,
    async_add_entities: Callable,
    discovery_info: Optional[DiscoveryInfoType] = None,
) -> None:
    """Set up the sensor platform."""
    sensors = [CoronaSensor(config[CONF_COUNTY], hass)]
    async_add_entities(sensors, update_before_add=True)


class CoronaSensor(Entity):
    """Collects and represents covid informations of a district"""

    def __init__(self, county: str, hass: HomeAssistantType):
        super().__init__()
        self.county = county
        self.hass = hass
        self.attrs: Dict[str, Any] = {CONF_COUNTY: self.county}
        self._name = county
        self._state = None
        self._available = True

    @property
    def name(self) -> str:
        """Return the name of the entity."""
        return self._name

    @property
    def unique_id(self) -> str:
        """Return the unique ID of the sensor."""
        return self.county

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._available

    @property
    def state(self) -> Optional[str]:
        return self._state

    @property
    def device_state_attributes(self) -> Dict[str, Any]:
        return self.attrs

    async def async_update(self):
        try:
            with async_timeout.timeout(30):
                url = 'https://services7.arcgis.com/mOBPykOjAyBO2ZKk/arcgis/rest/services/RKI_Landkreisdaten/FeatureServer/0/' \
                    f'query?where=county%20%3D%20%27{self.county}%27&outFields=GEN,cases7_per_100k,county,cases,deaths&outSR=4326&f' \
                    '=json'

                response = await aiohttp_client.async_get_clientsession(self.hass).get(url)
                raw_html = await response.text()

                json_data = json.loads(raw_html)
            
                self.attrs[ATTR_INCIDENCE] = json_data['features'][0]['attributes']['cases7_per_100k'],
                self.attrs[ATTR_DEATHS] = json_data['features'][0]['attributes']['deaths'],
                self.attrs[ATTR_CASES] = json_data['features'][0]['attributes']['cases']

                self._state = self.attrs[ATTR_INCIDENCE]
                self._available = True
        except:
            self._available = False
            _LOGGER.exception(f"Cannot retrieve data for district: '{county}'")
