from flask import Flask 
from app.extensions import db,migrate


def create_app():  # we define our app instance in this function

# This is going to be  the project.
    app = Flask(__name__)
    app.config.from_object('config.Config') # register the class within our application factory function.

    db.init_app(app)
    migrate.init_app(app,db)

    @app.route('/')
    def home():
        return "Authors API Project setup"


    return app