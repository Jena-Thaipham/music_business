CREATE TABLE IF NOT EXISTS `users` (
            `user_id` TEXT PRIMARY KEY,
            `country` TEXT,
            `followers` INTEGER,
            `user_uri` TEXT
);
