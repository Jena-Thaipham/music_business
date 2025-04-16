CREATE TABLE IF NOT EXISTS `playlists` (
    `playlist_id` TEXT PRIMARY KEY,
    `playlist_name` TEXT,
    `owner_id` TEXT,
    `track_id` TEXT NOT NULL,
    `total_tracks` INTEGER,
    `market` TEXT,
    `public` BOOLEAN,
    `created_at` TEXT,
    `playlist_uri` TEXT,
    FOREIGN KEY (`owner_id`) REFERENCES `users`(`user_id`)
);
