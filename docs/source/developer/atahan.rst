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
