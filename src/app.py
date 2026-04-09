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
from models import db, User, Character, Location
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
    
    existing_user= db.session.execute(select(User).where(User.user_name == user_name,User.email== email)).scalar_one_or_none()

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





#devuelve todos los usuarios del blog
@app.route('/users', methods=['GET'])
def users_on_file():
    users= db.session.execute(select(User)).scalars().all()

    return jsonify([user.serialize() for user in users])



# @app.route('/login',methods=['POST'])
# def user_login():
#     data=request.get_json()
#     email=data.get('email')
#     password=data.get('password')

#     if not email or not password:
#         return jsonify({'msg':'User not authorized'}),400
    
#     existing_user= db.session.execute(select(User).where(User.email ==  email)).scalar_one_or_none()

#     if not existing_user:
#         return jsonify({'msg':'email or password are required'}),401
    
#     else:
#         return jsonify({'msg':'login has been successfull'}),200
    


@app.route('/characters/create',methods=['POST'])
def characters_create():
    data=request.get_json()
    user_id=data.get('id')

    if user_id is None:
        return jsonify({'msg':'user id is required'}),400
    
    existing_user=db.session.get(User,int(user_id))

    if not existing_user:
        return jsonify({'msg':'user not authorized'}),401
    
    new_character=Character(
        user_id=user_id,
        name=data.get('name'),
        quote=data.get('quote'),
        image=data.get('image'),
        location_city=data.get('location_city')

    )

    db.session.add(new_character)
    db.session.commit()
    return jsonify({'msg':'character succesfully created'}),200






@app.route('/characters/favorites/',methods=['POST'])
def add_favorite():
    data=request.get_json()
    user_id=data.get('user_id')
    character_id=data.get('character_id')

    if not user_id or not character_id:
        return jsonify({'msg':'user_id or character_id are required'}),400

    user=db.session.get(User,user_id)
    character=db.session.get(Character,character_id)

    if not user or not character:
        jsonify({'msg':'user or character are required'}),401

    if character in user.favorites:
        return jsonify({'msg':'character already in favorites'}),402
    
    user.favorites.append(character)

    return jsonify({'msg':'character added in favorites'}),200



@app.route('/users/favorites', methods=['GET'])
def user_favorites():

    data=request.get_json()
    user_id=data.get('user_id')

    user=db.session.get(User,int(user_id))

    if not user:
        return jsonify({'msg':'user not found'}),400

    return jsonify([character.serialize() for character in user.favorites]),200



# 1.Registro de todos los personajers en la base de datos

@app.route('/characters/list',methods=['GET'])
def character_list():

    characters=db.session.execute(select(Character)).scalars().all()

    return jsonify([character.serialize() for character in characters]),200
    



#un solo personaje atraves de su id
@app.route('/character/<int:character_id>', methods=['GET'])
def single_character_by_id(character_id):

    character=db.session.execute(select(Character).where(Character.id == character_id)).scalar_one()

    return jsonify(character.serialize())





@app.route('/location/create', methods=['POST'])
def create_location():
     data=request.get_json()
     user_id=data.get('user_id')

     if user_id is None:
        return jsonify({'msg':'user id is required'}),400
    
     existing_user=db.session.get(User,int(user_id))

     if not existing_user:
        return jsonify({'msg':'user not authorized'}),400
    
     new_location=Location(
       
        name=data.get('name'),
        description=data.get('quote'),
        image=data.get('image'),
    )

     db.session.add(new_location)
     db.session.commit()
     return jsonify({'msg':'location succesfully created'}),200




@app.route('/locations',methods=['GET'])
def locations_list():

    locations=db.session.execute(select(Location)).scalars().all()

    return jsonify([location.serialize() for location in locations]),200
    




#información de una sola ubicación según su id
@app.route('/location/<int:location_id>',methods=['GET'])
def location_by_id(location_id):
    location=db.session.execute(select(Location).where(Location.id == location_id)).scalar_one()

    return jsonify(location.serialize()),200

   
#añade una ubicacion por su id a las ubicaciones favoritas del usuario
@app.route('/favorite/location/<int:location_id>',methods=['POST'])
def add_favorite_location(location_id):
    data=request.get_json()
    user_id=data.get('user_id')

    if not user_id :
        return jsonify({'msg':'user_id is required'}),400

    user=db.session.get(User,user_id)
    location=db.session.get(Location,location_id)

    if not user or not location:
        jsonify({'msg':'user or location are required'}),401

    if location in user.favorite_locations:
        return jsonify({'msg':'location already in favorites'}),402
    
    user.favorite_locations.append(location)

    return jsonify({'msg':'location added in favorites'}),200



#añade una personaje por su id a los personajes favoritos del usuario

@app.route('/favorite/character/<int:character_id>',methods=['POST'])
def add_favorite_character(character_id):
    data=request.get_json()
    user_id=data.get('user_id')

    if not user_id :
        return jsonify({'msg':'user_id is required'}),400

    user=db.session.get(User,user_id)
    character=db.session.get(Character,character_id)

    if not user or not character:
        jsonify({'msg':'user or location are required'}),401

    if character in user.favorites:
        return jsonify({'msg':'location already in favorites'}),402
    
    user.favorites.append(character)

    return jsonify({'msg':'character added in favorites'}),200



# elimina una ubicacion por su id de la lista de ubicaciones favoritas de un usuario
@app.route('/favorite/location/<int:location_id>', methods=['DELETE'])
def delete_favorite_location(location_id):
   data=request.get_json()
   user_id=data.get('user_id')

   if not user_id :
        return jsonify({'msg':'user_id is required'}),400

   user=db.session.get(User,user_id)
   location= db.session.get(Location,int(location_id))

   if not user or not location:
        jsonify({'msg':'user or location are required'}),401

   if location not in user.favorite_locations:

    return jsonify({'msg':'location is not in location-favorite list'}),402

   else:

    db.session.delete(location)
    db.session.commit()

    return jsonify({'msg':'location has been successfully deleted from location-favorite list'}),200
   


# elimina una ubicacion por su id de la lista de ubicaciones favoritas de un usuario
@app.route('/favorite/character/<int:character_id>', methods=['DELETE'])
def delete_favorite_character(character_id):
   data=request.get_json()
   user_id=data.get('user_id')

   if not user_id :
        return jsonify({'msg':'user_id is required'}),400

   user=db.session.get(User,user_id)
   character= db.session.get(Character,int(character_id))

   if not user or not character:
       return jsonify({'msg':'user or charcater are required'}),401

   if character not in user.favorites:

    return jsonify({'msg':'character is not in character-favorite list'}),402

   else:

    db.session.delete(character)
    db.session.commit()

    return jsonify({'msg':'character has been successfully deleted from character-favorite list'}),200
   







# This only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
