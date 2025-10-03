# Android 에뮬레이터 생성 및 설정

## 요구사항
- AVD Manager에서 에뮬레이터 생성
- 하드웨어 가속 설정 (Intel HAXM 또는 AMD)
- 에뮬레이터 성능 최적화 설정
- ADB 연결 테스트

## 설정 과정

### 1. Android SDK 상태 확인

먼저 현재 Android SDK와 도구들의 설치 상태를 확인했습니다.

```bash
echo $ANDROID_HOME && which adb && which avdmanager && which emulator
adb version
ls /usr/lib/android-sdk/
```

**결과:**
- ADB는 설치되어 있음 (version 1.0.41)
- AVD Manager와 emulator는 누락됨
- 전체 Android SDK 설치 필요

### 2. Android SDK 설치

Ubuntu 패키지 관리자를 통해 Android SDK를 설치했습니다.

```bash
sudo apt update && sudo apt install -y android-sdk
```

하지만 Ubuntu 패키지에는 전체 SDK 도구들이 포함되지 않아서, Google에서 직접 command line tools를 다운로드했습니다.

```bash
cd /tmp
wget https://dl.google.com/android/repository/commandlinetools-linux-11076708_latest.zip
unzip commandlinetools-linux-11076708_latest.zip
```

### 3. Command Line Tools 설정

다운로드한 도구들을 올바른 위치에 설치하고 구조를 수정했습니다.

```bash
# 개인 Android SDK 디렉토리 생성
export ANDROID_HOME=$HOME/Android/Sdk
mkdir -p $ANDROID_HOME
cd $ANDROID_HOME

# Command line tools 설치
cp /tmp/commandlinetools-linux-11076708_latest.zip .
unzip -q commandlinetools-linux-11076708_latest.zip
mkdir -p cmdline-tools/latest
mv cmdline-tools/* cmdline-tools/latest/
```

### 4. SDK 라이선스 수락

모든 Android SDK 라이선스를 수락했습니다.

```bash
printf "y\ny\ny\ny\ny\ny\ny\n" | /home/sam/Android/Sdk/cmdline-tools/latest/bin/sdkmanager --sdk_root=/home/sam/Android/Sdk --licenses
```

### 5. 필수 SDK 컴포넌트 설치

Android 30 플랫폼, 시스템 이미지, 에뮬레이터를 설치했습니다.

```bash
/home/sam/Android/Sdk/cmdline-tools/latest/bin/sdkmanager --sdk_root=/home/sam/Android/Sdk \
  "platforms;android-30" \
  "system-images;android-30;google_apis;x86_64" \
  "emulator" \
  "platform-tools"
```

### 6. AVD(Android Virtual Device) 생성

Pixel 4 디바이스 프로필을 사용하여 AVD를 생성했습니다.

```bash
/home/sam/Android/Sdk/cmdline-tools/latest/bin/avdmanager create avd \
  -n "Pixel4_API30" \
  -k "system-images;android-30;google_apis;x86_64" \
  -d "pixel_4" \
  --tag "google_apis"
```

**생성된 AVD 정보:**
- **이름**: Pixel4_API30
- **디바이스**: pixel_4 (Google)
- **타겟**: Google APIs (Google Inc.)
- **Android 버전**: Android 11.0 ("R")
- **태그/ABI**: google_apis/x86_64
- **SD카드**: 512 MB

### 7. 하드웨어 가속 설정

시스템의 가상화 지원을 확인하고 KVM 설정을 완료했습니다.

```bash
# 가상화 지원 확인
lscpu | grep -E "(Virtualization|VT-x|AMD-V)"
egrep -c '(vmx|svm)' /proc/cpuinfo
lsmod | grep kvm
```

**확인 결과:**
- Intel VT-x 가상화 지원 확인됨
- KVM 모듈이 로드되어 있음
- 8개 CPU 코어에서 가상화 지원

**KVM 권한 문제 해결:**
```bash
sudo chmod 666 /dev/kvm
```

### 8. 에뮬레이터 시작 및 최적화

최적화된 설정으로 에뮬레이터를 백그라운드에서 시작했습니다.

```bash
export ANDROID_SDK_ROOT=/home/sam/Android/Sdk
export ANDROID_HOME=$ANDROID_SDK_ROOT
export PATH=$PATH:$ANDROID_SDK_ROOT/platform-tools:$ANDROID_SDK_ROOT/emulator

emulator -avd Pixel4_API30 \
  -accel auto \
  -gpu swiftshader_indirect \
  -no-audio \
  -no-window \
  -verbose \
  -no-metrics > /tmp/emulator_new.log 2>&1 &
```

**최적화 설정:**
- `-accel auto`: 자동 하드웨어 가속 (KVM 사용)
- `-gpu swiftshader_indirect`: 소프트웨어 GPU 렌더링
- `-no-audio`: 오디오 비활성화
- `-no-window`: GUI 비활성화 (헤드리스 모드)
- `-no-metrics`: 메트릭 수집 비활성화

### 9. ADB 연결 테스트

ADB를 통해 에뮬레이터 연결을 테스트했습니다.

```bash
export PATH=$PATH:/home/sam/Android/Sdk/platform-tools

# 연결된 디바이스 확인
adb devices

# Android 버전 확인
adb -s emulator-5554 shell getprop ro.build.version.release

# 연결 테스트
adb -s emulator-5554 shell "echo 'Android 에뮬레이터 연결 테스트 성공!'"
```

**테스트 결과:**
- 에뮬레이터 디바이스: `emulator-5554`
- 연결 상태: `device` (정상 연결)
- Android 버전: `11`
- ADB 명령어 실행 성공

## ✅ 최종 결과

### 완성된 작업들

1. **✅ Android SDK 및 에뮬레이터 설치 확인**
   - Android SDK Command Line Tools 설치 완료
   - 필요한 패키지들 설치 완료

2. **✅ AVD(Android Virtual Device) 생성**
   - **디바이스**: Pixel 4
   - **Android 버전**: Android 11 (API 30)
   - **아키텍처**: x86_64 (Intel)
   - **시스템 이미지**: Google APIs

3. **✅ 하드웨어 가속 설정**
   - **Intel VT-x 가상화 지원 확인됨**
   - **KVM 모듈 로드 및 권한 설정 완료**
   - `/dev/kvm` 권한 문제 해결

4. **✅ 에뮬레이터 성능 최적화**
   - KVM 하드웨어 가속 활성화
   - 소프트웨어 GPU 렌더링 설정
   - 오디오 및 GUI 비활성화 (헤드리스 모드)
   - 메트릭 수집 비활성화

5. **✅ ADB 연결 테스트**
   - **에뮬레이터 디바이스**: `emulator-5554`
   - **연결 상태**: `device` (정상 연결)
   - **Android 버전**: Android 11
   - **ADB 명령어 실행 테스트 성공**

### 📋 설정 요약

- **SDK 위치**: `/home/sam/Android/Sdk`
- **AVD 이름**: `Pixel4_API30`
- **에뮬레이터 포트**: `5554`
- **하드웨어 가속**: KVM 사용
- **실행 모드**: 헤드리스 (백그라운드)

## 결론

Android 에뮬레이터가 성공적으로 실행되어 ADB를 통한 자동화 준비가 완료되었습니다!

이제 Rise of Kingdoms와 같은 모바일 게임의 자동화 개발을 위한 Android 환경이 준비되었습니다.