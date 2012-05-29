import web

db = web.database(dbn='mysql', db='webpy', user='root')

def get_users():
    return db.select('users', order='id DESC')

def get_user_by_name(name):
    try:
        return db.select('users', where='username=$name', vars=locals())[0]
    except IndexError:
        return None

def get_user_by_id(id):
    try:
        return db.select('users', where='id=$id', vars=locals())[0]
    except IndexError:
        return None

def checkPassword(username, password):
    try:
        return db.select('users',
        where='username=$username and password=$password', vars=locals())[0]
    except IndexError:
        return None

def new_user(**args):
    db.insert('users', **args)

def del_user(id):
    db.delete('users', where="id=$id", vars=locals())

def update_user(id, **args):
    db.update('users', where="id=$id", vars=locals(), **args)
