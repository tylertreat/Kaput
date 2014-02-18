"""Create a flask app blueprint."""

import furious_router
furious_router.setup_lib_path()

import flask
from flask.ext.github import GitHub

from kaput import settings
from kaput.api.blueprint import blueprint as api_blueprint
from kaput.view.blueprint import blueprint as views_blueprint


global github
github = None


def create_app(config='kaput.settings'):
    app = flask.Flask(__name__, template_folder='../templates')

    app.config.from_object(config)
    app.secret_key = settings.SESSION_SECRET

    global github
    github = GitHub(app)

    # Imported to register urls
    from kaput.api import controller as api_controller
    from kaput.view import controller as views_controller

    app.register_blueprint(views_blueprint)
    app.register_blueprint(api_blueprint, url_prefix='/api')

    # Enable jinja2 loop controls extension
    app.jinja_env.add_extension('jinja2.ext.loopcontrols')

    return app

