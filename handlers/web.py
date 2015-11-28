import webapp2, random, logging

from settings import JINJA_ENVIRONMENT
from google.appengine.api import users
from models.user import *


class RootHandler(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()

        if user:
            # Create a query for searching the User Entities
            query = User.query()

            # Filter by the google appengine user id property.
            query.filter(User.google_id == user.user_id())
            active_user = query.fetch(1)

            if not active_user:
                # If we couldn't find a user it means that is the first time it uses the application.
                # We just need to create a new entity with the get_current_user() information.
                new_user = User(email = user.email(), username = user.nickname(), google_id = user.user_id())
                new_user.put()
                logging.info("New user created. Email address is: %s", new_user.email)

            template_vars = {
                'user' : user,
                'logout_url' : users.create_logout_url('/welcome'),
                'containers' : [
                    {
                        'id' : 'to-do',
                        'name' : 'To do'
                    },
                    {
                        'id' : 'in-progress',
                        'name' : 'In Progress'
                    },
                    {
                        'id' : 'done',
                        'name' : 'Done'
                    }
                ],
                'cards' : [
                    [
                        {
                            'id' : random.randrange(1000, 10000, 1),
                            'status' : 'to-do',
                            'content' : 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Integer vitae posuere purus. Phasellus in molestie libero. Vivamus mollis massa orci.'
                        },
                        {
                            'id' : random.randrange(1000, 10000, 1),
                            'status' : 'to-do',
                            'content' : 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Integer vitae posuere purus. Phasellus in molestie libero. Vivamus mollis massa orci.'
                        },
                        {
                            'id' : random.randrange(1000, 10000, 1),
                            'status' : 'to-do',
                            'content' : 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Integer vitae posuere purus. Phasellus in molestie libero. Vivamus mollis massa orci.'
                        }
                    ],
                    [
                        {
                            'id' : random.randrange(1000, 10000, 1),
                            'status' : 'in-progress',
                            'content' : 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Integer vitae posuere purus. Phasellus in molestie libero. Vivamus mollis massa orci.'
                        },
                        {
                            'id' : random.randrange(1000, 10000, 1),
                            'status' : 'in-progress',
                            'content' : 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Integer vitae posuere purus. Phasellus in molestie libero. Vivamus mollis massa orci.'
                        },
                        {
                            'id' : random.randrange(1000, 10000, 1),
                            'status' : 'in-progress',
                            'content' : 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Integer vitae posuere purus. Phasellus in molestie libero. Vivamus mollis massa orci.'
                        }
                    ],
                    [
                        {
                            'id' : random.randrange(1000, 10000, 1),
                            'status' : 'done',
                            'content' : 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Integer vitae posuere purus. Phasellus in molestie libero. Vivamus mollis massa orci.'
                        },
                        {
                            'id' : random.randrange(1000, 10000, 1),
                            'status' : 'done',
                            'content' : 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Integer vitae posuere purus. Phasellus in molestie libero. Vivamus mollis massa orci.'
                        },
                        {
                            'id' : random.randrange(1000, 10000, 1),
                            'status' : 'done',
                            'content' : 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Integer vitae posuere purus. Phasellus in molestie libero. Vivamus mollis massa orci.'
                        }
                    ]
                ]
            }
            template = JINJA_ENVIRONMENT.get_template('root.html')
            self.response.write(template.render(template_vars))
        else:
            self.redirect('/welcome')


class WelcomeHandler(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()

        if not user:
            template = JINJA_ENVIRONMENT.get_template('welcome.html')
            self.response.write(template.render(login_url=users.create_login_url('/')))
        else:
            self.redirect('/')
