from google.appengine.ext import db
import os
import webapp2
import jinja2

template_dir = os.path.join(os.path.dirname(__file__),'templates')
jinja_env = jinja2.Environment(loader= jinja2.FileSystemLoader(template_dir),
                               autoescape = True)

class Handler(webapp2.RequestHandler):
    def write(self, *a,**kw):
        self.response.write(*a,**kw);
    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)
    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class MainPage(Handler):
    def render_front(self, title="", art= "", error=""):
        self.render("front.html", title= title, art= art, error= error)
    def get(self):
        self.render_front()
    def post(self):
        r = self.request
        title  = r.get('title')
        art = r.get('art')
        error = ''
        if not (title and art):
            error = "Sorry, something is missing"
        self.render_front(title, art, error)
application= webapp2.WSGIApplication([('/', MainPage)],debug = True)
