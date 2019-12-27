Parts Implemented by Ekrem UĞUR
================================

This page will be providing information on

* *User Functionality*
* *Movie Pages*
* *Atarem Forum*

1. User Functionality
=====================

While using Atarem, users are going to be able to accomplish *register* and *login* operations. Users can also *change their avatar image* and *delete their account* from the dashboard.

1.1 Registering New User
~~~~~~~~~~~~~~~~~~~~~~~~

Get to the route *http://itucsdb1965.herokuapp.com/register* and fill the form in order to create a new user.

.. note:: You need to provide correct/valid information in order to continue registration.

.. warning:: There can not be two accounts which share either same email or username.

.. figure:: ekrem/register.png
	:scale: 50 %
	:alt: Registeration Page
	:align: center

1.2 Logging in to an Account
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Get to the route *http://itucsdb1965.herokuapp.com/login* and provide your credentials.

.. figure:: ekrem/login.png
	:scale: 50 %
	:alt: Login Page
	:align: center

1.3 Change User Avatar & 1.4 Delete Account
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In the route *http://itucsdb1965.herokuapp.com/dashboard* you can delete your account, and upload the image you selected by pressing corresponding button.

.. note:: You must be logged in to see this page.

.. figure:: ekrem/dash.png
	:scale: 50 %
	:alt: User Dashboard
	:align: center

2. Movie Pages
==============

Movies are the foundation of what we do here. So it is not surprising we have some pages that belong to the movies themselves. We do not let our users create (C) movies, but we allow them to do RUD operations on them!

2.1 Adding Movies
~~~~~~~~~~~~~~~~~

Right now Atarem does not support movie creation by users.

.. note:: Altough we do not support this feature for users, our developers handled this process behind closed doors. They can be found in *http://itucsdb1965.herokuapp.com/movies*.

.. figure:: ekrem/movies.png
	:scale: 50 %
	:alt: Developer Added Movies
	:align: center

2.2 Viewing & 2.3 Rating & 2.4 Deleting Movies
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. note:: You must be logged in to see individual movie pages.

If you click on a movie's poster in route *http://itucsdb1965.herokuapp.com/movies*, you will be redirected to the that movie's own page where you can find more detailed information about that movie. In this page you can also delete the movie (we do not reccommend) and contribute to our work by rating the movie.

.. note:: While we encourage our users to vote to their likings, one user can use multiple votes for each movie, please do not abuse this to get your favourite movie to the top!

.. tip:: Each time you scroll down, you will find more movies. Up until you don't.

.. figure:: ekrem/movie.png
	:scale: 50 %
	:alt: Individual Movie Page
	:align: center

3. Atarem Forum
===============

Forum is a place where you are free to share your opinion on anything. If you can not find what you are looking for, there is nothing stopping you from starting the topic about it.

3.1 Creating Threads
~~~~~~~~~~~~~~~~~~~~

Using the button in route *http://itucsdb1965.herokuapp.com/forum*,
you can create a new thread about anything you want.

.. figure:: ekrem/forum.png
	:scale: 50 %
	:alt: Forum View
	:align: center


3.2 Viewing Threads and Comments
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you click on a thread or comment in the feed, you will be redirected to the associated thread page.

.. tip:: If you do not seem to find what you are looking for, you might want to *Load more*.

3.3 Updating Threads
~~~~~~~~~~~~~~~~~~~~

Using *+Rep* button, you can encourage the work you like!

.. figure:: ekrem/threadother.png
	:scale: 50 %
	:alt: Forum View
	:align: center

3.4 Deleting Threads
~~~~~~~~~~~~~~~~~~~~

If the thread belongs to you, you are free to remove it from our platform. But all kinds of contribution is welcomed, so we don't really want you to use this feature.

.. note:: We don't let you rep your own thread, instead you are able to edit your thread whenever you want.

.. figure:: ekrem/threadown.png
	:scale: 50 %
	:alt: Forum View
	:align: center