"""
Rise of Kingdoms Actions

Handles automated actions and tap sequences in RoK.
"""

import time
import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from android.adb_controller import SimpleADBController
    from common.ui_config import UIConfig
    from apps.rok.ui_detector import RoKUIDetector

logger = logging.getLogger(__name__)


class RoKActions:
    """Automated actions for Rise of Kingdoms"""

    def __init__(self, adb_controller: 'SimpleADBController',
                 ui_config: 'UIConfig',
                 ui_detector: 'RoKUIDetector'):
        """
        Initialize RoK Actions

        Args:
            adb_controller: ADB controller instance
            ui_config: UI configuration manager
            ui_detector: UI detector instance
        """
        self.adb = adb_controller
        self.ui_config = ui_config
        self.ui_detector = ui_detector

    def perform_startup_taps(self) -> bool:
        """
        Perform taps to bypass Weston lock screen and game startup screens
        Uses multiple taps at different time intervals to ensure we catch all loading screens

        Returns:
            True if main game screen was reached, False otherwise
        """
        logger.info("Performing extended startup tap sequence...")

        # Get positions from config
        weston_x, weston_y, weston_w, weston_h = self.ui_config.get_weston_window_geometry()
        center_x = weston_x + weston_w // 2
        center_y = weston_y + weston_h // 2
        tap_x, tap_y = self.ui_config.get_tap_to_start_position()

        # First: X11 clicks for Weston unlock (bypasses Wayland compositor)
        logger.info("Initial X11 clicks (0-3s): Unlocking Weston at X11 level...")
        for i in range(5):
            self.adb.x11_click(center_x, center_y)
            time.sleep(0.5)

        # Give Weston time to unlock
        time.sleep(2)

        # Then: Android taps for game startup
        logger.info("Android taps (5-10s): Initial game taps...")
        for i in range(3):
            self.adb.tap(tap_x, tap_y)
            time.sleep(1)

        # Tap at specific intervals: 20s, 30s, 40s, 50s, 60s, 70s, 80s
        # This catches various loading stages: initial loading, "Tap to Start", etc.
        tap_intervals = [20, 30, 40, 50, 60, 70, 80]  # seconds from start
        start_time = time.time()

        for target_time in tap_intervals:
            # Check if already in main game before next tap
            if self.ui_detector.is_in_main_game():
                logger.info(f"Main game screen detected at {time.time() - start_time:.1f}s, stopping tap sequence")
                return True

            # Wait until target time
            elapsed = time.time() - start_time
            wait_time = target_time - elapsed

            if wait_time > 0:
                logger.info(f"Waiting {wait_time:.1f}s until {target_time}s mark...")
                # Check periodically during wait
                for _ in range(int(wait_time)):
                    if self.ui_detector.is_in_main_game():
                        logger.info(f"Main game screen detected during wait at {time.time() - start_time:.1f}s")
                        return True
                    time.sleep(1)
                # Sleep remaining fraction
                time.sleep(wait_time % 1)

            # Perform taps at this interval (both X11 and Android)
            logger.info(f"Tapping at {target_time}s mark...")

            # Try X11 click first (for Weston)
            self.adb.x11_click(center_x, center_y)
            time.sleep(0.3)
            # Then Android tap (for game)
            for i in range(3):
                self.adb.tap(tap_x, tap_y)
                time.sleep(0.5)

        logger.info("Extended tap sequence completed")

        # Final check after all taps
        if self.ui_detector.is_in_main_game():
            logger.info("Main game screen confirmed after tap sequence")
            return True

        return False
