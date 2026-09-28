import os
import socket
import threading
import time

import pymysql
import pymysql.cursors

HOST = os.environ.get('MYSQL_HOST')
HOST_FILE = os.environ.get('MYSQL_HOST_FILE')
USER = os.environ.get('MYSQL_USER')
USER_FILE = os.environ.get('MYSQL_USER_FILE')
PASSWORD = os.environ.get('MYSQL_PASSWORD')
PASSWORD_FILE = os.environ.get('MYSQL_PASSWORD_FILE')
DB = os.environ.get('MYSQL_DB')
DB_FILE = os.environ.get('MYSQL_DB_FILE')

_conn = None
# A single pymysql connection isn't safe for concurrent use across the
# threadpool FastAPI runs sync routes in, so serialize access like the
# Node version's connection pool effectively does per-query.
_lock = threading.Lock()


def _read_secret(value, file_path):
    if file_path:
        with open(file_path) as f:
            return f.read().strip()
    return value


def _wait_port(host, port, timeout=10):
    deadline = time.time() + timeout
    last_err = None
    while time.time() < deadline:
        try:
            with socket.create_connection((host, port), timeout=1):
                return
        except OSError as err:
            last_err = err
            time.sleep(0.5)
    raise TimeoutError(f'Timed out waiting for {host}:{port}') from last_err


def init():
    global _conn

    host = _read_secret(HOST, HOST_FILE)
    user = _read_secret(USER, USER_FILE)
    password = _read_secret(PASSWORD, PASSWORD_FILE)
    database = _read_secret(DB, DB_FILE)

    _wait_port(host, 3306, timeout=10)

    _conn = pymysql.connect(
        host=host,
        user=user,
        password=password,
        database=database,
        charset='utf8mb4',
        autocommit=True,
        cursorclass=pymysql.cursors.DictCursor,
    )

    with _conn.cursor() as cursor:
        cursor.execute(
            'CREATE TABLE IF NOT EXISTS todo_items '
            '(id varchar(36), name varchar(255), completed boolean) DEFAULT CHARSET utf8mb4'
        )

    print(f'Connected to mysql db at host {HOST}')


def teardown():
    _conn.close()


def _row_to_item(row):
    # MySQL's `boolean` is a tinyint, so pymysql hands back 0/1. Coerce to a
    # real bool so the JSON response carries true/false, matching mysql.js.
    return dict(row, completed=bool(row['completed']))


def get_items():
    with _lock:
        _conn.ping(reconnect=True)
        with _conn.cursor() as cursor:
            cursor.execute('SELECT * FROM todo_items')
            rows = cursor.fetchall()
    return [_row_to_item(row) for row in rows]


def get_item(id):
    with _lock:
        _conn.ping(reconnect=True)
        with _conn.cursor() as cursor:
            cursor.execute('SELECT * FROM todo_items WHERE id=%s', (id,))
            rows = cursor.fetchall()
    if not rows:
        return None
    return _row_to_item(rows[0])


def store_item(item):
    with _lock:
        _conn.ping(reconnect=True)
        with _conn.cursor() as cursor:
            cursor.execute(
                'INSERT INTO todo_items (id, name, completed) VALUES (%s, %s, %s)',
                (item['id'], item['name'], 1 if item['completed'] else 0),
            )


def update_item(id, item):
    with _lock:
        _conn.ping(reconnect=True)
        with _conn.cursor() as cursor:
            cursor.execute(
                'UPDATE todo_items SET name=%s, completed=%s WHERE id=%s',
                (item['name'], 1 if item['completed'] else 0, id),
            )


def remove_item(id):
    with _lock:
        _conn.ping(reconnect=True)
        with _conn.cursor() as cursor:
            cursor.execute('DELETE FROM todo_items WHERE id = %s', (id,))
