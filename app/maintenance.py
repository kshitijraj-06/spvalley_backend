from flask import Flask, request, jsonify, Blueprint

maintenance = Blueprint('maintenance',__name__)

@maintenance.route('/maintenance',methods=['GET'])
def maintenance_page():
    return jsonify({'message':'Server is under maintenance'})