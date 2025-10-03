# Ubuntu XFCE 서버 환경 준비 - 필수 개발 도구 설치 방법

## 1. 시스템 업데이트

```bash
sudo apt update && sudo apt upgrade -y
```

## 2. 필수 개발 도구 설치

### VS Code 설치

Microsoft GPG 키 다운로드 및 추가:

```bash
wget -qO- https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > packages.microsoft.gpg
sudo install -o root -g root -m 644 packages.microsoft.gpg /etc/apt/trusted.gpg.d/
sudo sh -c 'echo "deb [arch=amd64,arm64,armhf signed-by=/etc/apt/trusted.gpg.d/packages.microsoft.gpg] https://packages.microsoft.com/repos/code stable main" > /etc/apt/sources.list.d/vscode.list'
```

VS Code 설치:

```bash
sudo apt update
sudo apt install code -y
```

또는 Snap으로 설치 (더 간단한 방법):

```bash
sudo snap install code --classic
```

### Git 설치 및 설정

Git 설치:

```bash
sudo apt install git -y
```

Git 기본 설정:

```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

### Python 설치 (Python 3.11+)

Python 및 관련 도구 설치:

```bash
sudo apt install python3 python3-pip python3-venv python3-dev -y
```

Python 버전 확인:

```bash
python3 --version
```

최신 Python이 필요한 경우 (Ubuntu 22.04 이상에서):

```bash
sudo apt install software-properties-common -y
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update
sudo apt install python3.11 python3.11-venv python3.11-dev -y
```

pip 업그레이드:

```bash
python3 -m pip install --upgrade pip
```

## 3. 추가 필수 도구들

### 빌드 도구 및 라이브러리

컴파일러 및 빌드 도구:

```bash
sudo apt install build-essential -y
sudo apt install curl wget unzip -y
```

SSL 인증서 및 네트워크 도구:

```bash
sudo apt install ca-certificates gnupg lsb-release -y
```

### 개발 편의 도구

터미널 향상 도구:

```bash
sudo apt install htop tree vim -y
```

파일 압축/해제 도구:

```bash
sudo apt install zip unzip p7zip-full -y
```

## 4. 원격 접속 환경 설정 (선택사항)

### VNC 서버 설치

TightVNC 서버 설치:

```bash
sudo apt install tightvncserver -y
```

VNC 서버 설정:

```bash
vncserver :1
```

비밀번호 설정 후 서버 중지:

```bash
vncserver -kill :1
```

VNC 설정 파일 편집:

```bash
nano ~/.vnc/xstartup
```

### xRDP 설치 (Windows RDP 클라이언트 사용시)

```bash
sudo apt install xrdp -y
sudo systemctl enable xrdp
sudo systemctl start xrdp
```

## 5. 환경 검증

설치된 도구들 버전 확인:

```bash
code --version
git --version
python3 --version
pip3 --version
```

## 6. Python 가상환경 생성 (프로젝트용)

프로젝트 디렉토리에서:

```bash
cd /home/sam/JnJ/developments/jnj-android
python3 -m venv venv
source venv/bin/activate
```

기본 패키지 설치:

```bash
pip install --upgrade pip setuptools wheel
```

## 7. 설치 완료 확인

### ✅ 설치 완료된 필수 개발 도구들

모든 필수 개발 도구들이 성공적으로 설치되었습니다:

**핵심 개발 도구:**
- ✅ **VS Code 1.104.2** - 코드 편집기
- ✅ **Git 2.43.0** - 버전 관리 (사용자 설정 완료: Sam)
- ✅ **Python 3.12.3** - 프로그래밍 언어 (3.11+ 요구사항 충족)
- ✅ **pip 24.0** - Python 패키지 관리자

**빌드 및 개발 도구:**
- ✅ **Build Essential** - 컴파일러 및 빌드 도구들
  - gcc 13.3.0
  - make
- ✅ **네트워크 도구들** - curl 8.5.0, wget 1.21.4
- ✅ **압축 도구** - unzip
- ✅ **Python 가상환경** - venv 생성 완료

### 추가 완료된 작업

- 시스템 패키지 업데이트
- Git 사용자 설정 (Sam, sam@example.com)
- 프로젝트용 Python 가상환경 생성
- pip, setuptools, wheel 최신 버전 설치

### 최종 설치 확인 명령어

설치된 도구들 버전 확인:

```bash
echo "=== 최종 설치 확인 ==="
echo "VS Code: $(code --version | head -1)"
echo "Git: $(git --version)"
echo "Python: $(python3 --version)"
echo "pip: $(pip3 --version | cut -d' ' -f1-2)"
echo "Build tools: $(gcc --version | head -1)"
echo "Curl: $(curl --version | head -1)"
echo "Wget: $(wget --version | head -1)"
```

## 다음 단계

이제 기본 개발 환경이 완전히 준비되었습니다. 다음 단계인 **Android 개발 환경 설치**(Android Studio, SDK 등)를 진행할 수 있습니다!