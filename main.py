from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:wamp1234@localhost:3306/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'wamp1234'

class Blog(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    entry = db.Column(db.String(500))

    def __init__(self, title, entry):
        self.title = title
        self.entry = entry

@app.route('/')
def index():
    blog_posts = Blog.query.all()
    return render_template('mainpage.html',blog_posts=blog_posts)

# @app.route('/home', methods=['POST', 'GET'])
# def home():
#     blog_posts = Blog.query.all()
#     return render_template('mainpage.html',blog_posts=blog_posts)


@app.route('/newpost', methods=['POST', 'GET'])
def newpost():

    if request.method == 'POST':
        blog_title = request.form['title']
        blog_entry = request.form['entry']

        new_blog = Blog(blog_title, blog_entry)
        db.session.add(new_blog)
        db.session.commit()
        
    blog_posts = Blog.query.all()
    return render_template('newpost.html',title="Add a Blog Entry",blog_posts=blog_posts)


    
@app.route('/blog', methods=['POST', 'GET'])
def main():

    blog_posts = Blog.query.all()
    return render_template('blog.html', blog_posts=blog_posts)



if __name__ == '__main__':
    app.run()
