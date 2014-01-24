import webapp2
import re
import cgi
from google.appengine.ext import db
import os
import jinja2
import hashlib
import random
import string
from google.appengine.ext import db

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

def make_salt():
    return ''.join(random.choice(string.letters) for x in xrange(5))

def make_pw_hash(name, pw, salt =None):
    if (not salt):
        salt = make_salt()
    h = hashlib.sha256(name + pw + salt).hexdigest()
    return '%s|%s' % (h, salt)

def valid_pw(name, pw, h):
    return make_pw_hash(name, pw, h.split("|")[1]) == h

class Signup(Handler):
  def render_front(self, username = '', email ='', error1 ='', error2='', error3 = '', error4 = ''):
    self.render('problem4_signup.html', username = username, email = email, 
                                        error1 = error1, error2= error2, 
                                        error3 = error3, error4 = error4)

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
    if ( Account.all().filter('username', username).get() != None):
        error1 = """ Username used!"""
        u = False

    if (u and p and v and e):
        username = str(username)
        pw = make_pw_hash(username, password)
        self.response.headers.add_header('Set-Cookie', 'username=%s|%s; Path=/'%(username, pw))
        newuser = Account(username = username, password = pw, email = email)
        newuser.put()
        self.redirect("/welcome")
    else:
        self.render_front(username, email, error1,error2,error3,error4)

class Account(db.Model):
  username = db.StringProperty(required = True)
  password = db.StringProperty(required = True)
  email    = db.StringProperty(required = False)

class Login(Handler):
  def render_front(self, username = '', error= ''):
    self.render('problem4_login.html', username = username, error = error)
  def get(self):
    self.render_front()
  def post(self):
    username = self.request.get('username')
    password = self.request.get('password')
  
    u = Account.all()
    u.filter('username', str(username))
    P = u.get()
    if P != None:
      pwd = P.password
      if (valid_pw(username, password, pwd)):
        self.response.headers.add_header('Set-Cookie', 'username=%s|%s; Path=/'%(str(username), str(pwd)))
        self.redirect('/welcome')
      else:
        error = 'Invalid password'
        self.render_front(username,error)
    else:
      error = 'Invalid user'
      self.render_front(username,error )
  
class Logout(Handler):
  def get(self):
    self.response.delete_cookie('username')
    self.redirect('/signup')

class ThanksHandler(Handler):
  def get(self):
      self.response.out.write('Welcome,' + str(self.request.cookies.get('username').split('|')[0] )+ '!')      
  
         
application = webapp2.WSGIApplication([ ('/signup', Signup),
                                        ('/welcome', ThanksHandler),
                                        ('/login', Login),
                                        ('/logout', Logout)
                                        ],
                                         debug=True)
