from flask import request
import psycopg2
from backend.utils import *
from app import app, conn

# Like a photo (user or visitor)
@app.route('/like-photo', methods=['POST'])
def like_photo():
    data = request.json
    user_id = decode_token(request)
    photo_id = data['photo_id']
    token = None

    if user_id is None:
        res = visitor_signup()

        if res["success"]:
            user_id = res["user_id"]
            token = encode_token(user_id)

    if user_id is None:
        return returnMsg(False, 'Unauthorized', 401)

    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO likes (user_id, photo_id) VALUES (%s, %s)",
                       (user_id, photo_id))
        conn.commit()

        return returnMsg(True, 'Photo liked successfully', 201, {"token": token})
    except psycopg2.Error as e:
        conn.rollback()
        return returnMsg(False, str(e), 400)

# Total likes of a photo, along with their associated users who liked (public)
@app.route('/photo-likes', methods=['GET'])
def photo_likes():
    photo_id = request.args.get('photo_id')

    if photo_id is None:
        return returnMsg(False, 'Photo ID is required', 400)

    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT U.user_id, U.fname, U.lname FROM likes L INNER JOIN users U ON U.user_id = L.user_id WHERE L.photo_id = %s", (photo_id,))
        likes = cursor.fetchall()

        return returnMsg(True, 'Likes of photo are returned', 200, {"users": likes})
    except psycopg2.Error as e:
        return returnMsg(False, str(e), 400)

# All comments of a photo, along with their associated users who commented (public)
@app.route('/photo-comments', methods=['GET'])
def photo_comments():
    photo_id = request.args.get('photo_id')

    if photo_id is None:
        return returnMsg(False, 'Photo ID is required', 400)

    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT U.user_id, U.fname, U.lname, C.text FROM comments C INNER JOIN users U ON U.user_id = C.user_id WHERE C.photo_id = %s", (photo_id,))
        comments = cursor.fetchall()

        return returnMsg(True, 'Comments of photo are returned', 200, {"comments": comments})
    except psycopg2.Error as e:
        return returnMsg(False, str(e), 400)

# Comment search, returns names of users, and photos with matching comments (public)
@app.route('/comment-search', methods=['POST'])
def comment_search():
    comment = request.json['comment']

    if comment is None:
        return returnMsg(False, 'Comment is required', 400)

    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT U.user_id, U.fname, U.lname, COUNT(C.text) as comment_count FROM comments C INNER JOIN users U ON U.user_id = C.user_id WHERE C.text = %s AND U.is_visitor = FALSE GROUP BY U.user_id ORDER BY comment_count DESC", (comment,))
        comments = cursor.fetchall()

        return returnMsg(True, 'Comments with matching comment are returned', 200, {"comments": comments})
    except psycopg2.Error as e:
        return returnMsg(False, str(e), 400)


def visitor_signup():
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (is_visitor) VALUES (TRUE) RETURNING user_id")
        conn.commit()

        user_id = cursor.fetchone()[0]
        res = {"success": True, "user_id": user_id}
        return res
    except psycopg2.Error as e:
        conn.rollback()
        return {"success": False}

# Add comment to a photo (user or visitor – should exist on the users table)
@app.route('/add-comment', methods=['POST'])
def add_comment():
    data = request.json
    user_id = decode_token(request)
    photo_id = data['photo_id']
    comment = data['comment']
    token = None

    if user_id is None:
        res = visitor_signup()

        if res["success"]:
            user_id = res["user_id"]
            token = encode_token(user_id)

    if comment is None:
        return returnMsg(False, 'Comment is required', 400)

    if photo_id is None:
        return returnMsg(False, 'Photo ID is required', 400)

    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT A.user_id FROM photos P INNER JOIN albums A ON A.album_id = P.album_id WHERE P.photo_id = %s", (photo_id,))
        album_owner_id = cursor.fetchone()[0]

        if (user_id == album_owner_id):
            return returnMsg(False, 'You can\'t add a comment to your own photo', 401)

        cursor.execute("INSERT INTO comments (user_id, photo_id, text) VALUES (%s, %s, %s)",
                       (user_id, photo_id, comment))
        conn.commit()

        return returnMsg(True, 'Comment added successfully', 201, {"token": token})
    except psycopg2.Error as e:
        conn.rollback()
        return returnMsg(False, str(e), 400)
