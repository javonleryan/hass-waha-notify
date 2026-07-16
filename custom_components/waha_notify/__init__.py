import logging
import voluptuous as vol

from homeassistant.config_entries import ConfigEntry, ConfigEntryState
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError, ServiceValidationError
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.typing import ConfigType

from .api import WahaApiClient
from .const import (
    DOMAIN,
    CONF_BASE_URL,
    CONF_CF_ACCESS_CLIENT_ID,
    CONF_CF_ACCESS_CLIENT_SECRET,
    ATTR_SENDER,
    ATTR_PHONE,
    ATTR_GROUP_ID,
    ATTR_MESSAGE,
    SERVICE_SEND_PERSONAL,
    SERVICE_SEND_GROUP,
    SERVICE_CHECK_PHONE,
)

_LOGGER = logging.getLogger(__name__)

SEND_PERSONAL_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_SENDER): str,
        vol.Required(ATTR_PHONE): str,
        vol.Required(ATTR_MESSAGE): str,
    }
)

SEND_GROUP_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_SENDER): str,
        vol.Required(ATTR_GROUP_ID): str,
        vol.Required(ATTR_MESSAGE): str,
    }
)

CHECK_PHONE_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_SENDER): str,
        vol.Required(ATTR_PHONE): str,
    }
)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    hass.data.setdefault(DOMAIN, {})

    def get_client() -> WahaApiClient:
        for entry in hass.config_entries.async_entries(DOMAIN):
            if entry.state is ConfigEntryState.LOADED:
                client = hass.data[DOMAIN].get(entry.entry_id)
                if client:
                    return client
        raise ServiceValidationError("No loaded WAHA Notify config entry found")

    async def handle_send_personal(call: ServiceCall):
        client = get_client()
        try:
            await client.send_personal(
                phone=call.data[ATTR_PHONE],
                message=call.data[ATTR_MESSAGE],
                session_name=call.data[ATTR_SENDER],
            )
        except Exception as err:
            raise HomeAssistantError(f"Failed to send personal message: {err}") from err

    async def handle_send_group(call: ServiceCall):
        client = get_client()
        try:
            await client.send_group(
                group_id=call.data[ATTR_GROUP_ID],
                message=call.data[ATTR_MESSAGE],
                session_name=call.data[ATTR_SENDER],
            )
        except Exception as err:
            raise HomeAssistantError(f"Failed to send group message: {err}") from err

    async def handle_check_phone(call: ServiceCall):
        client = get_client()
        try:
            result = await client.check_phone(
                phone=call.data[ATTR_PHONE],
                session_name=call.data[ATTR_SENDER],
            )
            _LOGGER.info("WAHA check_phone result: %s", result)
        except Exception as err:
            raise HomeAssistantError(f"Failed to check phone: {err}") from err

    hass.services.async_register(
        DOMAIN,
        SERVICE_SEND_PERSONAL,
        handle_send_personal,
        schema=SEND_PERSONAL_SCHEMA,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_SEND_GROUP,
        handle_send_group,
        schema=SEND_GROUP_SCHEMA,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_CHECK_PHONE,
        handle_check_phone,
        schema=CHECK_PHONE_SCHEMA,
    )

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    session = async_get_clientsession(hass)

    client = WahaApiClient(
        base_url=entry.data[CONF_BASE_URL],
        cf_access_client_id=entry.data[CONF_CF_ACCESS_CLIENT_ID],
        cf_access_client_secret=entry.data[CONF_CF_ACCESS_CLIENT_SECRET],
        session=session,
    )

    hass.data[DOMAIN][entry.entry_id] = client
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    hass.data[DOMAIN].pop(entry.entry_id, None)
    return True