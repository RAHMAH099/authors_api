# store all functions used to perform different authentication proses.
from flask import Blueprint,request,jsonify
from app.status_codes import HTTP_400_BAD_REQUEST, HTTP_409_CONFLICT, HTTP_500_INTERNAL_SERVER_ERROR,HTTP_201_CREATED,HTTP_401_UNAUTHORIZED,HTTP_200_OK
import validators
from app.models.users import User
from app.extensions import db,bcrypt
from flask_jwt_extended import create_access_token,jwt_required,get_jwt_identity,create_refresh_token

auth = Blueprint('auth', __name__, url_prefix ='/api/v1/auth')    # auth blueprint


# user registration

@auth.route('/register', methods = ['POST'])
def register_user():
    data = request.json
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    contact = data.get('contact')
    email = data.get('email')
    user_type = data.get('user_type') if 'user_type' in data else "author"
    password = data.get('password')
    biography = data.get('biography', '') if user_type == "author" else ''

#all the required attributes of our model are being submitted within the request.

# validations of the incoming request.

    if not first_name or not last_name or not contact or not password or not email:
        return jsonify({"error":"All fields are required."}),HTTP_400_BAD_REQUEST
    
    if user_type == "author" and not biography:
        return jsonify({"error":"Enter your author biography."}),HTTP_400_BAD_REQUEST
    
    if len(password) < 8:
        return jsonify({"error":"Password is too short."}),HTTP_400_BAD_REQUEST
    
    if not validators.email(email):
        return jsonify({"error":"Email address is already in use."}),HTTP_400_BAD_REQUEST
    
    # we have to cater for any constraints.

    if User.query.filter_by(email = email).first() is not None:   # this condition checks out for recotrds that match the incoming 
# requests interms of the email address
        return jsonify({"error":"Email address in use."}), HTTP_409_CONFLICT
    
    if User.query.filter_by(contact = contact).first() is not None:   # this condition checks out that no users have the same contact
        return jsonify({"error":" Contact is already in use."}), HTTP_409_CONFLICT
    

    # Logic that stores a new user to the database (catch errors that arise during creating a new user.)

    try:
        hashed_password = bcrypt.generate_password_hash(password)  # hashes our user passwords for security.
        new_user = User(first_name = first_name, last_name = last_name, password = hashed_password, email = email, contact=contact, biography=biography, user_type=user_type) # we are going to work with bcrypt to hash our passwords for security. 
        db.session.add(new_user)
        db.session.commit()

        # variable to keep track of the new user name
        user_name = new_user.get_full_name()

        return jsonify({'message': user_name + ' has been successfully created as an ' + new_user.user_type,
                        'user':{
                            'id':new_user.id,
                            'first_name': new_user.first_name,
                            'last_name': new_user.last_name,
                            'email': new_user.email,
                            'contact': new_user.contact,
                            'user_type': new_user.user_type,
                            'biography': new_user.biography,
                            'created_at':new_user.created_at,
                        } }),HTTP_201_CREATED
    
    except Exception as e:   # variable to reuse as e
        db.session.rollback()          # to rollback the database incase of any errors.
        return jsonify({'error' : str(e)}), HTTP_500_INTERNAL_SERVER_ERROR  # the error brought back
    
# User login
@auth.post("/login")
def login():

    email = request.json.get("email")
    password = request.json.get("password")

    try:

        if not password or not email:
            return jsonify({'Message':'Email and Password are required.'}), HTTP_400_BAD_REQUEST
        
        user = User.query.filter_by(email = email).first()

        if user:
            is_correct_password = bcrypt.check_password_hash(user.password, password)

            if is_correct_password:
                access_token = create_access_token(identity=str(user.id))
                refresh_token = create_refresh_token(identity=str(user.id))

                return jsonify({
                    'user':{
                        'id':user.id,
                        "username":user.get_full_name(),
                        'email':user.email,
                        'access_token':access_token,
                        'refresh_token':refresh_token,
                        'user_type':user.user_type
                    },
                    'message':"You have successfully logged into your account."
                }), HTTP_200_OK
            else:
                return jsonify({'Message':'Invalid password.'}),HTTP_401_UNAUTHORIZED
            
        else:
            return jsonify({'Message':'Invalid email address.'}),HTTP_401_UNAUTHORIZED

    except Exception as e:
        return jsonify({
            'error':str(e)
        }), HTTP_500_INTERNAL_SERVER_ERROR
    

# We are using the `refresh=True` options in jwt_required to only allow
# refresh tokens to access this route.
@auth.route("token/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity)
    return jsonify({'access_token' : access_token})
