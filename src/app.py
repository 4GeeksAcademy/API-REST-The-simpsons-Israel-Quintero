"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Character
from sqlalchemy import select
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None: app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
#Other configurations
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code


# Generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/user', methods=['GET'])
def handle_hello():
    users = User.query.all()
    response_body = {
        "msg": "Hello, this is your GET /user response "
    }

    return jsonify(response_body), 200

@app.route('/create/user', methods=['POST'])
def create_user():
    data=request.get_json()
    user_name=data.get('user_name')
    email=data.get('email')
    password=data.get('password')

    if not user_name or not email or not password:
        return jsonify({'msg':'Please fill all the blanks to complete the signup'}),400
    
    existing_user= db.session.execute(select(User).where(User.user_name,User.email == user_name, email)).scalar.one_or_none()

    if existing_user:
        return jsonify({'msg':'A user with this username or email already exists'}),401
    
    new_user=User(
        user_name=user_name,
        email=email,
        password=password
    )

    db.session.add(new_user)
    db.session.commit()

    return jsonify({'msg':'the user signup has been successfully completed'}),200





@app.route('/login',methods=['POST'])
def user_login():
    data=request.get_json()
    email=data.get('email')
    password=data.get('password')

    if not email or not password:
        return jsonify({'msg':'User not authorized'}),400
    
    existing_user= db.session.execute(select(User).where(User.email ==  email)).scalar.one_or_none()

    if not existing_user:
        return jsonify({'msg':'email or password are required'}),401
    
    else:
        return jsonify({'msg':'login has been successfull'}),200
    


@app.route('/characters/create',methods=['POST'])
def characters_create():
    data=request.get_json()
    user_id=data.get('id')
    existing_user=db.session.get(User,int(user_id))

    if not existing_user:
        return jsonify({'msg':'user not authorized'}),400
    
    new_character=Character(
        name=data.get('name'),
        quote=data.get('quote'),
        image=data.get('image'),
        location=data.get('location')

    )

    db.session.add(new_character)
    db.session.commit()
    return jsonify({'msg':'character succesfully created'}),200




@app.route('/characters/list',methods=['GET'])
def character_list():

    data=request.get_json()
    if not data:
        return jsonify({'msg':'unable request'}),400
    

    characters=db.session.execute(select(Character)).scalars().all()

    return jsonify(characters.serialize()),200
    
   



# This only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
