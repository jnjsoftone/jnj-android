"""
Rise of Kingdoms App Controller

Handles RoK app launch, entry, and basic app lifecycle.
"""

import time
import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from android.adb_controller import SimpleADBController

logger = logging.getLogger(__name__)


class RoKApp:
    """Controller for Rise of Kingdoms app lifecycle"""

    PACKAGE_NAME = "com.lilithgames.rok.gpkr"  # Korean version
    MAIN_ACTIVITY = ".MainActivity"
    TIMEOUT_APP_START = 30  # seconds
    TIMEOUT_SCREEN_LOAD = 10  # seconds

    def __init__(self, adb_controller: 'SimpleADBController'):
        """
        Initialize RoK App Controller

        Args:
            adb_controller: ADB controller instance
        """
        self.adb = adb_controller

    def is_running(self) -> bool:
        """
        Check if RoK is running

        Returns:
            True if running, False otherwise
        """
        return self.adb.is_app_running(self.PACKAGE_NAME)

    def start(self, force_restart: bool = False) -> bool:
        """
        Launch Rise of Kingdoms

        Args:
            force_restart: Force restart even if already running

        Returns:
            True if successful, False otherwise
        """
        try:
            # Check if already running and focused
            if self.is_running() and not force_restart:
                activity = self.adb.get_current_activity()
                if activity and self.PACKAGE_NAME in activity:
                    logger.info("RoK is already running and focused")
                    return True

            # Stop if force restart or already running
            if force_restart or self.is_running():
                logger.info("Stopping RoK for restart...")
                self.stop(force=True)
                time.sleep(3)

            # Start the app
            success = self.adb.start_app(
                self.PACKAGE_NAME,
                self.MAIN_ACTIVITY
            )

            if not success:
                logger.error("Failed to start RoK")
                return False

            logger.info("RoK launch command sent")
            return True

        except Exception as e:
            logger.error(f"Error starting RoK: {e}")
            return False

    def stop(self, force: bool = False) -> bool:
        """
        Close Rise of Kingdoms

        Args:
            force: Force stop the app

        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Stopping RoK (force={force})...")

            if force:
                # Force stop the app
                return self.adb.stop_app(self.PACKAGE_NAME)
            else:
                # Graceful exit: press HOME button
                self.adb.press_key("HOME")
                time.sleep(1)
                return True

        except Exception as e:
            logger.error(f"Error stopping RoK: {e}")
            return False

    def restart(self) -> bool:
        """
        Restart Rise of Kingdoms

        Returns:
            True if successful, False otherwise
        """
        logger.info("Restarting RoK...")

        if not self.stop(force=True):
            logger.error("Failed to stop RoK")
            return False

        time.sleep(3)
        return self.start()

    def wait_for_ready(self, timeout: int = TIMEOUT_APP_START) -> bool:
        """
        Wait until RoK is ready

        Args:
            timeout: Maximum time to wait in seconds

        Returns:
            True if ready, False if timeout
        """
        logger.info(f"Waiting for RoK to be ready (timeout: {timeout}s)...")

        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.is_running():
                # Check if main activity is focused
                activity = self.adb.get_current_activity()
                if activity and self.PACKAGE_NAME in activity:
                    logger.info("RoK is ready")
                    return True

            time.sleep(1)

        logger.error(f"Timeout waiting for RoK to be ready ({timeout}s)")
        return False
