CREATE TABLE IF NOT EXISTS `users` (
            `user_id` TEXT NOT NULL UNIQUE PRIMARY KEY,
            `country` TEXT,
            `followers` INTEGER ,
            `user_uri` TEXT 
        );
        