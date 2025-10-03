# Backend Python Development TODOs

## Phase 1: Core Infrastructure Setup

### 1.1 Environment Setup
- [x] Create project directory structure
- [ ] Create virtual environment
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```
- [ ] Create requirements.txt with dependencies
- [ ] Install dependencies
- [ ] Create .env configuration file
- [ ] Setup logging configuration

### 1.2 Dependencies to Install
```
fastapi==0.109.0
uvicorn[standard]==0.27.0
pydantic==2.5.3
pydantic-settings==2.1.0
sqlalchemy==2.0.25
alembic==1.13.1
psycopg2-binary==2.9.9
adb-shell==0.4.4
opencv-python==4.9.0.80
pytesseract==0.3.10
pillow==10.2.0
python-dotenv==1.0.0
```

## Phase 2: ADB & Waydroid Control

### 2.1 ADB Controller (`src/utils/adb_controller.py`)
- [ ] Implement WaydroidController class
  - [ ] `connect()` - Connect to Waydroid ADB
  - [ ] `disconnect()` - Disconnect from ADB
  - [ ] `is_connected()` - Check connection status
  - [ ] `tap(x, y)` - Tap at coordinates
  - [ ] `swipe(x1, y1, x2, y2, duration)` - Swipe gesture
  - [ ] `screenshot()` - Capture screenshot
  - [ ] `get_current_activity()` - Get current app activity
  - [ ] `get_device_info()` - Get device information
  - [ ] `input_text(text)` - Input text
  - [ ] `press_key(keycode)` - Press key (BACK, HOME, etc)

### 2.2 Screen Analyzer (`src/utils/screen_analyzer.py`)
- [ ] Implement ScreenAnalyzer class
  - [ ] `find_template(template_name)` - Find UI element by template
  - [ ] `find_text(text)` - Find text using OCR
  - [ ] `detect_button(button_name)` - Detect button position
  - [ ] `wait_for_element(element, timeout)` - Wait for element to appear
  - [ ] `get_screen_state()` - Identify current screen/state

## Phase 3: Game Automation Utilities

### 3.1 Game Controller (`src/utils/game_controller.py`)
- [ ] Implement GameController class
  - [ ] `start_game()` - Launch Rise of Kingdoms
    - [ ] Kill existing game process
    - [ ] Launch app via ADB
    - [ ] Wait for main screen
    - [ ] Handle splash screens
  - [ ] `end_game()` - Close game gracefully
    - [ ] Press HOME or BACK
    - [ ] Force stop if needed
  - [ ] `restart_game()` - Restart game
  - [ ] `check_game_running()` - Check if game is running
  - [ ] `wait_for_game_ready(timeout)` - Wait until game is ready

### 3.2 Account Manager (`src/utils/account_manager.py`)
- [ ] Implement AccountManager class
  - [ ] `get_current_account()` - Get current logged-in account
  - [ ] `change_account(email)` - Switch to different account
    - [ ] Navigate to settings
    - [ ] Logout current account
    - [ ] Login with new account
    - [ ] Wait for login completion
  - [ ] `logout()` - Logout current account
  - [ ] `login(email, password)` - Login to account

### 3.3 Character Manager (`src/utils/character_manager.py`)
- [ ] Implement CharacterManager class
  - [ ] `get_current_character()` - Get current character info
  - [ ] `change_character(character_name)` - Switch character
    - [ ] Open character selection
    - [ ] Select character
    - [ ] Wait for loading
  - [ ] `list_characters()` - List all characters in account
  - [ ] `get_character_info()` - Get character stats (power, level, etc)

### 3.4 Navigation Helper (`src/utils/navigation.py`)
- [ ] Implement Navigation class
  - [ ] `go_to_home()` - Navigate to home screen
  - [ ] `go_to_map()` - Navigate to kingdom map
  - [ ] `go_to_city()` - Navigate to city view
  - [ ] `open_menu(menu_name)` - Open specific menu
  - [ ] `close_all_popups()` - Close all popup windows

## Phase 4: Task Automation

### 4.1 Base Task (`src/utils/tasks/base_task.py`)
- [ ] Implement BaseTask abstract class
  - [ ] `execute(params)` - Execute task
  - [ ] `validate(params)` - Validate parameters
  - [ ] `get_status()` - Get task status
  - [ ] `cancel()` - Cancel running task

### 4.2 Resource Tasks (`src/utils/tasks/resource_tasks.py`)
- [ ] Implement ResourceTasks
  - [ ] `gather_resource(resource_type, node_level)` - Send troops to gather
  - [ ] `return_troops()` - Return gathering troops
  - [ ] `collect_resources()` - Collect resources from city

### 4.3 Building Tasks (`src/utils/tasks/building_tasks.py`)
- [ ] Implement BuildingTasks
  - [ ] `upgrade_building(building_type)` - Upgrade building
  - [ ] `start_research(tech_name)` - Start research
  - [ ] `train_troops(troop_type, amount)` - Train troops

## Phase 5: API Server

### 5.1 FastAPI Server Setup (`src/servers/main.py`)
- [ ] Create FastAPI application
- [ ] Setup CORS middleware
- [ ] Setup logging middleware
- [ ] Create health check endpoint
- [ ] Create API documentation

### 5.2 Game Control Endpoints (`src/servers/routes/game.py`)
- [ ] POST `/api/game/start` - Start game
- [ ] POST `/api/game/stop` - Stop game
- [ ] POST `/api/game/restart` - Restart game
- [ ] GET `/api/game/status` - Get game status
- [ ] POST `/api/game/screenshot` - Take screenshot

### 5.3 Account Endpoints (`src/servers/routes/accounts.py`)
- [ ] GET `/api/accounts/current` - Get current account
- [ ] POST `/api/accounts/login` - Login to account
- [ ] POST `/api/accounts/logout` - Logout
- [ ] POST `/api/accounts/switch` - Switch account

### 5.4 Character Endpoints (`src/servers/routes/characters.py`)
- [ ] GET `/api/characters` - List characters
- [ ] GET `/api/characters/{id}` - Get character info
- [ ] POST `/api/characters/switch` - Switch character
- [ ] GET `/api/characters/{id}/stats` - Get character stats

### 5.5 Task Endpoints (`src/servers/routes/tasks.py`)
- [ ] POST `/api/tasks/execute` - Execute task
- [ ] GET `/api/tasks/{id}` - Get task status
- [ ] DELETE `/api/tasks/{id}` - Cancel task
- [ ] GET `/api/tasks/history` - Get task history

## Phase 6: Testing

### 6.1 Unit Tests
- [ ] Test ADB controller connectivity
- [ ] Test screen analysis functions
- [ ] Test game controller methods
- [ ] Test account manager
- [ ] Test character manager

### 6.2 Integration Tests
- [ ] Test full game launch flow
- [ ] Test account switching flow
- [ ] Test character switching flow
- [ ] Test API endpoints

### 6.3 Manual Testing
- [ ] Test with real Waydroid instance
- [ ] Test with Rise of Kingdoms game
- [ ] Verify all game states handled correctly

## Phase 7: Documentation

### 7.1 Code Documentation
- [ ] Add docstrings to all classes
- [ ] Add docstrings to all methods
- [ ] Add inline comments for complex logic
- [ ] Generate API documentation

### 7.2 User Documentation
- [ ] Write setup guide
- [ ] Write API usage guide
- [ ] Write troubleshooting guide
- [ ] Create example scripts

## Phase 8: Optimization & Enhancement

### 8.1 Performance
- [ ] Implement connection pooling
- [ ] Add caching for screenshots
- [ ] Optimize image matching algorithms
- [ ] Add async/await for I/O operations

### 8.2 Reliability
- [ ] Add retry logic for failed operations
- [ ] Add timeout handling
- [ ] Add error recovery mechanisms
- [ ] Implement health checks

### 8.3 Features
- [ ] Add WebSocket support for real-time updates
- [ ] Add task scheduling
- [ ] Add multi-instance support
- [ ] Add configuration management

## Current Priority (Start Here)

1. **Setup environment** (Phase 1)
2. **Implement ADB controller** (Phase 2.1)
3. **Implement game controller with basic functions** (Phase 3.1)
   - start_game()
   - end_game()
4. **Create test API server** (Phase 5.1, 5.2)
5. **Test with Waydroid** (Phase 6.3)

## Notes

- All coordinates should be relative to screen resolution (1080x1920)
- All timeouts should be configurable
- All errors should be logged with context
- All operations should be atomic where possible
- Consider game loading times and network latency