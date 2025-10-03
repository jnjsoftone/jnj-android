"""
ADB Controller for Waydroid

This module provides a controller class to interact with Waydroid via ADB.
"""

import time
import io
import os
from pathlib import Path
from typing import Optional, Tuple
from PIL import Image
from adb_shell.adb_device import AdbDeviceTcp
from adb_shell.auth.sign_pythonrsa import PythonRSASigner
from adb_shell.auth.keygen import keygen
import logging

logger = logging.getLogger(__name__)


class WaydroidController:
    """Controller for Waydroid Android emulator via ADB"""

    def __init__(self, host: str = "192.168.240.112", port: int = 5555):
        """
        Initialize Waydroid controller

        Args:
            host: ADB host address (default: Waydroid IP)
            port: ADB port number
        """
        self.host = host
        self.port = port
        self.device: Optional[AdbDeviceTcp] = None
        self._connected = False

    def connect(self) -> bool:
        """
        Connect to Waydroid ADB

        Returns:
            True if connection successful, False otherwise
        """
        try:
            # Load ADB keys from default location
            adbkey_path = Path.home() / ".android" / "adbkey"
            adbkey_pub_path = Path(str(adbkey_path) + '.pub')

            signer = None
            if adbkey_path.exists() and adbkey_pub_path.exists():
                # Use existing keys
                with open(str(adbkey_path)) as f:
                    priv = f.read()
                with open(str(adbkey_pub_path)) as f:
                    pub = f.read()
                signer = PythonRSASigner(pub, priv)
                logger.debug("Loaded existing ADB keys")
            else:
                # Generate new keys
                logger.info("Generating new ADB keys...")
                adbkey_path.parent.mkdir(parents=True, exist_ok=True)
                keygen(str(adbkey_path))

                # Load the generated keys
                with open(str(adbkey_path)) as f:
                    priv = f.read()
                with open(str(adbkey_pub_path)) as f:
                    pub = f.read()

                signer = PythonRSASigner(pub, priv)
                logger.info("Generated new ADB keys")

            self.device = AdbDeviceTcp(self.host, self.port, default_transport_timeout_s=9.0)
            self.device.connect(rsa_keys=[signer], auth_timeout_s=10.0)
            self._connected = True
            logger.info(f"Connected to Waydroid at {self.host}:{self.port}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Waydroid: {e}")
            self._connected = False
            return False

    def disconnect(self) -> None:
        """Disconnect from ADB"""
        if self.device:
            try:
                self.device.close()
                self._connected = False
                logger.info("Disconnected from Waydroid")
            except Exception as e:
                logger.error(f"Error disconnecting: {e}")

    def is_connected(self) -> bool:
        """Check if connected to ADB"""
        return self._connected and self.device is not None

    def tap(self, x: int, y: int) -> bool:
        """
        Tap at specified coordinates

        Args:
            x: X coordinate
            y: Y coordinate

        Returns:
            True if successful, False otherwise
        """
        if not self.is_connected():
            logger.error("Not connected to Waydroid")
            return False

        try:
            result = self.device.shell(f"input tap {x} {y}")
            logger.debug(f"Tapped at ({x}, {y})")
            return True
        except Exception as e:
            logger.error(f"Failed to tap: {e}")
            return False

    def swipe(self, x1: int, y1: int, x2: int, y2: int, duration: int = 300) -> bool:
        """
        Swipe from one point to another

        Args:
            x1: Start X coordinate
            y1: Start Y coordinate
            x2: End X coordinate
            y2: End Y coordinate
            duration: Duration in milliseconds

        Returns:
            True if successful, False otherwise
        """
        if not self.is_connected():
            logger.error("Not connected to Waydroid")
            return False

        try:
            result = self.device.shell(f"input swipe {x1} {y1} {x2} {y2} {duration}")
            logger.debug(f"Swiped from ({x1}, {y1}) to ({x2}, {y2})")
            return True
        except Exception as e:
            logger.error(f"Failed to swipe: {e}")
            return False

    def screenshot(self) -> Optional[Image.Image]:
        """
        Capture screenshot

        Returns:
            PIL Image object if successful, None otherwise
        """
        if not self.is_connected():
            logger.error("Not connected to Waydroid")
            return None

        try:
            # Capture screenshot via ADB
            result = self.device.shell("screencap -p", decode=False)

            # Convert bytes to PIL Image
            image = Image.open(io.BytesIO(result))
            logger.debug("Screenshot captured")
            return image
        except Exception as e:
            logger.error(f"Failed to capture screenshot: {e}")
            return None

    def get_current_activity(self) -> Optional[str]:
        """
        Get current foreground activity

        Returns:
            Activity name if successful, None otherwise
        """
        if not self.is_connected():
            logger.error("Not connected to Waydroid")
            return None

        try:
            result = self.device.shell("dumpsys window | grep mCurrentFocus")
            # Parse result like: mCurrentFocus=Window{abc123 u0 com.example/com.example.MainActivity}
            if result and "Window{" in result:
                activity = result.split(" ")[-1].strip().rstrip("}")
                logger.debug(f"Current activity: {activity}")
                return activity
            return None
        except Exception as e:
            logger.error(f"Failed to get current activity: {e}")
            return None

    def get_device_info(self) -> dict:
        """
        Get device information

        Returns:
            Dictionary containing device info
        """
        if not self.is_connected():
            logger.error("Not connected to Waydroid")
            return {}

        info = {}
        try:
            # Get Android version
            info["android_version"] = self.device.shell("getprop ro.build.version.release").strip()

            # Get device model
            info["model"] = self.device.shell("getprop ro.product.model").strip()

            # Get screen resolution
            result = self.device.shell("wm size")
            if "Physical size:" in result:
                resolution = result.split("Physical size:")[-1].strip()
                info["resolution"] = resolution

            logger.debug(f"Device info: {info}")
            return info
        except Exception as e:
            logger.error(f"Failed to get device info: {e}")
            return info

    def input_text(self, text: str) -> bool:
        """
        Input text

        Args:
            text: Text to input

        Returns:
            True if successful, False otherwise
        """
        if not self.is_connected():
            logger.error("Not connected to Waydroid")
            return False

        try:
            # Escape special characters
            escaped_text = text.replace(" ", "%s").replace("&", "\\&")
            result = self.device.shell(f"input text '{escaped_text}'")
            logger.debug(f"Inputted text: {text}")
            return True
        except Exception as e:
            logger.error(f"Failed to input text: {e}")
            return False

    def press_key(self, keycode: str) -> bool:
        """
        Press a key

        Args:
            keycode: Key code (e.g., 'BACK', 'HOME', 'MENU')

        Returns:
            True if successful, False otherwise
        """
        if not self.is_connected():
            logger.error("Not connected to Waydroid")
            return False

        # Convert key name to keycode number if needed
        keycodes = {
            "BACK": "4",
            "HOME": "3",
            "MENU": "82",
            "POWER": "26",
            "ENTER": "66",
        }

        key = keycodes.get(keycode.upper(), keycode)

        try:
            result = self.device.shell(f"input keyevent {key}")
            logger.debug(f"Pressed key: {keycode}")
            return True
        except Exception as e:
            logger.error(f"Failed to press key: {e}")
            return False

    def start_app(self, package_name: str) -> bool:
        """
        Start an application

        Args:
            package_name: Package name of the app

        Returns:
            True if successful, False otherwise
        """
        if not self.is_connected():
            logger.error("Not connected to Waydroid")
            return False

        try:
            result = self.device.shell(f"monkey -p {package_name} -c android.intent.category.LAUNCHER 1")
            logger.info(f"Started app: {package_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to start app: {e}")
            return False

    def stop_app(self, package_name: str) -> bool:
        """
        Force stop an application

        Args:
            package_name: Package name of the app

        Returns:
            True if successful, False otherwise
        """
        if not self.is_connected():
            logger.error("Not connected to Waydroid")
            return False

        try:
            result = self.device.shell(f"am force-stop {package_name}")
            logger.info(f"Stopped app: {package_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to stop app: {e}")
            return False

    def is_app_running(self, package_name: str) -> bool:
        """
        Check if an application is running

        Args:
            package_name: Package name of the app

        Returns:
            True if running, False otherwise
        """
        if not self.is_connected():
            logger.error("Not connected to Waydroid")
            return False

        try:
            result = self.device.shell(f"pidof {package_name}")
            is_running = bool(result and result.strip())
            logger.debug(f"App {package_name} running: {is_running}")
            return is_running
        except Exception as e:
            logger.error(f"Failed to check if app is running: {e}")
            return False