from flask import request
import psycopg2
from utils import *
from app import app, conn

# add friend (user scope)
@app.route('/add-friend', methods=['POST'])
def add_friend():
    data = request.json
    user_id = decode_token(request)

    try:
        friend_id = data['friend_id']
        
        cursor = conn.cursor()
        cursor.execute("INSERT into friends (user_id, friend_id) VALUES(%s, %s)",
                       (user_id,friend_id))
        conn.commit()
        
        return returnMsg(True, 'Friend Added Successfully', 201)
    
    # not legitimate error
    except psycopg2.Error as e:
        conn.rollback()
        return returnMsg(False, str(e), 400)