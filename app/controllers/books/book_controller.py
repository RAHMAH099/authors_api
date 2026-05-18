# store all functions used to perform different authentication proses.
from flask import Blueprint,request,jsonify
from app.status_codes import HTTP_400_BAD_REQUEST, HTTP_409_CONFLICT, HTTP_500_INTERNAL_SERVER_ERROR,HTTP_201_CREATED,HTTP_401_UNAUTHORIZED,HTTP_200_OK,HTTP_404_NOT_FOUND,HTTP_403_FORBIDDEN
import validators
from app.models.companies import Company
from app.models.users import User
from app.models.books import Book
from app.extensions import db,bcrypt
from flask_jwt_extended import create_access_token,jwt_required,get_jwt_identity,create_refresh_token


books = Blueprint('books', __name__, url_prefix ='/api/v1/books')    # book blueprint


# book registration

@books.route('/create', methods = ['POST'])
@jwt_required()
def createNewBook():

    #storing request data
    data = request.get_json()
    title = data.get('title')
    pages = data.get('pages')
    price = data.get('price')
    price_unit = data.get('price_unit')
    description = data.get('description')
    genre = data.get('genre')
    isbn = data.get('isbn')
    publication_date = data.get('publication_date')
    image = data.get('image')
    company_id = data.get('company_id')
    user_id = get_jwt_identity()

# all the required attributes of our model are being submitted within the request.

# validations of the incoming request.

    if not title or not isbn or not pages or not description or not price or not  price_unit or not genre or not publication_date or not company_id:
        return jsonify({"error":"All fields are required."}),HTTP_400_BAD_REQUEST
    

    if Book.query.filter_by(title=title, user_id=user_id).first() is not None:   # this condition checks out for records that match the incoming 
# requests interms of the book title and user_id
        return jsonify({"error":"Book with this title and user_id already exists."}), HTTP_409_CONFLICT
    
    if Book.query.filter_by(isbn=isbn).first() is not None:   # this condition checks out whether isbn doesnt match with the rest. 
        return jsonify({"error":"Book isbn already use."}), HTTP_409_CONFLICT
    
    
    try:
        #creating new book
        new_book = Book(
            title=title,price=price,description=description,pages=pages,
            user_id=user_id,company_id=company_id,price_unit=price_unit,
            genre=genre,publication_date=publication_date,isbn=isbn,image=image
        )  
        db.session.add(new_book)
        db.session.commit()

        return jsonify({'message': title + ' has been created successfully.',
                        'book':{
                            'id':new_book.id,
                            'title': new_book.title,
                            'description': new_book.description,
                            'price':new_book.price,
                            'price_unit':new_book.price_unit,
                            'pages':new_book.pages,
                            'isbn':new_book.isbn,
                            'genre':new_book.genre,
                            'publication_date':new_book.publication_date,
                            'image':new_book.image,
                            'created_at':new_book.created_at,
                            'company':{
                                'id':new_book.company.id,
                                'name': new_book.company.name,
                                'origin': new_book.company.origin,
                                'description': new_book.company.description,
                                'created_at':new_book.company.created_at
                            },
                            'author':{
                                'id':new_book.user.id,
                                'first_name':new_book.user.first_name,
                                'last_name':new_book.user.last_name,
                                'email':new_book.user.email,
                                'contact':new_book.user.contact,
                                'type':new_book.user.user_type,
                                'biography':new_book.user.biography,
                                'created_at':new_book.user.created_at
                            }
                        } }),HTTP_201_CREATED
    
    except Exception as e:   # variable to reuse as e
        db.session.rollback()          # to rollback the database incase of any errors.
        return jsonify({'error' : str(e)}), HTTP_500_INTERNAL_SERVER_ERROR  # the error brought back
    


# get all books
@books.get("/")
@jwt_required()
def getAllBooks():

    try:

        all_books = Book.query.all()

        books_data = []

        for book in all_books:
            book_info ={
                'id':book.id,
                'title':book.title,
                'description':book.description,
                'price':book.price,
                'price_unit':book.price_unit,
                'pages':book.pages,
                'isbn':book.isbn,
                'genre':book.genre,
                'publication_date':book.publication_date,
                'image':book.image,
                'created_at':book.created_at,
                'company':{
                    'id':book.company.id,
                    'name': book.company.name,
                    'origin': book.company.origin,
                    'description':book.company.description,
                    'created_at':book.company.created_at
                }
            }
            books_data.append(book_info)


        return jsonify({
            'message':'All books retrieved successfully.',
            'total_books':len(books_data),
            'books':books_data
        }), HTTP_200_OK

    except Exception as e:
        return jsonify({
            'error':str(e)
        }), HTTP_500_INTERNAL_SERVER_ERROR
    



# getting book by id
@books.get("/book/<int:id>")
@jwt_required()
def getBook(id):

    try:

        book = Book.query.filter_by(id=id).first()

        if not book:
            return jsonify({'error':'Book not found.'}), HTTP_404_NOT_FOUND


        return jsonify({
            'message':'Book details retrieved successfully.',
            'book':{
                'id':book.id,
                'title': book.title,
                'description': book.description,
                'price':book.price,
                'price_unit':book.price_unit,
                'pages':book.pages,
                'isbn':book.isbn,
                'genre':book.genre,
                'publication_date':book.publication_date,
                'image':book.image,
                'created_at':book.created_at,
                'company':{
                    'id':book.company.id,
                    'name': book.company.name,
                    'origin': book.company.origin,
                    'description': book.company.description,
                    'created_at':book.company.created_at
                },
                'author':{
                    'id':book.user.id,
                    'first_name':book.user.first_name,
                    'last_name':book.user.last_name,
                    'email':book.user.email,
                    'contact':book.user.contact,
                    'type':book.user.user_type,
                    'biography':book.user.biography,
                    'created_at':book.user.created_at
                }
            }
        }), HTTP_200_OK

    except Exception as e:
        return jsonify({
            'error':str(e)
        }), HTTP_500_INTERNAL_SERVER_ERROR
    


# update book details
@books.route("/edit/<int:id>", methods = ['PUT','PATCH'])
@jwt_required()
def updateBookDetails(id):

    try:
        current_user = int(get_jwt_identity())
        loggedInUser = User.query.filter_by(id=current_user).first()

        # get book by id
        book = Book.query.filter_by(id=id).first()

        if not book:
            return jsonify({'error':'Book not found.'}), HTTP_404_NOT_FOUND
        
        elif loggedInUser.user_type!='admin' and book.user_id!= current_user:
            return jsonify({'error':'You are not authorized to update the book details.'}),HTTP_403_FORBIDDEN
        
        else:
            #store request data
            title = request.get_json().get('title',book.title)
            price = request.get_json().get('price',book.price)
            price_unit = request.get_json().get('price_unit',book.price_unit)
            description = request.get_json().get('description',book.description)
            genre = request.get_json().get('genre',book.genre)
            isbn = request.get_json().get('isbn',book.isbn)
            pages = request.get_json().get('pages',book.pages)
            publication_date = request.get_json().get('publication_date',book.publication_date)
            company_id = request.get_json().get('company_id',book.company_id)
            image = request.get_json().get('image',book.image)

            
            if isbn !=book.isbn and Book.query.filter_by(isbn=isbn).first():
                return jsonify({
                    'error':'Isbn already in use.'
                }),HTTP_409_CONFLICT
            
            if title !=book.title and Book.query.filter_by(title=title,user_id=current_user).first():
                return jsonify({
                    'error':'Title already in use.'
                }),HTTP_409_CONFLICT

            book.title = title
            book.price = price
            book.description = description
            book.price_unit = price_unit
            book.genre = genre
            book.isbn = isbn
            book.pages = pages
            book.publication_date = publication_date
            book.company_id = company_id
            book.image = image

            db.session.commit()

            return jsonify({
                'message':title + "'s details have been successfully updated." ,
                'book':{
                    'id':book.id,
                'title': book.title,
                'description': book.description,
                'price':book.price,
                'price_unit':book.price_unit,
                'pages':book.pages,
                'isbn':book.isbn,
                'genre':book.genre,
                'publication_date':book.publication_date,
                'image':book.image,
                'created_at':book.created_at,
                'company':{
                    'id':book.company.id,
                    'name': book.company.name,
                    'origin': book.company.origin,
                    'description': book.company.description,
                    'created_at':book.company.created_at
                },
                'author':{
                    'id':book.user.id,
                    'first_name':book.user.first_name,
                    'last_name':book.user.last_name,
                    'email':book.user.email,
                    'contact':book.user.contact,
                    'type':book.user.user_type,
                    'biography':book.user.biography,
                    'created_at':book.user.created_at
                }
            }
            })

    except Exception as e:
        return jsonify({
            'error':str(e)
        }), HTTP_500_INTERNAL_SERVER_ERROR
    


# deleting a book
@books.route("/delete/<int:id>", methods = ['DELETE'])
@jwt_required()
def deleteBook(id):

    try:
        current_user = get_jwt_identity()
        loggedInUser = User.query.filter_by(id=current_user).first()

        # get book by id
        book = Book.query.filter_by(id=id).first()

        if not book:
            return jsonify({'error':'Book not found.'}), HTTP_404_NOT_FOUND
        
        elif loggedInUser.user_type!='admin' and book.user_id!=current_user:
            return jsonify({'error':'You are not authorized to delete this book.'}),HTTP_403_FORBIDDEN
        
        else:


            db.session.delete(book)
            db.session.commit()

           
            return jsonify({
                'message':"Book deleted successfully."
            })

    except Exception as e:
        return jsonify({
            'error':str(e)
        }), HTTP_500_INTERNAL_SERVER_ERROR
