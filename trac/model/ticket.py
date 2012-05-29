import web
# ticket model

db = web.database(dbn='mysql', db='webpy', user='root')

def get_tickets():
    return db.select('tickets', order='id DESC')

def get_ticket_by_id(id):
    try:
        return db.select('tickets', where='id=$id', vars=locals())[0]
    except IndexError:
        return None

def get_changes_by_id(id):
    return db.select('changes', where='ticketId=$id', vars=locals())

def new_ticket(**args):
    id = db.insert('tickets', **args)
    return id

def new_change(**args):
    id = db.insert('changes', **args)
    return id

def del_ticket(id):
    db.delete('tickets', where="id=$id", vars=locals())

def update_ticket(id, **args):
    db.update('tickets', where="id=$id", vars=locals(), **args)
