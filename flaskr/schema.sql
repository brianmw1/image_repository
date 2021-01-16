DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS post;

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
);

CREATE TABLE post (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  author_id INTEGER NOT NULL,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  title TEXT NOT NULL,
  image TEXT NOT NULL,
  FOREIGN KEY (author_id) REFERENCES user (id)
);

insert into post(author_id, title, image) values
  (1, "a", "cyberpunk-01.jpg"),
  (2, "b", "rx7-2.jpg");

insert into user(username, password) values
  ("x", "faroa3w8hrawe"),
  ("z", "afjoeiuahysgt3");