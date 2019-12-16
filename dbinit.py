import os
import sys
import requests
import json
import random
import psycopg2 as dbapi2
import psycopg2.extras
from random import shuffle
from passlib.hash import pbkdf2_sha256

INIT_STATEMENTS = [
    """
    /* USERS */

CREATE TABLE IF NOT EXISTS USERS (
  id BIGSERIAL PRIMARY KEY NOT NULL,
  name VARCHAR(25) NOT NULL,
  email VARCHAR(35) NOT NULL,
  username VARCHAR(16) NOT NULL,
  password VARCHAR(200) NOT NULL,
  avatar VARCHAR NOT NULL DEFAULT '/static/img/defaultprofile.jpeg',
  birth_date DATE NOT NULL,
  gender VARCHAR(10) DEFAULT NULL,
  register_date DATE NOT NULL default CURRENT_DATE,
  UNIQUE(username)
);

CREATE TABLE  IF NOT EXISTS MOVIES (
  id BIGSERIAL PRIMARY KEY NOT NULL,
  title VARCHAR NOT NULL,
  year INTEGER NOT NULL,
  directors VARCHAR[] NOT NULL,
  writers VARCHAR[] NOT NULL,
  urlPoster VARCHAR NOT NULL,
  genres VARCHAR[] NOT NULL,
  idIMDB VARCHAR NOT NULL,
  plot TEXT NOT NULL,
  simpleplot TEXT NOT NULL,
  runtime VARCHAR NOT NULL,
  overallRating DOUBLE PRECISION DEFAULT 0,
  votes INTEGER NOT NULL DEFAULT 0,
  rating DOUBLE PRECISION NOT NULL,
   UNIQUE(idIMDB)
);
CREATE TABLE IF NOT EXISTS WATCHLIST(
  id BIGSERIAL PRIMARY KEY NOT NULL,
  username VARCHAR(25) REFERENCES users(username) on delete cascade NOT NULL,
  movie_id VARCHAR(25) REFERENCES movies(idIMDB)  on delete cascade  NOT NULL,
  type INT default 0,
  watchOrder INT default 1,
  register_date DATE NOT NULL default CURRENT_DATE,
  notes VARCHAR[] DEFAULT NULL
);

/* MOVIES */


CREATE TABLE IF NOT EXISTS STARS(
  id BIGSERIAL PRIMARY KEY NOT NULL,
  urlIMDB VARCHAR(50) NOT NULL,
  name VARCHAR(30) NOT NULL,
  knownFor VARCHAR[] NOT NULL,
  rating INT NOT NULL,
  user_rating INT DEFAULT 0,
  date_created DATE NOT NULL default CURRENT_DATE
);


/* FORUM */

CREATE TABLE IF NOT EXISTS FORUMPOSTS (
  id BIGSERIAL PRIMARY KEY NOT NULL,
  username VARCHAR(25) NOT NULL REFERENCES USERS(username) ON DELETE CASCADE,
  important int default 0,
  title VARCHAR NOT NULL,
  body VARCHAR NOT NULL,
  rep INT NOT NULL default 0,
  date_created DATE NOT NULL default CURRENT_DATE
);

CREATE TABLE  IF NOT EXISTS COMMENTS(
  id BIGSERIAL PRIMARY KEY NOT NULL,
  thread BIGSERIAL NOT NULL REFERENCES FORUMPOSTS(id) ON DELETE CASCADE,
  username VARCHAR(25) NOT NULL REFERENCES USERS(username) ON DELETE CASCADE,
  body VARCHAR NOT NULL,
  date_created DATE NOT NULL default CURRENT_DATE
);

/* ON AIR */

CREATE TABLE  IF NOT EXISTS IN_THEATERS(
  id BIGSERIAL PRIMARY KEY NOT NULL,
  type INT DEFAULT 0, -- 0 for in theaters, 1 for incoming
  title VARCHAR,
  year INT NOT NULL,
  releaseDate DATE NOT NULL ,
  directors VARCHAR[] NOT NULL,
  genres  VARCHAR[] NOT NULL,
  simpleplot VARCHAR NOT NULL,
  rating DOUBLE PRECISION NOT NULL,
  runtime VARCHAR NOT NULL,
  urlIMDB VARCHAR NOT NULL,
  urlPoster VARCHAR NOT NULL,
  writers VARCHAR[] NOT NULL,
  point int DEFAULT 0,
  plike VARCHAR[] DEFAULT NULL 
  
  
);

CREATE TABLE IF NOT EXISTS SHOWTIMES(
  id BIGSERIAL PRIMARY KEY NOT NULL,
  title VARCHAR NOT NULL,
  hours VARCHAR[] NOT NULL,
  cinema VARCHAR(20) NOT NULL,
  date VARCHAR(10) NOT NULL
);
   
    """,
]


def initialize(url):
    names = ["ugure17", "stranger", "hola"]
    content_part = """
    Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nam venenatis commodo magna sed sollicitudin. In vel venenatis libero. Fusce in ultricies est. Ut porta elit ac lacus consequat, quis malesuada ex aliquam. Aenean lorem arcu, pellentesque at mattis pretium, suscipit maximus arcu. Duis nulla orci, vulputate ac mauris et, tincidunt cursus odio. Cras ante ante, maximus eget erat nec, lobortis rutrum ante. Vivamus ac nunc ornare, viverra dui cursus, pretium neque. Cras non nisi vitae sem egestas tincidunt vel ac tellus. Suspendisse eleifend fermentum ultricies. Cras semper porta ex, vel posuere quam fermentum ut. 
    """.split(" ")
    head_part = """
      Lorem ipsum dolor sit amet Ut condimentum turpis at
    """.split(" ")
    with dbapi2.connect(url) as connection:
        cursor = connection.cursor()
        for statement in INIT_STATEMENTS:
            cursor.execute(statement)
        cur = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute('SELECT COUNT(*) FROM MOVIES')
        count = cur.fetchone()
        if count[0] < 200:
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
              cur.execute("INSERT INTO movies (title, year, directors, writers, urlPoster, genres, plot, simpleplot,rating, runtime, idIMDB) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                          (movie['title'], movie['year'], directors, writers, movie['urlPoster'], movie['genres'], movie['plot'], movie['simplePlot'] , movie['rating'], movie['runtime'], movie['idIMDB']))
        cur.execute('SELECT COUNT(*) FROM STARS')
        count_star=cur.fetchone()
        if count_star[0]<80:
          resp_star=requests.get("https://www.myapifilms.com/imdb/starmeter?token=93dd88e2-17fb-40e8-89a3-1707b3c8ac82&format=json")
          text= json.loads(resp_star.text)
          for star in text['data']:
            knownFor=[]
            knownFor.append(star['knownFor'])
            cur.execute("INSERT INTO stars (name, urlIMDB, knownFor, rating) VALUES (%s, %s, %s, %s)",
                          (star['name'], star['urlIMDB'],knownFor,random.randint(6,10) ))
        # cur.execute('SELECT COUNT(*) FROM forumposts')
        # count_posts = cur.fetchone()
        # if count_posts[0] < 10:
        #   for i in range(0, 25):
        #     shuffle(head_part) 
        #     shuffle(content_part)
        #     user = random.choice(names)
        #     cur.execute('INSERT INTO forumposts (username, title, body) VALUES (%s, %s, %s)', (user, " ".join(head_part), " ".join(content_part)))
        # cur.execute('SELECT COUNT(*) FROM comments')
        # count_comments = cur.fetchone()
        # if count_comments[0] < 10:
        #   for i in range(0, 3):
        #     for j in range(1, 26):
        #       shuffle(content_part)
        #       user = random.choice(names)
        #       bodddy  = " ".join(content_part)
        #       cur.execute(f"INSERT INTO comments (username, thread, body) VALUES ('{user}', '{j}', '{bodddy}')")
        # connection.commit()
        cursor.close()
        cur.execute('SELECT COUNT(*) FROM IN_THEATERS')
        count_theater=cur.fetchone()
        if count_theater[0]<4:
          resp_theaters=requests.get("https://www.myapifilms.com/imdb/inTheaters?token=93dd88e2-17fb-40e8-89a3-1707b3c8ac82&format=json&language=en-us")
          data_t= json.loads(resp_theaters.text)
          
          movies=data_t['data']['inTheaters']
          for movie in movies:
            try:
              movies=movie['movies']
            except:
              pass
          for movie in movies:
              directors = []
              writers = []
             
              for director in movie['directors']:
                  directors.append(director['name'])
              for writer in movie['writers']:
                  writers.append(writer['name'])
             
              cur.execute("INSERT INTO IN_THEATERS (title, year, directors, writers, urlPoster, genres, simpleplot,rating, runtime, urlIMDB,releaseDate) VALUES (%s, %s, %s, %s, %s, %s, %s, %s,%s,%s,%s)",
                          (movie['title'], movie['year'], directors, writers, movie['urlPoster'], movie['genres'], movie['simplePlot'] , movie['rating'], movie['runtime'], movie['urlIMDB'], movie['releaseDate']))      

if __name__ == "__main__":
    url = os.getenv("DATABASE_URL")
    if url is None:
        print("Usage: DATABASE_URL=url python dbinit.py", file=sys.stderr)
        sys.exit(1)
    initialize(url)
