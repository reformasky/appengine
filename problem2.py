import webapp2
from rot13 import *
import re
import cgi

textarea="""
<!DOCTYPE html>

<html>
  <head>
    <title>Unit 2 Rot 13</title>
  </head>

  <body>
    <h2>Enter some text to ROT13:</h2>
    <form method="post">
      <textarea name="text"
                style="height: 100px; width: 400px;">%s</textarea>
      <br>
      <input type="submit">
    </form>
  </body>

</html>
"""




class MainPage(webapp2.RequestHandler):
    def write_form(self, content=''):
        self.response.out.write(textarea%rot13(content))
   
    def get(self):
        self.write_form()
    def post(self):
        content = self.request.get('text')
        self.write_form(content)

pwd = '''
<!DOCTYPE html>

<html>
  <head>
    <title> Sign up</title>
    <style type="text/css">
      .label{text-align: right}
      .error{color:red}
    </style>
  </head>

  <body>
    <h2>Signup</h2>
    <form method="post">
       <table>
	 <tr>
	   <td class="label">
	     Username
	   </td>
	   <td>
	     <input type="text" name="username" value="%(username)s">
	   </td>
	   <td class="error"> %(error1)s
	   </td>
	 </tr>

	 <tr>
	   <td class="label">
	     Password
	   </td>
	   <td>
	     <input type="password" name="password">
	   </td>
	   <td class="error">%(error2)s
	   </td>
	 </tr>

	 <tr>
	   <td class="label">
	     Verify Password
	   </td>
	   <td>
	     <input type="password" name="verify">
	   </td>
	   <td class="error">%(error3)s
	   </td>
	 </tr>

	 <tr>
	   <td class="label">
	     Email(Optional)
	   </td>
	   <td>
	     <input type="text" name="email" value="%(email)s">
	   </td>
	    <td class= 'error'>%(error4)s
	   </td>
	 </tr>
	   
      </table>
      <input type="submit">
    </form>
  </body>

</html>
''' 

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

class PWD(webapp2.RequestHandler):
    def write_form(self, username='', email='', 
                   error1='', error2='', error3='', error4=''):
        self.response.out.write( pwd%{'username':escape(username), 'email':escape(email),
                                      'error1':error1, 'error2':error2, 
                                      'error3':error3, 'error4':error4})
    def get(self):
        self.write_form()
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
        
        
        
application = webapp2.WSGIApplication([
    ('/pwd', PWD),('/thanks', ThanksHandler)
], debug=True)
