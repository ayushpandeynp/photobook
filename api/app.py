from flask import Flask
from flask_bcrypt import Bcrypt
import psycopg2
from dotenv import load_dotenv
import os
from utils import *

load_dotenv()

app = Flask(__name__)
bcrypt = Bcrypt(app)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

# DB CREDS from .env
conn = psycopg2.connect(
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASS"),
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT")
)

@app.before_request
def only_json():
    if not request.is_json:
        return returnMsg(False, 'Only JSON body is allowed', 400)

@app.route('/', methods=['GET'])
def main():
    return returnMsg(True, 'api service is up and running', 200)

from friends import *
from login import *

    
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
