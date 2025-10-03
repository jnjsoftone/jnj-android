# Technical Requirements Document (TRD)
## Rise of Kingdoms Android Automation Platform

### 1. System Architecture

#### 1.1 High-Level Architecture
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Frontend  │    │   Backend API   │    │ Android Emulator│
│    (Next.js)    │◄──►│    (Python)     │◄──►│  (Rise of K)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │              ┌─────────────────┐              │
         │              │    Database     │              │
         └──────────────►│   (SQLite/PG)   │◄─────────────┘
                        └─────────────────┘
```

#### 1.2 Technology Stack

**Frontend**
- Framework: Next.js 14+
- Language: TypeScript
- UI Library: React + Tailwind CSS
- State Management: Zustand or Redux Toolkit
- WebSocket: Socket.IO client

**Backend**
- Language: Python 3.11+
- Framework: FastAPI
- WebSocket: Socket.IO server
- Task Queue: Celery with Redis
- Image Processing: OpenCV, Pillow
- OCR: Tesseract, EasyOCR

**Android Automation**
- Emulator: Android Studio AVD or Genymotion
- ADB (Android Debug Bridge)
- UI Automation: uiautomator2 or Appium
- Screen Capture: adb screencap

**Database**
- Primary: PostgreSQL (production) / SQLite (development)
- Cache: Redis
- ORM: SQLAlchemy

**Infrastructure**
- Containerization: Docker & Docker Compose
- OS: Ubuntu 22.04 LTS
- Process Management: Supervisor

### 2. System Components

#### 2.1 Frontend Components

**Dashboard Service**
- Real-time monitoring interface
- Configuration management UI
- Analytics and reporting dashboards
- User authentication and authorization

**Component Structure**
```
frontend/
├── components/
│   ├── dashboard/
│   ├── automation/
│   ├── monitoring/
│   └── settings/
├── hooks/
├── services/
├── types/
└── utils/
```

#### 2.2 Backend Services

**Automation Engine**
- Core automation logic
- Task scheduling and execution
- State management
- Error handling and recovery

**Computer Vision Service**
- Screen capture and analysis
- OCR text extraction
- UI element detection
- Template matching

**API Gateway**
- RESTful API endpoints
- WebSocket connections
- Authentication middleware
- Rate limiting

**Service Structure**
```
backend/
├── services/
│   ├── automation/
│   ├── vision/
│   ├── emulator/
│   └── notification/
├── models/
├── api/
├── core/
└── utils/
```

#### 2.3 Database Schema

**Core Tables**
```sql
-- Emulator instances
emulators (id, name, status, config, created_at, updated_at)

-- Automation tasks
tasks (id, emulator_id, type, config, status, priority, scheduled_at)

-- Execution logs
execution_logs (id, task_id, action, result, screenshot_path, timestamp)

-- User configurations
user_configs (id, emulator_id, settings_json, updated_at)

-- Performance metrics
metrics (id, emulator_id, metric_type, value, timestamp)
```

### 3. Technical Requirements

#### 3.1 Performance Requirements

**System Performance**
- CPU Usage: <70% average per emulator
- Memory Usage: <2GB per emulator instance
- Response Time: <5 seconds for automation actions
- Throughput: Support 5+ concurrent emulator instances

**Network Requirements**
- Bandwidth: Minimal (local emulator communication)
- Latency: <100ms for ADB commands
- WebSocket: Real-time updates <1 second

#### 3.2 Scalability Requirements

**Horizontal Scaling**
- Support multiple emulator instances
- Distributed task processing
- Load balancing for API requests

**Vertical Scaling**
- Optimized resource utilization
- Memory management for image processing
- Efficient database queries

#### 3.3 Security Requirements

**Authentication & Authorization**
- JWT-based authentication
- Role-based access control
- API key management for automation services

**Data Security**
- Encrypted configuration storage
- Secure emulator communication
- Activity logging and audit trails

### 4. Development Environment

#### 4.1 Docker Configuration

**Docker Compose Services**
```yaml
services:
  frontend:
    build: ./frontend
    ports: ["3000:3000"]

  backend:
    build: ./backend
    ports: ["8000:8000"]
    depends_on: [database, redis]

  database:
    image: postgres:15
    volumes: ["postgres_data:/var/lib/postgresql/data"]

  redis:
    image: redis:7-alpine

  android-emulator:
    image: budtmo/docker-android
    privileged: true
    ports: ["5554:5554", "5555:5555"]
```

#### 4.2 Development Tools

**Code Quality**
- Python: Black, isort, mypy, pytest
- TypeScript: ESLint, Prettier, TypeScript compiler
- Pre-commit hooks for code formatting

**Testing Framework**
- Backend: pytest, pytest-asyncio
- Frontend: Jest, React Testing Library
- Integration: Playwright for E2E testing

**Monitoring & Logging**
- Application logs: structlog
- Performance monitoring: Prometheus + Grafana
- Error tracking: Sentry

### 5. Deployment Architecture

#### 5.1 Container Orchestration

**Production Deployment**
```
┌─────────────────────────────────────────┐
│           Docker Host                    │
├─────────────────────────────────────────┤
│ ┌─────────┐ ┌─────────┐ ┌─────────────┐ │
│ │Frontend │ │Backend  │ │   Database  │ │
│ │Container│ │Container│ │  Container  │ │
│ └─────────┘ └─────────┘ └─────────────┘ │
│ ┌─────────┐ ┌─────────┐ ┌─────────────┐ │
│ │  Redis  │ │Emulator │ │   Nginx     │ │
│ │Container│ │Container│ │  Container  │ │
│ └─────────┘ └─────────┘ └─────────────┘ │
└─────────────────────────────────────────┘
```

#### 5.2 Configuration Management

**Environment Variables**
- Database connection strings
- Redis configuration
- Emulator settings
- API keys and secrets

**Volume Mounts**
- Database persistence
- Log file storage
- Screenshot and video storage
- Configuration files

### 6. Integration Requirements

#### 6.1 Android Emulator Integration

**ADB Commands**
```bash
# Screen capture
adb exec-out screencap -p > screenshot.png

# Input simulation
adb shell input tap <x> <y>
adb shell input text "message"
adb shell input keyevent <keycode>

# Package management
adb shell pm list packages
adb install app.apk
```

**Required Permissions**
- Developer options enabled
- USB debugging enabled
- Install from unknown sources
- Accessibility services (if needed)

#### 6.2 Computer Vision Pipeline

**Image Processing Workflow**
1. Screen capture via ADB
2. Image preprocessing (resize, denoise)
3. OCR text extraction
4. UI element detection
5. Action coordinate calculation
6. Input command execution

**OCR Configuration**
```python
# Tesseract settings for game text
tesseract_config = '--oem 3 --psm 8 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'

# EasyOCR for better accuracy
reader = easyocr.Reader(['en'])
```

### 7. Monitoring and Maintenance

#### 7.1 Health Checks

**System Health Endpoints**
- `/health` - Basic service status
- `/health/database` - Database connectivity
- `/health/emulator` - Emulator status
- `/health/automation` - Automation engine status

#### 7.2 Logging Strategy

**Log Levels and Categories**
- ERROR: System failures, exceptions
- WARNING: Recoverable errors, performance issues
- INFO: Task execution, state changes
- DEBUG: Detailed automation steps

**Log Storage**
- Structured JSON logging
- Log rotation and archival
- Centralized log aggregation