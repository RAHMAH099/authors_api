class Config:     # store configuration keys for the sqlalchemy
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:@localhost/flask_authors_db'
    JWT_SECRET_KEY = "authors"
