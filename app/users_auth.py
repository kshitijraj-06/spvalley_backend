from flask import Flask, Blueprint, request, jsonify
from .database import get_db_connection


users_auth = Blueprint('users_auth', __name__)

@users_auth.route('/get_users', methods=['GET'])
def get_users():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, email, display_name FROM users")
        users = cur.fetchall()
        cur.close()
        conn.close()

        users_list = [
            {"id" : user[0], "email" : user[1], "displayName" : user[2]} for user in users
        ]

        return jsonify({"status": 200, "message": "Users retrieved successfully", "users": users_list}), 200

    except Exception as e:
        return jsonify({"status": 500, "message": "Error retrieving users", "error": str(e)}), 500