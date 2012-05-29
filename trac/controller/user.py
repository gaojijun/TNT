import trac.model.user as tmu
import web
import markdown
import copy

render = None

def updateRender():
    t_globals = {
        'datestr': web.datestr,
        'markdown': markdown.markdown,
        'context': web.ctx.session
    }
    global render
    render = web.template.render(
        'templates/user',
        base='base',
        globals=t_globals
    )

def adminRequired(f):
    def _f(*args):
        if web.ctx.session.login and\
           web.ctx.session.user.isadmin:
            updateRender()
            return f(*args)
        else:
            raise web.seeother('/login')
    return _f

class Index:
    @adminRequired
    def GET(self):
        users = tmu.get_users()
        return render.index(users)

class View:
    @adminRequired
    def GET(self, id):
        user = tmu.get_user_by_id(id)
        if not user:
            raise web.seeother('/new?url=%s' % web.websafe(url))
        return render.view(user)

class New:
    def not_user_exists(username):
        return not bool(tmu.get_user_by_name(username))

    user_exists_validator = web.form.Validator(
        'User already exists', not_user_exists)

    form = web.form.Form(
        web.form.Textbox('username', web.form.notnull, user_exists_validator,
            size=30,
            description="User name:"),
        web.form.Password('password', web.form.notnull, 
            size=30,
            description="Password"),
        web.form.Textbox('email', web.form.notnull,
            size=30,
            description="Email:"),
        web.form.Checkbox('isadmin',
            value='1',
            description="Is admin:"),
        web.form.Button('Create user'),
    )

    @adminRequired
    def GET(self):
        form = self.form()
        return render.new(form)

    @adminRequired
    def POST(self):
        form = self.form()
        if not form.validates():
            return render.new(form)
        fields = copy.copy(form.d)
        del fields['Create user']
        tmu.new_user(**fields)
        raise web.seeother('/user')

class Delete:
    @adminRequired
    def GET(self, id):
        tmu.del_user(int(id))
        raise web.seeother('/user')

class Edit:

    form = web.form.Form(
        web.form.Textbox('username', web.form.notnull,
            size=30,
            readonly='true',
            description="User name:"),
        web.form.Password('password', web.form.notnull, 
            size=30,
            description="Password"),
        web.form.Textbox('email', web.form.notnull,
            size=30,
            description="Email:"),
        web.form.Checkbox('isadmin',
            value='1',
            description="Is admin:"),
        web.form.Checkbox('newwiki',
            value='1',
            description="New wiki:"),
        web.form.Checkbox('editwiki',
            value='1',
            description="Edit wiki:"),
        web.form.Checkbox('deletewiki',
            value='1',
            description="Delete wiki:"),
        web.form.Checkbox('newticket',
            value='1',
            description="New ticket:"),
        web.form.Checkbox('editticket',
            value='1',
            description="Edit ticket:"),
        web.form.Checkbox('deleteticket',
            value='1',
            description="Delete ticket:"),
        web.form.Button('Edit user'),
    )

    @adminRequired
    def GET(self, id):
        user = tmu.get_user_by_id(int(id))
        form = self.form()
        form.fill(user)
        return render.edit(user, form)


    @adminRequired
    def POST(self, id):
        form = self.form()
        user = tmu.get_user_by_id(int(id))
        if not form.validates():
            return render.edit(user, form)
        fields = copy.copy(form.d)
        del fields['Edit user']
        tmu.update_user(int(id),**fields)
        raise web.seeother('/user')

