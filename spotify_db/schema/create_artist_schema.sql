CREATE TABLE IF NOT EXISTS artists (
    artist_id TEXT PRIMARY KEY,
    name TEXT,
    followers INTEGER,
    genres TEXT,  
    popularity INTEGER
);