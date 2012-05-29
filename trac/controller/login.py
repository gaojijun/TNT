import web
import markdown
import trac.model.user as tmu

t_globals = {
    'datestr': web.datestr,
    'markdown': markdown.markdown
}

render = web.template.render(
    'templates/login',
    # base='base',
    globals=t_globals
)

class Login:
    form = web.form.Form(
        web.form.Textbox('username', web.form.notnull,
            size=30,
            description="User name:"),
        web.form.Password('password', web.form.notnull,
            size=30,
            description="Password:"),
        web.form.Button('Login'),
    )
    def GET(self):
        session = web.ctx.session
        if session.login:
            raise web.seeother('/wiki')
        return render.login(self.form)
    def POST(self):
        form = self.form()
        if not form.validates():
            return render.Login(form)
        print form.d.username
        user = tmu.checkPassword(form.d.username, form.d.password)
        if user: 
            session = web.ctx.session
            session.login = 1
            session.username = form.d.username
            session.user = user
            raise web.seeother('/wiki')
        else:
            raise web.seeother('/login')
        
class Logout:
    def GET(self):
        session = web.ctx.session
        if session.login:
            session.kill()
        raise web.seeother('/login')
