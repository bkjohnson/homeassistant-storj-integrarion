"""Global fixtures for Storj integration."""

from collections.abc import Generator
from unittest.mock import AsyncMock, MagicMock, patch
from pytest_homeassistant_custom_component.common import MockConfigEntry
from custom_components.storj.const import DOMAIN
from contextlib import contextmanager
import asyncio

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


# Copied from homeassistant:
# https://github.com/home-assistant/core/blob/2f121874987b5f19aed6b5769b9880c5322d95d0/tests/components/command_line/__init__.py#L9
@contextmanager
def mock_asyncio_subprocess_run(
    response: bytes = b"", returncode: int = 0, exception: Exception | None = None
):
    """Mock create_subprocess_shell."""

    class MockProcess(asyncio.subprocess.Process):
        @property
        def returncode(self):
            return returncode

        async def communicate(self):
            if exception:
                raise exception
            return response, b""

    mock_process = MockProcess(MagicMock(), MagicMock(), MagicMock())

    with patch(
        "asyncio.create_subprocess_exec",
        return_value=mock_process,
    ) as mock:
        yield mock


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    yield
