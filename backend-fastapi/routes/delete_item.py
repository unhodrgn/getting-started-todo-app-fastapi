from fastapi import Response

import persistence as db


def delete_item(id: str):
    db.remove_item(id)
    # res.sendStatus(200) in deleteItem.js replies with the plain-text status
    # message rather than JSON, so mirror that exactly.
    return Response(content='OK', status_code=200, media_type='text/plain')
