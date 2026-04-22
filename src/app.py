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
from models import db, User, Character, Fruit, FavoriteCharacter, FavoriteFruit
from sqlalchemy import select
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/user', methods=['GET'])
def get_users():
    users = db.session.execute(select(User)).scalars().all()
    return jsonify([u.serialize() for u in users]), 200

#Para Todos los usuarios
@app.route("/character", methods=['GET'])
def get_all_character():
    results = db.session.execute(select(Character)).scalars().all()
    return jsonify([char.serialize() for char in results]), 200

#Para un solo usuario

@app.route("/character/<int:character_id>", methods=['GET'])
def get_one_character(character_id):
    char = db.session.get(Character, character_id)
    if not char: return jsonify({"msg": "No existe"}), 404
    return jsonify(char.serialize()), 200

@app.route('/character', methods=['POST'])
def add_character():
    body = request.get_json()
    if "name" not in body: return jsonify({"msg": "Nombre no encontrado"})

    new_char = Character(name=body['name'], role=body.get('role'), bounty=body.get('bounty'))
    db.session.add(new_char)
    db.session.commit()
    return jsonify(new_char.serialize()), 200

@app.route('/character/<int:id>', methods=['DELETE'])
def delete_character(id):
    char = db.get(Character,id)
    if not char: return jsonify({"msg": "Personaje no encontrado"}), 404
    db.session.delete(char)
    db.session.commit()
    return jsonify({"msg": "Personaje borrado correctamente"}), 200

#Frutas

@app.route('/Fruit', methods=['GET'])
def get_all_fruits():
    results = db.session.execute(select(Fruit)).scalars().all()
    return jsonify([f.serialize() for f in results]), 200

@app.route('/Fruit', methods=['POST'])
def add_fruit():
    body = request.get_json()
    new_fruit = Fruit(name=body['name'], type=body.get('type'))
    db.session.add(new_fruit)
    db.session.commit()
    return jsonify(new_fruit.serialize()), 201

@app.route('/Fruit/<int:id>', methods=['DELETE'])
def delete_fruit(id):
    fruit = db.session.get(Fruit, id)
    if not fruit: return jsonify({"msg": "Fruta no encontrada"}), 404
    db.session.delete(fruit)
    db.session.commit()
    return jsonify({"msg": "Fruta eliminada correctamente"}), 200

#Favoritos Character

@app.route('/favorite/character/<int:character_id>', methods=['POST'])
def add_fav_character(character_id):
    # Verificar si el personaje existe
    char = db.session.get(Character, character_id)
    if not char: return jsonify({"msg": "Character does not exist"}), 404
    
    # Verificar si ya es favorito para este usuario
    exists = db.session.execute(select(FavoriteCharacter).filter_by(user_id=1, character_id=character_id)).scalar()
    if exists: return jsonify({"msg": "Already in favorites"}), 400

    new_fav = FavoriteCharacter(user_id=1, character_id=character_id)
    db.session.add(new_fav)
    db.session.commit()
    return jsonify({"msg": "Favorite character added"}), 201

@app.route('/favorite/character/<int:character_id>', methods=['DELETE'])
def remove_fav_character(character_id):
    fav = db.session.execute(select(FavoriteCharacter).filter_by(user_id=1, character_id=character_id)).scalar()
    if not fav: return jsonify({"msg": "Favorite not found"}), 404
    
    db.session.delete(fav)
    db.session.commit()
    return jsonify({"msg": "Favorite character removed"}), 200

# Frutas Favoritas

@app.route('/favorite/fruit/<int:fruit_id>', methods=['POST'])
def add_fav_fruit(fruit_id):
    fruit = db.session.get(Fruit, fruit_id)
    if not fruit: return jsonify({"msg": "Fruit does not exist"}), 404

    new_fav = FavoriteFruit(user_id=1, fruit_id=fruit_id)
    db.session.add(new_fav)
    db.session.commit()
    return jsonify({"msg": "Favorite fruit added"}), 201

@app.route('/favorite/fruit/<int:fruit_id>', methods=['DELETE'])
def remove_fav_fruit(fruit_id):
    fav = db.session.execute(select(FavoriteFruit).filter_by(user_id=1, fruit_id=fruit_id)).scalar()
    if not fav: return jsonify({"msg": "Favorite not found"}), 404
    
    db.session.delete(fav)
    db.session.commit()
    return jsonify({"msg": "Favorite fruit removed"}), 200


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)