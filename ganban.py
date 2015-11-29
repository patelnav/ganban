import webapp2, logging

from handlers import web
from handlers import api

from models.board import *

# We need to initialize the default board on the application startup.
# We search for them, in case they are not present, we create them.
if (Board.query(Board.name == 'To Do').fetch().count == 0):
    Board(name = 'To Do').put()

if (Board.query(Board.name == 'Doing').fetch().count == 0):
    Board(name = 'Doing').put()

if (Board.query(Board.name == 'Done').fetch().count == 0):
    Board(name = 'Done').put()

# Configure the WSGIApplication routes
app = webapp2.WSGIApplication([
    webapp2.Route(r'/', handler = web.RootHandler, methods = ['GET']),
    webapp2.Route(r'/welcome', handler = web.WelcomeHandler, methods = ['GET']),
    webapp2.Route(r'/api/cards', handler = api.CreateCardHandler, methods = ['POST']),
    webapp2.Route(r'/api/cards/<card_id>', handler = api.GetCardHandler, methods = ['GET']),
    webapp2.Route(r'/api/cards/<card_id>', handler = api.UpdateCardHandler, methods = ['PUT']),
    webapp2.Route(r'/api/cards/<card_id>', handler = api.DestroyCardHandler, methods = ['DELETE'])
], debug=True)
