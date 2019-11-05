import os
import sys
import requests
import json

import psycopg2 as dbapi2
import psycopg2.extras

INIT_STATEMENTS = [
    """
    /* USERS */

CREATE TABLE IF NOT EXISTS USERS (
  id BIGSERIAL PRIMARY KEY NOT NULL,
  name VARCHAR(25) NOT NULL,
  email VARCHAR(35) NOT NULL,
  username VARCHAR(16) NOT NULL,
  password VARCHAR(200) NOT NULL,
  register_date DATE NOT NULL default CURRENT_DATE
);


CREATE TABLE IF NOT EXISTS WATCHLIST(
  id BIGSERIAL PRIMARY KEY NOT NULL,
  username VARCHAR(25) NOT NULL,
  movie_id BIGSERIAL NOT NULL
);

/* MOVIES */

CREATE TABLE  IF NOT EXISTS MOVIEPOSTS(
  id BIGSERIAL PRIMARY KEY NOT NULL,
  movie_id VARCHAR(25) NOT NULL,
  type INT NOT NULL default 0, -- 0 for comments, 1 for reviews 
  username VARCHAR(25) NOT NULL,
  title VARCHAR(25) NOT NULL,
  body VARCHAR(250) NOT NULL,
  date_created DATE NOT NULL default CURRENT_DATE
);

CREATE TABLE  IF NOT EXISTS MOVIES (
  id BIGSERIAL PRIMARY KEY NOT NULL,
  title VARCHAR NOT NULL,
  year INTEGER NOT NULL,
  directors VARCHAR[] NOT NULL,
  writers VARCHAR[] NOT NULL,
  urlPoster VARCHAR NOT NULL,
  genres VARCHAR[] NOT NULL,
  plot TEXT NOT NULL,
  simpleplot TEXT NOT NULL,
  runtime VARCHAR NOT NULL,
  rating DOUBLE PRECISION NOT NULL
);

CREATE TABLE IF NOT EXISTS STARS(
  id BIGSERIAL PRIMARY KEY NOT NULL,
  urlIMDB VARCHAR(50) NOT NULL,
  name VARCHAR(30) NOT NULL,
  knownFor VARCHAR[] NOT NULL,
  rating INT NOT NULL
);

/* FORUM */

CREATE TABLE IF NOT EXISTS FORUMPOSTS (
  id BIGSERIAL PRIMARY KEY NOT NULL,
  username VARCHAR(25) NOT NULL,
  type INT NOT NULL, -- 0 for threads, 1 for news
  body VARCHAR(120) NOT NULL,
  date_created DATE NOT NULL default CURRENT_DATE
);

CREATE TABLE  IF NOT EXISTS COMMENTS(
  id BIGSERIAL PRIMARY KEY NOT NULL,
  thread BIGSERIAL NOT NULL,
  username VARCHAR(25) NOT NULL,
  body VARCHAR(120) NOT NULL,
  date_created DATE NOT NULL default CURRENT_DATE
);

CREATE TABLE IF NOT EXISTS DISCUSSION(
  id BIGSERIAL PRIMARY KEY NOT NULL,
  username VARCHAR(25) NOT NULL,
  body VARCHAR NOT NULL,
  date_created DATE NOT NULL default CURRENT_DATE
);

/* ON AIR */

CREATE TABLE  IF NOT EXISTS IN_THEATERS(
  id BIGSERIAL PRIMARY KEY NOT NULL,
  type INT NOT NULL, -- 0 for in theaters, 1 for incoming
  title VARCHAR,
  year INT NOT NULL,
  release_date DATE NOT NULL ,
  directors VARCHAR[] NOT NULL,
  genres  VARCHAR[] NOT NULL,
  simpleplot VARCHAR NOT NULL,
  rating DOUBLE PRECISION NOT NULL,
  runtime VARCHAR NOT NULL,
  urlIMDB VARCHAR NOT NULL,
  urlPoster VARCHAR NOT NULL,
  writers VARCHAR[] NOT NULL
);

CREATE TABLE IF NOT EXISTS SHOWTIMES(
  id BIGSERIAL PRIMARY KEY NOT NULL,
  title VARCHAR NOT NULL,
  hours VARCHAR[] NOT NULL,
  cinema VARCHAR(20) NOT NULL,
  date VARCHAR(10) NOT NULL
);

CREATE TABLE IF NOT EXISTS TICKETS(
  id BIGSERIAL PRIMARY KEY NOT NULL,
  hour VARCHAR(5) NOT NULL,
  cinema VARCHAR(20) NOT NULL,
  username VARCHAR(25) NOT NULL
);
   
    """,
]


def initialize(url):
    with dbapi2.connect(url) as connection:
        cursor = connection.cursor()
        for statement in INIT_STATEMENTS:
            cursor.execute(statement)
        cur = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
        resp = requests.get(
            'https://www.myapifilms.com/imdb/top?start=1&end=250&token=93dd88e2-17fb-40e8-89a3-1707b3c8ac82&format=json&data=1')
        real = json.loads(resp.text)
        for movie in real['data']['movies']:
            directors = []
            writers = []
            for director in movie['directors']:
                directors.append(director['name'])
            for writer in movie['writers']:
                writers.append(writer['name'])
            cur = connection.cursor()
            cur.execute("INSERT INTO movies (title, year, directors, writers, urlPoster, genres, plot, simpleplot,rating, runtime) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                        (movie['title'], movie['year'], directors, writers, movie['urlPoster'], movie['genres'], movie['plot'], movie['simplePlot'] , movie['rating'], movie['runtime']))
        connection.commit()
        cursor.close()


if __name__ == "__main__":
    url = os.getenv("DATABASE_URL")
    if url is None:
        print("Usage: DATABASE_URL=url python dbinit.py", file=sys.stderr)
        sys.exit(1)
    initialize(url)
