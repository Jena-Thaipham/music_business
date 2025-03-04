CREATE TABLE IF NOT EXISTS albums (
    album_id TEXT PRIMARY KEY,
    name TEXT,
    artist_id TEXT,
    release_date TEXT,
    total_tracks INTEGER,
    popularity INTEGER,
    label TEXT,
    genres TEXT  
);