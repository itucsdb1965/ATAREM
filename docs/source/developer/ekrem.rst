Parts Implemented by Ekrem UĞUR
================================
.. note:: All table are created in db_init.py file.

**************
Movies
**************

1. Initilization
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: sql

    CREATE TABLE IF NOT EXISTS MOVIES (
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

2. Create
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python
    
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
            
First we fetch the data with the associated API call from myapifilms, then we iterate through the response and insert each of them to the table MOVIES.

3. Read
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    # @Route /api/movie/id
    # @Methods GET
    # @Desc Get movie data with specific id  
    @app.route('/api/movie/<id>', methods=['GET'])
    def getMovie(id):
        cur = con.cursor(cursor_factory=extras.DictCursor)
        cur.execute(f"SELECT * FROM movies WHERE idimdb='{id}'")
        movie = cur.fetchone()
        cur.close()
        return {"content": dict(movie)}

.. code-block:: python

    # @Route /api/movie
    # @Methods GET
    # @Desc Get data of movies with counter
    @app.route('/api/movie', methods=['GET'])
    def getMovies():
        count = request.args.get("count")
        if int(count) >= 250:
            return {"content": {}}
        cur = con.cursor(cursor_factory=extras.DictCursor)
        cur.execute(f"SELECT * FROM movies LIMIT 9 OFFSET {int(count)}")
        movies = cur.fetchall()
        for i in range(0, len(movies)):
            movies[i] = dict(movies[i])
        cur.close()
        return {"content": movies}

First api call returns the data of a specific movie, second api call returns the next 9 movies' data with respect to the parameter count.

4. Update
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python
    # @Route /api/movie/rate
    # @Methods POST
    # @Desc Rating for a movie with id and rating parameters
    @app.route('/api/movie/rate', methods=['POST'])
    def RateMovie():
        cur = con.cursor(cursor_factory=extras.DictCursor)
        id = request.args.get('id')
        rating = request.args.get('rating')
        cur.execute(f"UPDATE MOVIES SET overallRating=(overallRating*votes + {rating})/(votes+1), votes=votes+1 WHERE id = {id}")
        con.commit()
        cur.close()
        return {"content": "success"}

Parameters rating and id determines which movie will get which rating, and the movie is updated in the database.

5. Delete 
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python
    
    # @Route /api/movie/delete
    # @Methods POST
    # @Desc Remove movie with parameter id
    @app.route('/api/movie/delete', methods=['POST'])
    def deleteMovie():
        id = request.args.get('id')
        cur = con.cursor(cursor_factory=extras.DictCursor)
        cur.execute(f"DELETE FROM MOVIES WHERE id={id}")
        con.commit()
        cur.close()
        return {"content": "success"}
        
Parameter id determines which movie will be deleted.

****************
FORUMPOSTS
****************

1. Initilization
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: sql

    CREATE TABLE IF NOT EXISTS FORUMPOSTS (
      id BIGSERIAL PRIMARY KEY NOT NULL,
      username VARCHAR(25) NOT NULL REFERENCES USERS(username) ON DELETE CASCADE,
      important int default 0,
      title VARCHAR NOT NULL,
      body VARCHAR NOT NULL,
      rep INT NOT NULL default 0,
      date_created DATE NOT NULL default CURRENT_DATE
    );
         
A basic template is created for a forum post.

2. Create
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python
    
    # @Route /api/forum/thread
    # @Methods POST
    # @Desc create a thread with parameters username, title and body
    @app.route('/api/forum/thread', methods=['POST'])
    def createThreadApi():
        username = request.args.get('username')
        title = request.args.get('title')
        body = request.args.get('body')
        cur = con.cursor()
        cur.execute("INSERT INTO forumposts (username, title, body) VALUES (%s, %s, %s)",
                    (username, title, body))
        con.commit()
        cur.close()
        return {"content": "success"}
         
Parameters username, title and body are sent to the associated API call via a post request, then the thread with the given data will be created.

3. Read
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    # @Route /api/forum/thread
    # @Methods GET
    # @Desc Get thread info with either id or count and offset as paramters,
    #   if both parameters provided, threads first with username, then with given id will be returned
    #   count will return latest submitted n threads disregarding first offset rows
    @app.route('/api/forum/thread')
    def getThread():
        cur = con.cursor(cursor_factory=extras.DictCursor)
        username = request.args.get('username')
        id = request.args.get('id')
        count = request.args.get('count')
        offset = request.args.get('offset')
        if username:
            cur.execute(f"SELECT * FROM forumposts WHERE username='{username}")
            threads = cur.fetchall()
            for i in range(0, len(threads)):
                threads[i] = dict(threads[i])
            cur.close()
            return {"content": threads}
        elif id:
            cur.execute(f'SELECT * FROM forumposts WHERE id={id}')
            thread = cur.fetchone()
            cur.close()
            return {"content": dict(thread)}
        elif count:
            if not offset:
                offset = 0
            cur.execute(f'SELECT * FROM forumposts ORDER BY id DESC LIMIT {count} OFFSET {offset}')
            threads = cur.fetchall()
            for i in range(0, len(threads)):
                threads[i] = dict(threads[i])
            cur.close()
            return {"content": threads}
        else:
            return {"content": "failure"}
   
This API call has 3 options, you either specify username, thread id or count. Specified username will return all the threads that belong to that user, id will return the distinct thread and the count will return the last {count} elements. You can also specify an offset for count option.

4. Update
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python
    
    # @Route /api/forum/thread/edit
    # @Methods POST
    # @Desc Edit thread with id, title and body parameters
    @app.route('/api/forum/thread/edit', methods=['POST'])
    def editThread():
        id = request.args.get('id')
        title = request.args.get('title')
        body = request.args.get('body')
        cur = con.cursor(cursor_factory=extras.DictCursor)
        cur.execute(f"UPDATE forumposts SET title='{title}', body='{body}' WHERE id={id}")
        con.commit()
        cur.close()
        return {"content": "success"}
      
Using parameters id, title and body you can update a movie, query is pretty straightforward.  

5. Delete
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python
        
    # @Route /api/forum/thread/delete
    # @Methods POST
    # @Desc Remove thread with parameter id
    @app.route('/api/forum/thread/delete', methods=['POST'])
    def deleteThread():
        id = request.args.get('id')
        cur = con.cursor(cursor_factory=extras.DictCursor)
        cur.execute(f"DELETE FROM FORUMPOSTS WHERE id={id}")
        con.commit()
        cur.close()
        return {"content": "success"}
          
Another straightforward query with only parameter id.

****************
USERS
****************

1. Initilization
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: sql

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

A simple table for authorization purposes.

2. Create
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    @app.route('/register', methods=['GET', 'POST'])
    @is_logged_out
    def register():
        form = RegistrationForm(request.form)
        if request.method == 'POST' and form.validate():
            name = form.name.data
            username = form.username.data
            email = form.email.data
            password = form.password.data
            birth = form.birth.data
            response = requests.post(f'{domain}/api/user/register?name={name}&username={username}&email={email}&password={password}&birth={birth}')
            if response.json()["content"] == "success":
                flash('Registration successful!', 'success')
                return redirect(url_for('login'))
            else:
                flash('Registration failed', 'danger')

.. code-block:: python

    # @Route /api/user/register
    # @Methods POST
    # @Desc Register a user with parameters
    @app.route('/api/user/register', methods=['POST'])
    def registerUser():
      name = request.args.get("name")
      username = request.args.get("username")
      email = request.args.get("email")
      password = request.args.get("password")
      birth = request.args.get("birth")
      cur = con.cursor()
      cur.execute(f"SELECT COUNT(*) FROM USERS WHERE username='{username}' OR email='{email}'")
      count = cur.fetchone()
      if count[0] > 0:
          return {"content": "failure"}
      cur.execute("INSERT INTO users (name, username, email, password, birth_date) VALUES (%s, %s, %s, %s, %s)",
                  (name, username, email, pbkdf2_sha256.hash(password), birth))
      con.commit()
      cur.close()
      return {"content": "success"}

The request is in the same url as its form. Using wtforms, we send the data we get from form to our API, just to keep our standard.

3. Read
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    # @Route /api/user/login
    # @Methods POST
    # @Desc Register a user with parameters
    @app.route('/api/user/login', methods=['POST'])
    def loginUser():
        username = request.args.get("username")
        password = request.args.get("password")
        cur = con.cursor(cursor_factory=extras.DictCursor)
        cur.execute(
            "SELECT * FROM users WHERE username='%s'" % (username))
        data = cur.fetchone()
        if(data):
            hash = data['password']
            if pbkdf2_sha256.verify(password, hash):
                return{"content": "success"}
            else:
                return{"content": "failure"}
        else:
            return{"content": "failure"}
        
Above is an example of reading from table USERS while validating a user login, parameters are username and password.

4. Update
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python
    
    # @Route /api/avatar
    # @Methods POST
    # @Desc parameters id and image route changes user avatar
    @app.route('/api/avatar', methods=["POST"])
    def setAvatar():
        cur = con.cursor(cursor_factory=extras.DictCursor)
        username = request.args.get('username')
        path = request.args.get('path')
        cur.execute(f"UPDATE USERS SET AVATAR='{path}' WHERE username='{username}'")
        con.commit()
        cur.close()
        return {"content": "success"}

When a users avatar is saved to our server, we send the path and username to our API so that we know where the latest avatar a user uploaded is.

5. Delete
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python
        
    # @Route /api/user/delete
    # @MEthods POST
    # @Desc Remove user with parameter username
    @app.route('/api/user/delete', methods=['POST'])
    def deleteUser():
        username = request.args.get('username')
        cur = con.cursor(cursor_factory=extras.DictCursor)
        cur.execute(f"DELETE FROM USERS WHERE username='{username}'")
        con.commit()
        cur.close() 
        return {"content": "success"}
          
Again a pretty straightforward query.

