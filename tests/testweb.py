from contextlib import closing
import os
from pathlib import Path
import socket
import sqlite3
import subprocess
import sys
import tempfile
import time
import unittest
import urllib.error
import urllib.parse
import urllib.request


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


class WebTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory()
        cls.db = Path(cls.temporary.name) / 'task.db'
        cls.log = open(Path(cls.temporary.name) / 'server.log', 'w+')
        with socket.socket() as sock:
            sock.bind(('127.0.0.1', 0))
            cls.port = sock.getsockname()[1]
        cls.url = f'http://127.0.0.1:{cls.port}'
        cls.opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect())
        cls.start()

    @classmethod
    def start(cls):
        environment = dict(os.environ, TASK_DB_URL='sqlite:///' + str(cls.db))
        cls.process = subprocess.Popen([sys.executable, '-m', 'uvicorn', 'app:app', '--host', '127.0.0.1', '--port', str(cls.port)], cwd=Path(__file__).resolve().parent.parent, env=environment, stdout=cls.log, stderr=subprocess.STDOUT)
        for _ in range(100):
            try:
                cls.opener.open(cls.url, timeout=1).close()
                return
            except (OSError, urllib.error.URLError):
                if cls.process.poll() is not None:
                    cls.log.seek(0)
                    raise RuntimeError(cls.log.read())
                time.sleep(0.05)
        cls.process.terminate()
        cls.process.wait(timeout=5)
        cls.log.flush()
        cls.log.seek(0)
        raise RuntimeError('server startup timeout\n' + cls.log.read())

    @classmethod
    def tearDownClass(cls):
        cls.process.terminate()
        cls.process.wait(timeout=5)
        cls.log.close()
        cls.temporary.cleanup()

    def setUp(self):
        with closing(sqlite3.connect(self.db)) as db, db:
            db.execute('DELETE FROM task')

    def request(self, path, data=None):
        request = urllib.request.Request(self.url + path, data=urllib.parse.urlencode(data).encode() if data is not None else None)
        try:
            response = self.opener.open(request, timeout=3)
        except urllib.error.HTTPError as error:
            response = error
        with response:
            return response.code, response.headers, response.read().decode()

    def test_crud_prg_and_refresh(self):
        status, headers, body = self.request('/tasks', {'title': '첫 할 일', 'description': '정리'})
        self.assertEqual(status, 303)
        path = headers['Location']
        for _ in range(3):
            self.assertIn('첫 할 일', self.request(path)[2])
        with closing(sqlite3.connect(self.db)) as db, db:
            self.assertEqual(db.execute('SELECT COUNT(*) FROM task').fetchone()[0], 1)
        self.assertEqual(self.request(path + '/edit', {'title': '수정', 'description': '변경 내용'})[0], 303)
        self.assertIn('변경 내용', self.request(path)[2])
        self.assertEqual(self.request(path + '/delete', {})[0], 303)
        self.assertEqual(self.request(path)[0], 404)

    def test_all_views_and_escaped_content(self):
        status, headers, body = self.request('/')
        self.assertEqual(status, 200)
        self.assertIn('href="/tasks"', body)
        self.assertIn('href="/tasks/new"', body)
        self.assertIn('name="title"', self.request('/tasks/new')[2])
        status, headers, body = self.request('/tasks', {'title': '<script>alert(1)</script>', 'description': 'safe'})
        path = headers['Location']
        self.assertIn('&lt;script&gt;', self.request(path)[2])
        self.assertIn('할 일 수정', self.request(path + '/edit')[2])
        self.assertIn('&lt;script&gt;', self.request('/tasks')[2])

    def test_validation_and_missing_data(self):
        self.assertEqual(self.request('/tasks', {'title': ' ', 'description': 'body'})[0], 400)
        self.assertEqual(self.request('/tasks', {'title': 'a' * 101, 'description': 'body'})[0], 400)
        status, headers, body = self.request('/tasks/9999')
        self.assertEqual(status, 404)
        self.assertIn('찾을 수 없습니다', body)
        self.assertEqual(self.request('/tasks/9999/delete', {})[0], 404)

    def test_database_survives_server_restart(self):
        status, headers, body = self.request('/tasks', {'title': '재시작', 'description': '유지'})
        path = headers['Location']
        self.process.terminate()
        self.process.wait(timeout=5)
        self.__class__.start()
        self.assertIn('재시작', self.request(path)[2])

    def test_search_literal_wildcards_and_empty_result(self):
        for title in ['예산 100%_완료', '예산 1000완료', '운동']:
            self.assertEqual(self.request('/tasks', {'title': title, 'description': '내용'})[0], 303)
        body = self.request('/tasks?' + urllib.parse.urlencode({'q': ' %_ '}))[2]
        self.assertIn('예산 100%_완료', body)
        self.assertNotIn('예산 1000완료', body)
        self.assertNotIn('운동</a>', body)
        self.assertIn('맞는 할 일이 없습니다', self.request('/tasks?q=missing')[2])
        self.assertIn('운동</a>', self.request('/tasks?q=')[2])
        self.assertEqual(self.request('/tasks?q=' + 'a' * 101)[0], 400)


if __name__ == '__main__':
    unittest.main()
