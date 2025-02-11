"""Test Storj config flow."""

from unittest.mock import AsyncMock, patch

from homeassistant import config_entries
from custom_components.storj.config_flow import CannotConnect, InvalidAuth
from custom_components.storj.const import DOMAIN, CONF_ACCESS_GRANT, CONF_BUCKET_NAME
from syrupy.assertion import SnapshotAssertion
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from .conftest import mock_asyncio_subprocess_run


async def test_form(
    hass: HomeAssistant, mock_setup_entry: AsyncMock, snapshot: SnapshotAssertion
) -> None:
    """Test we get the form."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {}

    with mock_asyncio_subprocess_run(responses=iter([b""])) as subprocess_exec:
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_ACCESS_GRANT: "abc123xyz",
                CONF_BUCKET_NAME: "my-backups",
            },
        )
        await hass.async_block_till_done()
        assert snapshot() == subprocess_exec.mock_calls[0].args

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == "Storj"
    assert result["data"] == {
        CONF_ACCESS_GRANT: "abc123xyz",
        CONF_BUCKET_NAME: "my-backups",
    }
    assert len(mock_setup_entry.mock_calls) == 1


async def test_form_invalid_auth(
    hass: HomeAssistant, mock_setup_entry: AsyncMock
) -> None:
    """Test we handle invalid auth."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    with patch(
        "custom_components.storj.api.StorjClient.authenticate",
        side_effect=InvalidAuth,
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_ACCESS_GRANT: "abc123xyz",
                CONF_BUCKET_NAME: "my-backups",
            },
        )

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "invalid_auth"}

    # Make sure the config flow tests finish with either an
    # FlowResultType.CREATE_ENTRY or FlowResultType.ABORT so
    # we can show the config flow is able to recover from an error.
    with patch(
        "custom_components.storj.api.StorjClient.authenticate",
        return_value=True,
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_ACCESS_GRANT: "abc123xyz",
                CONF_BUCKET_NAME: "my-backups",
            },
        )
        await hass.async_block_till_done()

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == "Storj"
    assert result["data"] == {
        CONF_ACCESS_GRANT: "abc123xyz",
        CONF_BUCKET_NAME: "my-backups",
    }
    assert len(mock_setup_entry.mock_calls) == 1


async def test_form_cannot_connect(
    hass: HomeAssistant, mock_setup_entry: AsyncMock
) -> None:
    """Test we handle cannot connect error."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    with patch(
        "custom_components.storj.api.StorjClient.authenticate",
        side_effect=CannotConnect,
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_ACCESS_GRANT: "abc123xyz",
                CONF_BUCKET_NAME: "my-backups",
            },
        )

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "cannot_connect"}

    # Make sure the config flow tests finish with either an
    # FlowResultType.CREATE_ENTRY or FlowResultType.ABORT so
    # we can show the config flow is able to recover from an error.

    with patch(
        "custom_components.storj.api.StorjClient.authenticate",
        return_value=True,
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_ACCESS_GRANT: "abc123xyz",
                CONF_BUCKET_NAME: "my-backups",
            },
        )
        await hass.async_block_till_done()

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == "Storj"
    assert result["data"] == {
        CONF_ACCESS_GRANT: "abc123xyz",
        CONF_BUCKET_NAME: "my-backups",
    }
    assert len(mock_setup_entry.mock_calls) == 1
