import psycopg # Postgres database adapter for Python
from flask import Flask, url_for, render_template, session # Flask web framework for Python
import os # Operating system library for environment variables and file paths
from dotenv import load_dotenv # loads environment variables from a .env file
load_dotenv()
from authlib.integrations.flask_client import OAuth # OAuth library for handling authentication with external providers

database_url = os.getenv("DATABASE_URL") # grab the database address from .env
conn = psycopg.connect(database_url, autocommit=True) # connect to the Postgres database with autocommit enabled

BACKGROUND = {
    "Acolyte": "You have spent your life in the service of a temple to a specific god or pantheon of gods.",
    "Criminal": "You have a history of breaking the law and living on the wrong side of the law.",
    "Folk Hero": "You come from humble beginnings and have risen to prominence through your deeds.",
    "Noble": "You were born into a wealthy and influential family.",
    "Sage": "You have spent years learning the lore of the multiverse.",
    "Soldier": "You have served in a military organization and are trained in combat.",
    "Urchin": "You grew up on the streets, fending for yourself from a young age.",
    "Hermit": "You lived in seclusion, away from society, to pursue your own personal goals or enlightenment.",
    "Entertainer": "You have spent your life performing for others, whether as a musician, actor, or other type of entertainer.",
    "Outlander": "You have spent your life in the wilds, far from civilization, and are skilled in survival and exploration.",
}


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
    races = conn.execute("SELECT id, name, description, traits FROM races ORDER BY id").fetchall() # fetch all races from the database
    classes = conn.execute("SELECT id, name,description, hit_die FROM classes ORDER BY id").fetchall() # fetch all classes from the database
    return render_template("index.html", races=races, classes=classes, backgrounds=BACKGROUND)

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
    session["player_id"] = player[0] # store the player's ID in the session for later use
    return f"Hello, {user['name']}! You're player #{player[0]}." # greet the user and show their player id

@app.route("/campaign") # route for the campaign page
def campaign():
    player_id = session.get('player_id')
    if not player_id:
            return "You must be logged in to view the campaign page."
    campaigns = conn.execute("SELECT id, character_name, genre FROM campaigns WHERE player_id = %s", (player_id,)).fetchall() # fetch all campaigns for the logged-in player
    if not campaigns:
        return "You have not started any adventures yet."
    return render_template("campaigns.html", campaigns=campaigns) # display the campaigns for the logged-in player

if __name__ == '__main__':
    app.run(debug=True)