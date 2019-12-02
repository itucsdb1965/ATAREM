from flask import Flask, render_template, url_for, redirect, flash, session, logging, request
from wtforms import Form, StringField, BooleanField, TextAreaField, PasswordField, validators, BooleanField, DateField
from psycopg2 import connect, extras
from passlib.hash import pbkdf2_sha256
from functools import wraps
import requests
import re

con = connect(dbname='de9gpi5nc7pnj5', user='fvpxkozyyyirvo', port='5432',
            host='ec2-54-217-234-157.eu-west-1.compute.amazonaws.com', password='2c9deabd2e3ceadf157c8cf47204c3aac97fff8d3179dc58d06814489b24fd5a')
app = Flask(__name__, static_url_path='/static')
app.secret_key = '65vet6'
domain = 'http://itucsdb1965.herokuapp.com:80'

def cleanhtml(raw_html):
  cleanr = re.compile('<.*?>')
  cleantext = re.sub(cleanr, '', raw_html)
  return cleantext # https://stackoverflow.com/questions/9662346/python-code-to-remove-html-tags-from-a-string

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
        response = requests.post(
            f'{domain}/api/user/login?username={username}&password={password}')
        print(response.json())
        if response.json()["content"] == "failure":
            flash('Invalid Credentials', 'danger')
            return redirect(url_for('login'))
        else:
            flash('Logged in successfully!', 'success')
            session['logged_in'] = True
            session['username'] = username
            return redirect(url_for('dashboard'))
    return render_template('login.html')


class RegistrationForm(Form):
    name = StringField('Name', [validators.Length(min=4, max=16)])
    username = StringField('Username', [validators.Length(min=4, max=16)])
    email = StringField('Email Address', [validators.Length(min=6, max=25)])
    birth = DateField('Birth Date', format='%d/%m/%Y')
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo(
            'confirm', message='Confirmation password do not match'),
        validators.Length(min=6, max=16)
    ])
    confirm = PasswordField('Confirm Password')
class UpdateForm(Form):
    name = StringField('Name', [validators.Length(min=4, max=16)])
    username = StringField('Username', [validators.Length(min=4, max=16)])
    email = StringField('Email Address', [validators.Length(min=6, max=25)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.Length(min=6, max=16)
    ])
    newpassword = PasswordField('New Password',[
        validators.DataRequired(),
        validators.Length(min=6, max=16)  ])

class RatingForm(Form):
    point = StringField('')


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
    return render_template('register.html', form=form)

@app.route('/dashboard', methods=['GET', 'POST'])
@is_logged_in
def update_infos():
    cur = con.cursor(cursor_factory=extras.DictCursor)
    username =session['username']
    cur.execute(f"SELECT * FROM users WHERE username='%s'"%username)
    user =cur.fetchone()
    cur.close() 
    
    form = UpdateForm(request.form)
    if request.method == 'POST' and form.validate():
        
        name = form.name.data
        username = form.username.data
        email = form.email.data
        password = form.password.data
        newpassword=form.newpassword.data
        cur = con.cursor(cursor_factory=extras.DictCursor)
        oldusername =session['username']
        cur.execute(f"SELECT * FROM users WHERE username='%s'"%username)
        user =cur.fetchone()
        cur.close() 
        hash = user['password']
        if pbkdf2_sha256.verify(password, hash):
            flash("Your password is wrong","danger")
            return render_template('dashboard.html', form=form,user=user)
       
        response = requests.post( f'http://localhost:5000/api/user/dashboard?name={name}&username={username}&email={email}&newpassword={newpassword}&oldusername={oldusername}')
        
        if response.json()["content"] == "success":          
            flash("Your informations has been updated","success")  
      
    return render_template('dashboard.html', form=form,user=user)


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
    return render_template('movies.html')


@app.route('/movie/<string:id>/',methods=['GET','POST'])
def movie(id):
    username = session['username']
    if(request.method == 'POST'):
        cur = con.cursor(cursor_factory=extras.DictCursor) 
        cur.execute(f"SELECT EXISTS(SELECT *FROM watchlist WHERE username='{username}' and movie_id = '{id}') ")
        exist=cur.fetchone()
        
        if(exist[0]==True): 
            flash('It is already in your watchlist', 'danger')
        else:
            cur.execute(f"INSERT INTO watchlist(username,movie_id) VALUES ('{username}','{id}')")
            con.commit()
            cur.close()
            flash('Added to your watchlist', 'success')
    movie = requests.get(f'{domain}/api/movie/'+id)
    return render_template('movie.html', movie=movie.json()["content"])

@app.route('/stars',methods=['GET','POST'])
def stars():
    form=RatingForm(request.form)
    id = request.form.get('user_id')
    cur = con.cursor(cursor_factory=extras.DictCursor)
    cur.execute(f"SELECT * FROM stars ORDER BY id ASC ")
    stars = cur.fetchall()
    cur.close()
    if(request.method == 'POST'):
        
        cur = con.cursor(cursor_factory=extras.DictCursor)
        cur.execute(f"SELECT user_rating FROM stars WHERE id={id} ")
        star_rate=cur.fetchone()
        try:
            user_rating = int(form.point.data) + int(star_rate['user_rating'])
        except:
            flash("Must be a integer value","danger")
            return redirect(url_for('stars'))

        cur.execute(
        f"UPDATE stars SET user_rating={user_rating}  WHERE id={id}")
        con.commit()
        cur.close
        return redirect(url_for('stars'))
       
    return render_template('stars.html', stars=stars , form=form)


@app.route('/dashboard')
@is_logged_in
def dashboard():
    return render_template('dashboard.html')

@app.route('/watchlist')
@is_logged_in
def watchlist():
    username=session['username']
    cur = con.cursor(cursor_factory=extras.DictCursor)
    cur.execute(f"SELECT movie_id FROM watchlist WHERE username='{username}'and type =0") 
    movie_id =cur.fetchall()
    title=[]
    for i in movie_id:
        cur.execute(f"SELECT title FROM movies WHERE idimdb='{i[0]}'" )
        temp=cur.fetchone()
        title.append(temp)
    cur.execute(f"SELECT movie_id FROM watchlist WHERE username='{username}'and type =1") 
    id =cur.fetchall()
    for i in id:
        cur.execute(f"SELECT title FROM in_theaters WHERE id='{i[0]}'" )
        temp=cur.fetchone()
        title.append(temp)
    cur.close()

   
    if(title==[]):
        return render_template('watchlist.html',username=username,title=[["No movie has been added"]])

    return render_template('watchlist.html',username=username,title=title)

@app.route('/inTheaters')
@is_logged_in
def inTheaters(): 
        
    return render_template('inTheaters.html')

@app.route('/inTheaters/<string:id>/',methods=['GET','POST'])
def theater(id):
    username = session['username']
    if(request.method == 'POST'):
        cur = con.cursor(cursor_factory=extras.DictCursor) 
        cur.execute(f"SELECT EXISTS(SELECT *FROM watchlist WHERE username='{username}' and movie_id = '{id}') ")
        exist=cur.fetchone()
        
        if(exist[0]==True): 
            flash('It is already in your watchlist', 'danger')
        else:
            cur.execute(f"INSERT INTO watchlist(username,movie_id,type) VALUES ('{username}','{id}','{1}')")
            con.commit()
            cur.close()
            flash('Added to your watchlist', 'success')
    movie = requests.get(f'{domain}/api/inTheater/'+id)
    return render_template('theater.html', movie=movie.json()["content"])


@app.route('/forum')
@is_logged_in
def forum():
    response = requests.get(f'{domain}/api/forum/thread?count=5')
    response2 = requests.get(f'{domain}/api/forum/comment?count=5')
    comments = []
    threads = []
    for comment in response2.json()["content"]:
        co = comment
        co["body"] = cleanhtml(comment["body"])
        comments.append(co)
    return render_template('forum.html', threads=response.json()["content"], comments=comments)

class ThreadForm(Form):
    title = StringField('Title', [validators.Length(min=6, max=200)])
    body = TextAreaField('Body', [validators.Length(min=30)])

@app.route('/forum/thread/create', methods=['POST', 'GET'])
@is_logged_in
def createThreadRoute():
    form = ThreadForm(request.form)
    if(request.method == 'POST'):
        title = form.title.data
        body = form.body.data
        username = session['username']
        response = requests.post(f"{domain}/api/forum/thread?title={title}&body={body}&username={username}")
        response = response.json()
        if(response['content'] == "success"):
            flash('Thanks for your contribution', 'success')
            return redirect(url_for('forum'))
        else:
            flash('Something went wrong, please try again later', 'warning')        
    return render_template('createthread.html', form=form)

class CommentForm(Form):
    body = TextAreaField('Body', [validators.Length(min=10)])

@app.route('/forum/thread/<id>', methods=['POST', 'GET'])
@is_logged_in
def singleThread(id):
    form = CommentForm(request.form)
    if request.method == 'POST':
        body = form.body.data
        username = session['username']
        requests.post(f"{domain}/api/forum/comment?username={username}&body={body}&thread={id}")
        return redirect(f"{domain}/forum/thread/{id}")
    return render_template('singlethread.html', id=id, form=form, user=session["username"])

class EditThreadForm(Form):
    title = StringField('Title', [validators.Length(min=6, max=200)])
    body = TextAreaField('Body', [validators.Length(min=30)])

@app.route('/forum/thread/edit/<id>', methods=['POST', 'GET'])
@is_logged_in
def editThreadRoute(id):
    form = EditThreadForm(request.form)
    thread = requests.get(f"{domain}/api/forum/thread?id={id}")
    if(request.method == 'POST'):
        title = form.title.data
        body = form.body.data
        response = requests.post(f"{domain}/api/forum/thread/edit?title={title}&body={body}&id={id}")
        response = response.json()
        if(response['content'] == "success"):
            flash('It is now correct', 'success')
            return redirect(url_for('forum'))
        else:
            flash('Something went wrong, please try again later', 'warning')        
    return render_template('editThread.html', form=form, thread=thread.json()["content"])


































# ATAREM API

# @Route /api/user/login
# @Methods GET and POST
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

# @Route /api/movie/id
# @Methods GET
# @Desc Get movie data with parameter id
@app.route('/api/movie/<id>', methods=['GET'])
def getMovie(id):
    cur = con.cursor(cursor_factory=extras.DictCursor)
    cur.execute(f"SELECT * FROM movies WHERE idimdb='{id}'")
    movie = cur.fetchone()
    cur.close()
    return {"content": dict(movie)}

# @Route /api/movie
# @Methods GET
# @Desc Get data of movies with counter
@app.route('/api/movie', methods=['GET'])
def getMovies():
    count = request.args.get("count")
    if int(count) >= 250:
        return {"content": {}}
    cur = con.cursor(cursor_factory=extras.DictCursor)
    cur.execute(f"SELECT * FROM movies WHERE id>{int(count)} AND id<={int(count)+9}")
    movies = cur.fetchall()
    for i in range(0, len(movies)):
        movies[i] = dict(movies[i])
    cur.close()
    return {"content": movies}

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

# @Route /api/user/dashboard
# @Methods POST
# @Desc Update a user with parameters
@app.route('/api/user/dashboard', methods=['POST'])#NOT WORKING
def updateUser():
   
    name = request.args.get("name")
    print(name)
    username = request.args.get("username")
    email = request.args.get("email")
    newpassword = pbkdf2_sha256.hash(request.args.get("newpassword"))
    oldusername =request.args.get('oldusername')
    cur = con.cursor()
    cur.execute(
        f"UPDATE users SET username='{username}',name='{name}',email='{email}',password='{newpassword}'  WHERE username='{oldusername}'")
        
    con.commit()
    cur.close()
    return {"content": "success"}



# @Route /api/forum/thread
# @Methods POST
# @Desc create a thread with parameters username, title and body
@app.route('/api/forum/thread', methods=['POST'])
def createThreadApi():
    username = request.args.get('username')
    title = request.args.get('title')
    body = request.args.get('body')
    print(body)
    cur = con.cursor()
    cur.execute("INSERT INTO forumposts (username, title, body) VALUES (%s, %s, %s)",
                (username, title, body))
    con.commit()
    cur.close()
    return {"content": "success"}

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

# @Route /api/forum/thread/single
# @Methods GET
# @Desc get thread with parameter id, get comments that belong to that id
@app.route('/api/forum/thread/single')
def getSingleThread():
    cur = con.cursor(cursor_factory=extras.DictCursor)
    id = request.args.get('id')
    cur.execute(f"SELECT * FROM forumposts WHERE id={id}")
    thread = cur.fetchone()
    cur.execute(f"SELECT * FROM comments WHERE thread={id}")
    comments = cur.fetchall()
    for i in range(0, len(comments)):
        comments[i] = dict(comments[i])
    return {"content": {"thread": dict(thread), "comments": comments}}

# @Route /api/forum/comment
# @Methods POST
# @Desc send comment via parameters thread id, body, username
@app.route('/api/forum/comment', methods=['POST'])
def sendComment():
    cur = con.cursor(cursor_factory=extras.DictCursor)
    thread = request.args.get('thread')
    body = request.args.get('body')
    username = request.args.get('username')
    cur.execute(f"INSERT INTO COMMENTS (username, body, thread) VALUES ('{username}', '{body}', '{thread}')")
    con.commit()
    cur.close()
    return {"content": "success"}

# @Route /api/forum/comment
# @Methods GET
# @Desc Get comment info with either username or thread or count and offset as paramters,
#   if both parameters provided comment with first username, then given thread will be returned
#   count will return latest submitted n comments disregarding first offset rows
@app.route('/api/forum/comment')
def getComment():
    cur = con.cursor(cursor_factory=extras.DictCursor)
    username = request.args.get('username')
    thread = request.args.get('thread')
    count = request.args.get('count')
    offset = request.args.get('offset')
    if username:
        cur.execute(f"SELECT * FROM comments WHERE username='{username}'")
        comments = cur.fetchall()
        for i in range(0, len(comments)):
            comments[i] = dict(comments[i])
        cur.close()
        return {"content": comments}
    elif thread:
        cur.execute(f'SELECT * FROM comments WHERE thread={thread}')
        comments = cur.fetchall()
        for i in range(0, len(comments)):
            comments[i] = dict(comments[i])
        cur.close()
        return {"content": comments}
    elif count:
        if not offset:
            offset = 0
        cur.execute(f'SELECT * FROM comments ORDER BY id DESC LIMIT {count} OFFSET {offset}')
        comments = cur.fetchall()
        for i in range(0, len(comments)):
            comments[i] = dict(comments[i])
        cur.close()
        return {"content": comments}
    else:
        return {"content": "failure"}

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

# @Route /api/inTheaters
# @Methods get
# @Desc getting the intheater movies from database
@app.route('/api/inTheaters', methods=['GET'])
def getTheaters():
    count = request.args.get("count")
    if int(count) >= 10:
        return {"content": {}}
    cur = con.cursor(cursor_factory=extras.DictCursor)
    cur.execute(f"SELECT * FROM in_theaters WHERE id>{int(count)} AND id<={int(count)+9}")
    movies = cur.fetchall()
    for i in range(0, len(movies)):
        movies[i] = dict(movies[i])
    cur.close()
    return {"content": movies}

@app.route('/api/inTheater/<id>', methods=['GET'])
def getTheater(id):
    cur = con.cursor(cursor_factory=extras.DictCursor)
    cur.execute(f"SELECT * FROM in_theaters WHERE id='{id}'")
    movie = cur.fetchone()
    cur.close()
    return {"content": dict(movie)}

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

# @Route /api/forum/thread/rep
# @Methods POST
# @Desc Update rep point with parameter id
@app.route('/api/forum/thread/rep', methods=['POST'])
def repThread():
    id = request.args.get('id')
    cur = con.cursor(cursor_factory=extras.DictCursor)
    cur.execute(f"UPDATE forumposts SET rep=rep+1 WHERE id={id}")
    con.commit()
    cur.close()
    return {"content": "success"}

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

if __name__ == '__main__':
    app.run(debug=True)
