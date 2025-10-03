"""
UI Configuration Manager

Loads and manages UI element configurations from JSON files.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Tuple

logger = logging.getLogger(__name__)


class UIConfig:
    """Manager for UI configuration from JSON files"""

    def __init__(self, database_path: str = None):
        """
        Initialize UI Config Manager

        Args:
            database_path: Path to JSON database directory
        """
        if database_path is None:
            # Default path relative to this file
            # src/apps/rok/ui_config.py -> backend/python/src/apps/rok
            # Go up to jnj-android directory
            current_file = Path(__file__).resolve()
            # backend/python/src/apps/rok -> backend/python/src/apps -> backend/python/src -> backend/python -> backend -> jnj-android
            jnj_android_dir = current_file.parent.parent.parent.parent.parent.parent
            database_path = jnj_android_dir / "database" / "json"

        self.database_path = Path(database_path)
        self._configs = {}
        self._load_all_configs()

    def _load_all_configs(self):
        """Load all JSON configuration files"""
        config_files = {
            "weston": "ui_weston.json",
            "rok_button": "ui_rok_button.json",
            "rok_unit": "ui_rok_unit.json"
        }

        for key, filename in config_files.items():
            filepath = self.database_path / filename
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    self._configs[key] = json.load(f)
                logger.info(f"Loaded UI config: {filename}")
            except FileNotFoundError:
                logger.warning(f"UI config file not found: {filepath}")
                self._configs[key] = {}
            except json.JSONDecodeError as e:
                logger.error(f"Error parsing JSON in {filename}: {e}")
                self._configs[key] = {}

    def reload(self):
        """Reload all configuration files"""
        logger.info("Reloading UI configurations...")
        self._configs = {}
        self._load_all_configs()

    def get_weston_config(self) -> Dict[str, Any]:
        """Get Weston UI configuration"""
        return self._configs.get("weston", {})

    def get_rok_button_config(self) -> Dict[str, Any]:
        """Get ROK button configuration"""
        return self._configs.get("rok_button", {})

    def get_rok_unit_config(self) -> Dict[str, Any]:
        """Get ROK unit configuration"""
        return self._configs.get("rok_unit", {})

    # Convenience methods for Weston

    def get_weston_display(self) -> str:
        """Get Weston DISPLAY value"""
        return self.get_weston_config().get("display", ":10.0")

    def get_weston_window_geometry(self) -> Tuple[int, int, int, int]:
        """
        Get Weston window geometry

        Returns:
            Tuple of (x, y, width, height)
        """
        geom = self.get_weston_config().get("window", {}).get("default_geometry", {})
        return (
            geom.get("x", 5),
            geom.get("y", 29),
            geom.get("width", 1024),
            geom.get("height", 600)
        )

    def get_unlock_button_position(self) -> Tuple[int, int]:
        """
        Get unlock button position

        Returns:
            Tuple of (x, y)
        """
        elements = self.get_weston_config().get("elements", {})
        btn = elements.get("button_unlock", {})
        pos = btn.get("position", {})
        return (pos.get("x", 129), pos.get("y", 104))

    def get_unlock_button_detection(self) -> Dict[str, Any]:
        """Get unlock button detection configuration"""
        elements = self.get_weston_config().get("elements", {})
        btn = elements.get("button_unlock", {})
        return btn.get("detection", {})

    def get_black_screen_detection(self) -> Dict[str, Any]:
        """Get black screen detection configuration"""
        elements = self.get_weston_config().get("elements", {})
        black = elements.get("black_screen", {})
        return black.get("detection", {})

    def get_unlock_sequence(self) -> Dict[str, Any]:
        """Get unlock sequence configuration"""
        return self.get_weston_config().get("unlock_sequence", {})

    # Convenience methods for ROK buttons

    def get_rok_screen_resolution(self) -> Tuple[int, int]:
        """
        Get ROK screen resolution

        Returns:
            Tuple of (width, height)
        """
        res = self.get_rok_button_config().get("screen_resolution", {})
        return (res.get("width", 1024), res.get("height", 568))

    def get_menu_button_position(self) -> Tuple[int, int]:
        """
        Get main menu button position

        Returns:
            Tuple of (x, y)
        """
        buttons = self.get_rok_button_config().get("buttons", {})
        menu = buttons.get("menu_main", {})
        pos = menu.get("position", {})
        return (pos.get("x", 990), pos.get("y", 530))

    def get_menu_button_detection(self) -> Dict[str, Any]:
        """Get main menu button detection configuration"""
        buttons = self.get_rok_button_config().get("buttons", {})
        menu = buttons.get("menu_main", {})
        return menu.get("detection", {})

    def get_tap_to_start_position(self) -> Tuple[int, int]:
        """
        Get tap to start position

        Returns:
            Tuple of (x, y)
        """
        buttons = self.get_rok_button_config().get("buttons", {})
        tap = buttons.get("tap_to_start", {})
        pos = tap.get("tap_position", {})
        return (pos.get("x", 512), pos.get("y", 284))


# Global singleton instance
_ui_config = None


def get_ui_config() -> UIConfig:
    """Get global UI config instance"""
    global _ui_config
    if _ui_config is None:
        _ui_config = UIConfig()
    return _ui_config


def reload_ui_config():
    """Reload global UI config"""
    global _ui_config
    if _ui_config is not None:
        _ui_config.reload()
    else:
        _ui_config = UIConfig()