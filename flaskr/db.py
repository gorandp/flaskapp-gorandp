from flask import current_app, g

from . import mongo


def get_db() -> mongo.DB:
    if 'db' not in g:
        g.db = mongo.connect(
            DB_CONNECTION_STRING=current_app.config['DB_CONNECTION_STRING']
        )
    return g.db
