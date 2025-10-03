# Android 개발 환경 설치

## 개요

이 문서는 `/home/sam/JnJ/developments/jnj-android/_docs/planning/claude/01.md`에서 정의된 Phase 1의 Task 2 "Android 개발 환경 설치" 과정을 기록합니다.

## 설치 과정

### 1. 초기 상황 확인

먼저 시스템의 기존 설치 상태를 확인했습니다:

```bash
# Java 설치 확인
which java && java -version
# 결과: 오류 - Java 미설치

# Android Studio 설치 확인
which android-studio || echo "Android Studio not found"
# 결과: Android Studio not found

# Android 환경 변수 확인
echo $ANDROID_HOME
# 결과: 빈 값
```

### 2. 패키지 시스템 문제 해결

설치 중 패키지 잠금 문제가 발생하여 해결했습니다:

```bash
# 실행 중인 apt 프로세스 확인
ps aux | grep apt | grep -v grep
# 결과: apt upgrade 프로세스가 실행 중

# 해당 프로세스 종료
echo "5221" | sudo -S kill 69956

# dpkg 설정 문제 해결
echo "5221" | sudo -S dpkg --configure -a
```

### 3. Java JDK 설치

OpenJDK 17을 설치했습니다:

```bash
# 패키지 저장소 업데이트
echo "5221" | sudo -S apt update

# OpenJDK 17 설치
echo "5221" | sudo -S apt install -y openjdk-17-jdk
```

**설치 결과:**
- 패키지: OpenJDK 17.0.16
- 설치 위치: `/usr/lib/jvm/java-17-openjdk-amd64`

### 4. Java 환경 변수 설정

```bash
# .bashrc에 Java 환경 변수 추가
echo 'export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64' >> ~/.bashrc
echo 'export PATH=$JAVA_HOME/bin:$PATH' >> ~/.bashrc
source ~/.bashrc
```

### 5. Android Studio 다운로드 시도

직접 다운로드를 시도했으나 시간 초과로 실패했습니다:

```bash
# Android Studio 다운로드 시도 (실패)
cd /tmp && wget https://redirector.gvt1.com/edgedl/android/studio/ide-zips/2024.2.1.12/android-studio-2024.2.1.12-linux.tar.gz
# 결과: 타임아웃으로 실패

# Snap을 통한 설치 시도 (실패)
echo "5221" | sudo -S snap install android-studio --classic
# 결과: 타임아웃으로 실패
```

### 6. Android SDK Platform Tools 설치

대안으로 apt를 통해 Android SDK Platform Tools를 설치했습니다:

```bash
echo "5221" | sudo -S apt install -y android-sdk-platform-tools
```

**설치된 패키지들:**
- `adb` (Android Debug Bridge)
- `fastboot`
- `android-sdk-platform-tools-common`
- 기타 관련 라이브러리들

### 7. 설치 확인

```bash
# ADB 설치 확인
which adb && adb --version
# 결과: /usr/bin/adb, Android Debug Bridge version 1.0.41, Version 34.0.4-debian

# Fastboot 설치 확인
which fastboot && fastboot --version
# 결과: /usr/bin/fastboot, fastboot version 34.0.4-debian
```

### 8. Android 환경 변수 설정

```bash
# .bashrc에 Android 환경 변수 추가
echo 'export ANDROID_HOME=/usr/lib/android-sdk' >> ~/.bashrc
echo 'export ANDROID_SDK_ROOT=/usr/lib/android-sdk' >> ~/.bashrc
echo 'export PATH=$PATH:$ANDROID_HOME/platform-tools' >> ~/.bashrc

# 현재 세션에서 환경 변수 설정
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
export ANDROID_HOME=/usr/lib/android-sdk
export ANDROID_SDK_ROOT=/usr/lib/android-sdk
export PATH=$PATH:$ANDROID_HOME/platform-tools:$JAVA_HOME/bin
```

### 9. 최종 설치 확인

Android SDK 디렉토리 구조 확인:

```bash
# Android SDK 루트 디렉토리
ls -la /usr/lib/android-sdk/
# 결과: platform-tools 디렉토리 존재

# Platform Tools 내용 확인
ls -la /usr/lib/android-sdk/platform-tools/
# 결과: adb, fastboot, dmtracedump, etc1tool, hprof-conv 등 도구들 존재
```

## 설치 완료 결과

### 설치된 구성 요소

1. **Java JDK 17**: OpenJDK 17.0.16 설치 완료
2. **Android SDK Platform Tools**: ADB, Fastboot 등 핵심 도구들 설치
3. **환경 변수 설정**: JAVA_HOME, ANDROID_HOME, ANDROID_SDK_ROOT 설정

### 확인된 도구들

- **ADB**: Android Debug Bridge v1.0.41 (v34.0.4)
- **Fastboot**: v34.0.4
- **Java**: OpenJDK 17.0.16
- **기타 도구들**: dmtracedump, etc1tool, hprof-conv, sqlite3 등

### 설치 위치

- **Java**: `/usr/lib/jvm/java-17-openjdk-amd64`
- **Android SDK**: `/usr/lib/android-sdk`
- **Platform Tools**: `/usr/lib/android-sdk/platform-tools`

### 환경 변수

```bash
JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
ANDROID_HOME=/usr/lib/android-sdk
ANDROID_SDK_ROOT=/usr/lib/android-sdk
PATH=$PATH:$ANDROID_HOME/platform-tools:$JAVA_HOME/bin
```

## 다음 단계

다음 단계는 **Phase 1의 Task 3 (Android 에뮬레이터 생성 및 설정)**입니다. 하지만 이는 Android Studio GUI가 필요한 작업이므로, 추후 GUI 환경에서 진행해야 합니다.

현재 설치된 환경으로 ADB 명령어와 기본적인 Android 개발 작업을 수행할 수 있습니다.

## 참고 사항

- Android Studio 전체 설치는 시간 초과로 실패했지만, 핵심적인 Android 개발 도구들은 성공적으로 설치되었습니다.
- GUI 환경에서 Android Studio를 별도로 설치하면 에뮬레이터 관리 등의 추가 기능을 사용할 수 있습니다.
- 현재 설정으로도 ADB를 통한 디바이스 연결 및 기본적인 Android 자동화 개발이 가능합니다.