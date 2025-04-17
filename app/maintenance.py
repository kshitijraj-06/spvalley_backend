from firebase_admin import auth
from flask import Flask, request, jsonify, Blueprint

from app.database import get_db_connection
from app.utils import custom_response

maintenance = Blueprint('maintenance',__name__)

@maintenance.route('/maintenance',methods=['GET'])
def maintenance_page():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer'):
        return custom_response(400, 'Missing Authorization header', None)

    id_token = auth_header.split('Bearer ')[1]
    try:
        decode_token = auth.verify_id_token(id_token)
        uid = decode_token['uid']

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, email, display_name, photo_url, block_number, flat_number, parking_number FROM users WHERE firebase_uid = %s", (uid,))
        user_data = cur.fetchone()
        cur.execute("""
                    SELECT id, amount, due_date, status, created_at
                    FROM maintenance
                    WHERE firebase_uid = %s
                """, (uid,))

        maintenance_data = cur.fetchone()
        cur.close()
        conn.close()

        if not maintenance_data or not user_data:
            return custom_response(404, 'User not found', None)

        maintenance_data = {
            "id": maintenance_data[0],
            "amount": float(maintenance_data[1]),
            "status": maintenance_data[2],
            "due_date": maintenance_data[3],
            "user_id": user_data[0],
            "email": user_data[1],
            "displayName": user_data[2],
            "photo_url": user_data[3],
            "block_number": user_data[4],
            "flat_number": user_data[5],
            "parking_number": user_data[6],
        }

        return jsonify({"status": 200,"message" : "Maintenance retrieved" , "data": maintenance_data}), 200

    except auth.InvalidIdTokenError:
        return custom_response(400, 'Invalid ID Token', None)
    except Exception as e:
        return custom_response(500,str(e),None)
