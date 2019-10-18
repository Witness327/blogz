from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
from hashutils import make_pw_hash, check_pw_hash

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:wamp1234@localhost:3306/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'wamp1234'

class Blog(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    entry = db.Column(db.String(500))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, entry, owner):
        self.title = title
        self.entry = entry
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    pw_hash = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    

    def __init__(self, email, password):
        self.email = email
        self.pw_hash = make_pw_hash(password)

@app.before_request
def require_login():
    allowed_routes = ['login', 'register']
    if request.endpoint not in allowed_routes and 'email' not in session:
        return redirect('/login')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and  check_pw_hash(password, user.pw_hash):
            session['email'] = email
            flash('Welcome Back!', 'logged-in')
            return redirect('/newpost')
        else:
            flash('User password incorrect, or user does not exist', 'error')

    return render_template('login.html')

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        verify = request.form['verify']


        existing_user = User.query.filter_by(email=email).first()
        if not existing_user:
            new_user = User(email, password)
            db.session.add(new_user)
            db.session.commit()
            session['email'] = email
            return redirect('/')
        else:
            flash('You already have an account with us! Just try logging in =)', 'dupicate')

    return render_template('signup.html')

@app.route('/logout')
def logout():
    del session['email']
    return redirect('/')



@app.route('/')
def index():
    owner = User.query.filter_by(email=session['email']).first()
    blog_posts = Blog.query.filter_by(owner=owner).all() 
    return render_template('mainpage.html',owner=owner,blog_posts=blog_posts)


@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    owner = User.query.filter_by(email=session['email']).first()
    if request.method == 'POST':
        blog_title = request.form['title']
        blog_entry = request.form['entry']

        new_blog = Blog(blog_title, blog_entry, owner)
        db.session.add(new_blog)
        db.session.commit()
        return redirect('/')
    

    blogs = Blog.query.filter_by(owner=owner).all() 
    blog_posts = Blog.query.all()     
    return render_template('newpost.html',title="Add a Blog Entry",blogs=blogs, blog_posts=blog_posts)

    # if request.method == 'GET':
    # return redirect('/')

@app.route('/home', methods=['POST', 'GET'])
def home():
    blog_posts = Blog.query.all()
    return render_template('index.html', blog_posts=blog_posts)

@app.route('/users', methods=['POST', 'GET'])
def users():
    owner = User.query.filter_by(email=session['email']).first()
    blog_posts = User.query.all()
    return render_template('singleusers.html',owner=owner, blog_posts=blog_posts)

@app.route('/userblog', methods=['POST', 'GET'])
def userblog():
    owner = User.query.filter_by(email=session['email']).first()
    if request.method == 'GET':
        postid = request.args.get('id')
        blog_posts = User.query.get(postid)
        blog_post = User.query.filter_by(owner=owner).all()
        return render_template('userblog.html', owner=owner, postid=postid, blog_posts=blog_posts, users=blog_post)

@app.route('/usersblogs', methods=['POST', 'GET'])
def usersblogs():
    owner = User.query.filter_by(email=session['email']).first()
    if request.method == 'GET':
        postid = request.args.get('id')
        blog_posts = Blog.query.get(postid)
        blog_post = Blog.query.filter_by(owner=owner).all()
        return render_template('mainpage.html', owner=owner, postid=postid, usersblogs=blog_posts, blog_post=blog_post)    
    
# @app.route('/home', methods=['POST', 'GET'])
# def home():
#     owner = User.query.filter_by(email=session['email']).first()
#     blog_posts = Blog.query.filter_by(owner=owner).all()
#     return render_template('blog.html', owner=owner,blog=blog_posts, blog_posts=blog_posts)

@app.route('/blog', methods=['POST', 'GET'])
def blog():
    owner = User.query.filter_by(email=session['email']).first()
    if request.method == 'GET':
        postid = request.args.get('id')
        blog_posts = Blog.query.get(postid)
        # owner_id = User.query.filter_by(blog_posts.owner_id)
        # email = User.query.get(owner_id)
        blog_post = Blog.query.filter_by(owner=owner).all()
        return render_template('blog.html', owner=owner, postid=postid, blog=blog_posts, blog_post=blog_post)

# @app.route('/blog?id=id', methods=['POST', 'GET'])
# def blog():

#     id = request.args.get('id')
#     blog_posts = Blog.query.get(id)
#     return render_template('blog.html', blog_posts=blog_posts,id=id)



if __name__ == '__main__':
    app.run()
