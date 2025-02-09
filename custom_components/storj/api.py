"""API for Home Assistant to interact with Storj."""

from __future__ import annotations

import asyncio
import logging

from homeassistant.components.backup import AgentBackup, suggested_filename

_LOGGER = logging.getLogger(__name__)


class StorjClient:
    """Client for Storj uplink CLI tool."""

    def __init__(
        self,
        ha_instance_id: str,
        bucket_name: str,
    ) -> None:
        """Initialize."""
        self._ha_instance_id = ha_instance_id
        self.bucket_name = bucket_name
        # self.satellite = satellite

    async def authenticate(self, access_grant: str) -> bool:
        """Test if we can authenticate with the host."""
        result = await asyncio.create_subprocess_exec(
            "uplink", "access", "import", "ha2", access_grant
        )
        await result.communicate()
        return result.returncode == 0

    async def async_upload_backup(
        self,
        backup_dir: str,
        backup: AgentBackup,
    ) -> None:
        """Upload a backup."""
        # backup_metadata = {
        #     "name": suggested_filename(backup),
        #     "description": json.dumps(backup.as_dict()),
        #     "properties": {
        #         "home_assistant": "backup",
        #         "instance_id": self._ha_instance_id,
        #         "backup_id": backup.backup_id,
        #     },
        # }
        _LOGGER.debug(
            "Uploading backup: %s as %s",
            backup.backup_id,
            suggested_filename(backup),
            # backup_metadata,
        )

        # TODO: Add metadata,
        backup_location = f"{backup_dir}/{suggested_filename(backup)}"
        result = await asyncio.create_subprocess_exec(
            "uplink", "cp", backup_location, f"sj://{self.bucket_name}"
        )
        await result.communicate()
        _LOGGER.debug("Uploaded backup: %s to '%s'", backup.backup_id, self.bucket_name)

    async def async_list_backups(self) -> list[AgentBackup]:
        """List the backups currently in the bucket."""
        # query = " and ".join(
        #     [
        #         "properties has { key='home_assistant' and value='backup' }",
        #         f"properties has {{ key='instance_id' and value='{self._ha_instance_id}' }}",
        #         "trashed=false",
        #     ]
        # )
        # res = await self._api.list_files(
        #     params={"q": query, "fields": "files(description)"}
        # )
        backups: list[AgentBackup] = []
        # for file in res["files"]:
        #     backup = AgentBackup.from_dict(json.loads(file["description"]))
        #     backups.append(backup)
        return backups

    # async def async_list_backups(self) -> None:
    #     """List the backups currently in the bucket."""
    #     _LOGGER.debug("TODO")

    async def async_delete_backup(self) -> None:
        """Delete a specified backup from the bucket."""
        _LOGGER.debug("TODO")

    async def async_download_backup(self) -> None:
        """Download a backup to the local system."""
        _LOGGER.debug("TODO")
