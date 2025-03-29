CREATE TABLE IF NOT EXISTS `playlists` (
    `playlist_id` TEXT PRIMARY KEY,
    `playlist_name` TEXT,
    `owner_id` TEXT,
    `track_id` TEXT NOT NULL,
    `total_tracks` INTEGER,
    `playlist_followers` INTEGER,
    `owner_followers` INTEGER,
    `market` TEXT,
    `public` BOOLEAN,
    `created_at` TEXT,
    `playlist_uri` TEXT
);
