import logging
import voluptuous as vol

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.exceptions import ServiceValidationError
from homeassistant.config_entries import ConfigEntry, ConfigEntryState

from .const import (
    DOMAIN,
    CONF_BASE_URL,
    CONF_CF_ACCESS_CLIENT_ID,
    CONF_CF_ACCESS_CLIENT_SECRET,
    CONF_SESSION_NAME,
    ATTR_CHAT_ID,
    ATTR_MESSAGE,
    ATTR_IMAGE_URL,
    SERVICE_SEND_TEXT,
    SERVICE_SEND_IMAGE,
)
from .api import WahaApiClient

_LOGGER = logging.getLogger(__name__)


SEND_TEXT_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_CHAT_ID): str,
        vol.Required(ATTR_MESSAGE): str,
    }
)

SEND_IMAGE_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_CHAT_ID): str,
        vol.Required(ATTR_IMAGE_URL): str,
        vol.Optional(ATTR_MESSAGE, default=""): str,
    }
)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    hass.data.setdefault(DOMAIN, {})

    def _get_loaded_client() -> WahaApiClient:
        for entry in hass.config_entries.async_entries(DOMAIN):
            if entry.state is ConfigEntryState.LOADED:
                client = hass.data[DOMAIN].get(entry.entry_id)
                if client:
                    return client
        raise ServiceValidationError("WAHA config entry is not loaded")

    async def handle_send_text(call: ServiceCall):
        client = _get_loaded_client()
        await client.send_text(
            chat_id=call.data[ATTR_CHAT_ID],
            message=call.data[ATTR_MESSAGE],
        )

    async def handle_send_image(call: ServiceCall):
        client = _get_loaded_client()
        await client.send_image(
            chat_id=call.data[ATTR_CHAT_ID],
            image_url=call.data[ATTR_IMAGE_URL],
            caption=call.data.get(ATTR_MESSAGE, ""),
        )

    hass.services.async_register(
        DOMAIN,
        SERVICE_SEND_TEXT,
        handle_send_text,
        schema=SEND_TEXT_SCHEMA,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_SEND_IMAGE,
        handle_send_image,
        schema=SEND_IMAGE_SCHEMA,
    )

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    session = async_get_clientsession(hass)

    client = WahaApiClient(
        base_url=entry.data[CONF_BASE_URL],
        cf_access_client_id=entry.data[CONF_CF_ACCESS_CLIENT_ID],
        cf_access_client_secret=entry.data[CONF_CF_ACCESS_CLIENT_SECRET],
        session_name=entry.data[CONF_SESSION_NAME],
        session=session,
    )

    hass.data[DOMAIN][entry.entry_id] = client
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    hass.data[DOMAIN].pop(entry.entry_id, None)
    return True