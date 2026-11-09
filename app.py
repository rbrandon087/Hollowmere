import psycopg # Postgres database adapter for Python
import random # for generating random numbers and choices
from flask import Flask, url_for, render_template, session, request, jsonify # Flask web framework for Python
from openai import OpenAI
import os # Operating system library for environment variables and file paths
from dotenv import load_dotenv # loads environment variables from a .env file
load_dotenv()
from authlib.integrations.flask_client import OAuth # OAuth library for handling authentication with external providers

database_url = os.getenv("DATABASE_URL") # grab the database address from .env
conn = psycopg.connect(database_url, autocommit=True) # connect to the Postgres database with autocommit enabled

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Starting equipment for each class in the game
starting_equipment = {
    "Barbarian": ["greataxe", "handaxe", "explorer's pack", "javelin"],
    "Wizard": ["quarterstaff", "component pouch", "spellbook", "scholar's pack"],
    "Rogue": ["shortsword", "dagger", "thieves' tools", "burglar's pack"],
    "Cleric": ["mace", "shield", "holy symbol", "priest's pack"],
    "Fighter": ["longsword", "shield", "chain mail", "dungeoneer's pack"],
    "Paladin": ["longsword", "shield", "chain mail", "priest's pack"],
    "Ranger": ["longbow", "shortsword", "explorer's pack", "quiver of arrows"],
    "Monk": ["quarterstaff", "dungeoneer's pack", "shortsword", "10 darts"],
    "Bard": ["rapier", "lute", "explorer's pack", "dagger"],
    "Druid": ["scimitar", "shield", "explorer's pack", "druidic focus"],
    "Warlock": ["light crossbow", "component pouch", "explorer's pack", "dagger"],
    "Sorcerer": ["dagger", "component pouch", "explorer's pack", "arcane focus"],
    "Artificer": ["light crossbow", "thieves' tools", "explorer's pack", "dagger"],
}
# Function to roll a die with a given number of sides
def roll_die(sides):
    return random.randint(1, sides)
# Roll 4d6 and drop the lowest die to generate an ability score.
def roll_ability_score():
    rolls = [roll_die(6), roll_die(6), roll_die(6), roll_die(6)]
    score = sum(rolls) - min(rolls)
    return score
# Background options for characters in the game
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

@app.route("/api/campaigns", methods=["POST"])
def create_campaign():
    player_id = session.get('player_id')
    if not player_id:
        return "You must be logged in to create a campaign"

    data = request.get_json() # get the JSON data from the request body
    name = data.get("name") # get the campaign name from the JSON data
    genre = data.get("genre") # get the campaign genre from the JSON data
    race_id = int(data.get("race_id")) # get the campaign race from the JSON data
    class_id = int(data.get("class_id")) # get the campaign class from the JSON data
    if data.get("background") == 'custom':
        background = data.get("background_custom")
    else:
        background = data.get("background")

    # Generate the character's ability scores randomly using the 4d6 drop lowest method
    strength = roll_ability_score()
    dexterity = roll_ability_score()
    constitution = roll_ability_score()
    intelligence = roll_ability_score()
    wisdom = roll_ability_score()
    charisma = roll_ability_score()
    # Insert the new campaign into the database with the player's chosen character details and ability scores
    campaign_id = conn.execute("INSERT INTO campaigns (player_id, character_name, genre, race_id, class_id, strength, dexterity, constitution, intelligence, wisdom, charisma, background) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id;", (player_id, name, genre, race_id, class_id, strength, dexterity, constitution, intelligence, wisdom, charisma, background)).fetchone()[0]
    class_name = conn.execute("SELECT name FROM classes WHERE id = %s;", (class_id,)).fetchone()[0]
    items = starting_equipment[class_name]
    for item in items:
        conn.execute("INSERT INTO equipment (campaign_id, item_name, quantity) VALUES (%s, %s, %s);", (campaign_id, item, 1))
    return jsonify({"campaign_id": campaign_id})
     

if __name__ == '__main__':
    app.run(debug=True)