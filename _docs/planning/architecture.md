# Rise of Kingdoms 자동화 시스템 아키텍처

## 시스템 개요

Rise of Kingdoms 게임 자동화를 위한 풀스택 시스템으로, 컴퓨터 비전 기반 화면 인식과 GraphQL API를 통한 원격 제어를 지원합니다.

## 기술 스택

### Infrastructure
- **OS**: Ubuntu 24.04 LTS with XFCE Desktop
- **Android Emulator**: Waydroid 1.5.4
  - Wayland Compositor: Weston (X11 backend)
  - Android Version: LineageOS 11 (GAPPS)
- **Task Scheduler**: systemd timers / cron
- **Containerization**: Docker (optional)

### Backend
- **Runtime**: Python 3.12+
- **Core Frameworks**:
  - FastAPI / Strawberry GraphQL
  - OpenCV / PyTesseract (OCR)
  - pyautogui / pynput (UI Automation)
  - adb-shell (Android Debug Bridge)

### Frontend
- **Framework**: Next.js 14+ (App Router)
- **UI Library**: shadcn/ui + Tailwind CSS
- **State Management**: Zustand / React Query
- **GraphQL Client**: Apollo Client / urql

### Database
- **RDBMS**: PostgreSQL 16+
- **ORM**: Prisma / SQLAlchemy
- **Migration**: Alembic / Prisma Migrate
- **Connection Pool**: pgBouncer (optional)

## 시스템 아키텍처

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend (Next.js)                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ Account Mgmt │  │Schedule Mgmt │  │  Manual Mgmt │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└─────────────────────────────┬───────────────────────────────────┘
                              │ GraphQL over HTTP/WebSocket
┌─────────────────────────────▼───────────────────────────────────┐
│                    GraphQL API Layer (Python)                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │Query Resolver│  │Mutation      │  │Subscription  │         │
│  │              │  │Resolver      │  │Resolver      │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└─────────────────────────────┬───────────────────────────────────┘
                              │
┌─────────────────────────────▼───────────────────────────────────┐
│                  Automation Engine (Python)                      │
│  ┌────────────────────────────────────────────────────────┐    │
│  │ Vision Module                                           │    │
│  │  - Template Matching (OpenCV)                          │    │
│  │  - OCR (PyTesseract / PaddleOCR)                       │    │
│  │  - Object Detection (YOLO - optional)                  │    │
│  └────────────────────────────────────────────────────────┘    │
│  ┌────────────────────────────────────────────────────────┐    │
│  │ Control Module                                          │    │
│  │  - Screen Capture (ADB screencap)                      │    │
│  │  - Input Simulation (ADB input tap/swipe/text)        │    │
│  │  - App Control (ADB shell commands)                    │    │
│  └────────────────────────────────────────────────────────┘    │
│  ┌────────────────────────────────────────────────────────┐    │
│  │ Task Executor                                           │    │
│  │  - Task Queue (Celery / RQ)                            │    │
│  │  - Task Scheduler (APScheduler)                        │    │
│  │  - State Machine (python-statemachine)                 │    │
│  └────────────────────────────────────────────────────────┘    │
└─────────────────────────────┬───────────────────────────────────┘
                              │
┌─────────────────────────────▼───────────────────────────────────┐
│                    Waydroid (Android Container)                  │
│  ┌────────────────────────────────────────────────────────┐    │
│  │ Rise of Kingdoms App                                    │    │
│  │  - Package: com.lilithgames.roc.gp                     │    │
│  │  - Resolution: 1080x1920                               │    │
│  │  - ADB Port: 5555                                       │    │
│  └────────────────────────────────────────────────────────┘    │
└─────────────────────────────┬───────────────────────────────────┘
                              │
┌─────────────────────────────▼───────────────────────────────────┐
│                    Database (PostgreSQL)                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ Game Data    │  │ User Data    │  │ System Data  │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└─────────────────────────────────────────────────────────────────┘
```

## 데이터베이스 스키마

### Core Tables

#### accounts
사용자 계정 정보 관리
```sql
CREATE TABLE accounts (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    google_account VARCHAR(255),
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

#### characters
게임 캐릭터 정보
```sql
CREATE TABLE characters (
    id SERIAL PRIMARY KEY,
    account_id INTEGER REFERENCES accounts(id),
    name VARCHAR(100) NOT NULL,
    governor_id VARCHAR(50),
    kingdom_id INTEGER,
    power BIGINT DEFAULT 0,
    level INTEGER DEFAULT 1,
    vip_level INTEGER DEFAULT 0,
    alliance_name VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

#### tasks
자동화 작업 정의
```sql
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    type VARCHAR(50) NOT NULL, -- 'resource_gather', 'building_upgrade', 'training', etc.
    priority INTEGER DEFAULT 5,
    parameters JSONB,
    enabled BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### schedules
작업 스케줄 관리
```sql
CREATE TABLE schedules (
    id SERIAL PRIMARY KEY,
    character_id INTEGER REFERENCES characters(id),
    task_id INTEGER REFERENCES tasks(id),
    cron_expression VARCHAR(100), -- '0 */2 * * *' (every 2 hours)
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    repeat_count INTEGER,
    enabled BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### actions
실행된 액션 로그
```sql
CREATE TABLE actions (
    id SERIAL PRIMARY KEY,
    character_id INTEGER REFERENCES characters(id),
    task_id INTEGER REFERENCES tasks(id),
    action_type VARCHAR(50) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending', -- 'pending', 'running', 'success', 'failed'
    result JSONB,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### buildings
건물 정보 및 상태
```sql
CREATE TABLE buildings (
    id SERIAL PRIMARY KEY,
    character_id INTEGER REFERENCES characters(id),
    building_type VARCHAR(50) NOT NULL, -- 'city_hall', 'academy', 'barracks', etc.
    level INTEGER DEFAULT 1,
    upgrade_in_progress BOOLEAN DEFAULT false,
    upgrade_complete_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

#### missions
게임 미션/퀘스트 관리
```sql
CREATE TABLE missions (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    mission_type VARCHAR(50) NOT NULL, -- 'daily', 'event', 'alliance', etc.
    description TEXT,
    rewards JSONB,
    requirements JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### game_config
게임 설정 및 메타데이터
```sql
CREATE TABLE game_config (
    id SERIAL PRIMARY KEY,
    config_key VARCHAR(100) UNIQUE NOT NULL,
    config_value JSONB NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

## GraphQL API 스키마

### Types

```graphql
type Account {
  id: ID!
  email: String!
  googleAccount: String
  status: String!
  characters: [Character!]!
  createdAt: DateTime!
  updatedAt: DateTime!
}

type Character {
  id: ID!
  accountId: ID!
  name: String!
  governorId: String
  kingdomId: Int
  power: BigInt!
  level: Int!
  vipLevel: Int!
  allianceName: String
  buildings: [Building!]!
  schedules: [Schedule!]!
  createdAt: DateTime!
  updatedAt: DateTime!
}

type Task {
  id: ID!
  name: String!
  type: String!
  priority: Int!
  parameters: JSON!
  enabled: Boolean!
  createdAt: DateTime!
}

type Schedule {
  id: ID!
  characterId: ID!
  taskId: ID!
  cronExpression: String
  startTime: DateTime
  endTime: DateTime
  repeatCount: Int
  enabled: Boolean!
  task: Task!
  createdAt: DateTime!
}

type Action {
  id: ID!
  characterId: ID!
  taskId: ID!
  actionType: String!
  status: String!
  result: JSON
  startedAt: DateTime
  completedAt: DateTime
  errorMessage: String
  createdAt: DateTime!
}

type Building {
  id: ID!
  characterId: ID!
  buildingType: String!
  level: Int!
  upgradeInProgress: Boolean!
  upgradeCompleteAt: DateTime
  createdAt: DateTime!
  updatedAt: DateTime!
}
```

### Queries

```graphql
type Query {
  # Account queries
  account(id: ID!): Account
  accounts(status: String): [Account!]!

  # Character queries
  character(id: ID!): Character
  characters(accountId: ID): [Character!]!

  # Task queries
  task(id: ID!): Task
  tasks(type: String, enabled: Boolean): [Task!]!

  # Schedule queries
  schedule(id: ID!): Schedule
  schedules(characterId: ID, enabled: Boolean): [Schedule!]!

  # Action queries
  action(id: ID!): Action
  actions(characterId: ID, status: String, limit: Int): [Action!]!

  # Building queries
  buildings(characterId: ID!): [Building!]!
}
```

### Mutations

```graphql
type Mutation {
  # Account mutations
  createAccount(email: String!, password: String!, googleAccount: String): Account!
  updateAccount(id: ID!, email: String, status: String): Account!
  deleteAccount(id: ID!): Boolean!

  # Character mutations
  createCharacter(accountId: ID!, name: String!, kingdomId: Int): Character!
  updateCharacter(id: ID!, name: String, power: BigInt, level: Int): Character!
  deleteCharacter(id: ID!): Boolean!

  # Task mutations
  createTask(name: String!, type: String!, parameters: JSON!): Task!
  updateTask(id: ID!, name: String, priority: Int, enabled: Boolean): Task!
  deleteTask(id: ID!): Boolean!

  # Schedule mutations
  createSchedule(characterId: ID!, taskId: ID!, cronExpression: String!): Schedule!
  updateSchedule(id: ID!, cronExpression: String, enabled: Boolean): Schedule!
  deleteSchedule(id: ID!): Boolean!

  # Action mutations
  executeAction(characterId: ID!, taskId: ID!): Action!
  cancelAction(id: ID!): Action!

  # Building mutations
  upgradeBuilding(characterId: ID!, buildingType: String!): Building!
}
```

### Subscriptions

```graphql
type Subscription {
  # Real-time action updates
  actionStatusChanged(characterId: ID!): Action!

  # Building upgrade completion
  buildingUpgradeCompleted(characterId: ID!): Building!

  # Task execution logs
  taskExecutionLog(characterId: ID!): String!
}
```

## Python Backend 구조

### 프로젝트 구조

```
backend/
├── src/
│   ├── api/
│   │   ├── graphql/
│   │   │   ├── schema.py          # GraphQL schema definition
│   │   │   ├── queries.py         # Query resolvers
│   │   │   ├── mutations.py       # Mutation resolvers
│   │   │   └── subscriptions.py   # Subscription resolvers
│   │   └── main.py                # FastAPI application entry
│   ├── automation/
│   │   ├── vision/
│   │   │   ├── detector.py        # Image detection
│   │   │   ├── ocr.py             # Text recognition
│   │   │   └── templates/         # Template images
│   │   ├── control/
│   │   │   ├── adb.py             # ADB wrapper
│   │   │   ├── input.py           # Input simulation
│   │   │   └── screen.py          # Screen capture
│   │   ├── tasks/
│   │   │   ├── base.py            # Base task class
│   │   │   ├── resource.py        # Resource gathering
│   │   │   ├── building.py        # Building management
│   │   │   ├── training.py        # Troop training
│   │   │   └── alliance.py        # Alliance activities
│   │   └── executor.py            # Task execution engine
│   ├── database/
│   │   ├── models.py              # SQLAlchemy models
│   │   ├── connection.py          # Database connection
│   │   └── migrations/            # Alembic migrations
│   ├── services/
│   │   ├── account_service.py     # Account business logic
│   │   ├── character_service.py   # Character business logic
│   │   ├── task_service.py        # Task business logic
│   │   └── scheduler_service.py   # Schedule management
│   ├── utils/
│   │   ├── config.py              # Configuration management
│   │   ├── logger.py              # Logging setup
│   │   └── exceptions.py          # Custom exceptions
│   └── __init__.py
├── tests/
│   ├── test_api/
│   ├── test_automation/
│   └── test_services/
├── requirements.txt
├── pyproject.toml
└── .env
```

### 핵심 모듈 구현 예시

#### automation/control/adb.py
```python
from typing import Tuple, Optional
import subprocess
from adb_shell.adb_device import AdbDeviceTcp

class WaydroidController:
    def __init__(self, host: str = "localhost", port: int = 5555):
        self.device = AdbDeviceTcp(host, port)
        self.device.connect()

    def tap(self, x: int, y: int) -> bool:
        """화면 탭"""
        result = self.device.shell(f"input tap {x} {y}")
        return result is not None

    def swipe(self, x1: int, y1: int, x2: int, y2: int, duration: int = 300) -> bool:
        """화면 스와이프"""
        result = self.device.shell(f"input swipe {x1} {y1} {x2} {y2} {duration}")
        return result is not None

    def screenshot(self, save_path: str = "/tmp/screen.png") -> bytes:
        """스크린샷 캡처"""
        return self.device.shell("screencap -p", decode=False)

    def get_current_activity(self) -> str:
        """현재 Activity 확인"""
        result = self.device.shell("dumpsys window | grep mCurrentFocus")
        return result
```

#### automation/vision/detector.py
```python
import cv2
import numpy as np
from typing import Optional, Tuple

class ImageDetector:
    def __init__(self, threshold: float = 0.8):
        self.threshold = threshold

    def find_template(self, screen: np.ndarray, template: np.ndarray) -> Optional[Tuple[int, int]]:
        """템플릿 매칭으로 이미지 위치 찾기"""
        result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        if max_val >= self.threshold:
            h, w = template.shape[:2]
            center_x = max_loc[0] + w // 2
            center_y = max_loc[1] + h // 2
            return (center_x, center_y)
        return None

    def detect_button(self, screen: np.ndarray, button_name: str) -> Optional[Tuple[int, int]]:
        """버튼 위치 감지"""
        template_path = f"templates/buttons/{button_name}.png"
        template = cv2.imread(template_path)
        return self.find_template(screen, template)
```

#### automation/tasks/base.py
```python
from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseTask(ABC):
    def __init__(self, controller, detector):
        self.controller = controller
        self.detector = detector

    @abstractmethod
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """작업 실행"""
        pass

    @abstractmethod
    def validate(self, params: Dict[str, Any]) -> bool:
        """파라미터 검증"""
        pass

    def wait_for_screen(self, screen_name: str, timeout: int = 30) -> bool:
        """특정 화면이 나타날 때까지 대기"""
        import time
        start_time = time.time()
        while time.time() - start_time < timeout:
            screen = self.controller.screenshot()
            if self.detector.detect_button(screen, screen_name):
                return True
            time.sleep(1)
        return False
```

## Frontend 구조 (Next.js)

### 프로젝트 구조

```
frontend/nextjs/
├── src/
│   ├── app/
│   │   ├── (auth)/
│   │   │   ├── login/
│   │   │   └── register/
│   │   ├── dashboard/
│   │   │   ├── page.tsx          # 대시보드 메인
│   │   │   ├── accounts/         # 계정 관리
│   │   │   ├── characters/       # 캐릭터 관리
│   │   │   ├── schedules/        # 일정 관리
│   │   │   └── manual/           # 매뉴얼 관리
│   │   ├── layout.tsx
│   │   └── page.tsx
│   ├── components/
│   │   ├── ui/                   # shadcn/ui components
│   │   ├── forms/
│   │   ├── tables/
│   │   └── charts/
│   ├── lib/
│   │   ├── graphql/
│   │   │   ├── client.ts         # Apollo Client setup
│   │   │   ├── queries.ts        # GraphQL queries
│   │   │   ├── mutations.ts      # GraphQL mutations
│   │   │   └── subscriptions.ts  # GraphQL subscriptions
│   │   ├── hooks/
│   │   └── utils/
│   ├── store/
│   │   ├── auth.ts               # Zustand auth store
│   │   └── characters.ts         # Zustand character store
│   └── types/
│       └── graphql.ts            # TypeScript types
├── public/
├── package.json
└── next.config.js
```

### 주요 페이지 구성

#### 1. Dashboard (대시보드)
- 전체 계정 상태 요약
- 실행 중인 작업 모니터링
- 리소스 현황 차트

#### 2. Accounts (계정 관리)
- 계정 목록 CRUD
- Google 계정 연동
- 계정별 캐릭터 조회

#### 3. Characters (캐릭터 관리)
- 캐릭터 목록 및 상세 정보
- 건물/연구/부대 현황
- 왕국/연맹 정보

#### 4. Schedules (일정 관리)
- 작업 스케줄 설정 (cron 표현식)
- 반복 작업 관리
- 작업 우선순위 설정

#### 5. Manual (게임 매뉴얼)
- 게임 기능별 가이드
- 작업 템플릿 라이브러리
- FAQ 및 팁

## 환경 설정

### .env 파일 구조

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/rok_automation
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=10

# API
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=true
CORS_ORIGINS=http://localhost:3000,http://localhost:8000

# Waydroid
WAYDROID_ADB_HOST=localhost
WAYDROID_ADB_PORT=5555
WAYDROID_SCREEN_WIDTH=1080
WAYDROID_SCREEN_HEIGHT=1920

# Authentication
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=1440

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
LOG_FILE=/var/log/rok-automation/app.log

# Task Scheduler
SCHEDULER_TIMEZONE=Asia/Seoul
SCHEDULER_MAX_WORKERS=4

# OCR
TESSERACT_PATH=/usr/bin/tesseract
TESSERACT_LANG=eng+kor

# Storage
SCREENSHOT_PATH=/tmp/screenshots
TEMPLATE_PATH=/app/templates
```

## 배포 및 운영

### systemd 서비스 설정

#### backend.service
```ini
[Unit]
Description=ROK Automation Backend
After=network.target postgresql.service waydroid-container.service

[Service]
Type=simple
User=sam
WorkingDirectory=/home/sam/JnJ/developments/jnj-android/backend
Environment="PATH=/home/sam/.local/bin:/usr/bin"
ExecStart=/usr/bin/python3 -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### scheduler.service
```ini
[Unit]
Description=ROK Task Scheduler
After=network.target postgresql.service backend.service

[Service]
Type=simple
User=sam
WorkingDirectory=/home/sam/JnJ/developments/jnj-android/backend
ExecStart=/usr/bin/python3 -m src.services.scheduler_service
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 모니터링

#### 로그 수집
```bash
# journalctl을 통한 서비스 로그 확인
journalctl -u backend.service -f
journalctl -u scheduler.service -f

# 애플리케이션 로그
tail -f /var/log/rok-automation/app.log
```

#### 성능 모니터링
- Prometheus + Grafana
- PostgreSQL 쿼리 성능 모니터링
- Waydroid 리소스 사용량 모니터링

## 보안 고려사항

1. **인증/인가**
   - JWT 기반 인증
   - GraphQL query depth limiting
   - Rate limiting

2. **데이터 보호**
   - 비밀번호 해싱 (bcrypt)
   - 환경변수 암호화
   - Google 계정 정보 암호화 저장

3. **네트워크 보안**
   - HTTPS/WSS 사용
   - CORS 설정
   - Firewall 규칙

## 확장성 고려사항

1. **Multi-instance 지원**
   - 여러 Waydroid 인스턴스 동시 관리
   - 작업 큐 기반 분산 처리

2. **캐싱**
   - Redis 캐싱 레이어
   - GraphQL query caching

3. **마이크로서비스 분리** (향후)
   - Vision Service
   - Control Service
   - Scheduler Service