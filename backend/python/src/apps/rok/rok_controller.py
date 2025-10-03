"""
Game Controller for Rise of Kingdoms

This module provides a controller class for game automation.
"""

import time
import logging
from typing import Optional, TYPE_CHECKING
from .ui_config import get_ui_config

if TYPE_CHECKING:
    from android.adb_controller import WaydroidController
    from android.adb_simple import SimpleADBController

logger = logging.getLogger(__name__)


class GameController:
    """Controller for Rise of Kingdoms game automation"""

    # Rise of Kingdoms package name (Korean version)
    PACKAGE_NAME = "com.lilithgames.rok.gpkr"

    # Common timeouts
    TIMEOUT_APP_START = 30  # seconds
    TIMEOUT_SCREEN_LOAD = 10  # seconds

    def __init__(self, adb_controller):
        """
        Initialize Game Controller

        Args:
            adb_controller: ADB controller instance
        """
        self.adb = adb_controller
        self.ui_config = get_ui_config()
        if not self.adb.is_connected():
            self.adb.connect()

    def is_waydroid_running(self) -> bool:
        """
        Check if Waydroid is running

        Returns:
            True if Waydroid container is running, False otherwise
        """
        import subprocess
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

    def start_waydroid(self) -> bool:
        """
        Start Waydroid using the start-waydroid.sh script

        This script handles:
        - Starting Weston compositor if not running
        - Setting up WAYLAND_DISPLAY
        - Starting Waydroid session

        Returns:
            True if started successfully, False otherwise
        """
        import subprocess
        from pathlib import Path

        try:
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

                # Check if Waydroid session is running
                status_result = subprocess.run(
                    ["waydroid", "status"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )

                if "RUNNING" in status_result.stdout:
                    logger.info("Waydroid session is running")

                    # Wait a bit more for ADB to be ready
                    time.sleep(5)

                    # Try to connect ADB
                    if self.adb.is_connected() or self.adb.connect():
                        logger.info("Waydroid is ready and ADB connected")
                        return True

            logger.error("Waydroid failed to become ready in time")
            return False

        except Exception as e:
            logger.error(f"Error starting Waydroid: {e}")
            return False

    def ensure_waydroid_running(self) -> bool:
        """
        Ensure Waydroid is running, start if needed

        Returns:
            True if Waydroid is running or was started successfully
        """
        if self.is_waydroid_running():
            logger.debug("Waydroid is already running")
            return True

        logger.info("Waydroid is not running, starting it...")
        return self.start_waydroid()

    def start_game(self, wait_for_ready: bool = True, auto_tap: bool = True, force_restart: bool = False) -> bool:
        """
        Launch Rise of Kingdoms

        Args:
            wait_for_ready: Whether to wait for game to be ready
            auto_tap: Whether to automatically tap "Tap to Start" screen
            force_restart: Force restart even if already running

        Returns:
            True if successful, False otherwise
        """
        logger.info("Starting Rise of Kingdoms...")

        try:
            # Ensure Waydroid is running
            if not self.ensure_waydroid_running():
                logger.error("Failed to start Waydroid")
                return False

            # Check if Weston is locked first
            if self.is_weston_locked():
                self._unlock_weston()
            # Check if already running and focused
            if self.check_game_running() and not force_restart:
                activity = self.adb.get_current_activity()
                if activity and self.PACKAGE_NAME in activity:
                    logger.info("Game is already running and focused")
                    # Still try to tap if requested, in case we're at "Tap to Start"
                    if auto_tap:
                        logger.info("Attempting tap in case at 'Tap to Start' screen...")
                        self._perform_startup_taps()
                    return True
                else:
                    logger.info("Game running but not focused, bringing to foreground...")
                    # Bring to foreground
                    self.adb.start_app(self.PACKAGE_NAME, "com.harry.engine.MainActivity")
                    time.sleep(2)
                    if auto_tap:
                        self._perform_startup_taps()
                    return True

            # Kill existing process if any
            self.adb.stop_app(self.PACKAGE_NAME)
            time.sleep(2)

            # Launch the app
            if not self.adb.start_app(self.PACKAGE_NAME):
                logger.error("Failed to launch game")
                return False

            logger.info("Game launch command sent")

            # Wait for game to be ready
            if wait_for_ready:
                if not self.wait_for_game_ready():
                    return False

                # Check if already in main game (quick resume case after stop)
                if self.is_in_main_game():
                    logger.info("Already in main game screen, skipping startup taps")
                    return True

                # Auto tap to bypass "Tap to Start" screen
                if auto_tap:
                    if self._perform_startup_taps():
                        logger.info("Successfully entered main game via startup taps")
                        return True

                # Final verification (in case auto_tap was False or taps didn't detect it)
                logger.info("Final verification of main game screen entry...")
                for i in range(10):  # Check for up to 10 seconds
                    if self.is_in_main_game():
                        logger.info("Successfully entered main game screen")
                        return True
                    time.sleep(1)

                logger.warning("Game started but could not confirm main game screen entry")
                return True  # Return True anyway as game process is running

            return True

        except Exception as e:
            logger.error(f"Error starting game: {e}")
            return False

    def _perform_startup_taps(self) -> bool:
        """
        Perform taps to bypass Weston lock screen and game startup screens
        Uses multiple taps at different time intervals to ensure we catch all loading screens

        Returns:
            True if main game screen was reached, False otherwise
        """
        logger.info("Performing extended startup tap sequence...")

        # First: X11 clicks for Weston unlock (bypasses Wayland compositor)
        logger.info("Initial X11 clicks (0-3s): Unlocking Weston at X11 level...")
        # Weston window is 1024x600 at position (5, 29)
        # Center of Weston window: (5 + 1024/2, 29 + 600/2) = (517, 329)
        for i in range(5):
            self.adb.x11_click(517, 329)
            time.sleep(0.5)

        # Give Weston time to unlock
        time.sleep(2)

        # Then: Android taps for game startup
        logger.info("Android taps (5-10s): Initial game taps...")
        for i in range(3):
            self.adb.tap(512, 284)
            time.sleep(1)

        # Tap at specific intervals: 20s, 30s, 40s, 50s, 60s, 70s, 80s
        # This catches various loading stages: initial loading, "Tap to Start", etc.
        tap_intervals = [20, 30, 40, 50, 60, 70, 80]  # seconds from start
        start_time = time.time()

        for target_time in tap_intervals:
            # Check if already in main game before next tap
            if self.is_in_main_game():
                logger.info(f"Main game screen detected at {time.time() - start_time:.1f}s, stopping tap sequence")
                return True

            # Wait until target time
            elapsed = time.time() - start_time
            wait_time = target_time - elapsed

            if wait_time > 0:
                logger.info(f"Waiting {wait_time:.1f}s until {target_time}s mark...")
                # Check periodically during wait
                for _ in range(int(wait_time)):
                    if self.is_in_main_game():
                        logger.info(f"Main game screen detected during wait at {time.time() - start_time:.1f}s")
                        return True
                    time.sleep(1)
                # Sleep remaining fraction
                time.sleep(wait_time % 1)

            # Perform taps at this interval (both X11 and Android)
            logger.info(f"Tapping at {target_time}s mark...")

            # Get positions from config
            weston_x, weston_y, weston_w, weston_h = self.ui_config.get_weston_window_geometry()
            center_x = weston_x + weston_w // 2
            center_y = weston_y + weston_h // 2
            tap_x, tap_y = self.ui_config.get_tap_to_start_position()

            # Try X11 click first (for Weston)
            self.adb.x11_click(center_x, center_y)
            time.sleep(0.3)
            # Then Android tap (for game)
            for i in range(3):
                self.adb.tap(tap_x, tap_y)
                time.sleep(0.5)

        logger.info("Extended tap sequence completed")

        # Final check after all taps
        if self.is_in_main_game():
            logger.info("Main game screen confirmed after tap sequence")
            return True

        return False

    def end_game(self, force: bool = False) -> bool:
        """
        Close Rise of Kingdoms

        Args:
            force: Whether to force stop the app

        Returns:
            True if successful, False otherwise
        """
        logger.info("Ending Rise of Kingdoms...")

        try:
            if force:
                # Force stop
                return self.adb.stop_app(self.PACKAGE_NAME)
            else:
                # Graceful exit: press HOME button
                self.adb.press_key("HOME")
                time.sleep(1)
                return True

        except Exception as e:
            logger.error(f"Error ending game: {e}")
            return False

    def restart_game(self) -> bool:
        """
        Restart Rise of Kingdoms

        Returns:
            True if successful, False otherwise
        """
        logger.info("Restarting Rise of Kingdoms...")

        # Ensure Waydroid is running
        if not self.ensure_waydroid_running():
            logger.error("Failed to start Waydroid")
            return False

        # Check if Weston is locked first
        if self.is_weston_locked():
            self._unlock_weston()

        if not self.end_game(force=True):
            logger.error("Failed to stop game")
            return False

        time.sleep(3)

        return self.start_game()

    def check_game_running(self) -> bool:
        """
        Check if Rise of Kingdoms is running

        Returns:
            True if running, False otherwise
        """
        return self.adb.is_app_running(self.PACKAGE_NAME)

    def wait_for_game_ready(self, timeout: int = TIMEOUT_APP_START) -> bool:
        """
        Wait until game is ready

        Args:
            timeout: Maximum time to wait in seconds

        Returns:
            True if game is ready, False if timeout
        """
        logger.info(f"Waiting for game to be ready (timeout: {timeout}s)...")

        start_time = time.time()

        while time.time() - start_time < timeout:
            # Check if app is running
            if not self.check_game_running():
                logger.debug("Game not running yet...")
                time.sleep(2)
                continue

            # Check if we can get current activity
            activity = self.adb.get_current_activity()
            if activity and self.PACKAGE_NAME in activity:
                logger.info(f"Game is ready! Current activity: {activity}")
                return True

            time.sleep(2)

        logger.error(f"Timeout waiting for game to be ready ({timeout}s)")
        return False

    def get_game_status(self) -> dict:
        """
        Get current game status

        Returns:
            Dictionary containing game status information
        """
        status = {
            "running": self.check_game_running(),
            "activity": None,
            "timestamp": time.time()
        }

        if status["running"]:
            status["activity"] = self.adb.get_current_activity()

        return status

    def take_screenshot(self, save_path: Optional[str] = None):
        """
        Take a screenshot of current game screen

        Args:
            save_path: Path to save screenshot (optional)

        Returns:
            PIL Image object if successful, None otherwise
        """
        image = self.adb.screenshot()

        if image and save_path:
            try:
                image.save(save_path)
                logger.info(f"Screenshot saved to {save_path}")
            except Exception as e:
                logger.error(f"Failed to save screenshot: {e}")

        return image

    def get_pixel_color(self, x: int, y: int) -> Optional[tuple]:
        """
        Get the RGB color at a specific pixel coordinate

        Args:
            x: X coordinate
            y: Y coordinate

        Returns:
            Tuple of (R, G, B) values, or None if failed
        """
        try:
            screenshot = self.adb.screenshot()
            if screenshot:
                pixel = screenshot.getpixel((x, y))
                # Handle both RGB and RGBA
                if len(pixel) >= 3:
                    return (pixel[0], pixel[1], pixel[2])
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

    def _unlock_weston(self) -> bool:
        """
        Unlock Weston using configuration from JSON

        Returns:
            True if unlocked successfully, False otherwise
        """
        logger.info("Weston is locked, unlocking...")

        # Get unlock sequence from config
        unlock_seq = self.ui_config.get_unlock_sequence()
        steps = unlock_seq.get("steps", [])
        retry_config = unlock_seq.get("retry", {})
        max_attempts = retry_config.get("max_attempts", 2)

        # Get window geometry for center calculation
        weston_x, weston_y, weston_w, weston_h = self.ui_config.get_weston_window_geometry()
        center_x = weston_x + weston_w // 2
        center_y = weston_y + weston_h // 2

        # Get unlock button position
        unlock_x, unlock_y = self.ui_config.get_unlock_button_position()

        for attempt in range(max_attempts):
            if attempt > 0:
                logger.info(f"Unlock attempt {attempt + 1}/{max_attempts}")

            # Execute unlock sequence steps
            for step in steps:
                action = step.get("action")
                target = step.get("target")
                wait_after = step.get("wait_after", 0)

                if action == "click":
                    if target == "center":
                        self.adb.x11_click(center_x, center_y)
                        logger.debug(f"Clicked center ({center_x}, {center_y})")
                    elif target == "button_unlock":
                        self.adb.x11_click(unlock_x, unlock_y)
                        logger.debug(f"Clicked unlock button ({unlock_x}, {unlock_y})")

                if wait_after > 0:
                    time.sleep(wait_after)

            # Verify if requested
            if retry_config.get("verify_after_each", False):
                if not self.is_weston_locked():
                    logger.info(f"Weston unlocked successfully on attempt {attempt + 1}")
                    return True
                elif attempt < max_attempts - 1:
                    logger.warning(f"Still locked after attempt {attempt + 1}, retrying...")

        # Final check
        if not self.is_weston_locked():
            logger.info("Weston unlocked successfully")
            return True
        else:
            logger.error(f"Failed to unlock Weston after {max_attempts} attempts")
            return False

    def is_weston_locked(self) -> bool:
        """
        Check if Weston desktop is locked by detecting:
        1. The green unlock circle
        2. Black screen (sleep/screensaver state)

        Uses configuration from ui_weston.json

        Returns:
            True if Weston is locked, False otherwise
        """
        try:
            import subprocess
            import re
            from PIL import Image
            import io

            # Get config values
            display = self.ui_config.get_weston_display()
            weston_x, weston_y, weston_w, weston_h = self.ui_config.get_weston_window_geometry()
            unlock_x, unlock_y = self.ui_config.get_unlock_button_position()
            unlock_detection = self.ui_config.get_unlock_button_detection()
            black_detection = self.ui_config.get_black_screen_detection()

            # Get actual window geometry from xwininfo
            xwininfo_result = subprocess.run(
                ["xwininfo", "-root", "-tree"],
                capture_output=True,
                text=True,
                timeout=5,
                env={**subprocess.os.environ, "DISPLAY": display}
            )

            for line in xwininfo_result.stdout.split('\n'):
                if 'Weston Compositor' in line:
                    match = re.search(r'(\d+)x(\d+)\+(\d+)\+(\d+)', line)
                    if match:
                        weston_w = int(match.group(1))
                        weston_h = int(match.group(2))
                        weston_x = int(match.group(3))
                        weston_y = int(match.group(4))
                        logger.debug(f"Weston window: {weston_w}x{weston_h} at ({weston_x}, {weston_y})")
                        break

            # Capture X11 screenshot
            result = subprocess.run(
                ["import", "-window", "root", "png:-"],
                capture_output=True,
                timeout=5,
                env={**subprocess.os.environ, "DISPLAY": display}
            )

            if result.returncode == 0:
                screenshot = Image.open(io.BytesIO(result.stdout))

                # Check 1: Black screen
                center_x = weston_x + weston_w // 2
                center_y = weston_y + weston_h // 2
                black_count, center_samples = 0, 0

                black_config = black_detection.get("sample_area", {})
                x_range = black_config.get("x_range", {})
                y_range = black_config.get("y_range", {})

                for dx in range(x_range.get("min", -10), x_range.get("max", 11), x_range.get("step", 5)):
                    for dy in range(y_range.get("min", -10), y_range.get("max", 11), y_range.get("step", 5)):
                        x, y = center_x + dx, center_y + dy
                        if 0 <= x < screenshot.size[0] and 0 <= y < screenshot.size[1]:
                            pixel = screenshot.getpixel((x, y))
                            r, g, b = pixel[0], pixel[1], pixel[2] if len(pixel) >= 3 else (0, 0, 0)

                            black_color = black_detection.get("color_range", {})
                            r_range = black_color.get("r", {})
                            g_range = black_color.get("g", {})
                            b_range = black_color.get("b", {})

                            if (r_range.get("min", 0) <= r <= r_range.get("max", 10) and
                                g_range.get("min", 0) <= g <= g_range.get("max", 10) and
                                b_range.get("min", 0) <= b <= b_range.get("max", 10)):
                                black_count += 1
                            center_samples += 1

                black_threshold = black_detection.get("threshold", {}).get("ratio", 0.8)
                if center_samples > 0 and black_count / center_samples > black_threshold:
                    logger.info(f"Weston is LOCKED (black screen: {black_count}/{center_samples})")
                    return True

                # Check 2: Unlock button
                unlock_sample = unlock_detection.get("sample_area", {})
                sample_w = unlock_sample.get("width", 3)
                sample_h = unlock_sample.get("height", 3)
                green_count, total_samples = 0, 0

                for dx in range(-(sample_w // 2), (sample_w // 2) + 1):
                    for dy in range(-(sample_h // 2), (sample_h // 2) + 1):
                        x, y = unlock_x + dx, unlock_y + dy
                        if 0 <= x < screenshot.size[0] and 0 <= y < screenshot.size[1]:
                            pixel = screenshot.getpixel((x, y))
                            r, g, b = pixel[0], pixel[1], pixel[2] if len(pixel) >= 3 else (0, 0, 0)

                            unlock_color = unlock_detection.get("color_range", {})
                            r_range = unlock_color.get("r", {})
                            g_range = unlock_color.get("g", {})
                            b_range = unlock_color.get("b", {})

                            if (r_range.get("min", 130) <= r <= r_range.get("max", 145) and
                                g_range.get("min", 125) <= g <= g_range.get("max", 140) and
                                b_range.get("min", 125) <= b <= b_range.get("max", 135)):
                                green_count += 1
                            total_samples += 1

                unlock_threshold = unlock_detection.get("threshold", {}).get("min_pixels", 1)
                if total_samples > 0 and green_count >= unlock_threshold:
                    logger.info(f"Weston is LOCKED (unlock button: {green_count}/{total_samples})")
                    return True

                logger.info("Weston is UNLOCKED")
                return False

            return False

        except Exception as e:
            logger.error(f"Error checking Weston lock status: {e}")
            return False

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
            if not self.check_game_running():
                logger.debug("Game not running")
                return False

            # Check 2: MainActivity must be focused
            activity = self.adb.get_current_activity()
            if not activity or self.PACKAGE_NAME not in activity:
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