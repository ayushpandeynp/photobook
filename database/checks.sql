-- Add a legit user
INSERT INTO users (fname, lname, email, dob, hometown, gender, password, is_visitor)
VALUES ('John', 'Doe', 'john.doe@example.com', '1990-01-01', 'dubai', 'M', 'password123', FALSE);

-- Add a visitor
INSERT INTO users (is_visitor) VALUES (TRUE);

-- Add Album for legit user
INSERT INTO albums (album_name, user_id, datetime) VALUES ('My Album', 1, NOW());

-- Add Album for visitor
INSERT INTO albums (album_name, user_id, datetime) VALUES ('Visitor Album', 2, NOW());

-- Invalid friend relationships
INSERT INTO friends (user_id, friend_id) VALUES (1, 2);
INSERT INTO friends (user_id, friend_id) VALUES (2, 1);

-- add photos to existing album
INSERT INTO photos (album_id, caption, data, datetime) VALUES (1, 'My Photo', '123', NOW());

-- add photos to non-existing album
INSERT INTO photos (album_id, caption, data, datetime) VALUES (5, 'My Photo', '123', NOW());

-- add tags to existing photo
INSERT INTO tags (photo_id, tag_name) VALUES (1, 'tag1');

-- add tags to non-existing photo
INSERT INTO tags (photo_id, tag_name) VALUES (5, 'tag1');

-- add comments to existing photo
INSERT INTO comments (photo_id, user_id, text, datetime)
VALUES (1, 1, 'Beautiful photo!', NOW());

-- add comments to non-existing photo
INSERT INTO comments (photo_id, user_id, text, datetime)
VALUES (999, 1, 'Invalid photo', NOW());

-- add comments to non-existing user
INSERT INTO comments (photo_id, user_id, text, datetime)
VALUES (1, 999, 'Invalid user', NOW());

-- add likes to existing photo
INSERT INTO likes (photo_id, user_id, datetime) VALUES (1, 1, NOW());

-- add likes to non-existing photo
INSERT INTO likes (photo_id, user_id, datetime) VALUES (999, 1, NOW());