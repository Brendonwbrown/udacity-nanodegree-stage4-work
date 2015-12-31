import os

from google.appengine.ext import db

import jinja2
import webapp2

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

#Set up the database
class Commentary(db.Model):
	author = db.StringProperty()
	comment = db.StringProperty(multiline=True, indexed=False)
	date = db.DateTimeProperty(auto_now_add=True)

#Create datastore key for the Comments entity.
def _CommentsKey(brendon_notes_comments=None):
	return db.Key.from_path('CommentSection', brendon_notes_comments or 'default_comments')

#MainPage class brings all the code together for the main page. The get section preps desired datastore saved entries to be invoked later. The third section looks at POST info and either returns an error to the web user or redirects to a thank you page and stores the entry. 
class MainPage(webapp2.RequestHandler):
	def get(self):
		brendon_notes_comments = self.request.get('brendon_notes_comments')
		comments_query = Commentary.all().ancestor(_CommentsKey(brendon_notes_comments)).order('-date')
		max_comments = 10
		comments = comments_query.fetch(max_comments)
		template_values = {
	    		'comments': comments
	    }
		template = jinja_env.get_template('comments.html')
		self.response.out.write(template.render(template_values))

	def post(self):
		brendon_notes_comments = self.request.get('brendon_notes_comments')
		comment = Commentary(parent=_CommentsKey(brendon_notes_comments))
		comment.author = self.request.get('author').strip()
		comment.comment = self.request.get('comment').strip()
		
		if comment.author and comment.comment:
			comment.put()
			self.redirect("/thanks")
		else:
			self.redirect("/nope")


#ThanksPage prepares and writes up a page to serve for when the form is submitted correctly.
class ThanksPage(webapp2.RequestHandler):
	def get(self):
		self.response.headers['Content-Type'] = 'text/html'
		template = jinja_env.get_template('thanks.html')
		self.response.out.write(template.render())

#Nope seves an error and encourages the user to try again.
class Nope(webapp2.RequestHandler):
	def get(self):
		self.response.headers['Content-Type'] = 'text/html'
		template = jinja_env.get_template('nope.html')
		self.response.out.write(template.render())

app = webapp2.WSGIApplication([
		('/', MainPage),
		('/thanks', ThanksPage),
		('/nope', Nope)
	], 
	debug=True)