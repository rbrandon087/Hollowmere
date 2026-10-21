CREATE TABLE players (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE races (
    id SERIAL PRIMARY KEY,
     name VARCHAR(50),
     description TEXT,
     traits TEXT

);

CREATE TABLE classes (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50),
    description TEXT,
    hit_die INTEGER
);

CREATE TABLE campaigns (
    id SERIAL PRIMARY KEY,
    player_id INTEGER REFERENCES players(id),
    character_name VARCHAR(50),
    race_id INTEGER REFERENCES races(id),
    class_id INTEGER REFERENCES classes(id),
    background VARCHAR(50),
    strength INTEGER,
    dexterity INTEGER,
    constitution INTEGER,
    intelligence INTEGER,
    wisdom INTEGER,
    charisma INTEGER,
    genre VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE turns (
    id SERIAL PRIMARY KEY,
    campaign_id INTEGER REFERENCES campaigns(id),
    role VARCHAR(20),
    content TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE dice_rolls (
    id SERIAL PRIMARY KEY,
    campaign_id INTEGER REFERENCES campaigns(id),
    die VARCHAR(10),
    result INTEGER,
    reason VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE equipment (
    id SERIAL PRIMARY KEY,
    campaign_id INTEGER REFERENCES campaigns(id),
    item_name VARCHAR(100),
    quantity INTEGER,
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);