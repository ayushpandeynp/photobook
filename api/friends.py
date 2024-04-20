from flask import request
import psycopg2
from utils import *
from app import app, conn

# add friend (user scope)
@app.route('/add-friend', methods=['POST'])
def add_friend():
    data = request.json
    user_id = decode_token(request)

    if user_id is None:
        return returnMsg(False, 'Unauthorized', 401)

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
    
# search for users by name (user scope)
@app.route('/list-friends', methods=['GET'])
def list_friends():
    data = request.json
    user_id = decode_token(request)
    
    if user_id is None:
        return returnMsg(False, 'Unauthorized', 401)
        
    try:   
        cursor = conn.cursor()
        cursor.execute("SELECT friend_id FROM friends WHERE user_id = %s", (user_id,))
        results = cursor.fetchall()
        
        friend_list = []
        for res in results:
            friend_id = res[0] 
            cursor.execute("SELECT fname, lname, email FROM users WHERE user_id = %s", (friend_id,))
            friend_details = cursor.fetchone()
            friend_list.append({
                "fname": friend_details[0],
                "lname": friend_details[1],
                "email": friend_details[2]
            })
            
        cursor.close()
        return returnMsg(True, 'Friend list retrieved successfully', 200, {"friends": friend_list})

    except psycopg2.Error as e:
        return returnMsg(False, str(e), 400)

    
# search for users by name
@app.route('/search-users', methods=['GET'])
def search_friend():
    user_id = decode_token(request)

    if user_id is None:
        return returnMsg(False, 'Unauthorized', 401)
    
    name = request.json['name']

    if name is None:
        return returnMsg(False, 'Name is required', 400)

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT user_id, fname, lname, email FROM users WHERE (fname || ' ' || lname) ILIKE %s AND user_id != %s", (f'%{name}%', user_id))
        friends = cursor.fetchall()
        
        return returnMsg(True, 'Friends is returned', 200, {"friends": friends})
    except psycopg2.Error as e:
        return returnMsg(False, str(e), 400)