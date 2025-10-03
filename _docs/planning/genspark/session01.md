> https://www.genspark.ai/agents?id=51740887-9bc8-4b37-94d0-c3ddae160ea7

"""
ubuntu에 android 에뮬레이터를 설치하고, 안드로이드용 앱을 설치하여 그 앱에 대한 자동화 작업을 하려고 해요.
"""

Ubuntu에서 Android 에뮬레이터를 설치하고 앱 자동화 작업을 하는 방법에 대해 종합적으로 안내해드리겠습니다.

## 🎯 Ubuntu에서 Android 에뮬레이터 설치 및 앱 자동화 완전 가이드

### 📱 1단계: Android 에뮬레이터 설치 방법

#### 방법 1: Android Studio 사용 (권장)

**시스템 요구사항:**
- Ubuntu 22.04/24.04 LTS
- 8GB+ RAM
- Intel VT-x 또는 AMD-V 하드웨어 가상화 지원

**설치 절차:**

```bash
# Java 설치
sudo apt update
sudo apt install openjdk-11-jdk

# Android Studio 설치 (Snap 사용)
sudo snap install android-studio --classic

# 또는 직접 다운로드 설치
wget https://redirector.gvt1.com/edgedl/android/studio/ide-zips/2024.1.1.12/android-studio-2024.1.1.12-linux.tar.gz
sudo tar -xzf android-studio-*.tar.gz -C /opt/
```

**환경변수 설정:**
```bash
# ~/.bashrc에 추가
export ANDROID_HOME="$HOME/Android/Sdk"
export PATH=$PATH:$ANDROID_HOME/emulator
export PATH=$PATH:$ANDROID_HOME/tools
export PATH=$PATH:$ANDROID_HOME/tools/bin
export PATH=$PATH:$ANDROID_HOME/platform-tools
export PATH=$PATH:$ANDROID_HOME/cmdline-tools/latest/bin
```

#### 방법 2: Waydroid 사용 (가벼운 대안)

**설치:**
```bash
# 필요한 패키지 설치
sudo apt install curl ca-certificates

# Waydroid 저장소 추가
curl https://repo.waydro.id | sudo bash

# Waydroid 설치
sudo apt install waydroid
```

**초기화:**
```bash
# 초기 설정 실행
waydroid first-launch

# Android 시스템 크기 조정
waydroid prop set persist.waydroid.width 506
waydroid prop set persist.waydroid.height 1000
```

**장점:**
- 컨테이너 기반으로 가벼움
- LineageOS 기반
- 실제 Android 환경에 가까움

![Waydroid Android 화면](https://ubuntuhandbook.org/wp-content/uploads/2023/12/waydroid-android-screen-600x455.webp)

### 🤖 2단계: 자동화 도구 선택 및 설치

#### 옵션 1: Appium (가장 강력하고 범용적)

**설치:**
```bash
# Node.js 설치 (NVM 사용)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.3/install.sh | bash
nvm install lts/gallium

# Appium 설치
npm install -g @appium/cli

# Android용 드라이버 설치
appium driver install uiautomator2

# Appium Doctor 설치 (환경 체크용)
npm install -g @appium/doctor
appium-doctor --android
```

**Python 클라이언트 설치:**
```bash
pip install Appium-Python-Client
pip install pytest  # 테스트 프레임워크
```

#### 옵션 2: UIAutomator2 (Python 전용, 간편함)

**설치:**
```bash
pip install uiautomator2
pip install uiautodev  # 요소 검사 도구
```

**기본 사용법:**
```python
import uiautomator2 as u2

# 디바이스 연결
d = u2.connect()  # USB 연결된 디바이스
# 또는 에뮬레이터
d = u2.connect('emulator-5554')

# 앱 시작
d.app_start('com.example.app')

# 요소 조작
d(text='로그인').click()
d(resourceId='com.example:id/username').set_text('사용자명')
d(className='android.widget.Button').click()

# 스크린샷
d.screenshot('screen.jpg')
```

#### 옵션 3: ADB + Python (기본 자동화)

**설치:**
```bash
pip install adb-shell
pip install pure-python-adb
```

**기본 사용법:**
```python
import subprocess

# 앱 실행
subprocess.run(['adb', 'shell', 'am', 'start', 'com.example.app/.MainActivity'])

# 텍스트 입력
subprocess.run(['adb', 'shell', 'input', 'text', 'hello'])

# 탭 이벤트
subprocess.run(['adb', 'shell', 'input', 'tap', '500', '300'])

# 키 이벤트
subprocess.run(['adb', 'shell', 'input', 'keyevent', '4'])  # 뒤로가기
```

### 🔧 3단계: 실제 자동화 작업 예제

#### 예제 1: UIAutomator2를 사용한 간단한 자동화

```python
import uiautomator2 as u2
import time

# 디바이스 연결
d = u2.connect()

# 설정 앱 열기
d.app_start('com.android.settings')
time.sleep(2)

# WiFi 설정으롤 이동
d(text='Wi-Fi').click()
time.sleep(1)

# 특정 네트워크 선택
d(text='MyNetwork').click()

# 비밀번호 입력
d(resourceId='com.android.settings:id/password').set_text('mypassword')

# 연결 버튼 클릭
d(text='Connect').click()

print("WiFi 연결 완료!")
```

#### 예제 2: Appium을 사용한 고급 자동화

```python
from appium import webdriver
from appium.options.android import UiAutomator2Options
import time

# 디바이스 설정
options = UiAutomator2Options()
options.platform_name = "Android"
options.device_name = "emulator-5554"
options.app_package = "com.example.app"
options.app_activity = ".MainActivity"
options.automation_name = "UiAutomator2"

# 드라이버 초기화
driver = webdriver.Remote("http://localhost:4723/wd/hub", options=options)

try:
    # 요소 찾기 및 클릭
    login_btn = driver.find_element("id", "com.example:id/login_button")
    login_btn.click()
    
    # 텍스트 입력
    username_field = driver.find_element("id", "com.example:id/username")
    username_field.send_keys("testuser")
    
    password_field = driver.find_element("id", "com.example:id/password")
    password_field.send_keys("testpass")
    
    # 로그인 버튼 클릭
    submit_btn = driver.find_element("xpath", "//android.widget.Button[@text='로그인']")
    submit_btn.click()
    
    time.sleep(3)
    
    # 결과 확인
    success_msg = driver.find_element("id", "com.example:id/success_message")
    print(f"로그인 결과: {success_msg.text}")
    
finally:
    driver.quit()
```

### 🛠️ 4단계: 고급 자동화 기능

#### 요소 검사 도구

**UIAutomator2 Device Inspector:**
```bash
# 요소 검사 도구 실행
uiautodev
# 브라우저에서 자동으로 열림
```

**Appium Inspector:**
- [GitHub 릴리스 페이지](https://github.com/appium/appium-inspector/releases)에서 다운로드
- GUI 환경에서 앱 요소 실시간 검사 가능

#### 자동화 스크립트 고도화

**1. 대기 조건 추가:**
```python
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 요소가 나타날 때까지 대기
wait = WebDriverWait(driver, 10)
element = wait.until(EC.presence_of_element_located(("id", "com.example:id/button")))
```

**2. 스크린샷 및 로깅:**
```python
import logging
from datetime import datetime

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def take_screenshot(driver, step_name):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"screenshot_{step_name}_{timestamp}.png"
    driver.save_screenshot(filename)
    logging.info(f"스크린샷 저장: {filename}")
```

**3. 예외 처리:**
```python
from selenium.common.exceptions import TimeoutException, NoSuchElementException

try:
    element = driver.find_element("id", "com.example:id/button")
    element.click()
except NoSuchElementException:
    logging.error("요소를 찾을 수 없습니다")
    take_screenshot(driver, "error")
except TimeoutException:
    logging.error("시간 초과")
    take_screenshot(driver, "timeout")
```

### 🎪 5단계: 자동화 작업 실용 예제

#### 예제: 쇼핑 앱 자동화
```python
import uiautomator2 as u2
import time

class ShoppingAppAutomator:
    def __init__(self, device_serial=None):
        self.d = u2.connect(device_serial)
        
    def login(self, username, password):
        """로그인 자동화"""
        self.d.app_start('com.shopping.app')
        time.sleep(3)
        
        # 로그인 버튼 클릭
        self.d(text='로그인').click()
        
        # 사용자명/비밀번호 입력
        self.d(resourceId='com.shopping.app:id/username').set_text(username)
        self.d(resourceId='com.shopping.app:id/password').set_text(password)
        
        # 로그인 확인
        self.d(text='확인').click()
        time.sleep(2)
        
    def search_product(self, keyword):
        """상품 검색"""
        # 검색창 클릭
        search_box = self.d(resourceId='com.shopping.app:id/search_box')
        search_box.click()
        search_box.set_text(keyword)
        
        # 검색 실행
        self.d.press('enter')
        time.sleep(3)
        
    def add_to_cart(self, product_index=0):
        """장바구니에 추가"""
        # 상품 목록에서 선택
        products = self.d(resourceId='com.shopping.app:id/product_item')
        if products.exists:
            products[product_index].click()
            time.sleep(2)
            
            # 장바구니 추가 버튼
            self.d(text='장바구니 담기').click()
            time.sleep(1)
            
            print(f"상품이 장바구니에 추가되었습니다")
        
# 사용 예제
automator = ShoppingAppAutomator()
automator.login('testuser', 'testpass')
automator.search_product('스마트폰')
automator.add_to_cart(0)
```

### 📊 6단계: 모니터링 및 디버깅

#### 로그 수집 스크립트
```python
import subprocess
import time
from datetime import datetime

def collect_device_logs():
    """디바이스 로그 수집"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = f"device_log_{timestamp}.txt"
    
    # logcat 실행
    with open(log_file, 'w') as f:
        process = subprocess.Popen(['adb', 'logcat'], stdout=f, stderr=subprocess.STDOUT)
        time.sleep(30)  # 30초 동안 로그 수집
        process.terminate()
    
    print(f"로그가 {log_file}에 저장되었습니다")

def get_device_info():
    """디바이스 정보 확인"""
    import uiautomator2 as u2
    d = u2.connect()
    
    info = d.info
    print("=== 디바이스 정보 ===")
    for key, value in info.items():
        print(f"{key}: {value}")
```

### 🚀 추천 워크플로우

1. **개발 환경 설정**
   - Android Studio 또는 Waydroid 설치
   - 자동화 도구 선택 (UIAutomator2 권장)

2. **앱 분석**
   - 대상 앱의 패키지명, 액티비티 확인
   - 요소 검사 도구로 UI 구조 파악

3. **스크립트 개발**
   - 단계별 자동화 로직 구현
   - 예외 처리 및 로깅 추가

4. **테스트 및 최적화**
   - 다양한 시나리오에서 테스트
   - 성능 최적화 및 안정성 향상

이 가이드를 따라하시면 Ubuntu에서 Android 앱 자동화 환경을 성공적으로 구축하실 수 있습니다. 특정 부분에 대해 더 자세한 설명이 필요하시면 언제든 말씀해 주세요!

===

"""
playstore에 있는 앱을 검색하고 설치한 후, 그 앱에 대한 자동화를 하려면 어떤 방법이 좋을까요?
'Rise of kingdoms' 앱을 설치하고, 계정에 로그인 후 캐릭터 관리로 여러 캐릭터들의 활동을 스케줄에 따라 제어하려고 해요.
"""


Rise of Kingdoms 자동화를 위한 완전한 가이드를 제공해드리겠습니다! 이 게임은 전략 게임이므로 여러 캐릭터 관리와 스케줄링이 매우 중요하죠.

## 🏰 Rise of Kingdoms 자동화 완벽 가이드

### 📱 1단계: Play Store 앱 설치 자동화

#### 방법 1: Google Play CLI 도구 사용

```bash
# Google Play CLI 설치
pip install gplaycli

# 또는 GitHub에서 최신 버전
git clone https://github.com/matlink/gplaycli.git
cd gplaycli
pip install -r requirements.txt
python setup.py install
```

**Rise of Kingdoms 검색 및 설치:**
```bash
# 앱 검색
gplaycli -s "Rise of Kingdoms"

# APK 다운로드
gplaycli -d com.lilithgames.roc.gp -f ./

# 에뮬레이터에 설치
adb install com.lilithgames.roc.gp.apk
```

#### 방법 2: APKPure나 대체 소스 사용

```python
import requests
import subprocess

def download_and_install_apk(app_name, apk_url, package_name):
    """APK 다운로드 및 설치"""
    # APK 다운로드
    response = requests.get(apk_url)
    apk_file = f"{app_name}.apk"
    
    with open(apk_file, 'wb') as f:
        f.write(response.content)
    
    # 에뮬레이터에 설치
    result = subprocess.run(['adb', 'install', apk_file], 
                          capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"{app_name} 설치 완료!")
        return True
    else:
        print(f"설치 실패: {result.stderr}")
        return False

# Rise of Kingdoms 설치
rok_url = "https://example-apk-source.com/rise-of-kingdoms.apk"
download_and_install_apk("Rise of Kingdoms", rok_url, "com.lilithgames.roc.gp")
```

### 🤖 2단계: Rise of Kingdoms 전용 자동화 시스템 구축

#### 핵심 자동화 클래스 설계

```python
import uiautomator2 as u2
import cv2
import numpy as np
import time
import json
import logging
from datetime import datetime, timedelta
import schedule
from PIL import Image

class RiseOfKingdomsBot:
    def __init__(self, device_serial=None):
        self.device = u2.connect(device_serial)
        self.package_name = "com.lilithgames.roc.gp"
        self.characters = {}
        self.schedules = {}
        self.setup_logging()
        
    def setup_logging(self):
        """로깅 설정"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('rok_bot.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def start_game(self):
        """게임 시작"""
        self.logger.info("Rise of Kingdoms 시작 중...")
        self.device.app_start(self.package_name, stop=True)
        time.sleep(10)  # 로딩 대기
        
        # 로딩 화면 완료 대기
        self.wait_for_element("로딩 완료 표시", timeout=60)
        
    def login_account(self, account_info):
        """계정 로그인"""
        self.logger.info(f"계정 로그인: {account_info['username']}")
        
        # 로그인 화면 감지 및 처리
        if self.device(text="로그인").exists(timeout=5):
            self.device(text="로그인").click()
            time.sleep(2)
            
            # 계정 정보 입력
            self.device(resourceId="username_field").set_text(account_info['username'])
            self.device(resourceId="password_field").set_text(account_info['password'])
            
            # 로그인 버튼 클릭
            self.device(text="확인").click()
            
            # 로그인 완료 대기
            self.wait_for_main_screen()
            
    def wait_for_main_screen(self, timeout=30):
        """메인 화면 로딩 대기"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            # 메인 성 화면의 특징적 요소 확인
            if self.device(text="건설").exists() or self.device(text="연구").exists():
                self.logger.info("메인 화면 로딩 완료")
                return True
            time.sleep(1)
        
        raise TimeoutError("메인 화면 로딩 실패")
        
    def detect_captcha(self):
        """캡차 감지"""
        screenshot = self.device.screenshot(format='opencv')
        # 캡차 패턴 감지 로직
        # 실제로는 더 정교한 이미지 분석 필요
        
    def farm_barbarians(self, level=1, commander="로하르"):
        """야만인 사냥 자동화"""
        self.logger.info(f"야만인 사냥 시작 - 레벨: {level}, 지휘관: {commander}")
        
        # 맵 화면으로 이동
        self.go_to_map()
        
        # 야만인 검색
        self.device(text="검색").click()
        time.sleep(1)
        self.device(text="야만인").click()
        time.sleep(1)
        
        # 레벨 선택
        self.select_barbarian_level(level)
        
        # 야만인 공격 루프
        for i in range(10):  # 최대 10번 공격
            if self.find_and_attack_barbarian(commander):
                self.logger.info(f"야만인 공격 {i+1}번 완료")
                time.sleep(30)  # 공격 완료 대기
            else:
                self.logger.info("더 이상 공격할 야만인이 없습니다")
                break
                
    def farm_resources(self, resource_type="food"):
        """자원 채집 자동화"""
        self.logger.info(f"{resource_type} 채집 시작")
        
        self.go_to_map()
        
        # 자원 검색
        self.device(text="검색").click()
        time.sleep(1)
        self.device(text=resource_type).click()
        time.sleep(1)
        
        # 자원 채집 루프
        for i in range(5):  # 최대 5개 자원 채집
            if self.find_and_gather_resource():
                self.logger.info(f"{resource_type} 채집 {i+1}번 시작")
                time.sleep(5)
            else:
                break
                
    def manage_city(self):
        """도시 관리 자동화"""
        self.logger.info("도시 관리 시작")
        
        # 메인 성으로 이동
        self.go_to_city()
        
        # 건설 완료된 건물들 수집
        self.collect_completed_buildings()
        
        # 연구 관리
        self.manage_research()
        
        # 훈련 관리
        self.manage_training()
        
    def collect_completed_buildings(self):
        """완료된 건설 수집"""
        # 완료 표시가 있는 건물들 클릭
        completed_buildings = self.device(className="android.widget.ImageView").find()
        for building in completed_buildings:
            if self.is_building_completed(building):
                building.click()
                time.sleep(1)
                
    def alliance_activities(self):
        """연맹 활동 자동화"""
        self.logger.info("연맹 활동 시작")
        
        # 연맹 화면으로 이동
        self.device(text="연맹").click()
        time.sleep(2)
        
        # 연맹 도움 보내기
        self.send_alliance_help()
        
        # 연맹 상점 확인
        self.check_alliance_shop()
        
    def daily_quests(self):
        """일일 퀘스트 자동 완료"""
        self.logger.info("일일 퀘스트 처리 시작")
        
        # 퀘스트 메뉴 열기
        self.device.xpath("//android.widget.Button[contains(@text, '퀘스트')]").click()
        time.sleep(2)
        
        # 완료 가능한 퀘스트들 수집
        while self.device(text="수령").exists():
            self.device(text="수령").click()
            time.sleep(1)
```

### 📅 3단계: 멀티 캐릭터 스케줄링 시스템

```python
class CharacterScheduler:
    def __init__(self):
        self.characters = {}
        self.schedules = {}
        
    def add_character(self, char_name, device_serial, account_info):
        """캐릭터 추가"""
        self.characters[char_name] = {
            'device': device_serial,
            'account': account_info,
            'bot': RiseOfKingdomsBot(device_serial),
            'last_activity': None,
            'energy': 100,
            'status': 'idle'
        }
        
    def create_schedule(self, char_name, activities):
        """캐릭터별 스케줄 생성"""
        self.schedules[char_name] = activities
        
        # 스케줄 등록
        for activity in activities:
            schedule.every().day.at(activity['time']).do(
                self.execute_activity, char_name, activity['action']
            )
            
    def execute_activity(self, char_name, action):
        """스케줄된 활동 실행"""
        if char_name not in self.characters:
            return
            
        char = self.characters[char_name]
        bot = char['bot']
        
        try:
            # 게임 시작 및 로그인
            bot.start_game()
            bot.login_account(char['account'])
            
            # 활동 실행
            if action == 'farm_barbarians':
                bot.farm_barbarians(level=1)
            elif action == 'farm_resources':
                bot.farm_resources('food')
            elif action == 'city_management':
                bot.manage_city()
            elif action == 'alliance_activities':
                bot.alliance_activities()
            elif action == 'daily_quests':
                bot.daily_quests()
                
            # 상태 업데이트
            char['last_activity'] = datetime.now()
            char['status'] = 'completed'
            
        except Exception as e:
            logging.error(f"캐릭터 {char_name} 활동 실행 실패: {e}")
            char['status'] = 'error'

# 사용 예제
scheduler = CharacterScheduler()

# 캐릭터들 추가
characters_config = [
    {
        'name': '메인계정',
        'device': 'emulator-5554',
        'account': {'username': 'main_account', 'password': 'password123'}
    },
    {
        'name': '부계정1',
        'device': 'emulator-5556', 
        'account': {'username': 'sub_account1', 'password': 'password456'}
    }
]

for char_config in characters_config:
    scheduler.add_character(
        char_config['name'],
        char_config['device'], 
        char_config['account']
    )

# 스케줄 설정
main_schedule = [
    {'time': '08:00', 'action': 'daily_quests'},
    {'time': '12:00', 'action': 'farm_barbarians'},
    {'time': '16:00', 'action': 'farm_resources'},
    {'time': '20:00', 'action': 'alliance_activities'},
    {'time': '23:00', 'action': 'city_management'}
]

sub_schedule = [
    {'time': '09:00', 'action': 'farm_resources'},
    {'time': '15:00', 'action': 'farm_barbarians'},
    {'time': '21:00', 'action': 'city_management'}
]

scheduler.create_schedule('메인계정', main_schedule)
scheduler.create_schedule('부계정1', sub_schedule)
```

### 🎯 4단계: 고급 자동화 기능

#### 이미지 인식 기반 자동화

```python
import cv2
import numpy as np
from PIL import Image

class ImageRecognition:
    def __init__(self, bot):
        self.bot = bot
        self.templates = self.load_templates()
        
    def load_templates(self):
        """게임 UI 템플릿 이미지들 로드"""
        templates = {
            'barbarian': cv2.imread('templates/barbarian.png'),
            'food_resource': cv2.imread('templates/food.png'),
            'completed_building': cv2.imread('templates/completed.png'),
            'alliance_help': cv2.imread('templates/help_button.png')
        }
        return templates
        
    def find_element_by_image(self, template_name, threshold=0.8):
        """이미지 템플릿 매칭으로 요소 찾기"""
        screenshot = self.bot.device.screenshot(format='opencv')
        template = self.templates[template_name]
        
        result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
        locations = np.where(result >= threshold)
        
        if len(locations[0]) > 0:
            # 첫 번째 매칭 위치 반환
            y, x = locations[0][0], locations[1][0]
            h, w = template.shape[:2]
            return (x + w//2, y + h//2)  # 중심점 좌표
        
        return None
        
    def click_if_found(self, template_name, threshold=0.8):
        """이미지를 찾아서 클릭"""
        position = self.find_element_by_image(template_name, threshold)
        if position:
            self.bot.device.click(position[0], position[1])
            return True
        return False
```

#### 지능형 자원 관리

```python
class ResourceManager:
    def __init__(self, bot):
        self.bot = bot
        self.resource_priorities = ['food', 'wood', 'stone', 'gold']
        
    def optimize_resource_gathering(self):
        """자원 수급 최적화"""
        current_resources = self.get_current_resources()
        
        # 가장 부족한 자원 찾기
        min_resource = min(current_resources.items(), key=lambda x: x[1])
        target_resource = min_resource[0]
        
        self.bot.logger.info(f"우선 채집 자원: {target_resource}")
        
        # 해당 자원 집중 채집
        self.bot.farm_resources(target_resource)
        
    def get_current_resources(self):
        """현재 자원 상태 확인"""
        # 게임 화면에서 자원 정보 추출
        # OCR이나 이미지 인식 사용
        return {
            'food': 1000000,
            'wood': 800000, 
            'stone': 600000,
            'gold': 400000
        }
```

### 🔄 5단계: 실행 및 모니터링

#### 메인 실행 스크립트

```python
#!/usr/bin/env python3
import time
import schedule
import threading
from datetime import datetime

class RoKAutomationManager:
    def __init__(self):
        self.scheduler = CharacterScheduler()
        self.is_running = True
        self.setup_characters()
        self.setup_schedules()
        
    def setup_characters(self):
        """캐릭터 설정 로드"""
        # JSON 파일에서 캐릭터 정보 로드
        with open('characters.json', 'r') as f:
            chars = json.load(f)
            
        for char in chars:
            self.scheduler.add_character(
                char['name'],
                char['device'],
                char['account']
            )
            
    def setup_schedules(self):
        """스케줄 설정"""
        # JSON 파일에서 스케줄 로드
        with open('schedules.json', 'r') as f:
            schedules = json.load(f)
            
        for char_name, activities in schedules.items():
            self.scheduler.create_schedule(char_name, activities)
            
    def run(self):
        """메인 실행 루프"""
        print("Rise of Kingdoms 자동화 시작!")
        
        while self.is_running:
            schedule.run_pending()
            time.sleep(60)  # 1분마다 체크
            
    def stop(self):
        """자동화 중지"""
        self.is_running = False
        print("자동화가 중지되었습니다.")

if __name__ == "__main__":
    manager = RoKAutomationManager()
    
    try:
        manager.run()
    except KeyboardInterrupt:
        manager.stop()
```

#### 설정 파일 예제

**characters.json:**
```json
[
    {
        "name": "메인계정",
        "device": "emulator-5554",
        "account": {
            "username": "main_user",
            "password": "secure_pass123"
        }
    },
    {
        "name": "농장계정1", 
        "device": "emulator-5556",
        "account": {
            "username": "farm_user1",
            "password": "secure_pass456"
        }
    }
]
```

**schedules.json:**
```json
{
    "메인계정": [
        {"time": "08:00", "action": "daily_quests"},
        {"time": "12:00", "action": "farm_barbarians"},
        {"time": "16:00", "action": "farm_resources"},
        {"time": "20:00", "action": "alliance_activities"}
    ],
    "농장계정1": [
        {"time": "09:00", "action": "farm_resources"},
        {"time": "15:00", "action": "farm_resources"},
        {"time": "21:00", "action": "city_management"}
    ]
}
```

### ⚠️ 주의사항 및 권장사항

1. **게임 정책 준수**
   - 게임 이용약관을 반드시 확인하세요
   - 과도한 자동화는 계정 제재를 받을 수 있습니다

2. **안전한 사용**
   - 캐릭터별로 적절한 휴식 시간을 두세요
   - 캡차 감지 기능을 반드시 포함하세요
   - 로그를 통해 활동을 모니터링하세요

3. **성능 최적화**
   - 여러 에뮬레이터 사용 시 시스템 리소스 모니터링
   - 네트워크 연결 안정성 확보
   - 정기적인 스크립트 업데이트

이 가이드를 통해 Rise of Kingdoms의 효율적인 멀티 캐릭터 자동화 시스템을 구축하실 수 있습니다. 필요한 부분에 대해 더 자세한 설명이 필요하시면 언제든 말씀해 주세요!


===

"""
android studio를 설치하고 emulator의 play store에서 게임을 설치하는데, 너무 느리네요.
게임으로 들어가서도 반응속도가 느릴 것 같은데, 리눅스에서 bluestack 같은 앱 중에 속도가 빠른 앱 추천해주세요.
"""

Linux에서 게임용으로 빠른 Android 에뮬레이터를 찾고 계시는군요! 확실히 Android Studio 에뮬레이터는 개발용이라 게임에는 너무 무겁죠. 게임 성능에 최적화된 몇 가지 훌륭한 대안들을 추천해드리겠습니다.

## 🚀 Linux용 고성능 Android 에뮬레이터 추천

### 🥇 1위: Waydroid (최고 성능, 게임 최적화)

**장점:**
- 🏃‍♂️ 네이티브 컨테이너 기반으로 매우 빠름
- 🎮 게임 성능이 뛰어남 (거의 네이티브 수준)
- 🔧 GPU 가속 완벽 지원
- 📱 최신 Android 11 기반 (LineageOS)
- 💾 낮은 메모리 사용량

**설치 및 최적화:**

```bash
# Waydroid 설치 (이미 설치하셨다면 건너뛰기)
sudo apt install curl ca-certificates
curl https://repo.waydro.id | sudo bash
sudo apt install waydroid

# 게임 최적화 설정
# 1. 해상도 최적화 (게임용으로 FHD 설정)
waydroid prop set persist.waydroid.width 1080
waydroid prop set persist.waydroid.height 1920

# 2. 성능 최적화
waydroid prop set persist.waydroid.multi_windows false
waydroid prop set ro.hardware.vulkan yes

# 3. GPU 가속 강화
waydroid prop set debug.hwui.renderer opengl
waydroid prop set ro.hardware.gralloc gbm

# 4. 게임 모드 활성화
waydroid prop set persist.vendor.radio.enable_voicecall 0
waydroid prop set persist.waydroid.suspend false
```

**Google Play Store 설치:**
```bash
# waydroid_script 사용
git clone https://github.com/casualsnek/waydroid_script
cd waydroid_script
python3 -m pip install -r requirements.txt

# GApps 설치
sudo python3 main.py install gapps
```

### 🥈 2위: Genymotion (안정성 + 성능)

**특징:**
- 💼 개발자용이지만 게임도 잘 돌아감
- 🎯 GPU 가속 최적화
- 🛠️ 다양한 기기 프로파일 제공
- ☁️ 클라우드 버전도 있음

**설치:**
```bash
# VirtualBox 설치 (필요)
sudo apt install virtualbox

# Genymotion 다운로드 및 설치
wget https://dl.genymotion.com/releases/genymotion-3.x.x/genymotion-3.x.x-linux_x64.bin
chmod +x genymotion-3.x.x-linux_x64.bin
./genymotion-3.x.x-linux_x64.bin

# 게임 최적화 설정
# GPU 모드: Host GPU 사용
# RAM: 4GB 이상 할당
# CPU: 4 코어 이상 할당
```

### 🥉 3위: Android-x86 (직접 부팅, 최고 성능)

**특징:**
- 🔥 가장 빠른 성능 (네이티브 부팅)
- 💯 하드웨어 직접 액세스
- 🎮 게임 성능 최적화

**설치 방법:**
```bash
# ISO 다운로드
wget https://www.android-x86.org/releases/releasenote-9-0-r2

# USB 부팅 디스크 생성 또는 VM 설치
# VirtualBox에서 설치하면 됩니다
```

### 🏆 추가 옵션: Bliss OS (게임 특화)

**특징:**
- 🎯 게임에 특화된 Android 배포판
- 🖥️ 데스크톱 환경 최적화
- 🎮 키보드/마우스 지원 완벽

## ⚡ 성능 최적화 팁

### Waydroid 게임 성능 극대화

```bash
# 1. CPU 성능 모드 설정
echo performance | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor

# 2. 메모리 최적화
echo 1 | sudo tee /proc/sys/vm/drop_caches

# 3. Waydroid 전용 설정 파일 생성
cat > ~/.waydroid_gaming.sh << 'EOF'
#!/bin/bash

# 성능 모드 활성화
sudo cpupower frequency-set -g performance

# 메모리 정리
sudo sync && echo 3 | sudo tee /proc/sys/vm/drop_caches

# Waydroid 시작
waydroid session start

# 게임 최적화 props 설정
waydroid prop set persist.waydroid.oom_score -1000
waydroid prop set persist.waydroid.cpu_boost true

echo "게임 모드 활성화 완료!"
EOF

chmod +x ~/.waydroid_gaming.sh
```

### 멀티 인스턴스 설정 (여러 계정용)

```bash
# 여러 Waydroid 인스턴스 생성
sudo waydroid init -s GAPPS -f
sudo waydroid init -s GAPPS -f --work-profile

# 각 인스턴스별 설정
waydroid prop set persist.waydroid.width 720
waydroid prop set persist.waydroid.height 1280

# 두 번째 인스턴스
waydroid -P work prop set persist.waydroid.width 720
waydroid -P work prop set persist.waydroid.height 1280
```

## 🎮 Rise of Kingdoms 특화 설정

### Waydroid용 RoK 최적화

```bash
# Rise of Kingdoms 전용 프로파일
waydroid prop set persist.waydroid.width 1080
waydroid prop set persist.waydroid.height 1920
waydroid prop set persist.waydroid.fake_touch false
waydroid prop set persist.waydroid.fake_wifi false

# 게임 성능 향상
waydroid prop set debug.composition.type gpu
waydroid prop set debug.egl.hw 1
waydroid prop set debug.sf.hw 1

# 배터리 최적화 비활성화 (백그라운드 실행용)
waydroid prop set persist.waydroid.idle_timeout 0
```

### 자동화 친화적 설정

```python
import subprocess
import time

class WaydroidGameManager:
    def __init__(self):
        self.instances = []
        
    def create_gaming_instance(self, instance_name):
        """게임용 인스턴스 생성"""
        commands = [
            f"waydroid prop set persist.waydroid.width 1080",
            f"waydroid prop set persist.waydroid.height 1920", 
            f"waydroid prop set persist.waydroid.fake_touch false",
            f"waydroid prop set debug.composition.type gpu"
        ]
        
        for cmd in commands:
            subprocess.run(cmd.split())
            
    def start_instance(self, instance_name="default"):
        """인스턴스 시작"""
        subprocess.run(['waydroid', 'session', 'start'])
        time.sleep(5)
        
    def install_apk(self, apk_path):
        """APK 설치"""
        result = subprocess.run(['waydroid', 'app', 'install', apk_path])
        return result.returncode == 0
        
    def launch_app(self, package_name):
        """앱 실행"""
        subprocess.run(['waydroid', 'app', 'launch', package_name])

# 사용 예제
manager = WaydroidGameManager()
manager.create_gaming_instance("rok_main")
manager.start_instance()
manager.install_apk("./rise_of_kingdoms.apk")
manager.launch_app("com.lilithgames.roc.gp")
```

## 📊 성능 비교표

| 에뮬레이터 | 게임 성능 | 설치 난이도 | RAM 사용량 | GPU 가속 |
|------------|-----------|-------------|------------|-----------|
| Waydroid | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | 낮음 | 완벽 |
| Genymotion | ⭐⭐⭐⭐ | ⭐⭐ | 중간 | 좋음 |
| Android-x86 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 낮음 | 완벽 |
| Android Studio | ⭐⭐ | ⭐ | 높음 | 보통 |

## 🚨 추가 팁

### 1. 시스템 요구사항 최적화
```bash
# 커널 모듈 로드 확인
sudo modprobe binder_linux
sudo modprobe ashmem_linux

# 권한 설정
sudo usermod -a -G waydroid $USER
```

### 2. 네트워크 최적화
```bash
# DNS 최적화
waydroid prop set net.dns1 8.8.8.8
waydroid prop set net.dns2 8.8.4.4
```

### 3. 멀티태스킹 설정
```bash
# 백그라운드 앱 제한 해제
waydroid prop set persist.waydroid.background_apps unlimited
```

**결론적으로, Rise of Kingdoms 같은 게임을 위해서는 Waydroid가 가장 좋은 선택입니다.** 컨테이너 기반이라 오버헤드가 적고, GPU 가속이 완벽하며, 자동화 스크립트와의 호환성도 뛰어납니다.

설치나 설정 과정에서 문제가 있으시면 언제든 말씀해 주세요!