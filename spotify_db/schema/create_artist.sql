CREATE TABLE IF NOT EXISTS `artists` (
    `artist_id` TEXT PRIMARY KEY,
    `artist_name` TEXT,
    `genre` TEXT,
    `popularity` INTEGER CHECK(popularity BETWEEN 0 AND 100),
    `followers` INTEGER,
    `artist_uri` TEXT
);
