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
