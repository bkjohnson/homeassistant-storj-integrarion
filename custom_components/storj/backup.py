"""Backup platform for the Storj integration."""

from __future__ import annotations

from collections.abc import AsyncIterator, Callable
import logging
from typing import Any
from pathlib import Path

from homeassistant.components.backup import AgentBackup, BackupAgent, BackupAgentError
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import HomeAssistantError

from . import DATA_BACKUP_AGENT_LISTENERS, StorjConfigEntry
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_get_backup_agents(
    hass: HomeAssistant,
    **kwargs: Any,
) -> list[BackupAgent]:
    """Return a list of backup agents."""
    entries = hass.config_entries.async_loaded_entries(DOMAIN)
    return [StorjBackupAgent(hass, entry) for entry in entries]


@callback
def async_register_backup_agents_listener(
    hass: HomeAssistant,
    *,
    listener: Callable[[], None],
    **kwargs: Any,
) -> Callable[[], None]:
    """Register a listener to be called when agents are added or removed.
    :return: A function to unregister the listener.
    """
    hass.data.setdefault(DATA_BACKUP_AGENT_LISTENERS, []).append(listener)

    @callback
    def remove_listener() -> None:
        """Remove the listener."""
        hass.data[DATA_BACKUP_AGENT_LISTENERS].remove(listener)
        if not hass.data[DATA_BACKUP_AGENT_LISTENERS]:
            del hass.data[DATA_BACKUP_AGENT_LISTENERS]

    return remove_listener


class StorjBackupAgent(BackupAgent):
    """Storj backup agent."""

    domain = DOMAIN

    def __init__(self, hass: HomeAssistant, config_entry: StorjConfigEntry) -> None:
        """Initialize the cloud backup sync agent."""
        super().__init__()
        assert config_entry.unique_id
        self.hass = hass
        self.name = config_entry.title
        self.unique_id = config_entry.unique_id
        self._backup_dir = Path(hass.config.path("backups"))
        self._client = config_entry.runtime_data

    async def async_upload_backup(
        self,
        *,
        backup: AgentBackup,
        **kwargs: Any,
    ) -> None:
        """Upload a backup.
        :param backup: Metadata about the backup that should be uploaded.
        """
        try:
            await self._client.async_upload_backup(self._backup_dir, backup)
        except (HomeAssistantError, TimeoutError) as err:
            raise BackupAgentError(f"Failed to upload backup: {err}") from err

    async def async_list_backups(self, **kwargs: Any) -> list[AgentBackup]:
        """List backups."""
        try:
            return await self._client.async_list_backups()
        except (HomeAssistantError, TimeoutError) as err:
            raise BackupAgentError(f"Failed to list backups: {err}") from err

    async def async_get_backup(
        self,
        backup_id: str,
        **kwargs: Any,
    ) -> AgentBackup | None:
        """Return a backup."""
        backups = await self.async_list_backups()
        for backup in backups:
            if backup.backup_id == backup_id:
                return backup
        return None

    async def async_download_backup(
        self,
        backup_id: str,
        **kwargs: Any,
    ) -> AsyncIterator[bytes]:
        """Download a backup file.
        :param backup_id: The ID of the backup that was returned in async_list_backups.
        :return: An async iterator that yields bytes.
        """
        _LOGGER.debug("Downloading backup_id: %s", backup_id)
        # try:
        #     file_id = await self._client.async_get_backup_file_id(backup_id)

    async def async_delete_backup(
        self,
        backup_id: str,
        **kwargs: Any,
    ) -> None:
        """Delete a backup file.
        :param backup_id: The ID of the backup that was returned in async_list_backups.
        """
        _LOGGER.debug("Deleting backup_id: %s", backup_id)
        # file_id = await self._client.async_get_backup_file_id(backup_id)
