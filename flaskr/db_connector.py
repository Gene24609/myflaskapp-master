import sqlite3  

from flask import current_app, g

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )

        #if not have this result after execute querry only can access through index
        #example:    result = cur.execute("SELECT username, password FROM users WHERE username = ?", [username]).fetchone()
        #            data = result
        #            password = data[1] #get password                Note:   if has it is  password = data['password']  
        g.db.row_factory = sqlite3.Row

    return g.db

#@app.teardown_appcontext
def close_db():
    db = g.pop('db', None)
    if db is not None:
        db.close()



    
