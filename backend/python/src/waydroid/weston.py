"""
Weston and Waydroid Controller

This module provides functions to manage Weston compositor and Waydroid.
"""

import subprocess
import time
import logging
import json
from pathlib import Path
from typing import Tuple, Optional, Dict, Any

logger = logging.getLogger(__name__)


class WestonController:
    """Controller for Weston compositor and Waydroid"""

    def __init__(self):
        """Initialize Weston controller"""
        self._load_config()
        self.weston_display = self.config.get("display", ":10.0")
        self.wayland_socket = "wayland-1"

    def _load_config(self):
        """Load UI configuration from JSON file"""
        try:
            # Path to ui_weston.json
            config_path = Path(__file__).resolve().parent.parent.parent.parent.parent / "database" / "json" / "ui_weston.json"

            with open(config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)

            logger.debug(f"Loaded Weston config from {config_path}")
        except Exception as e:
            logger.error(f"Error loading Weston config: {e}")
            # Use default config
            self.config = {
                "display": ":10.0",
                "window": {
                    "default_geometry": {"x": 0, "y": 0, "width": 1024, "height": 600}
                },
                "elements": {}
            }

    def reload_config(self):
        """Reload configuration from JSON file"""
        self._load_config()
        self.weston_display = self.config.get("display", ":10.0")

    def is_weston_running(self) -> bool:
        """
        Check if Weston compositor is running

        Returns:
            True if Weston is running, False otherwise
        """
        try:
            result = subprocess.run(
                ["pgrep", "-x", "weston"],
                capture_output=True,
                text=True,
                timeout=5
            )
            is_running = result.returncode == 0
            logger.debug(f"Weston running: {is_running}")
            return is_running
        except Exception as e:
            logger.error(f"Error checking Weston status: {e}")
            return False

    def is_weston_window_visible(self) -> bool:
        """
        Check if Weston window is visible on desktop using xwininfo

        Returns:
            True if Weston window is visible, False otherwise
        """
        try:
            result = subprocess.run(
                ["xwininfo", "-root", "-tree"],
                capture_output=True,
                text=True,
                timeout=5,
                env={**subprocess.os.environ, "DISPLAY": self.weston_display}
            )

            # Look for "Weston Compositor" in the window tree
            is_visible = "Weston Compositor" in result.stdout
            logger.debug(f"Weston window visible: {is_visible}")
            return is_visible

        except Exception as e:
            logger.error(f"Error checking Weston window visibility: {e}")
            return False

    def is_waydroid_running(self) -> bool:
        """
        Check if Waydroid is running

        Returns:
            True if Waydroid container is running, False otherwise
        """
        try:
            # Check if waydroid process is running
            result = subprocess.run(
                ["pgrep", "-f", "waydroid"],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode != 0:
                logger.debug("Waydroid process not running")
                return False

            # Also check waydroid status
            status_result = subprocess.run(
                ["waydroid", "status"],
                capture_output=True,
                text=True,
                timeout=5
            )

            is_running = "RUNNING" in status_result.stdout
            logger.debug(f"Waydroid running: {is_running}")
            return is_running

        except Exception as e:
            logger.error(f"Error checking Waydroid status: {e}")
            return False

    def start_weston(self) -> bool:
        """
        Start Weston compositor

        Returns:
            True if Weston started successfully, False otherwise
        """
        try:
            if self.is_weston_running():
                logger.info("Weston is already running")
                return True

            logger.info("Starting Weston compositor...")

            # Start Weston with X11 backend
            process = subprocess.Popen(
                ["weston", "--backend=x11-backend.so"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env={**subprocess.os.environ, "DISPLAY": self.weston_display}
            )

            # Wait for Weston to start
            for i in range(10):
                time.sleep(0.5)
                if self.is_weston_running():
                    logger.info("Weston started successfully")

                    # Move Weston window to top-left corner
                    time.sleep(1)  # Give Weston time to create the window
                    try:
                        import re
                        # Find Weston window ID using xwininfo
                        xwininfo_result = subprocess.run(
                            ["xwininfo", "-root", "-tree"],
                            capture_output=True,
                            text=True,
                            timeout=5,
                            env={**subprocess.os.environ, "DISPLAY": self.weston_display}
                        )

                        # Parse window ID from xwininfo output
                        # Format: 0x3000005 "Weston Compositor - screen0"
                        for line in xwininfo_result.stdout.split('\n'):
                            if 'Weston Compositor' in line:
                                match = re.search(r'(0x[0-9a-fA-F]+)', line)
                                if match:
                                    window_id = match.group(1)
                                    # Get default position from config
                                    default_geom = self.config.get("window", {}).get("default_geometry", {})
                                    target_x = default_geom.get("x", 0)
                                    target_y = default_geom.get("y", 0)
                                    # Move window to configured position
                                    subprocess.run(
                                        ["xdotool", "windowmove", window_id, str(target_x), str(target_y)],
                                        capture_output=True,
                                        timeout=5,
                                        env={**subprocess.os.environ, "DISPLAY": self.weston_display}
                                    )
                                    logger.info(f"Moved Weston window {window_id} to ({target_x}, {target_y})")
                                    break
                    except Exception as e:
                        logger.warning(f"Could not move Weston window: {e}")

                    return True

            logger.error("Weston failed to start in time")
            return False

        except Exception as e:
            logger.error(f"Error starting Weston: {e}")
            return False

    def stop_weston(self) -> bool:
        """
        Stop Weston compositor

        Returns:
            True if Weston stopped successfully, False otherwise
        """
        try:
            if not self.is_weston_running():
                logger.info("Weston is not running")
                return True

            logger.info("Stopping Weston compositor...")

            # Kill Weston process
            result = subprocess.run(
                ["pkill", "-x", "weston"],
                capture_output=True,
                text=True,
                timeout=5
            )

            # Wait for Weston to stop
            for i in range(10):
                time.sleep(0.5)
                if not self.is_weston_running():
                    logger.info("Weston stopped successfully")
                    return True

            logger.warning("Weston did not stop gracefully, forcing...")
            subprocess.run(["pkill", "-9", "-x", "weston"], timeout=5)
            time.sleep(1)

            return not self.is_weston_running()

        except Exception as e:
            logger.error(f"Error stopping Weston: {e}")
            return False

    def start_waydroid(self) -> bool:
        """
        Start Waydroid using the start-waydroid.sh script

        Returns:
            True if started successfully, False otherwise
        """
        from pathlib import Path

        try:
            # Check if already running
            if self.is_waydroid_running():
                logger.info("Waydroid is already running")
                return True

            # Use the existing start-waydroid.sh script
            script_path = Path.home() / ".local" / "bin" / "start-waydroid.sh"

            if not script_path.exists():
                logger.error(f"Waydroid start script not found: {script_path}")
                return False

            logger.info("Starting Waydroid using start-waydroid.sh...")

            # Run the script in background
            process = subprocess.Popen(
                [str(script_path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            # Wait for waydroid to be fully ready
            logger.info("Waiting for Waydroid to be ready...")
            for i in range(60):  # Wait up to 60 seconds
                time.sleep(1)

                if self.is_waydroid_running():
                    logger.info("Waydroid is running")
                    # Wait a bit more for full initialization
                    time.sleep(5)
                    return True

            logger.error("Waydroid failed to become ready in time")
            return False

        except Exception as e:
            logger.error(f"Error starting Waydroid: {e}")
            return False

    def stop_waydroid(self) -> bool:
        """
        Stop Waydroid session

        Returns:
            True if stopped successfully, False otherwise
        """
        try:
            if not self.is_waydroid_running():
                logger.info("Waydroid is not running")
                return True

            logger.info("Stopping Waydroid session...")

            # Stop waydroid session
            result = subprocess.run(
                ["waydroid", "session", "stop"],
                capture_output=True,
                text=True,
                timeout=30
            )

            # Wait for waydroid to stop
            for i in range(10):
                time.sleep(1)
                if not self.is_waydroid_running():
                    logger.info("Waydroid stopped successfully")
                    return True

            logger.warning("Waydroid did not stop gracefully, killing processes...")
            subprocess.run(["pkill", "-f", "waydroid"], timeout=5)
            time.sleep(2)

            return not self.is_waydroid_running()

        except Exception as e:
            logger.error(f"Error stopping Waydroid: {e}")
            return False

    def detect_weston_screen_state(self) -> str:
        """
        Detect detailed state of Weston screen using JSON configuration

        Returns:
            One of: "empty", "loading", "loaded", "lock", "black", "unknown"
        """
        try:
            import re
            from PIL import Image
            import io

            if not self.is_weston_running():
                return "unknown"

            # Reload config to get latest settings
            self.reload_config()

            # Get Weston window geometry from xwininfo (actual position)
            xwininfo_result = subprocess.run(
                ["xwininfo", "-root", "-tree"],
                capture_output=True,
                text=True,
                timeout=5,
                env={**subprocess.os.environ, "DISPLAY": self.weston_display}
            )

            # Use default geometry from config as fallback
            default_geom = self.config.get("window", {}).get("default_geometry", {})
            weston_x = default_geom.get("x", 0)
            weston_y = default_geom.get("y", 0)
            weston_w = default_geom.get("width", 1024)
            weston_h = default_geom.get("height", 600)

            # Get actual geometry from xwininfo
            for line in xwininfo_result.stdout.split('\n'):
                if 'Weston Compositor' in line:
                    match = re.search(r'(\d+)x(\d+)\+(\d+)\+(\d+)', line)
                    if match:
                        weston_w = int(match.group(1))
                        weston_h = int(match.group(2))
                        weston_x = int(match.group(3))
                        weston_y = int(match.group(4))
                        break

            # Capture screenshot
            result = subprocess.run(
                ["import", "-window", "root", "png:-"],
                capture_output=True,
                timeout=5,
                env={**subprocess.os.environ, "DISPLAY": self.weston_display}
            )

            if result.returncode != 0:
                return "unknown"

            screenshot = Image.open(io.BytesIO(result.stdout))
            center_x = weston_x + weston_w // 2
            center_y = weston_y + weston_h // 2

            elements = self.config.get("elements", {})

            # Check 0: If Waydroid is not running, it must be empty
            if not self.is_waydroid_running():
                return "empty"

            # Check 1: Black screen (from JSON config)
            black_config = elements.get("black_screen", {})
            if black_config:
                detection = black_config.get("detection", {})
                sample_area = detection.get("sample_area", {})
                color_range = detection.get("color_range", {})
                threshold = detection.get("threshold", {})

                x_range = sample_area.get("x_range", {})
                y_range = sample_area.get("y_range", {})

                black_count = 0
                total_samples = 0
                for dx in range(x_range.get("min", -10), x_range.get("max", 11), x_range.get("step", 5)):
                    for dy in range(y_range.get("min", -10), y_range.get("max", 11), y_range.get("step", 5)):
                        x, y = center_x + dx, center_y + dy
                        if 0 <= x < screenshot.size[0] and 0 <= y < screenshot.size[1]:
                            pixel = screenshot.getpixel((x, y))
                            r, g, b = pixel[0], pixel[1], pixel[2] if len(pixel) >= 3 else (0, 0, 0)

                            r_range = color_range.get("r", {})
                            g_range = color_range.get("g", {})
                            b_range = color_range.get("b", {})

                            if (r_range.get("min", 0) <= r <= r_range.get("max", 10) and
                                g_range.get("min", 0) <= g <= g_range.get("max", 10) and
                                b_range.get("min", 0) <= b <= b_range.get("max", 10)):
                                black_count += 1
                            total_samples += 1

                ratio_threshold = threshold.get("ratio", 0.8)
                if total_samples > 0 and black_count / total_samples > ratio_threshold:
                    return "black"

            # Check 2: Lock screen (from JSON config)
            unlock_config = elements.get("button_unlock", {})
            if unlock_config:
                position = unlock_config.get("position", {})
                detection = unlock_config.get("detection", {})
                sample_area = detection.get("sample_area", {})
                color_range = detection.get("color_range", {})
                threshold = detection.get("threshold", {})

                unlock_x = position.get("x", 129)
                unlock_y = position.get("y", 104)
                sample_w = sample_area.get("width", 3)
                sample_h = sample_area.get("height", 3)

                green_count = 0
                lock_samples = 0
                for dx in range(-(sample_w // 2), (sample_w // 2) + 1):
                    for dy in range(-(sample_h // 2), (sample_h // 2) + 1):
                        x, y = unlock_x + dx, unlock_y + dy
                        if 0 <= x < screenshot.size[0] and 0 <= y < screenshot.size[1]:
                            pixel = screenshot.getpixel((x, y))
                            r, g, b = pixel[0], pixel[1], pixel[2] if len(pixel) >= 3 else (0, 0, 0)

                            r_range = color_range.get("r", {})
                            g_range = color_range.get("g", {})
                            b_range = color_range.get("b", {})

                            if (r_range.get("min", 130) <= r <= r_range.get("max", 145) and
                                g_range.get("min", 125) <= g <= g_range.get("max", 140) and
                                b_range.get("min", 125) <= b <= b_range.get("max", 135)):
                                green_count += 1
                            lock_samples += 1

                min_pixels = threshold.get("min_pixels", 1)
                if lock_samples > 0 and green_count >= min_pixels:
                    return "lock"

            # Check 3: Loading vs Loaded (앱 아이콘 확인)
            # 하단 중앙 부근에서 컬러풀한 픽셀 확인 (앱 아이콘들)
            icon_area_y = weston_y + int(weston_h * 0.7)  # 하단 30% 영역
            icon_area_x_start = weston_x + int(weston_w * 0.3)
            icon_area_x_end = weston_x + int(weston_w * 0.7)

            colorful_count = 0
            icon_samples = 0
            for x in range(icon_area_x_start, icon_area_x_end, 20):
                for dy in range(-20, 21, 10):
                    y = icon_area_y + dy
                    if 0 <= x < screenshot.size[0] and 0 <= y < screenshot.size[1]:
                        pixel = screenshot.getpixel((x, y))
                        r, g, b = pixel[0], pixel[1], pixel[2] if len(pixel) >= 3 else (0, 0, 0)
                        # 컬러풀한 픽셀 (앱 아이콘)
                        if max(r, g, b) > 100 and (max(r, g, b) - min(r, g, b)) > 30:
                            colorful_count += 1
                        icon_samples += 1

            if icon_samples > 0 and colorful_count / icon_samples > 0.1:
                return "loaded"
            else:
                return "loading"

        except Exception as e:
            logger.error(f"Error detecting Weston screen state: {e}")
            return "unknown"

    def is_notification_panel_shown(self) -> bool:
        """
        Check if Android notification panel is shown

        Returns:
            True if notification panel is visible, False otherwise
        """
        try:
            # Check current activity
            result = subprocess.run(
                ["adb", "-s", "192.168.240.112:5555", "shell",
                 "dumpsys window | grep mCurrentFocus"],
                capture_output=True,
                text=True,
                timeout=5
            )

            current_focus = result.stdout.lower()

            # Check for notification panel indicators
            notification_indicators = [
                "statusbar",
                "notificationshade",
                "systemui",
                "panelview"
            ]

            for indicator in notification_indicators:
                if indicator in current_focus:
                    logger.info(f"Notification panel detected: {current_focus.strip()}")
                    return True

            return False

        except Exception as e:
            logger.error(f"Error checking notification panel: {e}")
            return False

    def close_notification_panel(self) -> bool:
        """
        Close Android notification panel by pressing BACK button

        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info("Closing notification panel with BACK button...")

            result = subprocess.run(
                ["adb", "-s", "192.168.240.112:5555", "shell", "input keyevent 4"],
                capture_output=True,
                text=True,
                timeout=5
            )

            time.sleep(1)

            # Verify it's closed
            if not self.is_notification_panel_shown():
                logger.info("Notification panel closed successfully")
                return True
            else:
                logger.warning("Notification panel still visible after BACK press")
                return False

        except Exception as e:
            logger.error(f"Error closing notification panel: {e}")
            return False

    def get_status(self) -> dict:
        """
        Get current status of Weston and Waydroid

        Returns:
            Dictionary with status information
        """
        weston_running = self.is_weston_running()
        weston_visible = self.is_weston_window_visible() if weston_running else False
        screen_state = self.detect_weston_screen_state() if weston_running else "unknown"
        notification_shown = self.is_notification_panel_shown() if self.is_waydroid_running() else False

        return {
            "weston": {
                "running": weston_running,
                "window_visible": weston_visible,
                "screen_state": screen_state
            },
            "waydroid": {
                "running": self.is_waydroid_running(),
                "notification_panel": notification_shown
            }
        }
