from flask import Blueprint, request, jsonify
from firebase_admin import auth, exceptions
from .database import get_db_connection
from .utils import custom_response

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data:
        return custom_response(400, 'No data provided', None)

    required_fields = ['email', 'password', 'displayName']
    missing = [field for field in required_fields if field not in data]
    if missing:
        return custom_response(400, f'Missing fields: {", ".join(missing)}', None)

    try:
        user = auth.create_user(
            email=data['email'],
            password=data['password'],
            display_name=data['displayName']
        )

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO users (email, firebase_uid, display_name) VALUES (%s, %s, %s) RETURNING id",
                    (data['email'], user.uid, data['displayName']))
        user_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()

        return custom_response(201, 'User registered successfully',
                               {'uid': user.uid, 'email': user.email, 'userId': user_id})

    except auth.EmailAlreadyExistsError:
        return custom_response(409, 'Email already exists', None)
    except exceptions.FirebaseError as e:
        return custom_response(400, f'Firebase error: {str(e)}', None)


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or 'idToken' not in data:
        return custom_response(400, 'Missing idToken', None)

    try:
        decoded_token = auth.verify_id_token(data['idToken'])
        uid = decoded_token['uid']

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, email, display_name FROM users WHERE firebase_uid = %s", (uid,))
        user_data = cur.fetchone()
        cur.close()
        conn.close()

        if not user_data:
            return custom_response(404, 'User not found', None)

        return custom_response(200, 'Login successful',
                               {'id': user_data[0], 'email': user_data[1], 'displayName': user_data[2]})

    except exceptions.FirebaseError as e:
        return custom_response(401, f'Authentication failed: {str(e)}', None)
    