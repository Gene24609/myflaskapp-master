import sqlite3  

from flask import current_app, g

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        return g.db
    else:
        return g.db

@app.teardown_appcontext
def close_db():
    db = g.pop('db', None)
    if db is not None:
            db.close()



    
