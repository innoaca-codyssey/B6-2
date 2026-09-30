# B6-2: 글을 쓰고 보고 고치고 지울 수 있는 게시판형 웹 서비스 만들기

할 일의 제목과 내용을 등록, 조회, 수정, 삭제하는 FastAPI 웹 앱입니다. Jinja2 화면과 SQLite 저장을 사용하며 POST 후 303으로 리다이렉트합니다.

## 실행 방법

Python 3.10 이상에서 실행합니다.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
uvicorn app:app --host 127.0.0.1 --port 8000
```

브라우저에서 http://localhost:8000 을 엽니다. task.db는 프로젝트 루트에 생성됩니다. 다른 DB 파일을 사용하려면 TASK_DB_URL에 SQLAlchemy SQLite URL을 지정합니다.

## 실행 환경

```bash
$ python3 --version
Python 3.14.7
```

macOS arm64에 미션 전용 가상환경을 생성합니다.
