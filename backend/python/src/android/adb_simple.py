"""
Simple ADB Controller using subprocess

This uses the system's adb command instead of adb-shell library.
"""

import subprocess
import time
import io
from typing import Optional
from PIL import Image
import logging

logger = logging.getLogger(__name__)


class SimpleADBController:
    """Simple ADB controller using subprocess"""

    def __init__(self, device_id: str = "192.168.240.112:5555"):
        """
        Initialize Simple ADB controller

        Args:
            device_id: ADB device ID
        """
        self.device_id = device_id
        self._connected = False

    def connect(self, timeout: int = 5) -> bool:
        """
        Connect to ADB device

        Args:
            timeout: Connection timeout in seconds (default: 5)

        Returns:
            True if connection successful, False otherwise
        """
        try:
            # Connect to device
            result = subprocess.run(
                ["adb", "connect", self.device_id],
                capture_output=True,
                text=True,
                timeout=timeout
            )

            if "connected" in result.stdout.lower() or "already connected" in result.stdout.lower():
                self._connected = True
                logger.info(f"Connected to {self.device_id}")
                return True
            else:
                logger.warning(f"Failed to connect: {result.stdout}")
                return False

        except subprocess.TimeoutExpired:
            logger.debug(f"ADB connect timeout after {timeout}s - device may not be ready")
            return False
        except Exception as e:
            logger.debug(f"Error connecting: {e}")
            return False

    def disconnect(self) -> None:
        """Disconnect from ADB"""
        try:
            subprocess.run(["adb", "disconnect", self.device_id], capture_output=True)
            self._connected = False
            logger.info("Disconnected")
        except Exception as e:
            logger.error(f"Error disconnecting: {e}")

    def is_connected(self) -> bool:
        """Check if connected"""
        if not self._connected:
            return False

        try:
            result = subprocess.run(
                ["adb", "-s", self.device_id, "get-state"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.stdout.strip() == "device"
        except:
            return False

    def shell(self, command: str) -> str:
        """
        Execute shell command

        Args:
            command: Shell command to execute

        Returns:
            Command output
        """
        try:
            result = subprocess.run(
                ["adb", "-s", self.device_id, "shell", command],
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.stdout
        except Exception as e:
            logger.error(f"Error executing shell command: {e}")
            return ""

    def tap(self, x: int, y: int) -> bool:
        """Tap at coordinates"""
        try:
            self.shell(f"input tap {x} {y}")
            logger.debug(f"Tapped at ({x}, {y})")
            return True
        except Exception as e:
            logger.error(f"Error tapping: {e}")
            return False

    def x11_click(self, x: int, y: int) -> bool:
        """
        Click at X11 coordinates (for Weston lock screen)
        This bypasses Android and clicks directly on the X11 window
        Weston runs on DISPLAY :10.0
        """
        try:
            # Use xdotool to click on X11 display
            # Weston Compositor window is on DISPLAY :10.0
            result = subprocess.run(
                ["xdotool", "mousemove", str(x), str(y), "click", "1"],
                capture_output=True,
                text=True,
                timeout=5,
                env={**subprocess.os.environ, "DISPLAY": ":10.0"}
            )
            logger.info(f"X11 clicked at ({x}, {y}) on DISPLAY :10.0")
            return True
        except Exception as e:
            logger.error(f"Error X11 clicking: {e}")
            return False

    def swipe(self, x1: int, y1: int, x2: int, y2: int, duration: int = 300) -> bool:
        """Swipe gesture"""
        try:
            self.shell(f"input swipe {x1} {y1} {x2} {y2} {duration}")
            logger.debug(f"Swiped from ({x1}, {y1}) to ({x2}, {y2})")
            return True
        except Exception as e:
            logger.error(f"Error swiping: {e}")
            return False

    def screenshot(self) -> Optional[Image.Image]:
        """Capture screenshot"""
        try:
            result = subprocess.run(
                ["adb", "-s", self.device_id, "exec-out", "screencap", "-p"],
                capture_output=True,
                timeout=10
            )

            if result.returncode == 0:
                image = Image.open(io.BytesIO(result.stdout))
                logger.debug("Screenshot captured")
                return image
            else:
                logger.error("Failed to capture screenshot")
                return None

        except Exception as e:
            logger.error(f"Error capturing screenshot: {e}")
            return None

    def get_current_activity(self) -> Optional[str]:
        """Get current foreground activity"""
        try:
            result = self.shell("dumpsys window | grep mCurrentFocus")
            if result and "Window{" in result:
                activity = result.split(" ")[-1].strip().rstrip("}")
                logger.debug(f"Current activity: {activity}")
                return activity
            return None
        except Exception as e:
            logger.error(f"Error getting activity: {e}")
            return None

    def get_device_info(self) -> dict:
        """Get device information"""
        info = {}
        try:
            info["android_version"] = self.shell("getprop ro.build.version.release").strip()
            info["model"] = self.shell("getprop ro.product.model").strip()

            result = self.shell("wm size")
            if "Physical size:" in result:
                resolution = result.split("Physical size:")[-1].strip()
                info["resolution"] = resolution

            logger.debug(f"Device info: {info}")
            return info
        except Exception as e:
            logger.error(f"Error getting device info: {e}")
            return info

    def input_text(self, text: str) -> bool:
        """Input text"""
        try:
            escaped_text = text.replace(" ", "%s").replace("&", "\\&")
            self.shell(f"input text '{escaped_text}'")
            logger.debug(f"Inputted text: {text}")
            return True
        except Exception as e:
            logger.error(f"Error inputting text: {e}")
            return False

    def press_key(self, keycode: str) -> bool:
        """Press a key"""
        keycodes = {
            "BACK": "4",
            "HOME": "3",
            "MENU": "82",
            "POWER": "26",
            "ENTER": "66",
        }

        key = keycodes.get(keycode.upper(), keycode)

        try:
            self.shell(f"input keyevent {key}")
            logger.debug(f"Pressed key: {keycode}")
            return True
        except Exception as e:
            logger.error(f"Error pressing key: {e}")
            return False

    def start_app(self, package_name: str, activity_name: str = None) -> bool:
        """Start an application"""
        try:
            # First, use monkey to start the process in background
            monkey_result = self.shell(f"monkey -p {package_name} -c android.intent.category.LAUNCHER 1")

            # Wait a bit for the app to initialize
            time.sleep(2)

            # Then use am start to bring it to foreground
            if activity_name:
                component = f"{package_name}/{activity_name}"
            else:
                # Try to find the main activity
                dump_result = self.shell(f"dumpsys package {package_name} | grep -A 3 'android.intent.action.MAIN'")

                # Look for activity in the dump
                component = None
                for line in dump_result.split('\n'):
                    if package_name in line and "/" in line:
                        parts = line.split()
                        for part in parts:
                            if package_name in part and "/" in part:
                                component = part.strip()
                                break
                        if component:
                            break

                if not component:
                    # Default to common main activity name
                    component = f"{package_name}/com.harry.engine.MainActivity"

            # Bring to foreground
            self.shell(f"am start -n {component} -a android.intent.action.MAIN -c android.intent.category.LAUNCHER")
            logger.info(f"Started app: {package_name}")
            return True

        except Exception as e:
            logger.error(f"Error starting app: {e}")
            return False

    def stop_app(self, package_name: str) -> bool:
        """Force stop an application"""
        try:
            self.shell(f"am force-stop {package_name}")
            logger.info(f"Stopped app: {package_name}")
            return True
        except Exception as e:
            logger.error(f"Error stopping app: {e}")
            return False

    def is_app_running(self, package_name: str) -> bool:
        """Check if an application is running"""
        try:
            result = self.shell(f"pidof {package_name}")
            is_running = bool(result and result.strip())
            logger.debug(f"App {package_name} running: {is_running}")
            return is_running
        except Exception as e:
            logger.error(f"Error checking app status: {e}")
            return False