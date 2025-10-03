- 현재 jnj-android는 ubuntu xfce 환경에서 android 앱을 자동화 하는 범용 프로젝트입니다.
- 우선 RoK 앱에 대한 자동화를 구현 중에 있지만, 다른 앱의 사용도 염두에 두어야 합니다.

- backend에서는 android 관련된 코드(adb 제어(실행, 중지, 실행 확인 등)), waydroid 사용에 관련된 코드(adb 제어, waydroid 실행, 중지 등)와 RoK 게임 관련 코드가 폴더 단위에서 분리되어 있어합니다
- android, waydroid, rok 의 서버 폴더를 생성하고, 코드들을 이동해주세요.
- waydroid에서 playstore 관련 내용(로그인, ...), waydroid 제어(실행, 중지, 실행 확인 등) 등도 파일 단위로 분리되어야 합니다.
- rok 폴더에서도 Rok 앱 실행/진입, RoK 내 미션.액션 관련된 내용은 파일 단위에서 분리되어야 합니다.

===



===

- /home/sam/JnJ/developments/jnj-android/emulator 디렉토리에 내용과 /home/sam/JnJ/developments/waydroid_script 디렉토리의 내용과 중복되어 있는지 확인후,
- 기존 내용 중 중복되는 내용은 삭제하고 기존 내용은 /home/sam/JnJ/developments/jnj-android/emulator/legacy 로 모두 이동하고,
- /home/sam/JnJ/developments/waydroid_script 를 
/home/sam/JnJ/developments/jnj-android/emulator/waydroid 로 이동합니다.
  - 다만 /home/sam/JnJ/developments/waydroid_script 에 있던 python 파일들은 /home/sam/JnJ/developments/jnj-android/backend/python/src/utils/waydroid로 이동해야 겠네요.

===

backend에 있는 python 코드들은 uv 로 관리합니다. 아래의 내용도 uv로 패키지들을 설치하고, 삭제해주세요.

/home/sam/JnJ/developments/jnj-android/backend/python/src/utils/waydroid/requirements.txt

===

 /home/sam/JnJ/developments/jnj-android/backend/python/src/utils/waydroid 에 있는 코드들의 기능은 어떤 것들인가요?


===

서버 코드 /home/sam/JnJ/developments/jnj-android/backend/python/src/servers/main.py 에서 엔드포인트에 포함된 '/game' 는 '/rok'로 변경해주세요.

===

 /home/sam/JnJ/developments/jnj-android/backend/python/src/waydroid, /home/sam/JnJ/developments/jnj-android/backend/python/src/utils/waydroid, /home/sam/JnJ/developments/jnj-android/backend/python/src/utils 흩어져 있는 weston 관련 코드들을 /home/sam/JnJ/developments/jnj-android/backend/python/src/utils/waydroid 에서 통합 관리해주세요.

/home/sam/JnJ/developments/jnj-android/backend/python/src/utils 에 android, rok 폴더를 생성하고, /home/sam/JnJ/developments/jnj-android/backend/python/src/utils 에 있는 코드 중 adb 관련 코드들은 android 폴더로, rok 관련 코드(game_controller.py -> rok_controller.py 변경) 들은 rok 폴더로 이동해주세요.


===

- weston/start, waydroid/start 가 잘 작동됩니다.
- 그런데, weston/status endpoint의 아래와 같은 결과에서 단순히 "running" 에 대해서만 t/f를 확인하지 않고,
weston 창(홈 화면)의 상태를 세분화해주세요. 이를 위해서는 상태별로 홈화면의 특징적인 변화를 확인하는 로직이 있어야겠네요.
현재 lock, black에 대해서는 확인하는 로직이 있는 것으로 알고 있는데...

- empty: waydroid가 시작하지 않은 상태
- loading: waydroid가 로딩중인 상태
- loaded: waydroid 로딩이 완료된 상태 / 홈 화면에 구글, 플레이스토어 아이콘 및 앱 아이콘들이 로딩된 상태

- lock: weston/check-lock 에서 확인하는 화면에 락이 걸린 상태(화면 가운데 부분에 초록색 원이 있는)
- black: content 영역이 검은색으로 된 상태(휴식 상태?)

===

토끼 아이콘은 weston 창 밖에 있는 것으로 보이는데요? 그리고 ui의 위치, 색상에 대한 정보는 /home/sam/JnJ/developments/jnj-android/database/json/ui_weston.json 에 넣어서 불러오도록 해주세요. json 파일을 변경하면 그 설정이 바로 적용될 수 있도록 해주세요. weston 창의 초기 위치 0, 0 으로 하드 코딩하지 않고, ui_weston.json 에 있는 default_geometry.x, y 값을 사용해주세요

===

weston/status는 기능이 성공적입니다. 고마워요.

이제 weston/status를 이용하여 rok/start, restart 를 weston 상태에 따라 실행하도록 수정해주세요.

> status의 running 값에 따라,
- weston running=false => weston/start
- waydroid runnig=false => waydroid/start

> screen_state
- empty: waydroid/start
- loading: loaded 때까지 기다림
- black: 탭 -> lock인지 확인 -> 탭 -> loaded 인지 확인
- lock: 탭-> loaded 인지 확인

===

rok/start에서 RoK 로딩 화면 도중에 
검은 스크린에 'No notifications' 메시지가 뜨는 화면으로 전환됩니다.
이렇게 화면이 전환되면, 게임 화면으로 진입하려면, 하단의 뒤로 가기 버튼을 눌러야 합니다.
화면이 전환되는 원인을 파악하고 원인 제거를 하거나,
항상 화면이 전환되는 것이라면 하단의 뒤로 가기 버튼을 누르도록 해야 합니다.