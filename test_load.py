import os                       # lets us read environment variables (our secret keys)
from dotenv import load_dotenv  # reads our .env file so os.getenv can find the keys
import psycopg                  # lets Python talk to our Postgres database

load_dotenv()  # load the secret values from .env into the environment

database_url = os.getenv("DATABASE_URL")      # grab the database address from .env

# Connect to the Render Postgres database.
# autocommit=True means every INSERT saves right away (no separate "commit" step needed).
conn = psycopg.connect(database_url, autocommit=True)

print("Connected to the database!")

rows = conn.execute(
    "SELECT role, content FROM turns WHERE campaign_id = %s ORDER BY id",
    (5,),
).fetchall()

story_log = []

for row in rows:
    story_log.append({
        "role": row[0],
        "content": row[1]
    })

print(story_log)
