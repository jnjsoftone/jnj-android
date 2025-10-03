"""
Waydroid Container Control

Manages Waydroid container and session lifecycle.
"""

import subprocess
import time
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class WaydroidContainer:
    """Controller for Waydroid container operations"""

    def __init__(self):
        """Initialize Waydroid container controller"""
        self.start_script_path = Path.home() / ".local" / "bin" / "start-waydroid.sh"

    def is_running(self) -> bool:
        """
        Check if Waydroid is running

        Returns:
            True if Waydroid container is running, False otherwise
        """
        try:
            # Check if waydroid container is running
            result = subprocess.run(
                ["pgrep", "-f", "waydroid"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception as e:
            logger.error(f"Error checking Waydroid status: {e}")
            return False

    def get_status(self) -> dict:
        """
        Get Waydroid status

        Returns:
            Dict with session and vendor_type info
        """
        try:
            result = subprocess.run(
                ["waydroid", "status"],
                capture_output=True,
                text=True,
                timeout=5
            )

            status = {"session": "UNKNOWN", "vendor_type": "UNKNOWN"}

            for line in result.stdout.split('\n'):
                if "Session:" in line:
                    status["session"] = line.split(":", 1)[1].strip()
                elif "Vendor type:" in line:
                    status["vendor_type"] = line.split(":", 1)[1].strip()

            return status

        except Exception as e:
            logger.error(f"Error getting Waydroid status: {e}")
            return {"session": "ERROR", "vendor_type": "ERROR", "error": str(e)}

    def start(self, adb_controller=None) -> bool:
        """
        Start Waydroid using the start-waydroid.sh script

        This script handles:
        - Starting Weston compositor if not running
        - Setting up WAYLAND_DISPLAY
        - Starting Waydroid session

        Args:
            adb_controller: Optional ADB controller to verify connection

        Returns:
            True if started successfully, False otherwise
        """
        try:
            if not self.start_script_path.exists():
                logger.error(f"Waydroid start script not found: {self.start_script_path}")
                return False

            logger.info("Starting Waydroid using start-waydroid.sh...")

            # Run the script in background
            process = subprocess.Popen(
                [str(self.start_script_path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            # Wait for waydroid to be fully ready
            logger.info("Waiting for Waydroid to be ready...")
            for i in range(60):  # Wait up to 60 seconds
                time.sleep(1)

                # Check if Waydroid session is running
                status = self.get_status()

                if status.get("session") == "RUNNING":
                    logger.info("Waydroid session is running")

                    # Wait a bit more for ADB to be ready
                    time.sleep(5)

                    # Try to connect ADB if controller provided
                    if adb_controller:
                        if adb_controller.is_connected() or adb_controller.connect():
                            logger.info("Waydroid is ready and ADB connected")
                            return True
                    else:
                        return True

            logger.error("Waydroid failed to become ready in time")
            return False

        except Exception as e:
            logger.error(f"Error starting Waydroid: {e}")
            return False

    def stop(self) -> bool:
        """
        Stop Waydroid session

        Returns:
            True if stopped successfully
        """
        try:
            logger.info("Stopping Waydroid session...")

            result = subprocess.run(
                ["waydroid", "session", "stop"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                logger.info("Waydroid session stopped")
                return True
            else:
                logger.error(f"Failed to stop Waydroid: {result.stderr}")
                return False

        except Exception as e:
            logger.error(f"Error stopping Waydroid: {e}")
            return False

    def ensure_running(self, adb_controller=None) -> bool:
        """
        Ensure Waydroid is running, start if needed

        Args:
            adb_controller: Optional ADB controller to verify connection

        Returns:
            True if Waydroid is running or was started successfully
        """
        if self.is_running():
            status = self.get_status()
            if status.get("session") == "RUNNING":
                logger.debug("Waydroid is already running")
                return True

        logger.info("Waydroid is not running, starting it...")
        return self.start(adb_controller)
