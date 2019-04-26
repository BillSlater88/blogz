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



@app.route('/blog', methods=['POST', 'GET'])
def blog_page():

    if request.args.get('id'):
         
        post_id = request.args.get('id')
        blog_entry = Blog.query.filter_by(id=post_id).first()

        return render_template('blogentry.html', blog=blog_entry)
    
    if request.method == 'POST':
        blog_title = request.form['title']
        blog_body = request.form['body']
        new_blog_post = Blog(blog_title, blog_body)
        db.session.add(new_blog_post)
        db.session.commit()

        blogs = Blog.query.all()


        return render_template('blog.html', blogs=blogs)

    else:
        blogs = Blog.query.all()
        return render_template('blog.html', blogs=blogs)



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

            blog_title = request.form['title']
            blog_body = request.form['body']
            new_blog_post = Blog(blog_title, blog_body, owner)
            db.session.add(new_blog_post)
            db.session.commit()

            new_post_id = Blog.query.filter_by(title=blog_title).first().id
            
            return redirect("/blog?id={0}".format(new_post_id))
        



        












if __name__ == '__main__':
    app.run()