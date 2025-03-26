CREATE TABLE IF NOT EXISTS `playlist_tracks` (
    `playlist_id` TEXT NOT NULL,
    `track_id` TEXT NOT NULL,
    `added_at` TEXT,
    PRIMARY KEY (`playlist_id`, `track_id`),
    FOREIGN KEY (`playlist_id`) REFERENCES `playlists`(`playlist_id`),
    FOREIGN KEY (`track_id`) REFERENCES `tracks`(`track_id`)
);
