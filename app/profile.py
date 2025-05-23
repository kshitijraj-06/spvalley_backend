from firebase_admin import auth
from flask import Blueprint, jsonify, Flask, request

from app.database import get_db_connection
from app.utils import custom_response

profile = Blueprint('profile', __name__)

@profile.route('/profile', methods=['GET'])
def get_profile():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return custom_response(400, 'Missing or invalid Authorization header', None)

    id_token = auth_header.split('Bearer ')[1]
    try:
        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token['uid']

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, email, display_name, photo_url, block_number, flat_number, parking_number FROM users WHERE firebase_uid = %s", (uid,))
        user_data = cur.fetchone()
        cur.close()
        conn.close()

        if not user_data:
            return jsonify({"status": 404, "message": "User not found"}), 404

        user_profile = {
                "id" : user_data[0],
                "email" : user_data[1],
                "displayName" : user_data[2],
                "photo_url" : user_data[3],
                "block_number" : user_data[4],
                "flat_number" : user_data[5],
                "parking_number" : user_data[6],
        }

        return jsonify({"status": 200, "message": "User profile retrieved successfully", "userProfile": user_profile}), 200

    except auth.InvalidIdTokenError:
        return jsonify({"status": 401, "message": "Invalid idToken"}), 401
    except Exception as e:
        return jsonify({"status": 500, "message": "Error retrieving user profile", "error": str(e)}), 500