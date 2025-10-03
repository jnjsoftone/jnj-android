## 앱 기본 구성

- OS: utuntu XFCE
- 에뮬레이터: Waydroid
- 스케줄 작업 cron

- backend:
  - python
    - 화면 인식 / 화면 조작(마우스, 키보드)

- graphql
  - client에서 action 요청(query, mutation) -> backend(python) action 실행

- frontend
  - 계정 관리 / 캐릭터 관리 / 왕국.연맹 관리
  - 일정 관리(게임내 action, task)
  - 게임 매뉴얼 관리

- database
  - 게임 관련 데이터 관리(게임내 설정, 사용자 계정.캐릭터 등 데이터)
    - accounts
    - charactors
    - actions
    - missions
    - buildings
    - tasks
    - actions
    - ...
  - postgresql
  - /home/sam/JnJ/developments/jnj-android/.env
