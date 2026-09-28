import persistence as db
from schemas import ItemUpdate


def update_item(id: str, payload: ItemUpdate):
    db.update_item(id, {'name': payload.name, 'completed': payload.completed})
    return db.get_item(id)
