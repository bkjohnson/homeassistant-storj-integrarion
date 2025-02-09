"""Test the Storj BackupAgent"""

from collections.abc import AsyncGenerator
from io import StringIO
from homeassistant.core import HomeAssistant
import asyncio

from pytest_homeassistant_custom_component.common import MockConfigEntry
from pytest_homeassistant_custom_component.typing import ClientSessionGenerator
from syrupy.assertion import SnapshotAssertion
from syrupy.matchers import path_type
from unittest.mock import Mock, AsyncMock, patch
from homeassistant.setup import async_setup_component
from homeassistant.components.backup import (
    DOMAIN as BACKUP_DOMAIN,
    AddonInfo,
    AgentBackup,
)

from custom_components.storj.const import DOMAIN
import pytest


TEST_AGENT_BACKUP = AgentBackup(
    addons=[AddonInfo(name="Test", slug="test", version="1.0.0")],
    backup_id="test-backup",
    database_included=True,
    date="2025-01-01T01:23:45.678Z",
    extra_metadata={
        "with_automatic_settings": False,
    },
    folders=[],
    homeassistant_included=True,
    homeassistant_version="2024.12.0",
    name="Test",
    protected=False,
    size=987,
)


@pytest.fixture(autouse=True)
async def setup_backup_integration(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
) -> AsyncGenerator[None]:
    """Set up Storj integration."""
    with (
        patch("homeassistant.components.backup.is_hassio", return_value=False),
        patch("homeassistant.components.backup.store.STORE_DELAY_SAVE", 0),
    ):
        assert await async_setup_component(hass, BACKUP_DOMAIN, {BACKUP_DOMAIN: {}})
        mock_config_entry.add_to_hass(hass)
        await hass.config_entries.async_setup(mock_config_entry.entry_id)

        await hass.async_block_till_done()
        yield


async def test_agents_upload(
    hass: HomeAssistant,
    hass_client: ClientSessionGenerator,
    caplog: pytest.LogCaptureFixture,
    mock_config_entry: MockConfigEntry,
    snapshot: SnapshotAssertion,
) -> None:
    """Test agent upload backup."""

    asyncio.create_subprocess_exec = AsyncMock()
    assert await async_setup_component(hass, BACKUP_DOMAIN, {})
    client = await hass_client()

    with (
        patch(
            "homeassistant.components.backup.manager.BackupManager.async_get_backup",
        ) as fetch_backup,
        patch(
            "homeassistant.components.backup.manager.read_backup",
            return_value=TEST_AGENT_BACKUP,
        ),
        patch("pathlib.Path.open") as mocked_open,
    ):
        mocked_open.return_value.read = Mock(side_effect=[b"test", b""])
        fetch_backup.return_value = TEST_AGENT_BACKUP
        resp = await client.post(
            f"/api/backup/upload?agent_id={DOMAIN}.{mock_config_entry.unique_id}",
            data={"file": StringIO("test")},
        )

    matcher = path_type(
        mapping={"2": (str,)},
        replacer=lambda _, match: "my_backup.tar",
    )

    assert resp.status == 201
    assert f"Uploading backup: {TEST_AGENT_BACKUP.backup_id}" in caplog.text
    assert f"Uploaded backup: {TEST_AGENT_BACKUP.backup_id}" in caplog.text
    asyncio.create_subprocess_exec.assert_called_once()
    assert (
        snapshot(matcher=matcher) == asyncio.create_subprocess_exec.mock_calls[0].args
    )
