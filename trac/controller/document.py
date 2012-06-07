import trac.model.user as tmu
import web
import markdown
import copy
import os

FILEDIR = 'static/documents'
render = None

def updateRender():
    t_globals = {
        'datestr': web.datestr,
        'context': web.ctx.session
    }
    global render
    render = web.template.render(
        'templates/document',
        base='../layout',
        globals=t_globals
    )

def loginRequired(f):
    def _f(*args):
        if web.ctx.session.login:
            updateRender()
            return f(*args)
        else:
            raise web.seeother('/login')
    return _f

def adminRequired(f):
    def _f(*args):
        if web.ctx.session.login and\
           web.ctx.session.user.isadmin:
            updateRender()
            return f(*args)
        else:
            raise web.seeother('/login')
    return _f

class Upload:
    form = web.form.Form(
        web.form.File('myfile', web.form.notnull,
            size=30,
            description="choose file:"),
        web.form.Button('upload file')
    )
    @loginRequired
    def GET(self):
        form = self.form()
        return render.upload(form)

    def POST(self):
        form = self.form()
        if not form.validates():
            return render.upload(form)
        x = web.input(myfile={})
        FILEDIR = 'static/documents'
        if 'myfile' in x:
            filepath=x.myfile.filename.replace('\\','/')
            filename=filepath.split('/')[-1]
            fout = open(FILEDIR +'/'+ filename,'w')
            fout.write(x.myfile.file.read())
            fout.close()
        raise web.seeother('/document')

class Index:
    @loginRequired
    def GET(self):
        files = os.listdir(FILEDIR)
        return render.index(files)

class Delete:
    @adminRequired
    def GET(self, fileName):
        f = os.path.join(FILEDIR, fileName)
        os.remove(f)
        raise web.seeother('/document')
