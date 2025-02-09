"""Custom integration to integrate Storj with Home Assistant as a backup location."""

from __future__ import annotations

from collections.abc import Callable

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import instance_id
from homeassistant.util.hass_dict import HassKey

from .api import StorjClient
from .const import DOMAIN, CONF_BUCKET_NAME

type StorjConfigEntry = ConfigEntry[StorjClient]

DATA_BACKUP_AGENT_LISTENERS: HassKey[list[Callable[[], None]]] = HassKey(
    f"{DOMAIN}.backup_agent_listeners"
)


async def async_setup_entry(hass: HomeAssistant, entry: StorjConfigEntry) -> bool:
    """Set up storj from a config entry."""

    # TODO 1. Create API instance
    # TODO 2. Validate the API connection (and authentication)
    # TODO 3. Store an API object for your platforms to access

    entry.runtime_data = StorjClient(
        await instance_id.async_get(hass), entry.data[CONF_BUCKET_NAME]
    )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: StorjConfigEntry) -> bool:
    """Unload a config entry."""
    hass.loop.call_soon(_notify_backup_listeners, hass)
    return True


def _notify_backup_listeners(hass: HomeAssistant) -> None:
    for listener in hass.data.get(DATA_BACKUP_AGENT_LISTENERS, []):
        listener()
