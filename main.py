from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogzit@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

app.secret_key = 'FD5R6X'

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), unique=True)
    body = db.Column(db.String(1500))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner


class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['log_in', 'signup', 'blog_page', 'index']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/blog', methods=['POST', 'GET'])
def blog_page():

    if request.args.get('id'):
        
        post_id = request.args.get('id')
        blog_entry = Blog.query.filter_by(id=post_id).first()
        user = User.query.filter_by(username=blog_entry.owner.username).first()
        return render_template('blogentry.html', blog=blog_entry, user=user)
    
    if request.args.get('user'):

        username = request.args.get('user')
        user = User.query.filter_by(username=username).first()
        blog_post = Blog.query.filter_by(owner_id=user.id).all()
        return render_template('singleuser.html',user=user, blogs=blog_post)

    if request.method == 'POST':
        blog_title = request.form['title']
        blog_body = request.form['body']
        owner = User.query.filter_by(username=session['username']).first()
        new_blog_post = Blog(blog_title, blog_body, owner)
        db.session.add(new_blog_post)
        db.session.commit()

        blogs = Blog.query.all()


        return render_template('blog.html', blogs=blogs, owner=owner)

    else:
        blogs = Blog.query.all()
        return render_template('blog.html', blogs=blogs)

@app.route('/login', methods=['POST', 'GET'])
def log_in():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            flash("Logged in")
            return redirect('/newpost')
        elif  user and user.password != password:
            flash('User password incorrect.', 'error')
            return redirect('/login')
        else:
            flash('That Username does not exist.', 'error')
            return redirect('/login')
    return render_template('login.html')


def proper_length(entry):
    
    if len(entry) > 2 and len(entry) < 21:
        return True



@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        if not proper_length(username):
            flash('Your username must be between 3-20 characters.', 'error')
            return redirect('/signup')

        if not proper_length(password):
            flash('Your password must be between 3-20 characters.', 'error')
            return redirect('/signup')

        if username == '' or password == '' or verify == '':
            flash('One of your fields is invalid.', 'error')
            return redirect('/signup')

        if password != verify:
            flash('Your passwords do not match.', 'error')
            return redirect('/signup')

        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')
        else:
            flash('This username already exists.', 'error')
            return redirect('/signup')

    return render_template('signup.html')



@app.route('/newpost', methods=['POST', 'GET'])
def new_entry():
    

    if request.method == 'GET':
        return render_template('newpost.html')

    else:

        if request.form['title'] == '' and request.form['body'] == '':
            flash("Please enter something.", 'error')
            return redirect('/newpost')

        elif request.form['title'] == '':
            flash("Please enter a title.", 'error')
            body = request.form['body']
            return render_template('/newpost.html', body=body)
            

        elif request.form['body'] == '':
            flash("Please enter a body.", 'error')
            title = request.form['title']
            return render_template('/newpost.html', title=title)
            
        else:
            
            owner = User.query.filter_by(username=session['username']).first()
            blog_title = request.form['title']
            blog_body = request.form['body']
            new_blog_post = Blog(blog_title, blog_body, owner)
            db.session.add(new_blog_post)
            db.session.commit()

            new_post_id = Blog.query.filter_by(title=blog_title).first().id
            
            return redirect("/blog?id={0}".format(new_post_id))
        

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')


@app.route('/', methods=['POST', 'GET'])
def index():
    users = User.query.all()
    return render_template('index.html', users=users)



        












if __name__ == '__main__':
    app.run()