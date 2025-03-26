CREATE TABLE IF NOT EXISTS `tracks` (
	`track_id` TEXT NOT NULL UNIQUE,
	`track_name` TEXT NOT NULL,
	`artist_id` TEXT NOT NULL,
	`artist_name` TEXT NOT NULL,
	`album_id` TEXT NOT NULL,
	`album_type` TEXT NOT NULL,
	`album_name` INTEGER NOT NULL,
	`track_uri` TEXT NOT NULL UNIQUE,
	`release_date` REAL NOT NULL,
	`track_number` INTEGER NOT NULL,
	`total_track` INTEGER NOT NULL,
	`market` TEXT NOT NULL,
	`disc_number` INTEGER NOT NULL,
	`explicit` REAL NOT NULL,
	`duration_ms` INTEGER NOT NULL,
	`popularity` INTEGER NOT NULL,
FOREIGN KEY(`track_id`) REFERENCES `playlist_tracks`(`track_id`),
FOREIGN KEY(`artist_id`) REFERENCES `artists`(`artist_id`),
FOREIGN KEY(`album_id`) REFERENCES `albums`(`album_id`)
);
CREATE TABLE IF NOT EXISTS `artists` (
	`artist_id` TEXT NOT NULL,
	`artist_name` TEXT NOT NULL,
	`genre` TEXT NOT NULL,
	`popularity` INTEGER NOT NULL,
	`followers` INTEGER NOT NULL,
	`artisit_uri` TEXT NOT NULL,
FOREIGN KEY(`genre`) REFERENCES `genres`(`genre_id`)
);
CREATE TABLE IF NOT EXISTS `albums` (
	`album_id` TEXT NOT NULL UNIQUE,
	`album_name` TEXT NOT NULL,
	`album_type` TEXT NOT NULL,
	`artist_id` TEXT NOT NULL,
	`artist_name` TEXT NOT NULL,
	`release_date` REAL NOT NULL,
	`total_tracks` INTEGER NOT NULL,
	`popularity` INTEGER NOT NULL,
	`markets` TEXT NOT NULL,
	`album_uri` TEXT NOT NULL,
FOREIGN KEY(`artist_id`) REFERENCES `artists`(`artist_id`)
);
CREATE TABLE IF NOT EXISTS `playlists` (
	`playlist_id` TEXT NOT NULL UNIQUE,
	`playlist_name` TEXT NOT NULL,
	`owner_id` TEXT NOT NULL,
	`track_id` TEXT NOT NULL,
	`total_tracks` INTEGER NOT NULL,
	`playlist_followers` INTEGER NOT NULL,
	`owner_followers` INTEGER NOT NULL,
	`market` TEXT NOT NULL,
	`public` REAL NOT NULL,
	`playlist_uri` TEXT NOT NULL,
FOREIGN KEY(`playlist_id`) REFERENCES `playlist_tracks`(`playlist_id`),
FOREIGN KEY(`track_id`) REFERENCES `tracks`(`track_id`)
);
CREATE TABLE IF NOT EXISTS `playlist_tracks` (
	`playlist_id` TEXT NOT NULL UNIQUE,
	`track_id` TEXT NOT NULL,
	`added_at` TEXT NOT NULL,
FOREIGN KEY(`playlist_id`) REFERENCES `playlists`(`playlist_id`)
);
CREATE TABLE IF NOT EXISTS `listening_history` (
	`album_id` TEXT NOT NULL UNIQUE,
	`track_id` TEXT NOT NULL,
	`played_at` TEXT NOT NULL,
FOREIGN KEY(`album_id`) REFERENCES `albums`(`album_id`),
FOREIGN KEY(`track_id`) REFERENCES `tracks`(`track_id`)
);