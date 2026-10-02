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

## 등록과 수정의 HTTP 응답

```bash
$ curl --noproxy '*' -sS -i http://127.0.0.1:8000/tasks --data-urlencode 'title=과제 정리' --data-urlencode 'description=실행 결과 확인'
HTTP/1.1 303 See Other
date: Wed, 30 Sep 2026 13:29:05 GMT
server: uvicorn
content-length: 0
location: /tasks/1


$ curl --noproxy '*' -sS http://127.0.0.1:8000/tasks/1
<!doctype html>
<html lang="ko">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>할 일 관리</title></head>
<body>
<nav><a href="/">홈</a> | <a href="/tasks">할 일 목록</a> | <a href="/tasks/new">할 일 등록</a></nav>
<main>
<h1>과제 정리</h1>
<dl><dt>ID</dt><dd>1</dd><dt>제목</dt><dd>과제 정리</dd><dt>내용</dt><dd><pre>실행 결과 확인</pre></dd><dt>작성일시 (UTC)</dt><dd>2026-09-30 13:29:06.576385</dd></dl>
<p><a href="/tasks/1/edit">수정</a> <a href="/tasks">목록으로</a></p>
<form method="post" action="/tasks/1/delete"><button type="submit">삭제</button></form>
</main>
</body>
</html>
$ curl --noproxy '*' -sS -i http://127.0.0.1:8000/tasks/1/edit --data-urlencode 'title=과제 검토' --data-urlencode 'description=README 확인'
HTTP/1.1 303 See Other
date: Wed, 30 Sep 2026 13:29:05 GMT
server: uvicorn
content-length: 0
location: /tasks/1


$ sqlite3 -header -column task.db 'SELECT id,title,description,created_at FROM task;'
id  title  description  created_at                
--  -----  -----------  --------------------------
1   과제 검토  README 확인    2026-09-30 13:29:06.576385

```

POST는 Location과 303을 반환하고 브라우저는 GET으로 상세 화면을 요청합니다. task.db를 직접 조회해 수정된 제목과 내용을 확인했습니다.

## 요청 흐름과 화면

| 경로 | 역할 |
|---|---|
| GET / | 목적과 목록/등록 링크 |
| GET /tasks | 할 일 목록 |
| GET /tasks/new | 등록 폼 |
| POST /tasks | 등록 후 상세로 303 |
| GET /tasks/{id} | 전체 필드와 수정/삭제/목록 링크 |
| GET /tasks/{id}/edit | 수정 폼 |
| POST /tasks/{id}/edit | 수정 후 상세로 303 |
| POST /tasks/{id}/delete | 삭제 후 목록으로 303 |

Chrome에서 localhost:8000의 홈 화면과 링크를 확인했습니다. 목록, 상세, 등록과 수정 폼은 Jinja2 TemplateResponse를 반환합니다. 등록과 수정 폼의 필수값은 브라우저와 서버에서 검증하며, 빈 제목이나 내용은 저장하지 않습니다. 없는 데이터는 404 안내 화면을 출력합니다.

라우터는 Form()으로 전달된 제목과 내용을 받고 서비스에 넘깁니다. 서비스는 필수값과 길이를 검사하며 저장소는 SQLAlchemy Session의 add/commit/refresh/get/delete로 DB에 접근합니다. 조회는 SELECT, 새 객체 add 후 commit은 INSERT, 수정된 객체의 commit은 UPDATE, delete 후 commit은 DELETE에 대응합니다. 서비스는 TaskView로 화면에 필요한 값을 반환해 ORM 객체를 라우터의 응답 모델로 사용하지 않습니다.

GET은 화면 조회에 사용하고 상태를 바꾸는 요청은 POST로 분리했습니다. POST 직후 303은 다음 요청을 GET으로 바꾸므로 결과 화면에서 새로고침해도 등록/수정/삭제가 반복되지 않습니다. 빠른 이중 클릭을 막는 멱등 키까지 제공하는 방식은 아닙니다.

모델은 id, 제목, 내용, 작성일시를 가집니다. 작성일시는 UTC 기준입니다. DB 세션은 Depends(get_db)에서 요청마다 생성하고 종료합니다. 라우터에 DB와 검증을 모두 넣으면 화면 처리와 저장 정책을 각각 테스트하거나 바꾸기 어렵습니다.

PostgreSQL로 옮기려면 DB URL, DB 드라이버와 운영 설정을 바꾸고 타입/쿼리 차이를 검증해야 합니다. 카테고리 관계를 추가하려면 모델과 FK/relationship, 저장소 조회와 DTO, 관계 선택 폼이 바뀝니다. REST API로 바꾸면 라우터의 폼 수신과 TemplateResponse를 JSON 요청/응답으로 변경하며 서비스와 저장소 책임은 유지할 수 있습니다.

템플릿 구성은 [FastAPI 문서](https://fastapi.tiangolo.com/advanced/templates/), DB 세션은 [SQLAlchemy 문서](https://docs.sqlalchemy.org/en/20/orm/session_basics.html)를 참고했습니다.

## 최종 회귀 확인

```bash
$ .venv/bin/python -W error::ResourceWarning -m unittest discover -s tests -v
test_all_views_and_escaped_content (testweb.WebTests.test_all_views_and_escaped_content) ... ok
test_crud_prg_and_refresh (testweb.WebTests.test_crud_prg_and_refresh) ... ok
test_database_survives_server_restart (testweb.WebTests.test_database_survives_server_restart) ... ok
test_validation_and_missing_data (testweb.WebTests.test_validation_and_missing_data) ... ok

----------------------------------------------------------------------
Ran 4 tests in 2.505s

OK
```

테스트용 SQLite 연결을 명시적으로 닫도록 수정했습니다. 리소스 경고를 오류로 처리한 검사에서도 같은 4개 시나리오가 통과했습니다.

## 보너스: 제목 검색

```bash
$ .venv/bin/python -W error::ResourceWarning -m unittest discover -s tests -v
test_all_views_and_escaped_content (testweb.WebTests.test_all_views_and_escaped_content) ... ok
test_crud_prg_and_refresh (testweb.WebTests.test_crud_prg_and_refresh) ... ok
test_database_survives_server_restart (testweb.WebTests.test_database_survives_server_restart) ... ok
test_search_literal_wildcards_and_empty_result (testweb.WebTests.test_search_literal_wildcards_and_empty_result) ... ok
test_validation_and_missing_data (testweb.WebTests.test_validation_and_missing_data) ... ok

----------------------------------------------------------------------
Ran 5 tests in 2.855s

OK
```

GET /tasks?q=검색어로 제목을 검색합니다. 빈 검색어는 전체 목록이며 조건은 폼에 유지됩니다. SQLAlchemy contains(autoescape=True)로 %와 _를 LIKE 와일드카드가 아닌 문자로 처리합니다. 기존 CRUD, 입력 검증, DB 재시작과 검색 검사 5개를 통과했습니다.
