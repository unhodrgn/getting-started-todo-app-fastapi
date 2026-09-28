import uuid

import persistence as db
from schemas import ItemCreate


def add_item(payload: ItemCreate):
    item = {
        'id': str(uuid.uuid4()),
        'name': payload.name,
        'completed': False,
    }

    db.store_item(item)
    return item
