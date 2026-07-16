import voluptuous as vol

from homeassistant import config_entries

from .const import (
    DOMAIN,
    CONF_BASE_URL,
    CONF_CF_ACCESS_CLIENT_ID,
    CONF_CF_ACCESS_CLIENT_SECRET,
)


class WahaNotifyConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            await self.async_set_unique_id(user_input[CONF_BASE_URL].lower())
            self._abort_if_unique_id_configured()

            return self.async_create_entry(
                title=f"WAHA Notify ({user_input[CONF_BASE_URL]})",
                data=user_input,
            )

        data_schema = vol.Schema(
            {
                vol.Required(CONF_BASE_URL, default="https://public-api.rmm-2.dev"): str,
                vol.Required(CONF_CF_ACCESS_CLIENT_ID): str,
                vol.Required(CONF_CF_ACCESS_CLIENT_SECRET): str,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )