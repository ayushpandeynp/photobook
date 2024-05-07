-- Create Database
CREATE DATABASE photobook;

-- Users Table
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    fname VARCHAR(50) NULL,
    lname VARCHAR(50) NULL,
    email VARCHAR(50) NULL UNIQUE,
    dob DATE NULL,
    hometown VARCHAR NULL,
    gender CHAR(1) NULL CHECK (gender IN ('M', 'F', 'O', NULL)),
    password VARCHAR(72) NULL,
    is_visitor BOOLEAN NOT NULL,
    
    CONSTRAINT chk_visitor CHECK (
        (is_visitor AND fname IS NULL AND lname IS NULL AND email IS NULL AND dob IS NULL AND hometown IS NULL AND gender IS NULL AND password IS NULL)
        OR
        (NOT is_visitor AND fname IS NOT NULL AND lname IS NOT NULL AND email IS NOT NULL AND hometown IS NOT NULL AND gender IS NOT NULL AND password IS NOT NULL)
    )
);

-- Albums Table
CREATE TABLE albums (
    album_id SERIAL PRIMARY KEY,
    album_name VARCHAR(50) NOT NULL,
    user_id INT NOT NULL,
    datetime TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_user_id FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- Check if user is not a visitor
CREATE OR REPLACE FUNCTION check_legit_user()
RETURNS TRIGGER AS $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM users WHERE user_id = NEW.user_id AND is_visitor = FALSE) THEN
        RAISE EXCEPTION 'User must be a non-visitor';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_check_legit_user
BEFORE INSERT OR UPDATE ON albums
FOR EACH ROW EXECUTE FUNCTION check_legit_user();

-- Photos Table
CREATE TABLE photos (
    photo_id SERIAL PRIMARY KEY,
    album_id INT NOT NULL,
    caption VARCHAR(250) NULL,
    path TEXT NOT NULL,
    datetime TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_album_id FOREIGN KEY (album_id) REFERENCES albums(album_id) ON DELETE CASCADE
);

-- Friends Table
CREATE TABLE friends (
    user_id INT NOT NULL,
    friend_id INT NOT NULL,
    
    CONSTRAINT pk_friends PRIMARY KEY (user_id, friend_id),
    CONSTRAINT fk_user_id FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    CONSTRAINT fk_friend_id FOREIGN KEY (friend_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- Check if friend relationship is legit, i.e. no visitors can be friends
CREATE OR REPLACE FUNCTION check_legit_friend_relationship()
RETURNS TRIGGER AS $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM users WHERE user_id = NEW.user_id AND is_visitor = FALSE) OR
       NOT EXISTS (SELECT 1 FROM users WHERE user_id = NEW.friend_id AND is_visitor = FALSE) OR
       NOT EXISTS (SELECT 1 WHERE NEW.user_id <> NEW.friend_id) THEN
        RAISE EXCEPTION 'Both users must be non-visitors and not the same user.';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_check_legit_friendship
BEFORE INSERT OR UPDATE ON friends
FOR EACH ROW EXECUTE FUNCTION check_legit_friend_relationship();

-- Tags Table
CREATE TABLE tags (
    photo_id INT NOT NULL,
    tag_name VARCHAR(50) NOT NULL,
    
    CONSTRAINT pk_tags PRIMARY KEY (photo_id, tag_name),
    CONSTRAINT fk_photo_id FOREIGN KEY (photo_id) REFERENCES photos(photo_id) ON DELETE CASCADE
);

-- Comments Table
CREATE TABLE comments (
    comment_id SERIAL PRIMARY KEY,
    photo_id INT NOT NULL,
    user_id INT NOT NULL,
    text VARCHAR(100) NOT NULL,
    datetime TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_photo_id FOREIGN KEY (photo_id) REFERENCES photos(photo_id) ON DELETE CASCADE,
    CONSTRAINT fk_user_id FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- Likes Table
CREATE TABLE likes (
    photo_id INT NOT NULL,
    user_id INT NOT NULL,
    datetime TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT pk_likes PRIMARY KEY (photo_id, user_id),
    CONSTRAINT fk_photo_id FOREIGN KEY (photo_id) REFERENCES photos(photo_id) ON DELETE CASCADE,
    CONSTRAINT fk_user_id FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);
