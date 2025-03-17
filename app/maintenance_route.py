from flask import Flask, request, jsonify, Blueprint
from .database import get_db_connection

maintenance_route = Blueprint('maintenance', __name__)

@maintenance_route.route('/maintenance', methods=['GET'])
def maintenance():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM maintenance")
        maintenance_data = cur.fetchall()
        cur.close()

