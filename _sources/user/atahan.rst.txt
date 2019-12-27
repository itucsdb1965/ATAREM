Parts Implemented by Atahan ÖZER
================================
This page will be providing information on

* *Watchlist page*
* *Coming soon page*
* *Starlist page*

1. Watchlist 
=====================

While using Atarem, users are going to be able to accomplish add movies to their watchlist from movies,keep notes with movies,find avaible platforms to watch ,keep the track of watch status and give order to movies .

1.1 Adding new movie and leaving a note
~~~~~~~~~~~~~~~~~~~~~~~~
Get to the route *https://itucsdb1965.herokuapp.com/movie/tt0167261/* and select watched or not watched and press to the add to my watchlist button.After the movie is added to watchlist you can leave a note .If you delete the movie it will be automaticly deleted from your watchlist.

.. note:: In order to route the link above you must be logged in.

.. warning:: You can not leave a note without adding it to watchlist.

.. figure:: atahan/add_watchlist.jpg
	:scale: 50 %
	:alt: Movie Page
	:align: center
	
1.2 Watchlist order ,status and notes 
~~~~~~~~~~~~~~~~~~~~~~~~
Get to the route *https://itucsdb1965.herokuapp.com/watchlist*.In this page it is possible to see movies which are added to  watchlist .You can give them a order so that you can see important movies at the top of your watchlist . You can read the notes of movies ,check their watch status and finaly you can reach to the platforms which you can watch the movie.
 
.. figure:: atahan/watchlist.jpg
	:scale: 50 %
	:alt: watchlist
	:align: center
	
1.3 Deleting movie from watchlist 
~~~~~~~~~~~~~~~~~~~~~~~~
If you press the "Delete from my watchlist button" the movie will be deleted from your watchlist .

2. Coming soon page
=====================
Here you can find movies that are coming soon . We do not let our users create (C) movies, but we allow them to do RUD operations on them!

2.1 Adding Movies
~~~~~~~~~~~~~~~~~
We do not support adding a upcoming movie by hand .It is automaticly updated by data from  IMDB.

.. figure:: atahan/coming_soon.jpg
	:scale: 50 %
	:alt: Developer Added  upcoming movies
	:align: center
	
2.2 Viewing & 2.3 Liking & 2.4 Deleting Movies
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
If you click on a movie's poster in route *https://itucsdb1965.herokuapp.com/inTheaters*, you will be redirected to the that movie's own page where you can find more detailed information about that movie. In this page you can also like the movie and delete the movie (we do not recommend).

.. note:: You can not delete the movie without checking the box  and you can only like it for once.
.. figure:: atahan/coming.jpg
	:scale: 50 %
	:alt:  upcoming movies
	:align: center
	
3. Starlist page
=====================
Here you can see a variety of movie stars,give them points and delete them from our website(we do not recommend).

3.1 Adding Stars
~~~~~~~~~~~~~~~~~
We do not support  adding a star by hand .It is automaticly added by data from  IMDB.

3.2 Viewing & 3.3 Giving a starpoint & 3.4 Deleting stars
~~~~~~~~~~~~~~~~~
In the stars page you can give starpoint to a star ,view  popular movies of and their IMDB rating and delete them from our app.

.. note:: The starpoint that you would like to give must be an integer.
.. figure:: atahan/starlist.png
	:scale: 50 %
	:alt:  upcoming movies
	:align: center
