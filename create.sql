CREATE TABLE users(
    id SERIAL PRIMARY KEY,
    username VARCHAR NOT NULL,
    pass VARCHAR NOT NULL
);

CREATE TABLE books(
    isbn BIGINT PRIMARY KEY,
    title VARCHAR NOT NULL,
    author VARCHAR NOT NULL,
    year INT NOT NULL
);

ALTER TABLE books
ALTER COLUMN isbn TYPE VARCHAR;

ALTER TABLE books
RENAME COLUMN year TO yr;

ALTER TABLE books
ALTER COLUMN yr TYPE VARCHAR;

CREATE TABLE reviews(
    id SERIAL PRIMARY KEY,
    u_id INT REFERENCES users,
    book_id VARCHAR REFERENCES books,
    rating INT NOT NULL,
    review VARCHAR NOT NULL
);