-- Initialize database schema for local development

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm"; -- For text search

-- Create games table
CREATE TABLE IF NOT EXISTS games (
    id BIGINT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    summary TEXT,
    storyline TEXT,
    first_release_date TIMESTAMP,
    rating DECIMAL(4, 2),
    rating_count INTEGER,
    aggregated_rating DECIMAL(4, 2),
    aggregated_rating_count INTEGER,
    cover_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create genres table
CREATE TABLE IF NOT EXISTS genres (
    id BIGINT PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);

-- Create platforms table
CREATE TABLE IF NOT EXISTS platforms (
    id BIGINT PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);

-- Create themes table
CREATE TABLE IF NOT EXISTS themes (
    id BIGINT PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);

-- Create join tables
CREATE TABLE IF NOT EXISTS games_genres (
    game_id BIGINT REFERENCES games(id) ON DELETE CASCADE,
    genre_id BIGINT REFERENCES genres(id) ON DELETE CASCADE,
    PRIMARY KEY (game_id, genre_id)
);

CREATE TABLE IF NOT EXISTS games_platforms (
    game_id BIGINT REFERENCES games(id) ON DELETE CASCADE,
    platform_id BIGINT REFERENCES platforms(id) ON DELETE CASCADE,
    PRIMARY KEY (game_id, platform_id)
);

CREATE TABLE IF NOT EXISTS games_themes (
    game_id BIGINT REFERENCES games(id) ON DELETE CASCADE,
    theme_id BIGINT REFERENCES themes(id) ON DELETE CASCADE,
    PRIMARY KEY (game_id, theme_id)
);

-- Create recommendations table
CREATE TABLE IF NOT EXISTS recommendations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    game_id BIGINT REFERENCES games(id) ON DELETE CASCADE,
    recommended_game_id BIGINT REFERENCES games(id) ON DELETE CASCADE,
    score DECIMAL(5, 4) NOT NULL,
    model_version VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (game_id, recommended_game_id, model_version)
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_games_name ON games USING gin (name gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_games_rating ON games (rating DESC);
CREATE INDEX IF NOT EXISTS idx_games_release_date ON games (first_release_date DESC);
CREATE INDEX IF NOT EXISTS idx_recommendations_game_id ON recommendations (game_id);
CREATE INDEX IF NOT EXISTS idx_recommendations_score ON recommendations (score DESC);

-- Insert some sample genres
INSERT INTO genres (id, name) VALUES
(1, 'Action'),
(2, 'Adventure'),
(3, 'RPG'),
(4, 'Strategy'),
(5, 'Simulation'),
(6, 'Sports'),
(7, 'Puzzle'),
(8, 'Racing'),
(9, 'Shooter'),
(10, 'Fighting')
ON CONFLICT (id) DO NOTHING;

-- Insert some sample platforms
INSERT INTO platforms (id, name) VALUES
(1, 'PC'),
(2, 'PlayStation 5'),
(3, 'Xbox Series X'),
(4, 'Nintendo Switch'),
(5, 'PlayStation 4'),
(6, 'Xbox One'),
(7, 'iOS'),
(8, 'Android'),
(9, 'Web')
ON CONFLICT (id) DO NOTHING;

-- Insert some sample themes
INSERT INTO themes (id, name) VALUES
(1, 'Fantasy'),
(2, 'Science Fiction'),
(3, 'Historical'),
(4, 'Horror'),
(5, 'Comedy'),
(6, 'Drama'),
(7, 'Thriller'),
(8, 'Mystery'),
(9, 'Survival'),
(10, 'Open World')
ON CONFLICT (id) DO NOTHING;
