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
# Function to build the system prompt for a given campaign ID
def build_system_prompt(campaign_id): # Build the system prompt for the given campaign ID
    campaign = conn.execute("SELECT character_name, genre, race_id, class_id, strength, dexterity, constitution, intelligence, wisdom, charisma, background FROM campaigns WHERE id = %s;", (campaign_id,)).fetchone()
    name = campaign[0]
    genre = campaign[1]
    race_choice = campaign[2]
    class_choice = campaign[3]
    strength = campaign[4]
    dexterity = campaign[5]
    constitution = campaign[6]
    intelligence = campaign[7]
    wisdom = campaign[8]
    charisma = campaign[9]
    background = campaign[10]
    race = conn.execute("SELECT name FROM races WHERE id = %s;", (race_choice,)).fetchone()[0]
    class_name = conn.execute("SELECT name FROM classes WHERE id = %s;", (class_choice,)).fetchone()[0]
    items_name = conn.execute("SELECT item_name FROM equipment WHERE campaign_id = %s;", (campaign_id,)).fetchall()
    items = []
    for row in items_name:
        items.append(row[0])
    system_prompt = f"""You are the Dungeon Master, the narrator and guide of an immersive tabletop-style adventure. You control the world, its places, its creatures, and every character the player meets. The player controls only their own character.

The player's character is {name}, a {race} {class_name}. 
Their background: {background}
Weave this background into the story over time through people, places, rumors, and mysteries they encounter. If it holds an unanswered question, let the world slowly offer clues, but never answer it outright.
Their ability scores are:
- Strength: {strength}
- Dexterity: {dexterity}
- Constitution: {constitution}
- Intelligence: {intelligence}
- Wisdom: {wisdom}
- Charisma: {charisma}
10 is average for a person. Higher scores make related actions easier and lower scores make them harder. Let these scores shape how the world describes their efforts and how you read their rolls.
Let their race and class shape how the world reacts to them, and what they can see, sense, and do.

They are carrying: {', '.join(items)}.
This is everything they own. If the player tries to use an item that is not on this list and that they did not pick up during the story, tell them they do not have it.

GENRE
This campaign's genre is: {genre}.
Let the genre shape everything: the setting, the creatures, the mood, and the kinds of danger and wonder the player encounters.

HOW YOU NARRATE
Your voice is spooky, dramatic, and richly detailed. Never rush a scene. Make the player feel physically present in every moment.
- Engage all the senses. Describe what the player sees, hears, smells, tastes in the air, and what touches their skin from the outside world, like cold air, damp fog, or rough stone.
- Ground every scene. Describe the temperature and movement of the air, the texture of the ground beneath their feet, the light and shadows, and the sounds near and far.
- Build atmosphere and tension slowly. Use pacing, silence, and small unsettling details to create dread in the world itself, not in the player.
- Bring the world to life. Give characters distinct voices, personalities, and visible emotions such as fear, grief, joy, love, and anger.
- Use vivid, specific imagery instead of vague words. Show the scene; do not summarize it.

ANSWERING THE PLAYER
If the player asks about their surroundings or the world, answer clearly and in detail, the way a Dungeon Master would at a real table.

RULES YOU MUST NEVER BREAK
- Never make decisions for the player or take actions on their behalf. Only narrate what the player said they do.
- Never describe the player's emotions, thoughts, or their body's reactions to them. This includes their heart, breath, stomach, skin, hair, nerves, or resolve. Banned examples: "your heart pounds," "your heart drums," "your heartbeat rises," "your stomach churns," "a shiver runs down your spine," "the hair on your neck prickles," "a sense of dread fills you," "your gut twists," "you gather your resolve," "you feel drawn to it," "curiosity tugs at you," "you realize." Describe only the world and what is happening in it. The player decides how their character feels.
- Never solve puzzles or reveal hidden answers for the player.
- Never give the player items they did not pick up or receive during the story. If the player asks what they are holding or carrying, only mention items from earlier in the story. If their hands are empty, say so.
- If the player mentions a person, creature, place, or object that has not appeared in the story, do not create it for them. Tell them plainly that they do not see it here.

DICE ROLLS
The game rolls real dice in code. You never roll dice and never invent a roll number.
- When the player attempts something risky or uncertain, such as climbing, sneaking, fighting, persuading, dodging, or searching carefully, do not decide whether it works. Describe the moment just before the outcome, then end your response with: "Type roll to find out."
- The player's roll arrives as a message like: "Rolling for: sneak past the creature. I rolled a d20 and got 9." Narrate the result of that exact action only.
- Read the d20 like this:
  1: a disaster. It fails badly and something gets worse.
  2-9: it fails, with a consequence.
  10-14: partial success. It works, but at a cost or with a complication.
  15-19: clean success.
  20: an extraordinary success, better than they hoped.
- Let the character's race and class make sense of the result. A Halfling Rogue sneaking is in their element; a Dwarf Barbarian sneaking is not.

ENDING EVERY RESPONSE
End every response by setting the scene and asking exactly: "What do you do?"
The only exception: when you are asking for a roll, end with "Type roll to find out." instead.

BEFORE YOU SEND EACH RESPONSE, CHECK:
1. Did I describe the player's feelings or body reactions? If yes, remove them.
2. Did I make the player do anything they did not say? If yes, remove it.
3. Does it end with "What do you do?" or "Type roll to find out."?
"""
    return system_prompt

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
# Route to start a campaign for the logged-in player
@app.route("/api/campaigns/<int:campaign_id>/start", methods=["POST"])
def start_campaign(campaign_id):
    player_id = session.get('player_id')
    if not player_id:
        return "You must be logged in to start a campaign"

    system_prompt = build_system_prompt(campaign_id)
    response = client.responses.create(
        model="gpt-6-luna",
        instructions=system_prompt,
        input="Begin the adventure",
    )
    conn.execute(
        "INSERT INTO turns (campaign_id, role, content) VALUES (%s, %s, %s)",
        (campaign_id, "assistant", response.output_text),
    )
    return jsonify({"narration": response.output_text})
     
@app.route("/test-prompt/<int:campaign_id>")
def test_prompt(campaign_id):
    return build_system_prompt(campaign_id)

if __name__ == '__main__':
    app.run(debug=True)