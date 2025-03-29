CREATE TABLE IF NOT EXISTS `albums` (
    `album_id` TEXT NOT NULL UNIQUE,
    `album_name` TEXT,
    `album_type` TEXT,
    `artist_id` TEXT NOT NULL,
    `artist_name` TEXT ,
    `release_date` TEXT,  
    `total_tracks` INTEGER,
    `popularity` INTEGER CHECK(popularity BETWEEN 0 AND 100),
    `markets` TEXT,
    `album_uri` TEXT
);
