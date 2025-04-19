from flask import Blueprint, request
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

    # Optional fields
    photo_url = data.get('photoUrl')
    block_number = data.get('blockNumber')
    flat_number = data.get('flatNumber')
    parking_number = data.get('parkingNumber')

    try:
        # Only supported fields passed to Firebase
        user = auth.create_user(
            email=data['email'],
            password=data['password'],
            display_name=data['displayName'],
            photo_url=photo_url
        )

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO users (
                email, firebase_uid, display_name, photo_url,
                block_number, flat_number, parking_number
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id
        """, (
            data['email'], user.uid, data['displayName'], photo_url,
            block_number, flat_number, parking_number
        ))
        user_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()

        return custom_response(201, 'User registered successfully',
                               {
                                   'uid': user.uid,
                                   'email': user.email,
                                   'userId': user_id,
                                   'photo_url': photo_url,
                                   'block_number': block_number,
                                   'flat_number': flat_number,
                                   'parking_number': parking_number
                               })

    except auth.EmailAlreadyExistsError:
        return custom_response(409, 'Email already exists', None)
    except exceptions.FirebaseError as e:
        return custom_response(400, f'Firebase error: {str(e)}', None)



@auth_bp.route('/login', methods=['POST'])
def login():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return custom_response(400, 'Missing or invalid Authorization header', None)

    id_token = auth_header.split('Bearer ')[1]

    try:
        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token['uid']

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT id, email, display_name, photo_url
            FROM users
            WHERE firebase_uid = %s
        """, (uid,))
        user_data = cur.fetchone()
        cur.close()
        conn.close()

        if not user_data:
            return custom_response(404, 'User not found', None)

        return custom_response(200, 'Login successful',
                               {
                                   'id': user_data[0],
                                   'email': user_data[1],
                                   'displayName': user_data[2],
                                   'photo_url': user_data[3]  # Might be None
                               })

    except exceptions.FirebaseError as e:
        return custom_response(401, f'Authentication failed: {str(e)}', None)
