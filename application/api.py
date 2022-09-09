#Api Controller. Principal code for executing the API as per API documentation 
from flask_restful import Resource, Api
from flask_restful import fields, marshal_with
from flask_restful import reqparse
from application.validation import BusinessValidationError, NotFoundError
from application.models import User, Article
from application.database import db
from flask import current_app as app
import werkzeug
from flask import abort

create_user_parser = reqparse.RequestParser()
create_user_parser.add_argument('username')
create_user_parser.add_argument('email')

update_user_parser = reqparse.RequestParser()
update_user_parser.add_argument('email')

resource_fields = { #Way the output has to be formatted
    'user_id':   fields.Integer,
    'username':    fields.String,
    'email':    fields.String
}


class UserAPI(Resource):
    @marshal_with(resource_fields)
    def get(self, username): #username contains username input in URL
        user = db.session.query(User).filter(User.username == username).first() #Get the user from database based on username
        if user is None:
            raise NotFoundError(status_code=404)
        return user

    @marshal_with(resource_fields)
    def put(self, username):
        args = update_user_parser.parse_args()
        email = args.get("email", None)

        if email is None:
            raise BusinessValidationError(status_code=400, error_code="BE1002", error_message="email is required")

        if "@" in email:
            pass
        else:
            raise BusinessValidationError(status_code=400, error_code="BE1003", error_message="Invalid email")
        
        user = db.session.query(User).filter(User.email == email).first()
        if user:
            raise BusinessValidationError(status_code=400, error_code="BE1006", error_message="Duplicate email")

        #check wether user exist 
        user = db.session.query(User).filter(User.username == username).first() #Get the user from database based on username
        if user is None:
            raise NotFoundError(status_code=404)
        
        user.email = email
        db.session.add(user)
        db.session.commit()
        return user   

    @marshal_with(resource_fields)
    def post(self):
        args = create_user_parser.parse_args()
        username = args.get("username", None)
        email = args.get("email", None)

        if username is None:
            raise BusinessValidationError(status_code=400, error_code="BE1001", error_message="username is required")

        if email is None:
            raise BusinessValidationError(status_code=400, error_code="BE1002", error_message="email is required")

        if "@" in email:
            pass
        else:
            raise BusinessValidationError(status_code=400, error_code="BE1003", error_message="Invalid email")

        user = db.session.query(User).filter((User.username == username) | (User.email == email)).first()
        if user:
            raise BusinessValidationError(status_code=400, error_code="BE1004", error_message="Duplicate user")            

        new_user = User(username=username, email=email)
        db.session.add(new_user)
        db.session.commit()
        return new_user                

    def delete(self, username):
        #check wether user exist 
        user = db.session.query(User).filter(User.username == username).first() #Get the user from database based on username
        if user is None:
            raise NotFoundError(status_code=404)

        articles=Article.query.filter(Article.authors.any(username=username))  
        if articles:
            raise BusinessValidationError(status_code=400, error_code="BE1005", error_message="articles not found")

        #If no dependency then delete
        db.session.delete(user)
        db.session.commit()
        return "",200
