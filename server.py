from flask import Flask, render_template, url_for, redirect, flash, session, logging, request
from wtforms import Form, StringField, BooleanField, TextAreaField, PasswordField, validators, BooleanField
from psycopg2 import connect, extras
from passlib.hash import pbkdf2_sha256
from functools import wraps
import requests
from flask_socketio import SocketIO, send
from furl import furl

con = connect(dbname='de9gpi5nc7pnj5', user='fvpxkozyyyirvo', port='5432',
            host='ec2-54-217-234-157.eu-west-1.compute.amazonaws.com', password='2c9deabd2e3ceadf157c8cf47204c3aac97fff8d3179dc58d06814489b24fd5a')
app = Flask(__name__, static_url_path='/static')
socketio = SocketIO(app, cors_allowed_origins="*")
app.secret_key = '65vet6'


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
        password = form.password.data
        response = requests.post(f'http://localhost:5000/api/user/register?name={name}&username={username}&email={email}&password={password}')
        if response.json()["content"] == "success":
            flash('Registration successful!', 'success')
            return redirect(url_for('login'))
        else:
            flash('Registration failed', 'danger')
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
    morollo = requests.get('http://localhost:5000/api/movie')
    return render_template('movies.html', movies=morollo.json()["content"])


@app.route('/movie/<string:id>/')
def movie(id):
    movie = requests.get('http://localhost:5000/api/movie/'+id)
    return render_template('movie.html', movie=movie.json()["content"])


@app.route('/dashboard')
@is_logged_in
def dashboard():
    return render_template('dashboard.html')

@app.route('/watchlist/<string:username>/')
@is_logged_in
def watchlist(username):
    username=session['username']
    title = requests.get(
            f'http://localhost:5000/api/user/watchlist/'+username)
    if(title.json()["content"]=='empty_list'):
        return render_template('watchlist.html',username=username,title=["No movie has been added"])

    return render_template('watchlist.html',username=username,title=title.json()["content"])



# ATAREM API

# @Route /api/movie/id
# @Methods GET ONLY
# @Desc Get movie data with parameter id
@app.route('/api/movie/<id>', methods=['GET'])
def getMovie(id):
    cur = con.cursor(cursor_factory=extras.DictCursor)
    cur.execute(f"SELECT * FROM movies WHERE idimdb='{id}'")
    movie = cur.fetchone()
    cur.close()
    return {"content": dict(movie)}

# @Route /api/movie
# @Methods GET ONLY
# @Desc Get data of all movies
@app.route('/api/movie', methods=['GET'])
def getMovies():
    cur = con.cursor(cursor_factory=extras.DictCursor)
    cur.execute("SELECT * FROM movies")
    movies = cur.fetchall()
    for i in range(0, len(movies)):
        movies[i] = dict(movies[i])
    cur.close()
    return {"content": movies}

# @Route /api/user/register
# @Methods POST ONLY
# @Desc Register a user with parameters
@app.route('/api/user/register', methods=['POST'])
def registerUser():
    f = furl(request.url)
    params = dict(f.args)
    name = params["name"]
    username = params["username"]
    email = params["email"]
    password = params["password"]
    cur = con.cursor()
    cur.execute(f"SELECT COUNT(*) FROM USERS WHERE username='{username}' OR email='{email}'")
    count = cur.fetchone()
    if count[0] > 0:
        return {"content": "failure"}
    cur.execute("INSERT INTO users (name, username, email, password) VALUES (%s, %s, %s, %s)",
                (name, username, email, pbkdf2_sha256.hash(password)))
    con.commit()
    cur.close()
    return {"content": "success"}

# @Route /api/user/watchlist
# @Methods GET ONLY
# @Desc get the parameters from db
@app.route('/api/user/watchlist/<username>',methods=['GET'])
def watchlist_user(username):
       
    cur = con.cursor(cursor_factory=extras.DictCursor)
    cur.execute(f"SELECT movie_id FROM watchlist WHERE username='{username}'") 
    movie_id =cur.fetchall()
    title=[]
    for i in movie_id:
        cur.execute(f"SELECT title FROM movies WHERE id='%s'" % (i[0]))
        temp=cur.fetchone()
        title.append(temp)
    cur.close()
    if(title==[]):
        return{"content": "empty_list"}
    return{"content": list(title)}
if __name__ == '__main__':
    socketio.run(app, debug=True)
