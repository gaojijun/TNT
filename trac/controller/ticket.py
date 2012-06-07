import trac.model.ticket as tmt
import copy
import datetime
import web
import markdown
import simplejson as json

render = None

def updateRender():
    t_globals = {
        'datestr': web.datestr,
        'markdown': markdown.markdown,
        'context': web.ctx.session
    }
    global render
    render = web.template.render(
        'templates/ticket',
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
        tickets = tmt.get_tickets()
        return render.index(tickets)

class Ticket:
    @loginRequired
    def GET(self, id):
        ticket = tmt.get_ticket_by_id(id)
        if not ticket:
            raise web.seeother('/new?id=%s' % web.websafe(id))
        return render.view(ticket)

class New:
    def not_ticket_exists(url):
        return not bool(tmt.get_ticket_by_url(url))

    ticket_exists_validator = web.form.Validator(
        'Page already exists', not_ticket_exists)

    form = web.form.Form(
        web.form.Textbox('summary', web.form.notnull,
            size=30,
            description="Summary:"),
        web.form.Textbox('reporter', web.form.notnull,
            size=30,
            description="Reporter:"),
        web.form.Textarea('description', web.form.notnull, 
            rows=15, cols=80,
            description="Description:", post="Use <a href='http://en.wikipedia.org/wiki/Markdown'>markdown</a> syntax"),
        web.form.Dropdown('type',
            args = ['task', 'feature', 'defect', 'enhancement'],
            value = 'feature',
            description="Type:"),
        web.form.Dropdown('priority',
            args = ['blocker', 'critical', 'major', 'minor', 'trivial'],
            value = 'major',
            description="Priority:"),
        web.form.Textbox('start', web.form.notnull,
            size=30,
            description="Start date:"),
        web.form.Textbox('end', web.form.notnull,
            size=30,
            description="End date:"),
        web.form.Textbox('assignee',
            size=30,
            description="Assign to:"),

        web.form.Button('Create ticket'),
    )

    @loginRequired
    def GET(self):
        url = web.input(url='').url
        form = self.form()
        form.fill({'reporter': web.ctx.session.user.username})
        return render.new(form)

    @loginRequired
    def POST(self):
        form = self.form()
        if not form.validates():
            return render.new(form)
        fields = copy.copy(form.d)
        del fields['Create ticket']
        id = tmt.new_ticket(**fields)
        raise web.seeother('/ticket/edit/%s' % id)

class Delete:
    @loginRequired
    def POST(self, id):
        tmt.del_ticket(int(id))
        raise web.seeother('/ticket')

class Edit:

    form = web.form.Form(
        web.form.Textbox('summary', web.form.notnull,
            size=30,
            readonly='true',
            description="Summary:"),
        web.form.Textbox('reporter', web.form.notnull,
            size=30,
            readonly='true',
            description="Reporter:"),
        web.form.Textarea('description', web.form.notnull, 
            rows=15, cols=80,
            readonly='true',
            description="Description:"),
        web.form.Dropdown('type',
            args = ['task', 'feature', 'defect', 'enhancement'],
            value = 'feature',
            readonly='true',
            description="Type:"),
        web.form.Dropdown('priority',
            args = ['blocker', 'critical', 'major', 'minor', 'trivial'],
            value = 'major',
            readonly='true',
            description="Priority:"),
        web.form.Textbox('start', web.form.notnull,
            size=30,
            readonly='true',
            description="Start date:"),
        web.form.Textbox('end', web.form.notnull,
            size=30,
            readonly='true',
            description="End date:"),
        web.form.Textbox('assignee',
            size=30,
            readonly='true',
            description="Assign to:"),
        web.form.Button('Update ticket'),
    )

    form2 = web.form.Form(
        web.form.Dropdown('type',
            args = ['task', 'feature', 'defect', 'enhancement'],
            value = 'feature',
            description="Type:"),
        web.form.Dropdown('priority',
            args = ['blocker', 'critical', 'major', 'minor', 'trivial'],
            value = 'major',
            description="Priority:"),
        web.form.Textbox('start', web.form.notnull,
            size=30,
            description="Start date:"),
        web.form.Textbox('end', web.form.notnull,
            size=30,
            description="End date:"),
        web.form.Textbox('assignee',
            size=30,
            description="Assign to:"),
        web.form.Textarea('notes', web.form.notnull, 
            rows=15, cols=40,
            description="Notes:"),
        web.form.Button('Update ticket'),
    )

    @loginRequired
    def GET(self, id):
        ticket = tmt.get_ticket_by_id(int(id))
        history = tmt.get_changes_by_id(int(id))
        changes = []
        for i in history:
            i.comment = json.loads(i.comment)
            changes.append(i)
        # print changes[0]['author']
        form = self.form()
        form.fill(ticket)
        form2 = self.form2()
        form2.fill(ticket)
        return render.edit(ticket, form, form2, changes)


    @loginRequired
    def POST(self, id):
        form2 = self.form2()
        ticket = tmt.get_ticket_by_id(int(id))
        if not form2.validates():
            return render.edit(ticket, form2)
        fields = copy.copy(form2.d)
        del fields['Update ticket']
        notes = fields.pop('notes')
        tmt.update_ticket(int(id), **fields)
        diff = []
        for k, v in fields.iteritems():
            oldValue = getattr(ticket, k)
            if v != oldValue:
                diff.append([k, v, oldValue])
        if diff or notes:
            change = {
                'author': web.ctx.session.user.username,
                'ticketId': id,
                'time': '%s' % datetime.datetime.now(), 
                'comment': json.dumps(diff),
                'notes': notes
            }
            tmt.new_change(**change)
        raise web.seeother('/ticket/edit/%s' % id)

