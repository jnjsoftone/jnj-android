import sys
sys.path.insert(0, 'src')

from utils.adb_controller import WaydroidController
import logging

logging.basicConfig(level=logging.DEBUG)

print("Testing ADB connection...")
controller = WaydroidController()

print(f"Connecting to {controller.host}:{controller.port}")
if controller.connect():
    print("✓ Connected successfully!")
    
    print("\nGetting device info...")
    info = controller.get_device_info()
    print(f"Device info: {info}")
    
    print("\nChecking if Rise of Kingdoms is running...")
    is_running = controller.is_app_running("com.lilithgames.roc.gp")
    print(f"Game running: {is_running}")
    
    if not is_running:
        print("\nStarting Rise of Kingdoms...")
        success = controller.start_app("com.lilithgames.roc.gp")
        print(f"Start result: {success}")
    
    controller.disconnect()
else:
    print("✗ Connection failed!")
