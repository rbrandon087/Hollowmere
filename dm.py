# ============================================================
# Hollowmere: The Narrator Awakens
# An AI Dungeon Master text adventure
# ============================================================

# ---------- Imports ----------
import random
import os
import re                       # lets us read environment variables (our secret keys)
from openai import OpenAI       # the OpenAI library, so we can talk to the AI
from dotenv import load_dotenv  # reads our .env file so os.getenv can find the keys
import psycopg                  # lets Python talk to our Postgres database

# ---------- Setup: keys and connections ----------
load_dotenv()  # load the secret values from .env into the environment

openai_api_key = os.getenv("OPENAI_API_KEY")  # grab the OpenAI key from .env
database_url = os.getenv("DATABASE_URL")      # grab the database address from .env
client = OpenAI(api_key=openai_api_key)       # create the OpenAI client we'll send requests through

# Connect to the Render Postgres database.
# autocommit=True means every INSERT saves right away (no separate "commit" step needed).
conn = psycopg.connect(database_url, autocommit=True)

# ---------- Dice ----------
def roll_die(sides):
    return random.randint(1, sides)
# Roll 4d6 and drop the lowest die to generate an ability score.
def roll_ability_score():
    rolls = [roll_die(6), roll_die(6), roll_die(6), roll_die(6)]
    score = sum(rolls) - min(rolls)
    return score

# ---------- Starting Equipment ----------
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


print("Connected to the database!")

# Create a new player row.
# DEFAULT VALUES = let the database fill in id and created_at by itself.
# RETURNING id = hand back the new player's id.
# .fetchone()[0] = grab that first row, then the first value in it (the id number).
player_id = conn.execute("INSERT INTO players DEFAULT VALUES RETURNING id").fetchone()[0]
print(f"Player created with ID {player_id}")


# ---------- Genre menu ----------
print("Hollowmere: The Narrator Awakens")
# Show the main menu for starting or loading an adventure
while True:
    print("1. New Adventure")
    print("2. Load Adventure")
    print("3. Delete Adventure")
    option_choice = input("Choose an option (1, 2, or 3):")
    if option_choice == "1":
        break  # start a new adventure
    elif option_choice == "2":
        # Load an existing adventure
        break  # exit the main menu loop even though loading isn't implemented
    elif option_choice == "3":
        existing_campaigns = conn.execute("SELECT id, character_name, genre FROM campaigns ORDER BY id;")# Fetch all existing campaigns to display for deletion
        for row in existing_campaigns:
            print(f"{row[0]}. {row[1]} ({row[2]})")# Display each existing campaign with its ID, character name, and genre
        delete_id = int(input(f"Enter the ID of the adventure to delete: "))
        confirm_delete = input(f"Are you sure you want to delete adventure with ID {delete_id}? (yes/no): ")# Ask the player to confirm deletion
        if confirm_delete.lower() != "yes":# If the player does not confirm deletion, skip the deletion process
            print("Deletion cancelled.")
            continue  # skip deletion if not confirmed

        conn.execute("DELETE FROM turns WHERE campaign_id = %s;", (delete_id,)) # Delete all turns associated with the campaign
        conn.execute("DELETE FROM dice_rolls WHERE campaign_id = %s;", (delete_id,))#Delete all dice rolls associated with the campaign
        conn.execute("DELETE FROM equipment WHERE campaign_id = %s;", (delete_id,)) # Delete all equipment associated with the campaign
        conn.execute("DELETE FROM campaigns WHERE id = %s;", (delete_id,)) # Delete the campaign itself
        print(f"Adventure with ID {delete_id} has been deleted.")
        # Delete an existing adventure
        continue  # go back to the top of the menu loop
    else:
        print("Invalid choice. Please select 1, 2, or 3.")
        continue  # go back to the top of the menu loop
if option_choice == "1": # the new adventure option
    while True:  # keep showing the menu until the player picks a valid option
        print("1. Horror")
        print("2. Fantasy")
        print("3. Horror and Fantasy")
        choice = input("Choose a genre (1, 2, or 3): ")  # input() always gives back a string

        if choice == "1":
            genre = "Horror"
            print("Welcome to the world of horror! Prepare to be scared.")
            break     # valid choice, so leave the menu loop
        elif choice == "2":
            genre = "Fantasy"
            print("Welcome to the world of fantasy! Get ready for an epic adventure.")
            break
        elif choice == "3":
            genre = "Horror and Fantasy"
            print("Welcome to the world of horror and fantasy! Brace yourself for a thrilling journey.")
            break
        else:
            print("Invalid choice. Please select 1, 2, or 3.")
            continue  # bad choice, so jump back to the top of the loop and show the menu again
        # After selecting a genre, show the available races for the player to choose from.
    races_table = conn.execute("SELECT id, name, description, traits FROM races ORDER BY id;")
    for row in races_table:
        print(f"{row[0]}. {row[1]} ({row[2]} - {row[3]})")
    race_choice = int(input("Choose your race by entering the corresponding number: "))
    race = conn.execute("SELECT name FROM races WHERE id = %s;", (race_choice,)).fetchone()[0]
    # Show the available classes for the player to choose from.
    class_table = conn.execute("SELECT id, name, description, hit_die FROM classes ORDER BY id;")
    for row in class_table:
        print(f"{row[0]}. {row[1]} ({row[2]} - Hit Die: {row[3]})")
    class_choice = int(input("Choose your class adventurer by entering the corresponding number: "))
    class_name = conn.execute("SELECT name FROM classes WHERE id = %s;", (class_choice,)).fetchone()[0]
    strength = roll_ability_score()
    dexterity = roll_ability_score()
    constitution = roll_ability_score()
    intelligence = roll_ability_score()
    wisdom = roll_ability_score()
    charisma = roll_ability_score()
    print(f"Your ability scores are:\nStrength: {strength}\nDexterity: {dexterity}\nConstitution: {constitution}\nIntelligence: {intelligence}\nWisdom: {wisdom}\nCharisma: {charisma}")
    # Show the available backgrounds for the player to choose from.
    for number, (bg_name, bg_description) in enumerate(BACKGROUND.items(), start=1):
        print(f"{number}. {bg_name} - {bg_description}")
    print("11. Write your own background story.")
    background_choice = int(input("Choose your background by entering the corresponding number: "))
    # Determine the background based on the player's choice.
    if background_choice == 11:
        background = input("Write your own background story: ")
    else:
        background = list(BACKGROUND.keys())[background_choice - 1]
    name = input("What is your name, adventurer? ")
    # Insert the new campaign into the database with the player's chosen character details and ability scores.
    campaign_id = conn.execute("INSERT INTO campaigns (player_id, character_name, genre, race_id, class_id, strength, dexterity, constitution, intelligence, wisdom, charisma, background) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id;", (player_id, name, genre, race_choice, class_choice, strength, dexterity, constitution, intelligence, wisdom, charisma, background)).fetchone()[0]
    # Assign starting equipment based on the chosen class.
    items = starting_equipment[class_name]
    print(f"Your starting equipment includes: {', '.join(items)}")
    for item in items:
        conn.execute("INSERT INTO equipment (campaign_id, item_name, quantity) VALUES (%s, %s, %s);", (campaign_id, item, 1)) # Insert each starting equipment item into the database for the new campaign.
    print(campaign_id)
    print(f"Welcome {name}, to the world of {genre}! Your journey begins now.")

else: # the load existing adventure option
    # Here you would implement loading an existing campaign
    existing_campaigns = conn.execute("SELECT id, character_name, genre FROM campaigns ORDER BY id;")
    for row in existing_campaigns:
        print(f"{row[0]}. {row[1]} ({row[2]})")
    campaign_id = int(input("Enter the ID of the campaign you want to load: "))
    campaign = conn.execute("SELECT character_name, genre, race_id, class_id, strength, dexterity, constitution, intelligence, wisdom, charisma, background FROM campaigns WHERE id = %s;", (campaign_id,)).fetchone()
    name = campaign[0]
    genre = campaign[1]
    # Retrieve the character's race and class choices from the campaign record.
    race_choice = campaign[2]
    class_choice = campaign[3]
    # Retrieve the character's ability scores from the campaign record.
    strength = campaign[4]
    dexterity = campaign[5]
    constitution = campaign[6]
    intelligence = campaign[7]
    wisdom = campaign[8]
    charisma = campaign[9]
    # Retrieve the character's background from the campaign record.
    background = campaign[10]
    race = conn.execute("SELECT name FROM races WHERE id = %s;", (race_choice,)).fetchone()[0]
    class_name = conn.execute("SELECT name FROM classes WHERE id = %s;", (class_choice,)).fetchone()[0]
    rows = conn.execute("SELECT role, content FROM turns WHERE campaign_id = %s ORDER BY id",
        (campaign_id,),
    ).fetchall()
    items_name = conn.execute("SELECT item_name FROM equipment WHERE campaign_id = %s;", (campaign_id,)).fetchall()
    items = []
    for row in items_name:
        items.append(row[0])

    story_log = []

    for row in rows:
        story_log.append({
            "role": row[0],
            "content": row[1]
        })
    print(story_log[-1]["content"])
    

# ---------- The DM's instructions (system prompt) ----------
# f""" ... """ is a multi-line f-string, so {name} and {genre} get filled in with the player's choices.
# This tells the AI how to behave as the Dungeon Master every single turn.
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

# ---------- Opening scene ----------
# Ask the AI to start the story.
# instructions = the DM rules above. input = a behind-the-scenes nudge (not saved as part of the story).
if option_choice == "1":
    response = client.responses.create(
        model="gpt-6-luna",
        instructions=system_prompt,
        input="Begin the adventure.",
    )
    print(response.output_text)  # show the DM's opening scene to the player

    # The story log is the DM's memory: a list of dictionaries, one per line of the story.
    # Each dictionary has a "role" (who spoke) and "content" (what they said).
    story_log = []
    story_log.append({
        "role": "assistant",                # "assistant" = the DM
        "content": response.output_text     # the opening scene text
    })

    # Save the opening scene to the turns table.
    # No RETURNING id here, because nothing else points to a turn.
    # Quotes vs. no quotes: "assistant" is the literal word; campaign_id and response.output_text are variables.
    conn.execute(
        "INSERT INTO turns (campaign_id, role, content) VALUES (%s, %s, %s)",
        (campaign_id, "assistant", response.output_text),
    )

# ---------- Main game loop ----------
while True:  # keep the game going until the player quits
    user_input = input(">")  # wait for the player to type an action or question

    if user_input == "":
        continue  # player just pressed Enter, so ignore it and ask again

    if user_input.lower() == "roll": # handle rolling a d20 die
        reason = input("What are you rolling for? ")
        roll_result = roll_die(20)
        print(f"Rolled a d20: {roll_result}")
        conn.execute(
            "INSERT INTO dice_rolls (campaign_id, die, result, reason) VALUES (%s, %s, %s, %s)",
            (campaign_id, "d20", roll_result, reason),
        )
        user_input = f"I attempt to {reason}. I rolled a d20 and got {roll_result}."
        
    if user_input == "help":
        print("Type your actions or questions to interact with the world. Type 'quit' to exit.")
        continue  # show help, then go back to waiting for input

    # .lower() makes "QUIT" or "Quit" count too
    if user_input.lower() in ["quit", "exit"]:
        print("Thank you for playing! Farewell, adventurer.")
        break  # leave the game loop, which ends the program

    # Add the player's move to the story log
    story_log.append({
        "role": "user",           # "user" = the player
        "content": user_input     # what the player typed
    })
    # 
    conn.execute(
        "INSERT INTO turns (campaign_id, role, content) VALUES (%s, %s, %s)",
        (campaign_id, "user", user_input),
    )


    # Send the WHOLE story log to the AI, so the DM remembers everything that happened so far
    response = client.responses.create(
        model="gpt-6-luna",
        instructions=system_prompt,
        input=story_log,
    )
    print(response.output_text)  # show the DM's reply

    # Add the DM's reply to the story log, so it's remembered next turn
    story_log.append({
        "role": "assistant",
        "content": response.output_text
    })
    conn.execute(
            "INSERT INTO turns (campaign_id, role, content) VALUES (%s, %s, %s)",
            (campaign_id, "assistant", response.output_text),
    )