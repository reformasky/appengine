from google.appengine.ext import db
import os
import webapp2
import jinja2
import json
import re
import re
import cgi
import hashlib
import random
import string
from google.appengine.api import memcache
import time

template_dir = os.path.join(os.path.dirname(__file__),'templates')
jinja_env = jinja2.Environment(loader= jinja2.FileSystemLoader(template_dir),
                               autoescape = True)
time_query = -1
numOfCached = 0
keys = []
# databases
class Blog(db.Model):
	subject = db.StringProperty(required = True)
	content = db.TextProperty(required = True)
	created = db.DateTimeProperty(auto_now_add = True)

class Account(db.Model):
  username = db.StringProperty(required = True)
  password = db.StringProperty(required = True)
  email    = db.StringProperty(required = False)

#end databases


class Handler(webapp2.RequestHandler):
	def write(self,*a, ** kw):
		self.response.write(*a,**kw)
	def render_str(self, template, **kw):
		t = jinja_env.get_template(template);
		return t.render(kw)
	def render(self, template, **kw):
		self.write(self.render_str(template, **kw))

class NewPost(Handler):
	def render_front(self, subject = '', content = '', error = ''):
		self.render('problem3_newpost.html', subject = subject, content = content, error = error)
	def get(self):
		self.render_front()
	def post(self):
		global numOfCached, keys
		request = self.request
		subject = request.get('subject')
		content = request.get('content')
		error = ''
		if (subject and content):
			newpost = Blog(subject = subject, content= content)
			newpost.put();
			x = str(newpost.key().id())
			keys.append(x)	
			numOfCached += 1
			memcache.set(x, [newpost.subject, newpost.content, newpost.created.strftime("%A, %d. %B %Y %I:%M%p"), time.time()])				
			
			self.redirect('/%s'%x)
		else:
			error = 'Sorry, both subject and content should be present.'
			self.render_front(subject, content, error);
class MainPage(Handler):
	def get(self):
		global numOfCached, keys,time_query

		if numOfCached <=0:
			blogs = db.GqlQuery('select * from Blog order by created ASC')
			for b in blogs:
				memcache.set(str(b.key().id()), [b.subject, b.content, b.created.strftime("%A, %d. %B %Y %I:%M%p"), time.time()])
				keys.append(str(b.key().id()))
				numOfCached += 1				
			time_query = time.time()
		if numOfCached < 10:
			number = numOfCached
		else:
			number = 10
		key_copy = keys[-10:]
		key_copy.reverse()
		self.render('problem3_front.html', keys = key_copy, memcache = memcache, query ='%.2f'%( time.time()- time_query))

class Perm(Handler):	
	def get(self, post_id):
		data = memcache.get(post_id)
		if not data:
			self.time_query = time.time()
			p = Blog.get_by_id(int(post_id))
			if p:
				memcache.set(post_id, [p.subject, p.created.strftime("%A, %d. %B %Y %I:%M%p"), p.content, time.time()])				
				data = memcache.get(post_id)		
			else:
				self.response.write("404. Does not exist")
		self.render('problem3_perm.html', subject = data[0], content = data[2], created = data[1], 
			                         query = '%.2f'%(time.time() -data[3]))

class Json(Handler):
	def get(self, post_id = ''):
		self.response.headers['Content-Type'] = "application/json; charset=utf-8"
		self.writeJson()
	def writeJson(self):		
		uid = self.request.url.split('/')		
		if uid[-1] == '.json':
			lists = []
			for blog in db.GqlQuery('select * from Blog order by created DESC'):
				dicts = {}
				dicts['content'] = blog.content
				dicts['subject'] = blog.subject
				dicts['created'] = blog.created.strftime("%A, %d. %B %Y %I:%M%p")
				lists.append(dicts)
		else:
			uid = uid[-1].split('.')[0]
			p = Blog.get_by_id(int(uid))
			lists = {}
			lists['content'] = p.content
			lists['subject'] = p.subject
			lists['created'] = p.created.strftime("%A, %d. %B %Y %I:%M%p") 
		self.response.write(json.dumps(lists))


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

class Flush(Handler):
	def get(self):
		global time_query, keys, numOfCached
		memcache.flush_all()
		numOfCached = 0
		keys = []
		self.redirect('/')




application = webapp2.WSGIApplication([('/([0-9]+)/?', Perm),
									   ('/newpost/?', NewPost),
									   ('/', MainPage),
									   ('/.json/?', Json),
									   ('/([0-9]+).json', Json),									   
									   ('/signup/?', Signup),
                                       ('/welcome/?', ThanksHandler),
                                       ('/login/?', Login),
                                       ('/logout/?', Logout),
                                       ('/flush/?', Flush)], 
                                       debug = True)