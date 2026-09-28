import os

# Same adapter pattern as persistence/index.js: MySQL if MYSQL_HOST is set,
# otherwise fall back to SQLite. Both modules expose an identical interface.
if os.environ.get('MYSQL_HOST'):
    from . import mysql as _impl
else:
    from . import sqlite as _impl

init = _impl.init
teardown = _impl.teardown
get_items = _impl.get_items
get_item = _impl.get_item
store_item = _impl.store_item
update_item = _impl.update_item
remove_item = _impl.remove_item
