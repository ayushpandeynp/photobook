from flask import jsonify


def returnMsg(success, message, status_code, data=None):
    if data:
        return jsonify({'success': success, 'message': message, 'data': data}), status_code
    else:
        return jsonify({'success': success, 'message': message}), status_code
