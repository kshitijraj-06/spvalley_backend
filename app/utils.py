from flask import jsonify

def custom_response(status, message, data):
    return jsonify({'status': status, 'message': message, 'data': data}), status
