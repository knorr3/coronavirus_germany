from copy import deepcopy
import logging
import json
from typing import Any, Dict, Optional

import async_timeout
import asyncio

from homeassistant import config_entries, core
from homeassistant.core import callback
from homeassistant.helpers import aiohttp_client
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity_registry import (
    async_entries_for_config_entry,
    async_get_registry,
)
import voluptuous as vol

from .const import DOMAIN, CONF_COUNTY

_LOGGER = logging.getLogger(__name__)

COUNTY_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_COUNTY): cv.string
    }
)

async def validate_county(county: str, hass: core.HomeAssistant) -> bool:
    with async_timeout.timeout(30):
        if county is None:
            _LOGGER.exception("County cannot be 'none'")
            raise ValueError

        url = 'https://services7.arcgis.com/mOBPykOjAyBO2ZKk/arcgis/rest/services/RKI_Landkreisdaten/FeatureServer/0/' \
            f'query?where=county%20%3D%20%27{county}%27&outFields=GEN,cases7_per_100k,county,cases,deaths&outSR=4326&f' \
            '=json'

        response = await aiohttp_client.async_get_clientsession(hass).get(url)
        raw_html = await response.text()

        json_data = json.loads(raw_html)
        
        try:
            incidence = json_data['features'][0]['attributes']['cases7_per_100k'],
            deaths = json_data['features'][0]['attributes']['deaths'],
            cases = json_data['features'][0]['attributes']['cases']

        except:
            _LOGGER.exception(f"Invalid district: '{county}'")
            raise ValueError

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Custom config flow."""

    data: Optional[Dict[str, Any]]

    async def async_step_user(self, user_input: Optional[Dict[str, Any]] = None):
        """Invoked when a user initiates a flow via the user interface."""
        errors: Dict[str, str] = {}
        if user_input is not None:
            try:
                await validate_county(user_input[CONF_COUNTY], self.hass)
            except ValueError:
                errors["base"] = "wrong_format"
            if not errors:
                # Input is valid, set data.
                self.data = user_input
                # Return the form of the next step.
                return self.async_create_entry(title=f"Coronavirus in {self.data[CONF_COUNTY]}", data=self.data)

        return self.async_show_form(
            step_id="user", data_schema=COUNTY_SCHEMA, errors=errors
        )

#     @staticmethod
#     @callback
#     def async_get_options_flow(config_entry):
#         """Get the options flow for this handler."""
#         return OptionsFlowHandler(config_entry)


# class OptionsFlowHandler(config_entries.OptionsFlow):
#     """Handles options flow for the component."""

#     def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
#         self.config_entry = config_entry

#     async def async_step_init(
#         self, user_input: Dict[str, Any] = None
#     ) -> Dict[str, Any]:
#         """Manage the options for the custom component."""
#         errors: Dict[str, str] = {}
#         # Grab all configured repos from the entity registry so we can populate the
#         # multi-select dropdown that will allow a user to remove a repo.
#         entity_registry = await async_get_registry(self.hass)
#         entries = async_entries_for_config_entry(
#             entity_registry, self.config_entry.entry_id
#         )
#         # Default value for our multi-select.
#         all_repos = {e.entity_id: e.original_name for e in entries}
#         repo_map = {e.entity_id: e for e in entries}

#         if user_input is not None:
#             updated_repos = deepcopy(self.config_entry.data[CONF_REPOS])

#             # Remove any unchecked repos.
#             removed_entities = [
#                 entity_id
#                 for entity_id in repo_map.keys()
#                 if entity_id not in user_input["repos"]
#             ]
#             for entity_id in removed_entities:
#                 # Unregister from HA
#                 entity_registry.async_remove(entity_id)
#                 # Remove from our configured repos.
#                 entry = repo_map[entity_id]
#                 entry_path = entry.unique_id
#                 updated_repos = [e for e in updated_repos if e["path"] != entry_path]

#             if user_input.get(CONF_PATH):
#                 # Validate the path.
#                 access_token = self.hass.data[DOMAIN][self.config_entry.entry_id][
#                     CONF_ACCESS_TOKEN
#                 ]
#                 try:
#                     await validate_path(user_input[CONF_PATH], access_token, self.hass)
#                 except ValueError:
#                     errors["base"] = "invalid_path"

#                 if not errors:
#                     # Add the new repo.
#                     updated_repos.append(
#                         {
#                             "path": user_input[CONF_PATH],
#                             "name": user_input.get(CONF_NAME, user_input[CONF_PATH]),
#                         }
#                     )

#             if not errors:
#                 # Value of data will be set on the options property of our config_entry
#                 # instance.
#                 return self.async_create_entry(
#                     title="",
#                     data={CONF_REPOS: updated_repos},
#                 )

#         options_schema = vol.Schema(
#             {
#                 vol.Optional("repos", default=list(all_repos.keys())): cv.multi_select(
#                     all_repos
#                 ),
#                 vol.Optional(CONF_PATH): cv.string,
#                 vol.Optional(CONF_NAME): cv.string,
#             }
#         )
#         return self.async_show_form(
#             step_id="init", data_schema=options_schema, errors=errors
#         )
