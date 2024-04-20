from flask import request
import psycopg2
from utils import *
from app import app, conn

# list photos by tag name (public)
@app.route('/photos-with-tags', methods=['GET'])
def photos_with_tags_public():
    tag = request.json['tag']

    if tag is None:
        return returnMsg(False, 'Tag is required', 400)

    try:
        cursor = conn.cursor()
        
        # with limit of 100 photos
        cursor.execute("SELECT photo_id, caption, path, album_id FROM photos WHERE photo_id IN (SELECT photo_id FROM tags WHERE tag_name = %s) LIMIT 100", (tag,))
        photos = cursor.fetchall()
        
        return returnMsg(True, 'Photos with tag are returned', 200, {"photos": photos})
    except psycopg2.Error as e:
        return returnMsg(False, str(e), 400)
    

# list photos by tag name (user scope)
@app.route('/photos-with-tags-user', methods=['GET'])
def photos_with_tags_user():
    tag = request.json['tag']
    user_id = decode_token(request)

    if tag is None:
        return returnMsg(False, 'Tag is required', 400)

    if user_id is None:
        return returnMsg(False, 'Unauthorized', 401)

    try:
        cursor = conn.cursor()
        
        cursor.execute("SELECT P.photo_id, P.caption, P.path, P.album_id FROM photos P INNER JOIN albums A ON A.album_id = P.album_id WHERE P.photo_id IN (SELECT photo_id FROM tags WHERE tag_name = %s) AND A.user_id = %s", (tag, user_id))
        photos = cursor.fetchall()
        
        return returnMsg(True, 'Photos with tag are returned', 200, {"photos": photos})
    except psycopg2.Error as e:
        return returnMsg(False, str(e), 400)
    
# list 10 most popular tags (public)
@app.route('/popular-tags', methods=['GET'])
def popular_tags():
    try:
        cursor = conn.cursor()
        
        cursor.execute("SELECT tag_name, COUNT(photo_id) FROM tags GROUP BY tag_name ORDER BY COUNT(photo_id) DESC LIMIT 10")
        tags = cursor.fetchall()
        
        return returnMsg(True, 'Popular tags are returned', 200, {"tags": tags})
    except psycopg2.Error as e:
        return returnMsg(False, str(e), 400)