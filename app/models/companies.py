from app.extensions import db # to be able to inherit from our model class
from datetime import datetime

class Company(db.Model):
    __tablename__ = 'companies' # customize the table name
    id = db.Column(db.Integer, primary_key = True)    # ids are automatically incrimated
    name =  db.Column(db.String(100), unique = True )
    origin =  db.Column(db.String(100), nullable = False)
    description =  db.Column(db.Text(100), nullable = False)
    user_id =  db.Column(db.Integer, db.ForeignKey('users.id'))  # foreign key
    user = db.relationship('User', backref = 'companies') # relationship user can access the different companies they have made.
    created_at = db.Column(db.DateTime, default = datetime.now())
    updated_at = db.Column(db.DateTime, onupdate = datetime.now())
    

# add a constructor for the company class
    def __init__(self,name,origin,description,user_id):
        super(Company,self).__init__() 
        self.name = name
        self.origin= origin
        self.description = description
        self.user_id = user_id
        

    def __repr__(self):        # add string representation of the companies that will be made.
         return f"{self.name} {self.origin}"
