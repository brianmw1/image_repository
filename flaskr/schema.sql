DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS posts;

CREATE TABLE users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL,
  balance INTEGER NOT NULL
);

CREATE TABLE posts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  title TEXT NOT NULL,
  private INTEGER NOT NULL,
  filepath TEXT NOT NULL,
  price REAL,
  stock INTEGER,
  FOREIGN KEY (user_id) REFERENCES user (id)
);

--tests
-- insert into post(author_id, title, image) values
--   (1, "a", "cyberpunk-01.jpg"),
--   (2, "b", "rx7-2.jpg");

-- insert into user(username, password) values
--   ("x", "faroa3w8hrawe"),
--   ("z", "afjoeiuahysgt3");