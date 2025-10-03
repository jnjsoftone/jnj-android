"""
FastAPI Test Server for Rise of Kingdoms Automation

This server provides REST API endpoints to control the game automation.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import logging
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from android.adb_simple import SimpleADBController
from apps.rok.rok_controller import GameController
from apps.rok.ui_config import reload_ui_config
from waydroid.weston import WestonController

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app with tags metadata
tags_metadata = [
    {
        "name": "System",
        "description": "System status and health check endpoints",
    },
    {
        "name": "ADB",
        "description": "Android Debug Bridge control endpoints",
    },
    {
        "name": "Config",
        "description": "Configuration management endpoints",
    },
    {
        "name": "ROK",
        "description": "Rise of Kingdoms game control endpoints",
    },
    {
        "name": "Waydroid",
        "description": "Waydroid container management endpoints",
    },
    {
        "name": "Weston",
        "description": "Weston compositor control endpoints",
    },
]

app = FastAPI(
    title="Rise of Kingdoms Automation API",
    description="REST API for Rise of Kingdoms game automation",
    version="0.1.0",
    openapi_tags=tags_metadata
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global controllers
adb_controller = None
game_controller = None
weston_controller = None


# Pydantic models
class GameStartRequest(BaseModel):
    wait_for_ready: bool = True
    auto_tap: bool = True
    force_restart: bool = False


class GameEndRequest(BaseModel):
    force: bool = False


class ScreenshotRequest(BaseModel):
    save_path: Optional[str] = None


@app.on_event("startup")
async def startup_event():
    """Initialize controllers on startup"""
    global adb_controller, game_controller, weston_controller

    logger.info("Starting ROK Automation API Server...")

    try:
        # Initialize Weston controller
        weston_controller = WestonController()
        logger.info("Weston controller initialized")

        # Initialize ADB controller
        adb_controller = SimpleADBController()
        # Try to connect, but don't fail if Waydroid is not running yet
        # It will be started automatically when needed
        try:
            if adb_controller.connect():
                logger.info("Connected to Waydroid")
            else:
                logger.warning("Waydroid not running - will start automatically when needed")
        except Exception as e:
            logger.warning(f"Could not connect to Waydroid at startup: {e}")
            logger.info("Waydroid will be started automatically when needed")

        # Initialize game controller
        game_controller = GameController(adb_controller)
        logger.info("Game controller initialized")

    except Exception as e:
        logger.error(f"Error during startup: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    global adb_controller

    logger.info("Shutting down API server...")

    if adb_controller:
        adb_controller.disconnect()


@app.get("/", tags=["System"])
async def root():
    """Root endpoint"""
    return {
        "name": "Rise of Kingdoms Automation API",
        "version": "0.1.0",
        "status": "running"
    }


@app.get("/health", tags=["System"])
async def health_check():
    """Health check endpoint"""
    is_connected = adb_controller.is_connected() if adb_controller else False

    return {
        "status": "healthy" if is_connected else "unhealthy",
        "adb_connected": is_connected
    }


# Game control endpoints
@app.post("/api/rok/start", tags=["ROK"])
async def start_game(request: GameStartRequest):
    """Start Rise of Kingdoms with automatic Weston/Waydroid management"""
    if not game_controller or not weston_controller:
        raise HTTPException(status_code=500, detail="Controllers not initialized")

    try:
        import time as time_module

        logger.info("=== ROK Start: Checking Weston status ===")

        # Step 1: Check Weston/Waydroid status
        status = weston_controller.get_status()
        weston_running = status["weston"]["running"]
        waydroid_running = status["waydroid"]["running"]
        screen_state = status["weston"].get("screen_state", "unknown")

        logger.info(f"Initial state - Weston: {weston_running}, Waydroid: {waydroid_running}, Screen: {screen_state}")

        # Step 2: Start Weston if not running
        if not weston_running:
            logger.info("Starting Weston...")
            if not weston_controller.start_weston():
                raise HTTPException(status_code=500, detail="Failed to start Weston")
            time_module.sleep(2)
            # Refresh status
            status = weston_controller.get_status()
            screen_state = status["weston"].get("screen_state", "unknown")

        # Step 3: Start Waydroid if not running
        if not waydroid_running:
            logger.info("Starting Waydroid...")
            if not weston_controller.start_waydroid():
                raise HTTPException(status_code=500, detail="Failed to start Waydroid")
            time_module.sleep(5)
            # Refresh status
            status = weston_controller.get_status()
            screen_state = status["weston"].get("screen_state", "unknown")

        # Step 4: Handle screen state
        logger.info(f"Handling screen state: {screen_state}")

        if screen_state == "empty":
            logger.info("Screen is empty, starting Waydroid...")
            if not weston_controller.start_waydroid():
                raise HTTPException(status_code=500, detail="Failed to start Waydroid")
            time_module.sleep(5)

        elif screen_state == "loading":
            logger.info("Waydroid is loading, waiting for loaded state...")
            # Wait up to 60 seconds for loaded state
            for i in range(60):
                time_module.sleep(1)
                status = weston_controller.get_status()
                new_state = status["weston"].get("screen_state", "unknown")
                if new_state == "loaded":
                    logger.info("Waydroid loaded successfully")
                    break
                elif new_state in ["black", "lock"]:
                    logger.info(f"State changed to {new_state}, will handle it")
                    screen_state = new_state
                    break
            else:
                logger.warning("Timeout waiting for loaded state, continuing anyway")

        if screen_state == "black":
            logger.info("Screen is black, tapping to wake...")
            # Tap center to wake
            adb_controller.tap(512, 284)
            time_module.sleep(2)
            # Check if lock appeared
            status = weston_controller.get_status()
            screen_state = status["weston"].get("screen_state", "unknown")
            if screen_state == "lock":
                logger.info("Lock screen appeared, tapping to unlock...")
                adb_controller.tap(512, 284)
                time_module.sleep(2)
            # Verify loaded
            status = weston_controller.get_status()
            screen_state = status["weston"].get("screen_state", "unknown")

        elif screen_state == "lock":
            logger.info("Screen is locked, tapping to unlock...")
            adb_controller.tap(512, 284)
            time_module.sleep(2)
            # Verify loaded
            status = weston_controller.get_status()
            screen_state = status["weston"].get("screen_state", "unknown")

        # Step 5: Start the game
        logger.info(f"Final screen state: {screen_state}, starting ROK game...")
        success = game_controller.start_game(
            wait_for_ready=request.wait_for_ready,
            auto_tap=request.auto_tap,
            force_restart=request.force_restart
        )

        # Step 6: Check for notification panel during game loading and close it if shown
        # Wait a bit for game to start loading, then check periodically
        time_module.sleep(10)  # Initial wait for game to start loading

        # Check for notification panel for up to 90 seconds during loading
        logger.info("Monitoring for notification panel during game loading...")
        for check_count in range(18):  # 18 checks * 5 seconds = 90 seconds
            if weston_controller.is_notification_panel_shown():
                logger.info(f"Notification panel detected (check #{check_count + 1}), closing it...")
                weston_controller.close_notification_panel()
                time_module.sleep(2)
                # Check if it's closed
                if not weston_controller.is_notification_panel_shown():
                    logger.info("Notification panel closed successfully")
                else:
                    logger.warning("Notification panel still shown after BACK press, trying again...")
                    weston_controller.close_notification_panel()
                    time_module.sleep(2)

            # Check if game has fully loaded (main screen reached)
            if game_controller.is_in_main_game():
                logger.info("Game main screen detected, stopping notification panel monitoring")
                break

            time_module.sleep(5)  # Wait 5 seconds before next check
        else:
            logger.info("Notification panel monitoring completed (90s timeout)")

        if success:
            return {
                "status": "success",
                "message": "Game started successfully",
                "weston_state": status
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to start game")

    except Exception as e:
        logger.error(f"Error starting game: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/rok/stop", tags=["ROK"])
async def stop_game(request: GameEndRequest):
    """Stop Rise of Kingdoms (send to background with HOME button)"""
    if not game_controller:
        raise HTTPException(status_code=500, detail="Game controller not initialized")

    try:
        success = game_controller.end_game(force=request.force)

        if success:
            return {"status": "success", "message": "Game stopped successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to stop game")

    except Exception as e:
        logger.error(f"Error stopping game: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/rok/end", tags=["ROK"])
async def end_game():
    """Completely terminate Rise of Kingdoms process (force stop)"""
    if not game_controller:
        raise HTTPException(status_code=500, detail="Game controller not initialized")

    try:
        success = game_controller.end_game(force=True)

        if success:
            return {"status": "success", "message": "Game terminated successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to terminate game")

    except Exception as e:
        logger.error(f"Error terminating game: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/rok/restart", tags=["ROK"])
async def restart_game():
    """Restart Rise of Kingdoms with automatic Weston/Waydroid management"""
    if not game_controller or not weston_controller:
        raise HTTPException(status_code=500, detail="Controllers not initialized")

    try:
        logger.info("=== ROK Restart: Stopping game first ===")

        # Stop the game first
        game_controller.end_game(force=True)

        import time as time_module
        time_module.sleep(3)

        # Use the same logic as start_game
        logger.info("=== ROK Restart: Restarting with status check ===")

        # Call the start_game logic
        request = GameStartRequest(wait_for_ready=True, auto_tap=True, force_restart=True)
        return await start_game(request)

    except Exception as e:
        logger.error(f"Error restarting game: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/rok/status", tags=["ROK"])
async def get_game_status():
    """Get current game status"""
    if not game_controller:
        raise HTTPException(status_code=500, detail="Game controller not initialized")

    try:
        status = game_controller.get_game_status()
        return {"status": "success", "data": status}

    except Exception as e:
        logger.error(f"Error getting game status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/rok/check-main-screen", tags=["ROK"])
async def check_main_screen():
    """Check if game is in main screen (fully loaded)"""
    if not game_controller:
        raise HTTPException(status_code=500, detail="Game controller not initialized")

    try:
        is_in_main = game_controller.is_in_main_game()
        return {
            "status": "success",
            "in_main_game": is_in_main,
            "message": "In main game screen" if is_in_main else "Not in main game (loading or at startup screen)"
        }

    except Exception as e:
        logger.error(f"Error checking main screen: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/config/reload", tags=["Config"])
async def reload_config():
    """Reload UI configuration from JSON files"""
    try:
        reload_ui_config()
        return {
            "status": "success",
            "message": "UI configuration reloaded successfully"
        }

    except Exception as e:
        logger.error(f"Error reloading config: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/weston/check-lock", tags=["Weston"])
async def check_weston_lock():
    """Check if Weston desktop is locked"""
    if not game_controller:
        raise HTTPException(status_code=500, detail="Game controller not initialized")

    try:
        is_locked = game_controller.is_weston_locked()
        return {
            "status": "success",
            "is_locked": is_locked,
            "message": "Weston is locked (green unlock circle detected)" if is_locked else "Weston is unlocked"
        }

    except Exception as e:
        logger.error(f"Error checking Weston lock: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/weston/pixel-color", tags=["Weston"])
async def get_pixel_color(x: int, y: int):
    """Get RGB color at specific coordinates"""
    if not game_controller:
        raise HTTPException(status_code=500, detail="Game controller not initialized")

    try:
        color = game_controller.get_pixel_color(x, y)
        if color:
            return {
                "status": "success",
                "x": x,
                "y": y,
                "color": {"r": color[0], "g": color[1], "b": color[2]},
                "hex": f"#{color[0]:02x}{color[1]:02x}{color[2]:02x}"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to get pixel color")

    except Exception as e:
        logger.error(f"Error getting pixel color: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/rok/screenshot", tags=["ROK"])
async def take_screenshot(request: ScreenshotRequest):
    """Take a screenshot"""
    if not game_controller:
        raise HTTPException(status_code=500, detail="Game controller not initialized")

    try:
        image = game_controller.take_screenshot(save_path=request.save_path)

        if image:
            return {
                "status": "success",
                "message": "Screenshot captured",
                "saved_to": request.save_path if request.save_path else None,
                "size": image.size
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to capture screenshot")

    except Exception as e:
        logger.error(f"Error taking screenshot: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ADB control endpoints
@app.post("/api/adb/tap", tags=["ADB"])
async def adb_tap(x: int, y: int):
    """Tap at coordinates"""
    if not adb_controller:
        raise HTTPException(status_code=500, detail="ADB controller not initialized")

    try:
        success = adb_controller.tap(x, y)

        if success:
            return {"status": "success", "message": f"Tapped at ({x}, {y})"}
        else:
            raise HTTPException(status_code=500, detail="Failed to tap")

    except Exception as e:
        logger.error(f"Error tapping: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/adb/swipe", tags=["ADB"])
async def adb_swipe(x1: int, y1: int, x2: int, y2: int, duration: int = 300):
    """Swipe from one point to another"""
    if not adb_controller:
        raise HTTPException(status_code=500, detail="ADB controller not initialized")

    try:
        success = adb_controller.swipe(x1, y1, x2, y2, duration)

        if success:
            return {"status": "success", "message": f"Swiped from ({x1}, {y1}) to ({x2}, {y2})"}
        else:
            raise HTTPException(status_code=500, detail="Failed to swipe")

    except Exception as e:
        logger.error(f"Error swiping: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/adb/device-info", tags=["ADB"])
async def get_device_info():
    """Get device information"""
    if not adb_controller:
        raise HTTPException(status_code=500, detail="ADB controller not initialized")

    try:
        info = adb_controller.get_device_info()
        return {"status": "success", "data": info}

    except Exception as e:
        logger.error(f"Error getting device info: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Weston and Waydroid control endpoints
@app.get("/api/weston/status", tags=["Weston"])
async def get_weston_status():
    """Get Weston and Waydroid status"""
    if not weston_controller:
        raise HTTPException(status_code=500, detail="Weston controller not initialized")

    try:
        status = weston_controller.get_status()
        return {"status": "success", "data": status}

    except Exception as e:
        logger.error(f"Error getting Weston status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/weston/start", tags=["Weston"])
async def start_weston():
    """Start Weston compositor"""
    if not weston_controller:
        raise HTTPException(status_code=500, detail="Weston controller not initialized")

    try:
        success = weston_controller.start_weston()

        if success:
            return {"status": "success", "message": "Weston started successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to start Weston")

    except Exception as e:
        logger.error(f"Error starting Weston: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/weston/stop", tags=["Weston"])
async def stop_weston():
    """Stop Weston compositor"""
    if not weston_controller:
        raise HTTPException(status_code=500, detail="Weston controller not initialized")

    try:
        success = weston_controller.stop_weston()

        if success:
            return {"status": "success", "message": "Weston stopped successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to stop Weston")

    except Exception as e:
        logger.error(f"Error stopping Weston: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/waydroid/start", tags=["Waydroid"])
async def start_waydroid():
    """Start Waydroid"""
    if not weston_controller:
        raise HTTPException(status_code=500, detail="Weston controller not initialized")

    try:
        success = weston_controller.start_waydroid()

        if success:
            return {"status": "success", "message": "Waydroid started successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to start Waydroid")

    except Exception as e:
        logger.error(f"Error starting Waydroid: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/waydroid/stop", tags=["Waydroid"])
async def stop_waydroid():
    """Stop Waydroid"""
    if not weston_controller:
        raise HTTPException(status_code=500, detail="Weston controller not initialized")

    try:
        success = weston_controller.stop_waydroid()

        if success:
            return {"status": "success", "message": "Waydroid stopped successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to stop Waydroid")

    except Exception as e:
        logger.error(f"Error stopping Waydroid: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )