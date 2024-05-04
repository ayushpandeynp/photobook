from flask import request, render_template
import psycopg2
from backend.utils import *
from app import app, conn

# login page
@app.route('/login-page', methods=['GET'])
def login_page():
   return render_template('login.html')

# signup page
@app.route('/signup-page', methods=['GET'])
def sign_page():
   return render_template('signup.html')

# dashboard page
@app.route('/', methods=['GET'])
def dashboard():
   return render_template('dashboard.html')

# friends page
@app.route('/friends-page', methods=['GET'])
def friends_page():
   return render_template('friends.html')

# photo view page
@app.route('/photo-view', methods=['GET'])
def photo_view():
   return render_template('photo.html')

# add album page
@app.route('/add-album-page', methods=['GET'])
def add_album_page():
   return render_template('add-album.html')

# add photo page
@app.route('/add-photo-page', methods=['GET'])
def add_photo_page():
   return render_template('add-photo.html')

# search photo page
@app.route('/search-photos-page', methods=['GET'])
def search_photo_page():
   return render_template('search-photos.html')

# view album photos
@app.route('/album-photos-page', methods=['GET'])
def search_album_photos_page():
   return render_template('album-photos.html')

# view tag photos
@app.route('/tag-photos-page', methods=['GET'])
def search_tag_photos_page():
   return render_template('tag-photos.html')
