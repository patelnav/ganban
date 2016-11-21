import webapp2, logging

from settings import JINJA_ENVIRONMENT
from google.appengine.api import channel, memcache, users
from google.appengine.ext import ndb
from google.appengine.ext.db import metadata

from models.user import User
from models.board import Board
from models.card import Card

ENTITY_TYPES = [User, Board, Card]


class RootHandler(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()

        if user:
            # Filter by the google appengine user id property.
            active_user = User.query(User.google_id == user.user_id()).fetch(1)

            if not active_user:
                # If we couldn't find a user it means that is the first time it uses the application.
                # We just need to create a new entity with the get_current_user() information.
                active_user = User(email=user.email(), username=user.nickname(), google_id=user.user_id())
                active_user.put()
                logging.info("New user created. Email address is: %s", active_user.email)
            else:
                active_user = active_user[0]

            token = channel.create_channel(str(active_user.key.id()))
            memcache.add(key=str(active_user.key.id()), value=token)

            template_vars = {
                'user': active_user,
                'token': token,
                'logout_url': users.create_logout_url('/welcome'),
                'boards': Board.query().order(Board.created_at)

            }
            template = JINJA_ENVIRONMENT.get_template('root.html')
            self.response.write(template.render(template_vars))
        else:
            self.redirect('/welcome')


class AdminHandler(webapp2.RequestHandler):

    def get(self):
        if users.is_current_user_admin():
            template = JINJA_ENVIRONMENT.get_template('admin.html')
            namespaces = metadata.get_namespaces()
            namespace_info = []

            for namespace in namespaces:
                info = {}

                for entity_type in ENTITY_TYPES:
                    kind = entity_type._get_kind()
                    info[kind] = len(entity_type.query(namespace=namespace).fetch(keys_only=True))

                text = ', '.join('{}: {}'.format(key, val) for key, val in info.items())
                info['text'] = "Namespace: '{}' | {}".format(namespace, text)
                info['namespace'] = namespace

                namespace_info.append(info)

            template_vars = {
                'namespace_info': namespace_info
            }

            self.response.write(template.render(template_vars))
        else:
            self.redirect(users.create_logout_url('/welcome'))

    def post(self):
        def clone_entity(e, **extra_args):
            # TODO: Move this to an appropriate place
            # FROM: http://stackoverflow.com/questions/2687724/copy-an-entity-in-google-app-engine-datastore-in-python-without-knowing-property#answer-2712401
            klass = e.__class__
            props = dict((v._code_name, v.__get__(e, klass)) for v in klass._properties.itervalues() if type(v) is not ndb.ComputedProperty)
            props.update(extra_args)
            return klass(**props)

        if users.is_current_user_admin():
            source_namespace = self.request.POST.get("namespace")
            target_namespace = self.request.POST.get("target_namespace")
            logging.info("Transferring namespaces from '{}' to '{}'".format(source_namespace, target_namespace))

            for entity_type in ENTITY_TYPES:
                new_entities = []
                kind = entity_type._get_kind()
                logging.info("Copying {}".format(kind))
                entities = entity_type.query(namespace=source_namespace).fetch()
                for entity in entities:
                    clone = clone_entity(entity, namespace=target_namespace)
                    new_entities.append(clone)

                ndb.put_multi(new_entities)

            self.redirect('/admin')
        else:
            self.redirect(users.create_logout_url('/welcome'))


class WelcomeHandler(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()

        if not user:
            template = JINJA_ENVIRONMENT.get_template('welcome.html')
            self.response.write(template.render(login_url=users.create_login_url('/')))
        else:
            self.redirect('/')
