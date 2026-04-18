# 말씀의 숨결 · 설교문 생성기

성경 본문이나 주제를 입력하면 김병삼 목사 스타일을 참고한 설교문을 생성하는 Flask 웹 애플리케이션입니다. Claude Opus 4.7 API를 사용합니다.

## GitHub Codespaces에서 바로 실행하기 (권장)

가장 쉬운 방법입니다. 로컬 설치 없이 브라우저에서 바로 실행됩니다.

### 1. Codespace 시크릿 등록 (최초 1회)

1. GitHub에서 본인 계정의 **Settings → Codespaces → Codespaces secrets** 로 이동
2. **New secret** 클릭하여 추가:
   - 이름: `ANTHROPIC_API_KEY`, 값: 본인의 Anthropic API 키
   - 이름: `FLASK_SECRET_KEY`, 값: 임의의 긴 문자열 (예: `openssl rand -hex 32`)
3. **Repository access** 에서 본 저장소를 선택

### 2. Codespace 시작

1. 저장소 메인 페이지에서 초록색 **Code** 버튼 → **Codespaces** 탭 → **Create codespace on `claude/bible-sermon-generator-wGKAe`**
2. 컨테이너가 빌드되며 자동으로 의존성을 설치합니다 (1~2분 소요)
3. 빌드가 끝나면 `python app.py`가 자동 실행되고, 5000번 포트가 열립니다
4. 우측 하단 알림 또는 **PORTS** 탭에서 미리 보기 URL을 클릭하여 사용

### 3. 종료

- 사용을 마치면 **Codespaces 페이지**에서 해당 codespace를 **Stop** 또는 **Delete**
- 무료 사용량(월 60시간/Pro 플랜은 90시간) 안에서 자유롭게 활용

## 로컬에서 실행하기

```bash
git clone <repository-url>
cd psh1968
git checkout claude/bible-sermon-generator-wGKAe

pip install -r requirements.txt
cp .env.example .env
# .env 파일을 열어 ANTHROPIC_API_KEY를 입력

python app.py
# http://localhost:5000 접속
```

## 외부 호스팅 옵션

장기간 운영하려면 다음 플랫폼 중 하나에 GitHub 저장소를 연결하면 됩니다:

| 플랫폼 | 무료 티어 | 한 줄 요약 |
|--------|----------|-----------|
| **Render** | 있음 (sleep) | GitHub 연결 → Web Service 생성 → 환경변수 등록 |
| **Railway** | $5 크레딧 | GitHub 연결 → Deploy → 환경변수 등록 |
| **Fly.io** | 있음 | `fly launch` 후 `fly secrets set ANTHROPIC_API_KEY=...` |
| **Heroku** | 유료 | `Procfile` 추가 후 GitHub 연결 |

어느 플랫폼에서든 시작 명령은 `python app.py` 또는 `gunicorn app:app` 입니다.
환경변수 `ANTHROPIC_API_KEY`, `FLASK_SECRET_KEY`, `PORT` 만 등록하면 동작합니다.

## 주요 파일

- `app.py` — Flask 백엔드. 시스템 프롬프트와 SSE 스트리밍 엔드포인트
- `templates/index.html` — UI
- `static/style.css`, `static/script.js` — 스타일과 클라이언트 로직
- `.devcontainer/devcontainer.json` — Codespaces 설정
- `.github/workflows/ci.yml` — 푸시 시 Python 구문 검증
