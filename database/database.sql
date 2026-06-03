-- PollPoint database schema
-- If you already have your own schema, we can merge/align later.

CREATE TABLE IF NOT EXISTS users (
  id SERIAL PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  name VARCHAR(255) NOT NULL,
  role VARCHAR(20) NOT NULL CHECK (role IN ('student', 'teacher')),
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS presentations (
  id SERIAL PRIMARY KEY,
  teacher_id INT NOT NULL REFERENCES users(id),
  title VARCHAR(255) NOT NULL,
  description TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS slides (
  id SERIAL PRIMARY KEY,
  presentation_id INT NOT NULL REFERENCES presentations(id) ON DELETE CASCADE,
  order_index INT NOT NULL DEFAULT 0,
  question TEXT NOT NULL,
  test_type VARCHAR(20) NOT NULL CHECK (test_type IN ('choice', 'tags')),
  is_active BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS slide_options (
  id SERIAL PRIMARY KEY,
  slide_id INT NOT NULL REFERENCES slides(id) ON DELETE CASCADE,
  label CHAR(1),
  text TEXT NOT NULL
);

CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS poll_sessions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  slide_id INT NOT NULL REFERENCES slides(id) ON DELETE CASCADE,
  started_at TIMESTAMPTZ DEFAULT NOW(),
  closed_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS responses (
  id SERIAL PRIMARY KEY,
  session_id UUID NOT NULL REFERENCES poll_sessions(id) ON DELETE CASCADE,
  user_id INT NOT NULL REFERENCES users(id),
  option_id INT REFERENCES slide_options(id),
  tags TEXT[],
  created_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(session_id, user_id)
);

