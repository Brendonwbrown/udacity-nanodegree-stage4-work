import os
import cgi
import urllib

from google.appengine.api import users
from google.appengine.ext import db

import jinja2
import webapp2

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

#thanks variable will contain html for the page we redirect to after a comment is submitted.
thanks = """
<h3>Why thank you, %s! </h3> 
<p>I will certainly take that under advisement.</p>
<a href="/">Head on back.</a>
"""
#An error message for invalid entries.
error = """
<div class="error">
Something's not quite right with that, %s! Let's <a href="/">head on back</a> and try it again!"
</div>
"""

#A function to return a string with substitution.
def sub1(t, s):
	return t % s

#Set up the database
class Commentary(db.Model):
  author = db.StringProperty()
  comment = db.StringProperty(multiline=True, indexed=False)
  date = db.DateTimeProperty(auto_now_add=True)

#Create datastore key for the Comments entity.
def _CommentsKey(brendon_notes_comments=None):
  return db.Key.from_path('CommentSection', brendon_notes_comments or 'default_comments')

#Handler class helps us save on writing some code when invoked within other classes.
class Handler(webapp2.RequestHandler):
	def write(self, *a, **kw):
		self.response.out.write(*a, **kw)

#MainPage class brings all the code together for the main page. The get section preps desired datastore saved entries to be invoked later. The third section looks at POST info and either returns an error to the web user or redirects to a thank you page and stores the entry. 
class MainPage(Handler):
	def get(self):
		brendon_notes_comments = self.request.get('brendon_notes_comments')
		comments_query = Commentary.all().ancestor(_CommentsKey(brendon_notes_comments)).order('-date')
		comments = comments_query.fetch(10)
		template_values = {
	    		'comments': comments
	    }
		template = jinja_env.get_template('comments.html')
		self.response.out.write(template.render(template_values))

	def post(self):
		brendon_notes_comments = self.request.get('brendon_notes_comments')
		comment = Commentary(parent=_CommentsKey(brendon_notes_comments))
		comment.author = self.request.get('author')
		comment.comment = self.request.get('comment')
		
		if comment.author and comment.comment:
			comment.put()
			self.redirect("/thanks")
		else:
			self.redirect("/nope")


#ThanksPage prepares and writes up a page to serve for when the form is submitted correctly.
class ThanksPage(Handler):
	def get(self):
		self.response.headers['Content-Type'] = 'text/html'
		commenter = self.request.get("commenter")
		self.write(sub1(thanks, commenter))

#Nope seves an error and encourages the user to try again.
class Nope(Handler):
	def get(self):
		self.response.headers['Content-Type'] = 'text/html'
		commenter = self.request.get("commenter")
		self.write(sub1(error, commenter))

app = webapp2.WSGIApplication([
		('/', MainPage),
		('/thanks', ThanksPage),
		('/nope', Nope)
	], 
	debug=True)