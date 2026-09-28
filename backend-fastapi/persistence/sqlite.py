import os
import sqlite3
import threading

LOCATION = os.environ.get('SQLITE_DB_LOCATION', '/etc/todos/todo.db')

_conn = None
# FastAPI runs sync path functions in a threadpool, so guard the shared
# connection the same way a single-writer sqlite3 connection needs to be.
_lock = threading.Lock()


def init():
    global _conn

    dir_name = os.path.dirname(LOCATION)
    if dir_name and not os.path.exists(dir_name):
        os.makedirs(dir_name, exist_ok=True)

    _conn = sqlite3.connect(LOCATION, check_same_thread=False)
    _conn.execute(
        'CREATE TABLE IF NOT EXISTS todo_items (id varchar(36), name varchar(255), completed boolean)'
    )
    _conn.commit()

    if os.environ.get('NODE_ENV') != 'test':
        print(f'Using sqlite database at {LOCATION}')


def teardown():
    _conn.close()


def _row_to_item(row):
    return {
        'id': row[0],
        'name': row[1],
        'completed': bool(row[2]),
    }


def get_items():
    with _lock:
        rows = _conn.execute('SELECT * FROM todo_items').fetchall()
    return [_row_to_item(row) for row in rows]


def get_item(id):
    with _lock:
        rows = _conn.execute('SELECT * FROM todo_items WHERE id=?', (id,)).fetchall()
    return _row_to_item(rows[0]) if rows else None


def store_item(item):
    with _lock:
        _conn.execute(
            'INSERT INTO todo_items (id, name, completed) VALUES (?, ?, ?)',
            (item['id'], item['name'], 1 if item['completed'] else 0),
        )
        _conn.commit()


def update_item(id, item):
    with _lock:
        _conn.execute(
            'UPDATE todo_items SET name=?, completed=? WHERE id = ?',
            (item['name'], 1 if item['completed'] else 0, id),
        )
        _conn.commit()


def remove_item(id):
    with _lock:
        _conn.execute('DELETE FROM todo_items WHERE id = ?', (id,))
        _conn.commit()
