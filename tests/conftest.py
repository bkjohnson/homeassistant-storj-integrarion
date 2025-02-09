"""Global fixtures for Storj integration."""

from collections.abc import Generator
from unittest.mock import AsyncMock, patch
from pytest_homeassistant_custom_component.common import MockConfigEntry
from custom_components.storj.const import DOMAIN

import pytest


TEST_ACCESS_GRANT = "123xyz"
CONFIG_ENTRY_TITLE = "Storj entry title"


@pytest.fixture
def mock_setup_entry() -> Generator[AsyncMock]:
    """Override async_setup_entry."""
    with patch(
        "custom_components.storj.async_setup_entry", return_value=True
    ) as mock_setup_entry:
        yield mock_setup_entry


@pytest.fixture(name="mock_config_entry")
def mock_config_entry() -> MockConfigEntry:
    """Fixture for MockConfigEntry."""
    return MockConfigEntry(
        domain=DOMAIN,
        unique_id=TEST_ACCESS_GRANT,
        title=CONFIG_ENTRY_TITLE,
        data={"access_grant": TEST_ACCESS_GRANT, "bucket_name": "ha-backups"},
    )


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    yield
