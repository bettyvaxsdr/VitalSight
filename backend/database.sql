DROP TABLE IF EXISTS health_data;

CREATE TABLE health_data(
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    heart_rate INTEGER,
    temperature FLOAT,
    state VARCHAR(10)
);