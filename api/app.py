from flask import Flask
import psycopg2

app = Flask(__name__)

# DB CREDS
DB_HOST = "localhost"  # Database host
DB_NAME = "photobook"  # Database name
DB_USER = ""  # Database username
DB_PASS = ""  # Database password

conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)

# fetch all users, and return json
@app.route('/users')
def users():
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users')

    users = cursor.fetchall()
    cursor.close()
    conn.close()

    return {'users': users}

if __name__ == '__main__':
    app.run(debug=True)
