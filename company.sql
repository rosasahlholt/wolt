
PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS users;

CREATE TABLE users(
    user_pk         TEXT,
    user_username   TEXT UNIQUE,
    user_name       TEXT,
    user_last_name  TEXT,
    user_email      TEXT UNIQUE,
    user_password   TEXT,
    PRIMARY KEY(user_pk)
) WITHOUT ROWID;

INSERT INTO users VALUES ("1", "Santiago");

SELECT * FROM users;

-- ##############################
-- Phones table and data
DROP TABLE IF EXISTS phones;
-- Lookup table
CREATE TABLE phones(
    user_fk         TEXT,
    phone_number    TEXT,
    PRIMARY KEY(user_fk, phone_number), -- Composite key
    FOREIGN KEY(user_fk) REFERENCES users(user_pk) ON DELETE CASCADE -- Constraint
) WITHOUT ROWID;

-- FOREIGN KEY(trackartist) REFERENCES artist(artistid)
INSERT INTO phones VALUES("1", "111");
SELECT * FROM phones;

DELETE FROM users WHERE user_pk = "1";
SELECT * FROM phones;


SELECT * FROM users WHERE user_email = "sand@kea.dk" AND user_password="password"











