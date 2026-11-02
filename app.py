from requests import session

import psycopg # Postgres database adapter for Python
from flask import Flask, url_for, session # Flask web framework for Python
import os # Operating system library for environment variables and file paths
from dotenv import load_dotenv # loads environment variables from a .env file
load_dotenv()
from authlib.integrations.flask_client import OAuth # OAuth library for handling authentication with external providers

database_url = os.getenv("DATABASE_URL") # grab the database address from .env
conn = psycopg.connect(database_url, autocommit=True) # connect to the Postgres database with autocommit enabled

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")

oauth = OAuth(app)
oauth.register(
    name="google",
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)

@app.route('/')
def home():
    return "Welcome to Hollowmere!"

@app.route('/login')
def login():
    redirect_uri = url_for("auth", _external=True) # build the redirect URI for the OAuth callback
    return oauth.google.authorize_redirect(redirect_uri) # redirect the user to the Google OAuth login page

@app.route("/callback")
def auth():
    token = oauth.google.authorize_access_token()
    user = token["userinfo"]
    player = conn.execute("SELECT * FROM players WHERE sub = %s", (user["sub"],)).fetchone() # fetch the player row if it exists
    if not player: 
        conn.execute( # insert a new player row into the database if it doesn't exist
            "INSERT INTO players (sub, name, email) VALUES (%s, %s, %s)", # SQL query to insert a new player row
            (user["sub"], user["name"], user["email"]) # values to insert into the new player row
        )
        player = conn.execute("SELECT * FROM players WHERE sub = %s", (user["sub"],)).fetchone() # fetch the newly inserted player row
        session["player_id"] = player["0"] # store the player's ID in the session for later use
    return f"Hello, {user['name']}! Your email is {user['email']}." # greet the user with their name and email after successful login

if __name__ == '__main__':
    app.run(debug=True)