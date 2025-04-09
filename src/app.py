"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_cors import CORS
from utils import APIException, generate_sitemap
from datastructures import FamilyStructure
# from models import Person


app = Flask(__name__)
app.url_map.strict_slashes = False
CORS(app)

# Create the jackson family object
jackson_family = FamilyStructure("Jackson")


# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code


# Generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)


@app.route('/members', methods=['GET'])
def handle_hello():
    # This is how you can use the Family datastructure by calling its methods
    members = jackson_family.get_all_members()
    #response_body = {"hello": "world",
                     #"family": members}
    return jsonify(members), 200

@app.route('/members/<int:member_id>', methods=['GET'])
def get_family_member(member_id):
    member = jackson_family.get_member(member_id)
    if member:
        return jsonify(member), 200
    else:
        return jsonify({"msg": "Member not found"}), 404
    
@app.route('/members', methods=['POST'])
def add_new_member():
    request_body = request.get_json()
    if request_body is None:
        return jsonify({"msg": "Request body is missing"}), 400

    required_fields = ["first_name", "age", "lucky_numbers"]
    if not all(field in request_body for field in required_fields):
        return jsonify({"msg": "Missing required fields: first_name, age, lucky_numbers"}), 400

    # Asegurarse de que age sea un entero y mayor que 0
    if not isinstance(request_body.get("age"), int) or request_body.get("age") <= 0:
        return jsonify({"msg": "Age must be a positive integer"}), 400

    # Asegurarse de que lucky_numbers sea una lista
    if not isinstance(request_body.get("lucky_numbers"), list):
        return jsonify({"msg": "Lucky numbers must be a list"}), 400

    jackson_family.add_member(request_body)
    return jsonify({"msg": "Member added successfully"}), 200

@app.route('/members/<int:member_id>', methods=['DELETE'])
def delete_family_member(member_id):
    member = jackson_family.get_member(member_id)
    if not member:
        return jsonify({"msg": "Member not found"}), 404

    jackson_family.delete_member(member_id)
    return jsonify({"done": True}), 200


# This only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=True)
