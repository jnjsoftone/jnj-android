## 서버 시작

```sh
cd /home/sam/JnJ/developments/jnj-android/backend/python && uv run python src/servers/main.py
```

## dashboard

```
http://192.168.0.25:8000/docs
http://14.34.23.70:8000/docs
```

```sh

```
POST /api/config/reload: JSON 파일 수정 후 즉시 reload
테스트 방법:
JSON 파일 수정 (예: unlock button y 좌표 변경)
curl -X POST http://14.34.23.70:8000/api/config/reload