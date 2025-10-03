# Rise of Kingdoms 설치 및 초기 설정

## 개요
Android 에뮬레이터 환경에서 Rise of Kingdoms 게임을 설치하고 초기 설정하는 과정

---

## 1. 환경 확인

### Android SDK 상태 확인
```bash
# 에뮬레이터 프로세스 확인
ps aux | grep -E "emulator|adb"

# ADB 데몬 시작
adb devices

# Android SDK 경로 확인
echo $ANDROID_HOME
# Output: /usr/lib/android-sdk
```

### AVD 상태 확인
```bash
/usr/lib/android-sdk/cmdline-tools/latest/bin/avdmanager list avd
```

**문제점:**
- AVD "Pixel4_API30" 존재하나 시스템 이미지 누락
- 에뮬레이터 바이너리 미설치

---

## 2. Android 에뮬레이터 컴포넌트 설치

### 설치 가능한 패키지 확인
```bash
/usr/lib/android-sdk/cmdline-tools/latest/bin/sdkmanager --list | grep -E "emulator|system-images"
```

### 필요 패키지 설치
```bash
# 홈 디렉토리 Android SDK 사용
ANDROID_HOME=/home/sam/Android/Sdk

# 라이센스 동의 및 패키지 설치
yes | /home/sam/Android/Sdk/cmdline-tools/latest/bin/sdkmanager \
  --sdk_root=/home/sam/Android/Sdk \
  "emulator" \
  "system-images;android-30;google_apis;x86_64" \
  "platform-tools"
```

### 설치 확인
```bash
ANDROID_HOME=/home/sam/Android/Sdk
/home/sam/Android/Sdk/cmdline-tools/latest/bin/sdkmanager --list_installed
```

**설치 완료된 패키지:**
- Android Emulator (36.1.9)
- Android SDK Platform-Tools (36.0.0)
- Android SDK Platform 30
- Google APIs Intel x86_64 Atom System Image (API 30)

---

## 3. AVD 생성

### 기존 AVD 삭제
```bash
ANDROID_HOME=/home/sam/Android/Sdk
/home/sam/Android/Sdk/cmdline-tools/latest/bin/avdmanager delete avd -n Pixel4_API30
```

### 태블릿 AVD 생성 (최종)

#### 사용 가능한 디바이스 프로파일 확인
```bash
/home/sam/Android/Sdk/cmdline-tools/latest/bin/avdmanager list device
```

**선택한 디바이스:** Nexus 9 (2048x1536)

#### AVD 생성 명령
```bash
export ANDROID_HOME=/home/sam/Android/Sdk

echo "no" | /home/sam/Android/Sdk/cmdline-tools/latest/bin/avdmanager \
  create avd \
  -n RiseOfKingdoms_Tablet \
  -k "system-images;android-30;google_apis;x86_64" \
  -d "Nexus 9"
```

#### 생성 확인
```bash
/home/sam/Android/Sdk/cmdline-tools/latest/bin/avdmanager list avd
```

**생성된 AVD:**
- Name: RiseOfKingdoms_Tablet
- Device: Nexus 9 (Google)
- Resolution: 2048x1536
- Target: Google APIs (Android 11)
- Tag/ABI: google_apis/x86_64

---

## 4. 에뮬레이터 실행

### GUI 모드로 실행
```bash
export ANDROID_HOME=/home/sam/Android/Sdk
export DISPLAY=:10

/home/sam/Android/Sdk/emulator/emulator \
  -avd RiseOfKingdoms_Tablet \
  -no-snapshot \
  -wipe-data \
  > /tmp/emulator_tablet.log 2>&1 &
```

**주요 설정:**
- DISPLAY=:10 (XFCE GUI 환경)
- -no-snapshot (스냅샷 사용 안 함)
- -wipe-data (초기화된 상태로 시작)

### 부팅 완료 대기
```bash
# 부팅 상태 확인
/home/sam/Android/Sdk/platform-tools/adb shell getprop sys.boot_completed
# Output: 1 (부팅 완료)

# 연결된 디바이스 확인
/home/sam/Android/Sdk/platform-tools/adb devices
# Output: emulator-5554	device
```

**부팅 완료 시간:** 약 180초 (3분)

---

## 5. Google 계정 설정

### 계정 추가 화면 열기
```bash
export ANDROID_HOME=/home/sam/Android/Sdk
/home/sam/Android/Sdk/platform-tools/adb shell am start -a android.settings.ADD_ACCOUNT_SETTINGS
```

### 로그인 정보
- **이메일:** deverlife@gmail.com
- **비밀번호:** Answjdtka1!

### GUI에서 수동 진행 단계
1. 에뮬레이터 화면에서 "Google" 계정 선택
2. 이메일 입력
3. 비밀번호 입력
4. 2단계 인증 처리 (필요시)
5. 약관 동의 및 로그인 완료

---

## 6. Rise of Kingdoms 설치 (예정)

### Play Store를 통한 설치
1. Google 계정 로그인 완료 후
2. Play Store 앱 실행
3. "Rise of Kingdoms" 검색
4. 설치 진행

---

## 문제 해결

### Qt 플랫폼 플러그인 오류
**증상:**
```
INFO | Warning: could not connect to display (:0, )
INFO | Fatal: This application failed to start because no Qt platform plugin could be initialized.
```

**해결방법:**
```bash
# XFCE 디스플레이 확인
ps aux | grep xfce

# DISPLAY 환경변수 설정
export DISPLAY=:10

# 에뮬레이터 재시작
```

### Headless 모드 실행 (GUI 없이)
```bash
/home/sam/Android/Sdk/emulator/emulator \
  -avd RiseOfKingdoms_Tablet \
  -no-window \
  -no-audio \
  -no-snapshot \
  -wipe-data
```

---

## 현재 상태

### ✅ 완료된 작업
- Android 에뮬레이터 컴포넌트 설치
- 시스템 이미지 (Android 11) 설치
- Nexus 9 태블릿 AVD 생성 (2048x1536)
- 에뮬레이터 GUI 모드 실행 완료
- 에뮬레이터 부팅 완료 (emulator-5554)
- Google 계정 추가 화면 열림

### ⏳ 진행 중
- Google 계정 로그인 (GUI에서 수동 진행)

### 📋 대기 중
- Rise of Kingdoms Play Store 설치

---

## 참고 정보

### 주요 경로
- Android SDK: `/home/sam/Android/Sdk`
- AVD 설정: `/home/sam/.android/avd/RiseOfKingdoms_Tablet.avd`
- 에뮬레이터 로그: `/tmp/emulator_tablet.log`

### 주요 명령어
```bash
# AVD 관리
avdmanager list avd                    # AVD 목록
avdmanager delete avd -n <name>        # AVD 삭제
avdmanager create avd ...              # AVD 생성

# 에뮬레이터 제어
adb devices                            # 연결된 디바이스 확인
adb shell getprop sys.boot_completed   # 부팅 완료 확인
adb shell am start ...                 # 앱/액티비티 시작

# 프로세스 관리
pgrep -f emulator                      # 에뮬레이터 프로세스 찾기
pkill -f emulator                      # 에뮬레이터 종료
```

### 에뮬레이터 사양
- **디바이스:** Nexus 9 (Google)
- **해상도:** 2048x1536
- **DPI:** 320x320
- **RAM:** 2048MB
- **Android 버전:** 11 (API 30)
- **시스템 이미지:** Google APIs x86_64

---

## 다음 단계

1. ✅ XFCE GUI 원격 데스크톱 접속
2. ⏳ Google 계정 로그인 완료
3. 📋 Play Store 접속
4. 📋 Rise of Kingdoms 검색 및 설치
5. 📋 게임 초기 설정 및 튜토리얼 완료
6. 📋 테스트용 계정 준비