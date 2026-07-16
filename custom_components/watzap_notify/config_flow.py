import aiohttp
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    DOMAIN,
    CONF_BASE_URL,
    CONF_CF_ACCESS_CLIENT_ID,
    CONF_CF_ACCESS_CLIENT_SECRET,
    CONF_SESSION_NAME,
)
from .api import WahaApiClient


class WahaNotifyConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            session = async_get_clientsession(self.hass)
            client = WahaApiClient(
                base_url=user_input[CONF_BASE_URL],
                cf_access_client_id=user_input[CONF_CF_ACCESS_CLIENT_ID],
                cf_access_client_secret=user_input[CONF_CF_ACCESS_CLIENT_SECRET],
                session_name=user_input[CONF_SESSION_NAME],
                session=session,
            )

            try:
                await client.validate()
            except aiohttp.ClientResponseError:
                errors["base"] = "auth"
            except aiohttp.ClientError:
                errors["base"] = "cannot_connect"
            except Exception:
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(
                    title=f"WAHA ({user_input[CONF_SESSION_NAME]})",
                    data=user_input,
                )

        schema = vol.Schema(
            {
                vol.Required(CONF_BASE_URL): str,
                vol.Required(CONF_CF_ACCESS_CLIENT_ID): str,
                vol.Required(CONF_CF_ACCESS_CLIENT_SECRET): str,
                vol.Required(CONF_SESSION_NAME): str,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors,
        )