from firebase_admin import auth
from flask import Flask, request, jsonify, Blueprint
from flask_jwt_extended import decode_token

from app.database import get_db_connection
from app.utils import custom_response

social = Blueprint('social', __name__)

@social.route('/upload_social', methods=['POST'])
def upload_social():
    data = request.get_json()
    if not data:
        return jsonify({"status": 400, "message": "Missing data"}), 400

    required_fields = ['title', 'caption', 'photo_url']
    missing = [field for field in required_fields if field not in data]
    if missing:
        return jsonify({"status": 400, "message": "Missing data"}), 400

    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer'):
        return custom_response(400, 'Missing Authorization header' , None)

    id_token = auth_header.split('Bearer ')[1]

    try:
        decode_token = auth.verify_id_token(id_token)
        uid = decode_token['uid']
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO social (firebase_uid, title, caption, photo_url)
            VALUES (%s, %s, %s, %s)
            """ , (
                uid,
                data['title'],
                data['caption'],
                data['photo_url'],
            )
        )
        conn.commit()
        cur.close()
        conn.close()

        return jsonify( 'Post Uploaded Successfully',
                               {
                                   'uid' : uid,
                                   'title' : data['title'],
                                   'caption' : data['caption'],
                                   'photo_url' : data['photo_url']
                               }),200,

    except Exception as e:
        return jsonify({"status": 400, "message": str(e)}), 400

@social.route('/getpost', methods=['GET'])
def get_post():

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, title, caption, photo_url, created_at FROM social")
        social = cur.fetchall()
        cur.close()
        conn.close()

        socials_data = [
            {
                "id": social[0],
                "title": social[1],
                "caption": social[2],
                "photo_url": social[3],
                "created_at": social[4]
            } for social in social
        ]

        return jsonify({
            "status": 200,
            "message": "Post retrieved successfully",
            "socials": socials_data,
        }),200

    except Exception as e:
        return jsonify({"status": 400, "message": str(e)}), 400
