import trac.model.wiki as tmw
import web
import markdown

render = None

def updateRender():
    t_globals = {
        'datestr': web.datestr,
        'markdown': markdown.markdown,
        'context': web.ctx.session
    }
    global render
    render = web.template.render(
        'templates/wiki',
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

class Index:
    @loginRequired
    def GET(self):
        pages = tmw.get_pages()
        return render.index(pages)

class Page:
    @loginRequired
    def GET(self, url):
        page = tmw.get_page_by_url(url)
        if not page:
            raise web.seeother('/new?url=%s' % web.websafe(url))
        return render.view(page)

class New:
    def not_page_exists(url):
        return not bool(tmw.get_page_by_url(url))

    page_exists_validator = web.form.Validator(
        'Page already exists', not_page_exists)

    form = web.form.Form(
        web.form.Textbox('url', web.form.notnull, page_exists_validator,
            size=30,
            description="Wiki URL:"),
        web.form.Textbox('title', web.form.notnull, 
            size=30,
            description="Page title:"),
        web.form.Textarea('content', web.form.notnull, 
            rows=30, cols=120,
            description="Page content:", post="Use <a href='http://en.wikipedia.org/wiki/Markdown'>markdown</a> syntax"),
        web.form.Button('Create page'),
    )

    @loginRequired
    def GET(self):
        url = web.input(url='').url
        form = self.form()
        form.fill({'url': url})
        return render.new(form)

    @loginRequired
    def POST(self):
        form = self.form()
        if not form.validates():
            return render.new(form)
        tmw.new_page(form.d.url, form.d.title, form.d.content)
        raise web.seeother('/wiki/' + form.d.url)

class Delete:
    @loginRequired
    def GET(self, id):
        tmw.del_page(int(id))
        raise web.seeother('/wiki')

class Edit:

    form = web.form.Form(
        web.form.Textbox('url', web.form.notnull, 
            size=30,
            description="Location:"),
        web.form.Textbox('title', web.form.notnull, 
            size=30,
            description="Page title:"),
        web.form.Textarea('content', web.form.notnull, 
            rows=30, cols=120,
            description="Page content:", post="Use <a href='http://en.wikipedia.org/wiki/Markdown'>markdown</a> syntax"),
        web.form.Button('Update page'),
    )

    @loginRequired
    def GET(self, id):
        page = tmw.get_page_by_id(int(id))
        form = self.form()
        form.fill(page)
        return render.edit(page, form)


    @loginRequired
    def POST(self, id):
        form = self.form()
        page = tmw.get_page_by_id(int(id))
        if not form.validates():
            return render.edit(page, form)
        tmw.update_page(int(id), form.d.url, form.d.title, form.d.content)
        raise web.seeother('/wiki/%s' % form.d.url)

