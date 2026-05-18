from flask import Flask 
from app.extensions import db,migrate,jwt
from app.controllers.auth.auth_controller import auth
from app.controllers.users.user_controller import users
from app.controllers.companies.company_controller import companies
from app.controllers.books.book_controller import books


def create_app():  # we define our app instance in this function

# This is going to be  the project.
    app = Flask(__name__)
    app.config.from_object('config.Config') # register the class within our application factory function.

    db.init_app(app)
    migrate.init_app(app,db)        # Registering the flask migrate with the app and the db
    jwt.init_app(app)



     # Importing and registering models
    from app.models.users import User
    from app.models.companies import Company
    from app.models.books import Book


    # registering blueprints
    app.register_blueprint(auth)
    app.register_blueprint(users)
    app.register_blueprint(companies)
    app.register_blueprint(books)

    @app.route('/')
    def home():
        return "Authors API Project setup"


    return app