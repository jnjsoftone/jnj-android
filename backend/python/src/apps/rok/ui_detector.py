"""
Rise of Kingdoms UI Detector

Detects various UI states and elements in RoK.
"""

import logging
from typing import TYPE_CHECKING, Tuple, Optional

if TYPE_CHECKING:
    from android.adb_controller import SimpleADBController
    from common.ui_config import UIConfig

logger = logging.getLogger(__name__)


class RoKUIDetector:
    """Detects UI elements and states in Rise of Kingdoms"""

    def __init__(self, adb_controller: 'SimpleADBController', ui_config: 'UIConfig'):
        """
        Initialize RoK UI Detector

        Args:
            adb_controller: ADB controller instance
            ui_config: UI configuration manager
        """
        self.adb = adb_controller
        self.ui_config = ui_config

    def is_in_main_game(self) -> bool:
        """
        Check if the game has fully loaded and entered the main game screen

        This uses multiple checks:
        1. Game process is running
        2. MainActivity is focused
        3. Blue menu button in bottom-right corner (definitive check)

        Returns:
            True if in main game, False otherwise
        """
        try:
            # Check 1: Game must be running
            if not self.adb.is_app_running("com.lilithgames.rok.gpkr"):
                logger.debug("Game not running")
                return False

            # Check 2: MainActivity must be focused
            activity = self.adb.get_current_activity()
            if not activity or "com.lilithgames.rok.gpkr" not in activity:
                logger.debug(f"Game not focused. Current activity: {activity}")
                return False

            # Check 3: Look for blue menu button using config
            screenshot = self.adb.screenshot()
            if screenshot:
                menu_x, menu_y = self.ui_config.get_menu_button_position()
                menu_detection = self.ui_config.get_menu_button_detection()

                sample_area = menu_detection.get("sample_area", {})
                offsets = sample_area.get("offsets", [-2, 0, 2])

                blue_count = 0
                total_samples = 0

                for dx in offsets:
                    for dy in offsets:
                        x = menu_x + dx
                        y = menu_y + dy

                        if 0 <= x < screenshot.size[0] and 0 <= y < screenshot.size[1]:
                            pixel = screenshot.getpixel((x, y))
                            r, g, b = pixel[0], pixel[1], pixel[2] if len(pixel) >= 3 else (0, 0, 0)

                            # Check color range from config
                            color_range = menu_detection.get("color_range", {})
                            r_range = color_range.get("r", {})
                            g_range = color_range.get("g", {})
                            b_range = color_range.get("b", {})

                            if (r_range.get("min", 0) <= r <= r_range.get("max", 50) and
                                g_range.get("min", 60) <= g <= g_range.get("max", 140) and
                                b_range.get("min", 110) <= b <= b_range.get("max", 170)):
                                blue_count += 1
                            total_samples += 1

                threshold = menu_detection.get("threshold", {}).get("min_pixels", 1)
                if total_samples > 0 and blue_count >= threshold:
                    logger.info(f"In main game (menu button: {blue_count}/{total_samples})")
                    return True

            logger.debug("Not in main game")
            return False

        except Exception as e:
            logger.error(f"Error checking if in main game: {e}")
            return False

    def get_pixel_color(self, x: int, y: int) -> Optional[Tuple[int, int, int]]:
        """
        Get RGB color at specific coordinates

        Args:
            x: X coordinate
            y: Y coordinate

        Returns:
            (R, G, B) tuple or None if error
        """
        try:
            screenshot = self.adb.screenshot()
            if screenshot and 0 <= x < screenshot.size[0] and 0 <= y < screenshot.size[1]:
                pixel = screenshot.getpixel((x, y))
                return (pixel[0], pixel[1], pixel[2] if len(pixel) >= 3 else 0)
            return None
        except Exception as e:
            logger.error(f"Error getting pixel color at ({x}, {y}): {e}")
            return None

    def is_color_in_range(self, color: tuple, target_color: tuple, tolerance: int = 30) -> bool:
        """
        Check if a color is within tolerance of a target color

        Args:
            color: (R, G, B) tuple
            target_color: (R, G, B) tuple to compare against
            tolerance: Allowed difference per channel (0-255)

        Returns:
            True if color is within tolerance
        """
        if not color or not target_color:
            return False

        return all(abs(c - t) <= tolerance for c, t in zip(color, target_color))
