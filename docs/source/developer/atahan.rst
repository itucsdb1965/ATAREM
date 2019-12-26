Parts Implemented by Atahan ÖZER
================================
.. note:: All table creations exist in db_init.py file.

**************
Watchlist 
**************

1. Creation
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: sql

    CREATE TABLE IF NOT EXISTS WATCHLIST(
      id BIGSERIAL PRIMARY KEY NOT NULL,
      username VARCHAR(25) REFERENCES users(username) on delete cascade NOT NULL,
      movie_id VARCHAR(25) REFERENCES movies(idIMDB)  on delete cascade  NOT NULL,
      status INT default 0,
      watchOrder INT default 1,
      register_date DATE NOT NULL default CURRENT_DATE,
      notes VARCHAR(200) DEFAULT NULL,
      stream VARCHAR(80) DEFAULT NULL 
    );

Username references the users table and movie_id references to movies table .If one of the references is deleted the corresponding row will also be deleted


2. Inserting
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python
    
        if(request.method == 'POST' and formname =="add"):
        check=request.form['check']
        status=0
        if(check=="ok"):
            status=1
        
        cur = con.cursor(cursor_factory=extras.DictCursor) 
        cur.execute(f"SELECT EXISTS(SELECT *FROM watchlist WHERE username='{username}' and movie_id = '{id}') ")
        exist=cur.fetchone()
        
        if(exist[0]==True): 
            flash('It is already in your watchlist', 'danger')
        else:
            cur.execute(f"INSERT INTO watchlist(username,movie_id,status) VALUES ('{username}','{id}','{status}')")
            con.commit()
            cur.close()
            flash('Added to your watchlist', 'success')
            
In the first query it is checked if the movie already exist in your watchlist,if it is not then it is inserted into the table.


3. Reading
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    username = session['username']
    cur = con.cursor(cursor_factory=extras.DictCursor)
    cur.execute(
        f"SELECT * from watchlist WHERE username='{username}'ORDER BY watchorder DESC")
    watch = cur.fetchall()
    title = []

    for i in watch:
        cur.execute(f"SELECT title FROM movies WHERE idimdb='{i[2]}'")
        temp = cur.fetchone()
        temp.append(i[2])
        temp.append(0)
        temp.append(i[4])
        temp.append(i[6])
        temp.append(i[3])
        title.append(temp)

     return render_template('watchlist.html', username=username, title=title)
     
In the first query  watchlist from a user  is read from database later on in the second query details of a movie stored in title in order to send it to html.

4.Updating
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    if request.method == 'POST' and(formname == "order"):
        movie_id = request.form.get('movie_id')

        cur = con.cursor(cursor_factory=extras.DictCursor)
        cur.execute(
            f"SELECT watchorder FROM watchlist WHERE username='{username}'and movie_id ='{movie_id}'")
        order = cur.fetchone()

        order = order[0]

        if(request.form.get("minus") == '-' and order > 1):
            order = order-1

        if(request.form.get("plus") == "+"and order < 3):
            order = order+1

        cur.execute(
            f"UPDATE  watchlist SET watchorder ={order} WHERE username='{username}'and movie_id ='{movie_id}'")
        con.commit()
        cur.close
        return redirect(url_for('watchlist'))

Orders of the movies in watchlist are updated with orderform.First query finds the corresponding watchorder and the second query updates the watchorder

5.Deleting 
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python
    
    if request.method == 'POST'and formname == "delete":

        movie_id = request.form.get('movie_id')
        type = request.form.get('type')
        cur = con.cursor(cursor_factory=extras.DictCursor)

        cur.execute(
            f"DELETE FROM watchlist WHERE movie_id='{movie_id}'  and username='{username}'")
        con.commit()
        cur.close()
        return redirect(url_for('watchlist'))
        
Movie is deleted if delete form is triggered.

****************
Stars
****************

1. Creation
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: sql

      CREATE TABLE IF NOT EXISTS STARS(
      id BIGSERIAL PRIMARY KEY NOT NULL,
      urlIMDB VARCHAR(50) NOT NULL,
      name VARCHAR(30) NOT NULL,
      knownFor VARCHAR[] NOT NULL,
      rating INT NOT NULL,
      user_rating INT DEFAULT 0,
      date_created DATE NOT NULL default CURRENT_DATE
         );
         
2. Inserting
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python
    
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
         
Inserting made by using myapifilms API.First star data requested from API then it is inserted to database automatically .Firts query exist in order to keep the size limited since inserting is automated any error may overload the database.

3. Reading
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    cur = con.cursor(cursor_factory=extras.DictCursor)
    try:
        cur.execute(f"SELECT * FROM stars ORDER BY id ASC ")
    except :
            con.rollback()
    stars = cur.fetchall()
    cur.close()
    return render_template('stars.html', stars=stars , form=form)
   
Reading is implemented with this simple query.

4. Updating
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python
    
    formname=request.form.get('formname')
    if(request.method == 'POST' and formname=="update"):
        
        cur = con.cursor(cursor_factory=extras.DictCursor)
        try:
            cur.execute(f"SELECT user_rating FROM stars WHERE id={id} ")
        except :
            con.rollback()
        star_rate=cur.fetchone()
        try:
            user_rating = int(form.point.data) + int(star_rate['user_rating'])
        except:
            flash("Must be a integer value","danger")
            return redirect(url_for('stars'))
        try:
            cur.execute(
            f"UPDATE stars SET user_rating={user_rating}  WHERE id={id}")
        except :
            con.rollback()
        con.commit()
        cur.close
        return redirect(url_for('stars'))
   
If the formname is update ,the star will be found with the first query then the point of the star will be updated.


5. Delete
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python
        
          elif (request.method == 'POST' and formname=="delete"):
          cur = con.cursor(cursor_factory=extras.DictCursor)
          name =request.form.get('name')
          try:
            cur.execute(f"DELETE FROM stars WHERE name='{name}'")
          except :
            con.rollback()
          con.commit()
          cur.close()
          return redirect(url_for('stars'))
          
If the formname is "delete" the star will be deleted with this simple query.

****************
IN THEATERS
****************

1. Creation
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: sql

      CREATE TABLE  IF NOT EXISTS IN_THEATERS(
      id BIGSERIAL PRIMARY KEY NOT NULL,
      type INT DEFAULT 0, 
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
      plike VARCHAR[] DEFAULT NULL );
      

2. Inserting
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

                cur.execute('SELECT COUNT(*) FROM IN_THEATERS')
                count_theater=cur.fetchone()
                if count_theater[0]<4:
                  resp_theaters=requests.get("https://www.myapifilms.com/imdb/inTheaters?token=93dd88e2-17fb-40e8-89a3-                                     1707b3c8ac82&format=json&language=en-us")
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

                      cur.execute("INSERT INTO IN_THEATERS (title, year, directors, writers, urlPoster, genres, simpleplot,rating,                                          runtime, urlIMDB,releaseDate) VALUES (%s, %s, %s, %s, %s, %s, %s, %s,%s,%s,%s)",
                                  (movie['title'], movie['year'], directors, writers, movie['urlPoster'], movie['genres'],                                                  movie['simplePlot'] , movie['rating'], movie['runtime'], movie['urlIMDB'], movie['releaseDate']))
 
3. Reading
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    # @Route /api/inTheaters
    # @Methods get
    # @Desc getting the intheater movies from database
    @app.route('/api/inTheaters', methods=['GET'])
    def getTheaters():
        count = request.args.get("count")
        if int(count) >= 10:
            return {"content": {}}
        cur = con.cursor(cursor_factory=extras.DictCursor)
        cur.execute(f"SELECT * FROM in_theaters LIMIT 9 OFFSET {int(count)}")
        movies = cur.fetchall()
        for i in range(0, len(movies)):
            movies[i] = dict(movies[i])
        cur.close()
        return {"content": movies}
        
Above is the python code which queries has been made and below is code that requests from API
        
.. code-block:: javascript

        function loadItems() {
            fetch(`/api/inTheaters?count=${count}`)
              .then(response => response.json())
              .then(data => {
                if (!data.content.length) {
                  sentinel.innerHTML = "For this is the end, hold your breath and count to ten...";
                  setTimeout(() => {
                    console.log("https://www.youtube.com/watch?v=DeumyOzKqgI")
                  }, 10000)

4. Updating
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python
    
        elif(request.method == 'POST' and formname=="like"):
        cur = con.cursor(cursor_factory=extras.DictCursor)
        cur.execute(f"SElECT plike FROM in_theaters where  id ='{id}'")
        people = cur.fetchone()
        
        if(people[0]!=None and username in people[0] ):
            flash("You have already liked it","danger")
        else:
            people=[]
            people.append(username)
            cur.execute(f"SElECT point FROM in_theaters where  id ='{id}'")
            
            point=cur.fetchone()
            point[0]=int(point[0]) +1                    
            cur.execute(f"UPDATE in_theaters set point = '{point[0]}'  WHERE id ='{id}' ")
            cur.execute(f"UPDATE in_theaters SET plike = array_append(plike,'{username}')  WHERE id ='{id}' ")
    
        con.commit()
        cur.close()

If  like form is posted the value of the people who liked will increase and your name will be kept in a array so that you can not like it once more .

5. Delete
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python
        
    if(request.method == 'POST' and formname=="delete"):
        check= request.form.get('check')
        if(check!="ok"):
            flash("You must check the box ","danger")
        else:
            cur = con.cursor(cursor_factory=extras.DictCursor)
            cur.execute(f"DELETE from watchlist  WHERE movie_id ='{id}' ")
            cur.execute(f"DELETE from in_theaters  WHERE id ='{id}' ")
            con.commit()
            cur.close()
            return redirect(url_for('inTheaters'))
          
If the formname is "delete" and the box is checked then the movie will be deleted with this simple query.


