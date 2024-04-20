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
    
# create an album (user scope)
@app.route('/create-album', methods=['POST'])
def create_album():
    data = request.json
    user_id = decode_token(request)
    if user_id is None:
        return returnMsg(False, 'Unauthorized', 401)

    try:
        album_name = data['album_name']
        
        if not album_name:
            return returnMsg(False, 'Album name is required', 400)

        cursor = conn.cursor()
        cursor.execute("INSERT INTO albums (album_name, user_id) VALUES (%s, %s)",
                       (album_name, user_id))
        conn.commit()
        cursor.close()
        
        return returnMsg(True, 'Album created successfully', 200)
        
    except psycopg2.Error as e:
        return returnMsg(False, str(e), 400)

# list albums user-scope
@app.route('/list-albums', methods=['GET'])
def list_albums():
    user_id = decode_token(request)
    if user_id is None:
        return returnMsg(False, 'Unauthorized', 401)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT album_name, datetime FROM albums WHERE user_id = %s", (user_id,))
        albums = cursor.fetchall()
        cursor.close()

        album_list = [{"album_name": album[0], "datetime": album[1]} for album in albums]
        
        return returnMsg(True, 'Albums retrieved successfully', 200, {"albums": album_list})
        
    except psycopg2.Error as e:
        return returnMsg(False, str(e), 400)
    
# list albums public scope
@app.route('/list-albums-public', methods=['GET'])
def list_albums_public():
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT album_name, datetime FROM albums")
        albums = cursor.fetchall()
        cursor.close()

        album_list = [{"album_name": album[0], "datetime": album[1]} for album in albums]
        
        return returnMsg(True, 'Albums retrieved successfully', 200, {"albums": album_list})
        
    except psycopg2.Error as e:
        return returnMsg(False, str(e), 400)

# List all photos, by album (public) 
@app.route('/list-photos-by-album', methods=['GET'])
def list_photos_by_album():
    data = request.json
    try:
        album_name = data['album_name']
        if album_name is None:
            return returnMsg(False, 'Album name is required', 400)
        
        cursor = conn.cursor()
        cursor.execute("SELECT photo_id, caption, path FROM photos WHERE album_id = (SELECT album_id FROM albums WHERE album_name = %s)", (album_name,))
        photos = cursor.fetchall()
        cursor.close()
        
        return returnMsg(True, 'Photos retrieved successfully', 200, {"photos": photos})
        
    except psycopg2.Error as e:
        return returnMsg(False, str(e), 400)

# Delete album (user scope)
@app.route('/delete-album', methods=['DELETE'])
def delete_album():
    data = request.json
    user_id = decode_token(request)
    if user_id is None:
        return returnMsg(False, 'Unauthorized', 401)
    try:
        album_name = data['album_name']
        if album_name is None:
            return returnMsg(False, 'Album name is required', 400)
        
        cursor = conn.cursor()
        cursor.execute("DELETE FROM albums WHERE album_name = %s AND user_id = %s", (album_name, user_id))
        conn.commit()
        cursor.close()
        
        return returnMsg(True, 'Album deleted successfully', 200)
        
    except psycopg2.Error as e:
        return returnMsg(False, str(e), 400)
    
