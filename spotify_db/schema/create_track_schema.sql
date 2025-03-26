CREATE TABLE IF NOT EXISTS `tracks` (
	`track_id` TEXT NOT NULL UNIQUE PRIMARY KEY,
	`track_name` TEXT,
	`artist_id` TEXT,
	`artist_name` TEXT,
	`album_id` TEXT,
	`album_type` TEXT,
	`album_name` INTEGER,
	`track_uri` TEXT,
	`release_date` REAL,
	`track_number` INTEGER,
	`total_track` INTEGER,
	`market` TEXT,
	`disc_number` INTEGER,
	`explicit` REAL,
	`duration_ms` INTEGER,
	`popularity` INTEGER
);