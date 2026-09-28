import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

import persistence as db
from routes.add_item import add_item
from routes.delete_item import delete_item
from routes.get_greeting import get_greeting
from routes.get_items import get_items
from routes.update_item import update_item

STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')


@asynccontextmanager
async def lifespan(app: FastAPI):
    db.init()
    yield
    db.teardown()


app = FastAPI(lifespan=lifespan)

app.get('/api/greeting')(get_greeting)
app.get('/api/items')(get_items)
app.post('/api/items')(add_item)
app.put('/api/items/{id}')(update_item)
app.delete('/api/items/{id}')(delete_item)

# Mounted last so the /api/* routes above take precedence over the
# catch-all static file server, equivalent to express.static() in index.js.
app.mount('/', StaticFiles(directory=STATIC_DIR, html=True), name='static')
