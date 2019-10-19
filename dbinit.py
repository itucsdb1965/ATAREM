import os
import sys
import requests
import json

import psycopg2 as dbapi2
import psycopg2.extras

INIT_STATEMENTS = [
    """
    CREATE TABLE IF NOT EXISTS USERS (
    id BIGSERIAL PRIMARY KEY NOT NULL,
    name VARCHAR(25) NOT NULL,
    email VARCHAR(35) NOT NULL,
    username VARCHAR(16) NOT NULL,
    password VARCHAR(200) NOT NULL,
    register_date DATE NOT NULL default CURRENT_DATE
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS MOVIES (
    id BIGSERIAL PRIMARY KEY NOT NULL,
    title VARCHAR NOT NULL,
    year INTEGER NOT NULL,
    directors VARCHAR[] NOT NULL,
    writers VARCHAR[] NOT NULL,
    urlPoster VARCHAR NOT NULL,
    genres VARCHAR[] NOT NULL,
    plot TEXT NOT NULL,
    simpleplot TEXT NOT NULL,
    idIMDB VARCHAR NOT NULL,
    runtime VARCHAR NOT NULL,
    rating DOUBLE PRECISION NOT NULL
    )
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
            cur.execute("INSERT INTO movies (title, year, directors, writers, urlPoster, genres, plot, simpleplot, idIMDB, rating, runtime) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                        (movie['title'], movie['year'], directors, writers, movie['urlPoster'], movie['genres'], movie['plot'], movie['simplePlot'], movie['idIMDB'], movie['rating'], movie['runtime']))
        connection.commit()
        cursor.close()


if __name__ == "__main__":
    url = os.getenv("DATABASE_URL")
    if url is None:
        print("Usage: DATABASE_URL=url python dbinit.py", file=sys.stderr)
        sys.exit(1)
    initialize(url)
