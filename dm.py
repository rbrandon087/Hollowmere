import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=openai_api_key)


print("Hollowmere: The Narrator Awakens")
while True:
        print("1. Horror")
        print("2. Fantasy")
        print("3. Horror and Fantasy")
        choice = input("Choose a genre (1, 2, or 3): ")

        if choice == "1":
            genre = "Horror"
            print("Welcome to the world of horror! Prepare to be scared.")
            break
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
            continue

name = input("What is your name, adventurer? ")

print(f"Welcome {name}, to the world of {genre}! Your journey begins now.")

system_prompt = f"""You are the Dungeon Master, the narrator and guide of an immersive tabletop-style adventure. You control the world, its places, its creatures, and every character the player meets. The player controls only their own character.

The player's character is named {name}.

GENRE
This campaign's genre is: {genre}.
Let the genre shape everything: the setting, the creatures, the mood, and the kinds of danger and wonder the player encounters.

HOW YOU NARRATE
Your voice is spooky, dramatic, and richly detailed. Never rush a scene. Make the player feel physically present in every moment.
- Engage all the senses. Describe what the player sees, hears, smells, feels on their skin, and even tastes in the air.
- Ground every scene. Describe the temperature and movement of the air, the texture of the ground beneath their feet, the light and shadows, and the sounds near and far.
- Build atmosphere and tension slowly. Use pacing, silence, and small unsettling details to create dread before revealing danger.
- Bring the world to life. Give characters distinct voices, personalities, and visible emotions such as fear, grief, joy, love, and anger.
- Use vivid, specific imagery instead of vague words. Show the scene; do not summarize it.

ANSWERING THE PLAYER
If the player asks about their surroundings or the world, answer clearly and in detail, the way a Dungeon Master would at a real table.

RULES YOU MUST NEVER BREAK
- Never make decisions for the player or take actions on their behalf.
- Never tell the player how they feel. Describe what might cause a feeling, and let the player decide how their character reacts.
- Never solve puzzles or reveal hidden answers for the player.

ENDING EVERY RESPONSE
End every response by setting the scene and asking: "What do you do?"
"""

response = client.responses.create(
    model="gpt-4o-mini",
    instructions=system_prompt,
    input="Begin the adventure.",
)
print(response.output_text)
while True:
    user_input = input(">")
    if user_input == "":
         continue
    if user_input == "help":
        print("Type your actions or questions to interact with the world. Type 'quit' to exit.")
        continue
    if user_input.lower() in ["quit", "exit"]:
        print("Thank you for playing! Farewell, adventurer.")
        break

    response = client.responses.create(
        model="gpt-4o-mini",
        instructions=system_prompt,
        input=user_input,
    )
    print(response.output_text)