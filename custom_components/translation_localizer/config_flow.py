"""Config flow for Translation Localizer integration."""
import logging
from typing import Dict, Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN, CONF_ZHIPU_API_KEY, CONF_CUSTOM_COMPONENTS_PATH

_LOGGER = logging.getLogger(__name__)


class TranslationLocalizerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Translation Localizer."""

    VERSION = 1

    async def async_step_user(
        self, user_input: Dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: Dict[str, str] = {}

        if user_input is not None:
            # Basic validation
            api_key = user_input.get(CONF_ZHIPU_API_KEY, "").strip()
            if not api_key:
                errors["base"] = "missing_api_key"
            elif len(api_key) < 10:
                errors["base"] = "invalid_api_key"
            else:
                return self.async_create_entry(
                    title="Translation Localizer",
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_ZHIPU_API_KEY): str,
                vol.Optional(
                    CONF_CUSTOM_COMPONENTS_PATH,
                    default="custom_components"
                ): str,
            }),
            errors=errors,
        )

    async def async_step_import(self, import_data: Dict[str, Any]) -> FlowResult:
        """Handle import from configuration.yaml."""
        return await self.async_step_user(import_data)