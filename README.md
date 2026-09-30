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

## 패키지 설치

```bash
Resolved 18 packages in 1.04s
Downloading pydantic-core (1.8MiB)
Downloading sqlalchemy (2.3MiB)
 Downloaded pydantic-core
 Downloaded sqlalchemy
Prepared 18 packages in 1.42s
Installed 18 packages in 67ms
 + annotated-doc==0.0.5
 + annotated-types==0.8.0
 + anyio==4.15.1
 + click==8.5.0
 + fastapi==0.142.2
 + h11==0.16.0
 + idna==3.20
 + jinja2==3.1.6
 + markupsafe==3.0.3
 + opentelemetry-api==1.45.0
 + pydantic==2.13.5
 + pydantic-core==2.46.5
 + python-multipart==0.0.32
 + sqlalchemy==2.1.1
 + starlette==1.7.0
 + typing-extensions==4.16.0
 + typing-inspection==0.4.4
 + uvicorn==0.54.0
```

미션 전용 .venv에 설치했습니다. 아래 주요 패키지 버전을 requirements.txt에 고정합니다.

## CRUD와 저장 유지

```bash
$ .venv/bin/python -m unittest discover -s tests -v
test_all_views_and_escaped_content (testweb.WebTests.test_all_views_and_escaped_content) ... ok
test_crud_prg_and_refresh (testweb.WebTests.test_crud_prg_and_refresh) ... ok
test_database_survives_server_restart (testweb.WebTests.test_database_survives_server_restart) ... ok
test_validation_and_missing_data (testweb.WebTests.test_validation_and_missing_data) ... ok

----------------------------------------------------------------------
Ran 4 tests in 4.544s

OK
```

테스트 서버에 HTTP 요청을 보내 등록/수정/삭제의 303 응답, GET 새로고침의 중복 없음, 입력 검증과 HTML 이스케이프, 없는 데이터 안내, 서버 재시작 후 DB 유지를 검사했습니다.
