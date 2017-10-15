from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:12345678@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class Posts(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(1000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    def __init__(self,title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25))
    password = db.Column(db.String(20))
    blogs = db.relationship('Posts',backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

def get_posts():
    return Posts.query.all()

@app.route('/blog')
def index():

    return render_template('blog.html', posts=get_posts())

@app.route('/newpost', methods=['POST','GET'])
def newpost():
    if request.method == 'POST':
        title_error=''
        body_error=''

        title=request.form['title']
        body=request.form['body']
    
        
        if len(title) < 1:
            title_error="Enter a title"
            return render_template('newpost.html', title=title, body=body, title_error=title_error)
        if len(body) <1:
            body_error="Enter a body"
            return render_template('newpost.html', title=title, body=body, body_error=body_error)

        post=Posts(title, body)
        db.session.add(post)
        db.session.commit()
        
    

        return redirect('/post?id=' + str(post.id))
    else:
        return render_template('newpost.html')

@app.route('/post')
def individual_post():
    post_id = request.args.get("id")
    post = Posts.query.get(post_id)
    return render_template('post.html', post=post)

if __name__ == '__main__':
    app.run()