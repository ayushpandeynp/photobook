from flask import jsonify
import jwt
import os

def returnMsg(success, message, status_code, data=None):
    if data:
        return jsonify({'success': success, 'message': message, 'data': data}), status_code
    else:
        return jsonify({'success': success, 'message': message}), status_code

def decode_token(request):
    token = request.headers.get('Authorization')
    if not token:
        return None

    try:
        decoded_token = jwt.decode(
            token, os.getenv('SECRET_KEY'), algorithms=['HS256'])
        user_id = decoded_token['user_id']

        return user_id
    except (jwt.DecodeError, jwt.ExpiredSignatureError):
        return None
