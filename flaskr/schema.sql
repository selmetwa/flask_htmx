DROP TABLE IF EXISTS tasks;
DROP TABLE IF EXISTS stream;

CREATE TABLE stream (
  stream_id INTEGER PRIMARY KEY AUTOINCREMENT,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  title VARCHAR(100),
  priority_level INTEGER CHECK (priority_level >= 1 AND priority_level <= 5),
  description VARCHAR(100)
);

CREATE TABLE tasks (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  stream_id INTEGER,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  title VARCHAR(100),
  description VARCHAR(100),
  is_completed BOOLEAN DEFAULT FALSE,
  priority_level INTEGER CHECK (priority_level >= 1 AND priority_level <= 5),
  FOREIGN KEY (stream_id) REFERENCES stream (stream_id)
);

