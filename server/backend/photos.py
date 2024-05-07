from flask import request
import psycopg2
from backend.utils import *
from app import app, conn
import os
import uuid

# list all photos (public)


@app.route('/list-photos', methods=['GET'])
def list_photos_public():
    try:
        cursor = conn.cursor()

        cursor.execute("SELECT P.photo_id, P.caption, P.path, A.album_name, U.fname, U.lname FROM photos P INNER JOIN albums A ON P.album_id = A.album_id INNER JOIN users U ON A.user_id = U.user_id LIMIT 100")
        photos = cursor.fetchall()

        return returnMsg(True, 'Photos are returned', 200, {"photos": photos})
    except psycopg2.Error as e:
        conn.rollback()
        return returnMsg(False, str(e), 400)


def upload_photo(file):
    folderpath = 'static/images'
    os.makedirs(folderpath, exist_ok=True)

    # random filename
    filename = str(uuid.uuid4())
    extension = file.filename.split('.')[-1]
    path = f'{folderpath}/{filename}.{extension}'
    file.save(path)
    return path

# add a photo (user scope)


@app.route('/add-photo', methods=['POST'])
def add_photo():
    data = request.form
    user_id = decode_token(request)

    if user_id is None:
        return returnMsg(False, 'Unauthorized', 401)

    try:
        photo = request.files['photo']
        caption = data.get('caption')
        album_name = data.get('album')
        tags = data.get('tags').replace(r" ", "").split(",")

        if not photo or not caption or not album_name:
            return returnMsg(False, 'Caption, photo, and album name are required', 400)

        cursor = conn.cursor()

        # get album_id
        cursor.execute(
            "SELECT album_id FROM albums WHERE album_name = %s AND user_id = %s", (album_name, user_id))
        album_id = cursor.fetchone()[0]

        if album_id is None:
            return returnMsg(False, 'Album not found', 404)

        # upload photo write path to database
        path = upload_photo(photo)

        cursor.execute("INSERT INTO photos (caption, path, album_id) VALUES (%s, %s, %s) RETURNING photo_id",
                       (caption, path, album_id))
        photo_id = cursor.fetchone()[0]

        # insert tags
        for tag in tags:
            if tag != "":
                cursor.execute(
                    "INSERT INTO tags (photo_id, tag_name) VALUES (%s, %s)", (photo_id, tag))

        conn.commit()
        cursor.close()

        return returnMsg(True, 'Photo added successfully', 201)

    except psycopg2.Error as e:
        conn.rollback()
        return returnMsg(False, str(e), 400)

# list photos by tag name (public)


@app.route('/photos-with-tags', methods=['GET'])
def photos_with_tags_public():
    tag = request.args.get('tag')

    if tag is None:
        return returnMsg(False, 'Tag is required', 400)

    try:
        cursor = conn.cursor()

        # with limit of 100 photos
        cursor.execute(
            "SELECT P.photo_id, P.caption, P.path, A.album_name, U.fname, U.lname FROM photos P INNER JOIN albums A ON P.album_id = A.album_id INNER JOIN users U ON A.user_id = U.user_id WHERE photo_id IN (SELECT photo_id FROM tags WHERE tag_name = %s) LIMIT 100", (tag,))
        photos = cursor.fetchall()

        return returnMsg(True, 'Photos with tag are returned', 200, {"photos": photos})
    except psycopg2.Error as e:
        conn.rollback()
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
        conn.rollback()
        return returnMsg(False, str(e), 400)

# list 10 most popular tags (public)


@app.route('/popular-tags', methods=['GET'])
def popular_tags():
    try:
        cursor = conn.cursor()

        cursor.execute(
            "SELECT tag_name, COUNT(photo_id) FROM tags GROUP BY tag_name ORDER BY COUNT(photo_id) DESC LIMIT 10")
        tags = cursor.fetchall()

        return returnMsg(True, 'Popular tags are returned', 200, {"tags": tags})
    except psycopg2.Error as e:
        conn.rollback()
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
        conn.rollback()
        return returnMsg(False, str(e), 400)

# list albums user-scope


@app.route('/list-albums', methods=['GET'])
def list_albums():
    user_id = decode_token(request)
    if user_id is None:
        return returnMsg(False, 'Unauthorized', 401)
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT album_name, datetime FROM albums WHERE user_id = %s", (user_id,))
        albums = cursor.fetchall()
        cursor.close()

        album_list = [{"album_name": album[0], "datetime": album[1]}
                      for album in albums]

        return returnMsg(True, 'Albums retrieved successfully', 200, {"albums": album_list})

    except psycopg2.Error as e:
        conn.rollback()
        return returnMsg(False, str(e), 400)

# list albums public scope


@app.route('/list-albums-public', methods=['GET'])
def list_albums_public():
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT album_name, album_id, datetime FROM albums")
        albums = cursor.fetchall()
        cursor.close()

        album_list = [{"album_name": album[0], "album_id": album[1], "datetime": album[2]}
                      for album in albums]

        return returnMsg(True, 'Albums retrieved successfully', 200, {"albums": album_list})

    except psycopg2.Error as e:
        conn.rollback()
        return returnMsg(False, str(e), 400)

# List all photos, by album (public)


@app.route('/list-photos-by-album', methods=['GET'])
def list_photos_by_album():
    try:
        album_id = request.args.get('album_id')
        print(album_id)
        if album_id is None:
            return returnMsg(False, 'Album is required', 400)

        cursor = conn.cursor()
        cursor.execute("SELECT P.photo_id, P.caption, P.path, A.album_name, U.fname, U.lname FROM photos P INNER JOIN albums A ON P.album_id = A.album_id INNER JOIN users U ON A.user_id = U.user_id WHERE A.album_id = %s LIMIT 100", (album_id,))
        photos = cursor.fetchall()
        cursor.close()

        return returnMsg(True, 'Photos retrieved successfully', 200, {"photos": photos})

    except psycopg2.Error as e:
        conn.rollback()
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
        cursor.execute(
            "DELETE FROM albums WHERE album_name = %s AND user_id = %s", (album_name, user_id))
        conn.commit()
        cursor.close()

        return returnMsg(True, 'Album deleted successfully', 200)

    except psycopg2.Error as e:
        conn.rollback()
        return returnMsg(False, str(e), 400)


# Top 10 users who make the largest contribution (comments + photos count) (public)
@app.route('/top-contributors', methods=['GET'])
def top_contributors():
    try:
        cursor = conn.cursor()

        cursor.execute("SELECT U.user_id, U.fname, U.lname, COUNT(P.photo_id) + COUNT(C.comment_id) AS contribution FROM users U LEFT JOIN albums A ON U.user_id = A.user_id LEFT JOIN photos P ON A.album_id = P.album_id LEFT JOIN comments C ON U.user_id = C.user_id GROUP BY U.user_id HAVING COUNT(P.photo_id) + COUNT(C.comment_id) > 0 ORDER BY contribution DESC LIMIT 10")
        contributors = cursor.fetchall()

        return returnMsg(True, 'Top contributors are returned', 200, {"contributors": contributors})
    except psycopg2.Error as e:
        conn.rollback()
        return returnMsg(False, str(e), 400)

# You-may-also-like functionality (user scope)


@app.route('/you-may-also-like', methods=['GET'])
def you_may_also_like():
    user_id = decode_token(request)

    if user_id is None:
        return returnMsg(False, 'Unauthorized', 401)

    try:
        cursor = conn.cursor()

        # five most commonly used tags among the user's photos
        cursor.execute("""
            SELECT tag_name, COUNT(tag_name) as tag_count
            FROM tags
            WHERE photo_id IN (
                SELECT photo_id FROM photos WHERE album_id IN (
                    SELECT album_id FROM albums WHERE user_id = %s
                )
            )
            GROUP BY tag_name
            ORDER BY tag_count DESC
            LIMIT 5
        """, (user_id,))
        user_tags = cursor.fetchall()
        user_tags = [tag[0] for tag in user_tags]  # just the tag names

        if (len(user_tags) > 0):
            # get recommended photos
            cursor.execute("""
                SELECT P.photo_id, P.caption, P.path, COUNT(T.tag_name) as matched_tags, A.album_name, U.fname, U.lname 
                FROM photos P
                INNER JOIN tags T ON P.photo_id = T.photo_id
                INNER JOIN albums A ON P.album_id = A.album_id
                INNER JOIN users U ON A.user_id = U.user_id
                WHERE T.tag_name IN %s
                AND U.user_id != %s
                GROUP BY P.photo_id, P.caption, P.path, A.album_name, U.fname, U.lname
                ORDER BY matched_tags DESC
                LIMIT 10
            """, (tuple(user_tags),) + (user_id,))

            recommended_photos = cursor.fetchall()

            # formatted result
            formatted_photos = [{
                "photo_id": photo[0],
                "caption": photo[1],
                "path": photo[2],
                "album_name": photo[4],
                "fname": photo[5],
                "lname": photo[6]
            } for photo in recommended_photos]

        else:
            formatted_photos = []

        return returnMsg(True, 'Recommended photos are returned', 200, {"photos": formatted_photos})
    except psycopg2.Error as e:
        conn.rollback()
        return returnMsg(False, str(e), 400)
