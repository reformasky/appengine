import webapp2
import re
import cgi
from google.appengine.ext import db
import os
import jinja2

template_dir = os.path.join(os.path.dirname(__file__),'templates')
jinja_env = jinja2.Environment(loader= jinja2.FileSystemLoader(template_dir),
                               autoescape = True)

def valid_username(s):
    patten = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
    return patten.match(s)

def valid_pwd(s):
    patten = re.compile(r"^.{3,20}$")
    return patten.match(s)

def valid_email(s):
    patten = re.compile(r"^[\S]+@[\S]+\.[\S]+$")
    return patten.match(s) 
 
def escape(s):
    return cgi.escape(s, quote = True)

class Handler(webapp2.RequestHandler):
  def write(self,*a, ** kw):
    self.response.write(*a,**kw)
  def render_str(self, template, **kw):
    t = jinja_env.get_template(template);
    return t.render(kw)
  def render(self, template, **kw):
    self.write(self.render_str(template, **kw))


class PWD(Handler):
    def render_front(self, username = '', email ='', error1 ='', error2='', error3 = '', error4 = ''):
      self.render('problem4_signup', username = username, email = email, error1 = error1, error2= error2, error3 = error3. error4 = error4)

    def get(self):
        self.render_front();
    def post(self):
        request = self.request
        username = request.get('username')
        password = request.get('password')
        verify = request.get('verify')
        email = request.get('email')
        error1=error2=error3=error4=''
        u = valid_username(username)
        p = valid_pwd(password)
        e = valid_email(email) or (email=='')
        v = (password ==  verify)
        if not u:
            error1 = '''That's not a valid username.'''
        if not p:
            error2 = '''That wasn't a valid password. '''
        elif not v:
            error3 = '''Your passwords didn't match. '''
        if not e:
            error4 = ''' That's not a valid email. '''
            
        if (u and p and v and e):
            self.redirect("/thanks?username=%s"%username)
        else:
            self.write_form(username, email, error1, error2, error3, error4)

class ThanksHandler(PWD):
    def get(self):
        self.response.out.write('Welcome,' + self.request.get('username') + '!')        
        
        
        
application = webapp2.WSGIApplication([('/', MainPage),
    ('/pwd', PWD),('/thanks', ThanksHandler)
], debug=True)
