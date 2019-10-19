from flask import Flask, render_template, url_for, redirect, flash, session, logging, request
from wtforms import Form, StringField, BooleanField, TextAreaField, PasswordField, validators, BooleanField
from psycopg2 import connect, extras
from passlib.hash import pbkdf2_sha256
from functools import wraps
from flask_socketio import SocketIO, send

con = connect(dbname='atarem', user='postgres',
              host='localhost', password='sudouser')
app = Flask(__name__, static_url_path='/static')
socketio = SocketIO(app)


def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash(
                'You must login to your account in order to continue browsing', 'warning')
            return redirect(url_for('login'))
    return wrap


def is_logged_out(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' not in session:
            return f(*args, **kwargs)
        else:
            return redirect(url_for('dashboard'))
    return wrap


@socketio.on('message')
def handleMessage(msg):
    send(msg, broadcast=True)


@app.route('/')
@is_logged_out
def index():
    return render_template('landing.html')


@app.route('/login', methods=['GET', 'POST'])
@is_logged_out
def login():
    if(request.method == 'POST'):
        username = request.form['username']
        password = request.form['password']
        cur = con.cursor(cursor_factory=extras.DictCursor)
        cur.execute(
            "SELECT * FROM users WHERE username='%s'" % (username))
        data = cur.fetchone()
        if(data):
            hash = data['password']
            if pbkdf2_sha256.verify(password, hash):
                session['logged_in'] = True
                session['username'] = username
                flash('Logged in successfully!', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid Credentials', 'danger')
        else:
            flash('Invalid Credentials', 'danger')
    return render_template('login.html')


class RegistrationForm(Form):
    name = StringField('Name', [validators.Length(min=4, max=16)])
    username = StringField('Username', [validators.Length(min=4, max=16)])
    email = StringField('Email Address', [validators.Length(min=6, max=25)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo(
            'confirm', message='Confirmation password do not match'),
        validators.Length(min=6, max=16)
    ])
    confirm = PasswordField('Confirm Password')


@app.route('/register', methods=['GET', 'POST'])
@is_logged_out
def register():
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        username = form.username.data
        email = form.email.data
        password = pbkdf2_sha256.hash(form.password.data)
        cur = con.cursor()
        cur.execute("INSERT INTO users (name, username, email, password) VALUES (%s, %s, %s, %s)",
                    (name, username, email, password))
        con.commit()
        cur.close()
        flash('Registration successful!', 'success')
        return redirect(url_for('register'))
    return render_template('register.html', form=form)


@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('Logged out successfully', 'success')
    return redirect(url_for('login'))


@app.route('/discussion')
@is_logged_in
def discussion():
    return render_template('discussion.html')


@app.route('/movies')
def movies():
    cur = con.cursor(cursor_factory=extras.DictCursor)
    cur.execute("SELECT * FROM movies")
    movies = cur.fetchall()
    cur.close()
    return render_template('movies.html', movies=movies)


@app.route('/movie/<string:id>/')
def movie(id):
    cur = con.cursor(cursor_factory=extras.DictCursor)
    cur.execute(f"SELECT * FROM movies WHERE idimdb='{id}'")
    movie = cur.fetchone()
    cur.close()
    return render_template('movie.html', movie=movie)


@app.route('/dashboard')
@is_logged_in
def dashboard():
    return render_template('dashboard.html')


if __name__ == '__main__':
    app.secret_key = '65vet6'
    socketio.run(app, debug=True)
