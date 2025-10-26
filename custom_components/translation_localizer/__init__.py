"""Translation Localizer integration for Home Assistant."""
import asyncio
import json
import logging
from pathlib import Path
from typing import Dict, Any

import voluptuous as vol
import requests
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.config_entries import ConfigEntry
from .const import DOMAIN, CONF_ZHIPU_API_KEY, CONF_CUSTOM_COMPONENTS_PATH

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: Dict) -> bool:
    """Set up the Translation Localizer component."""
    # Only support ConfigEntry setup
    _LOGGER.debug("Translation Localizer async_setup called")
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Translation Localizer from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry.data

    # Register the translation service
    hass.services.async_register(
        DOMAIN,
        "translate_components",
        async_translate_components_service,
        schema=vol.Schema({})
    )

    _LOGGER.info("Translation Localizer integration initialized successfully")
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if entry.entry_id in hass.data[DOMAIN]:
        hass.data[DOMAIN].pop(entry.entry_id)
    return True


async def async_translate_components_service(call: ServiceCall) -> None:
    """Service to translate all components."""
    hass = call.hass

    # Get API key from any available config entry
    api_key = None
    custom_path = "custom_components"

    # Debug: Log what's in hass.data
    domain_data = hass.data.get(DOMAIN, {})
    _LOGGER.debug(f"Domain data keys: {list(domain_data.keys())}")
    _LOGGER.debug(f"Domain data content: {domain_data}")

    # Try to find API key in config entries
    config_entries = hass.config_entries.async_entries(DOMAIN)
    _LOGGER.debug(f"Found {len(config_entries)} config entries for {DOMAIN}")

    for entry in config_entries:
        _LOGGER.debug(f"Entry {entry.entry_id}: {entry.data}")
        if entry.data and CONF_ZHIPU_API_KEY in entry.data:
            api_key = entry.data[CONF_ZHIPU_API_KEY]
            custom_path = entry.data.get(CONF_CUSTOM_COMPONENTS_PATH, "custom_components")
            _LOGGER.info(f"Found API key in config entry {entry.entry_id}")
            break

    # Fallback: try domain data
    if not api_key and domain_data:
        for key, value in domain_data.items():
            if isinstance(value, dict) and CONF_ZHIPU_API_KEY in value:
                api_key = value[CONF_ZHIPU_API_KEY]
                custom_path = value.get(CONF_CUSTOM_COMPONENTS_PATH, "custom_components")
                _LOGGER.info(f"Found API key in domain data {key}")
                break

    if not api_key:
        _LOGGER.error("Zhipu API key not configured. Please configure the integration first.")
        _LOGGER.error(f"Available domain data: {domain_data}")
        _LOGGER.error(f"Available config entries: {[(e.entry_id, e.data) for e in config_entries]}")
        return

    _LOGGER.info("Starting component translation...")

    # Run translation in background thread
    await hass.async_add_executor_job(
        translate_all_components,
        custom_path,
        api_key
    )


def translate_all_components(custom_components_path: str, api_key: str) -> None:
    """Translate all components in the custom_components directory."""
    # Find the custom components directory
    base_path = None

    # Try common paths
    paths_to_try = [
        Path(custom_components_path),
        Path("/config") / custom_components_path,
        Path.home() / ".homeassistant" / custom_components_path,
    ]

    for path in paths_to_try:
        if path.exists() and path.is_dir():
            base_path = path
            break

    if not base_path:
        _LOGGER.warning(f"Custom components directory not found: {custom_components_path}")
        return

    _LOGGER.info(f"Scanning components in: {base_path}")

    translated = 0
    skipped = 0

    # Process each component directory
    for component_dir in base_path.iterdir():
        if not component_dir.is_dir() or component_dir.name == "translation_localizer":
            continue

        try:
            result = translate_component(component_dir, api_key)
            if result == "translated":
                translated += 1
            else:
                skipped += 1
        except Exception as e:
            _LOGGER.error(f"Error processing {component_dir.name}: {e}")

    _LOGGER.info(f"Translation completed: {translated} translated, {skipped} skipped")


def translate_component(component_dir: Path, api_key: str) -> str:
    """Translate a single component."""
    translations_dir = component_dir / "translations"
    en_file = translations_dir / "en.json"
    zh_file = translations_dir / "zh-Hans.json"

    # Check if translation is needed
    if not translations_dir.exists() or not en_file.exists():
        return "skipped"

    if zh_file.exists():
        return "skipped"

    _LOGGER.info(f"Translating {component_dir.name}")

    try:
        # Load English translations
        with open(en_file, 'r', encoding='utf-8') as f:
            en_data = json.load(f)

        # Translate the data
        zh_data = translate_json_values(en_data, api_key)

        # Save Chinese translations
        with open(zh_file, 'w', encoding='utf-8') as f:
            json.dump(zh_data, f, ensure_ascii=False, indent=2)

        _LOGGER.info(f"Successfully translated {component_dir.name}")
        return "translated"

    except Exception as e:
        _LOGGER.error(f"Failed to translate {component_dir.name}: {e}")
        return "error"


def translate_json_values(data: Any, api_key: str) -> Any:
    """Recursively translate JSON values."""
    if isinstance(data, dict):
        return {key: translate_json_values(value, api_key) for key, value in data.items()}
    elif isinstance(data, list):
        return [translate_json_values(item, api_key) for item in data]
    elif isinstance(data, str) and data.strip():
        # Translate strings
        return translate_text(data, api_key)
    else:
        return data


def translate_text(text: str, api_key: str) -> str:
    """Translate text using Zhipu AI while preserving placeholders."""
    if not text or len(text.strip()) < 2:
        return text

    # Skip placeholders and code - use regex to find placeholder patterns
    import re

    # Pattern to match {placeholder}, %placeholder, ${placeholder}, etc.
    placeholder_pattern = r'\{[^}]+\}|%\w+|\$\{[^}]+\}'

    # Check if text is primarily a placeholder
    if re.fullmatch(placeholder_pattern, text.strip()):
        return text

    # Check if text starts with placeholder patterns
    if text.startswith(("{", "%", "${")) or text.isupper():
        return text

    # Find all placeholders in the text
    placeholders = re.findall(placeholder_pattern, text)

    if not placeholders:
        # No placeholders, translate directly
        return _translate_simple_text(text, api_key)

    # Extract placeholders and replace them with temporary markers
    placeholder_map = {}
    temp_text = text
    for i, placeholder in enumerate(placeholders):
        marker = f"__PLACEHOLDER_{i}__"
        placeholder_map[marker] = placeholder
        temp_text = temp_text.replace(placeholder, marker, 1)

    # Translate the text with placeholders removed
    translated_temp = _translate_simple_text(temp_text, api_key)

    # Restore the original placeholders
    translated_text = translated_temp
    for marker, placeholder in placeholder_map.items():
        translated_text = translated_text.replace(marker, placeholder)

    return translated_text


def _translate_simple_text(text: str, api_key: str) -> str:
    """Simple translation function for text without placeholders."""
    url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "glm-4-flash-250414",
        "messages": [
            {
                "role": "system",
                "content": "Translate English to Chinese. Return only the translation, no explanation."
            },
            {
                "role": "user",
                "content": text
            }
        ],
        "temperature": 0.3,
        "max_tokens": 2048
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()

        result = response.json()
        translated = result["choices"][0]["message"]["content"].strip()

        _LOGGER.debug(f"Translated: {text} -> {translated}")
        return translated

    except Exception as e:
        _LOGGER.error(f"Translation failed for '{text}': {e}")
        return text  # Return original on failure