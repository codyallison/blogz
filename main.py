from flask import Flask, request, redirect, render_template, session
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

def get_user_posts(username):
    owner = User.query.filter_by(username=username).first()
    return Posts.query.filter_by(owner=owner).all()
def get_post_by_id(id):
    return Posts.query.filter_by(id=id)

@app.route('/')
def index():

    #lists all authors
    users = User.query.all()
    return render_template('index.html',users=users)

@app.route('/blog')
def blog():
    user = request.args.get('user')
    id = request.args.get('id')

    #dynamic content based on route (all, by author, by post id)
    if user:
        return render_template('blog.html', posts=get_user_posts(user))
    elif id:
        return render_template('blog.html', posts = get_post_by_id(id))
    else:
        return render_template('blog.html', posts=get_posts())

@app.route('/newpost', methods=['POST','GET'])
def newpost():
    if request.method == 'POST':
        title_error=''
        body_error=''
        
        owner = User.query.filter_by(username=session['user']).first()
        title=request.form['title']
        body=request.form['body']
    
        # validate title/body
        if len(title) < 1:
            title_error="Enter a title"
            return render_template('newpost.html', title=title, body=body, title_error=title_error)
        if len(body) <1:
            body_error="Enter a body"
            return render_template('newpost.html', title=title, body=body, body_error=body_error)

        #write newpost to database
        post=Posts(title, body, owner)
        db.session.add(post)
        db.session.commit()
        

        return redirect('/blog?id=' + str(post.id))
    else:
        return render_template('newpost.html')


@app.route('/signup', methods=['GET','POST'])
def signup():
    if request.method =="POST":
        
        password=request.form['password']
        verify=request.form['verify']
        username=request.form['username']
        
        user_error =''
        password_error =''
        verify_error = ''
        
        #validation - username    
        if len(username) < 1:
            user_error = "Please enter a user name"
            return render_template("signup.html", username=username, username_error=user_error, password_error=password_error, verify_error=verify_error)            
        elif len (username) <3:
            user_error = "Please enter a username longer than 3 characters"
            return render_template("signup.html", username=username, username_error=user_error, password_error=password_error, verify_error=verify_error)

        #validation - password
        if len(password) <1:
            password_error = "Please enter a password"
            return render_template("signup.html", username=username, username_error=user_error, password_error=password_error, verify_error=verify_error)
            
        elif password != verify:
            verify_error = "Passwords do not match"
            return render_template("signup.html", username=username, username_error=user_error, password_error=password_error, verify_error=verify_error)
            
        elif len(password) <3:
            password_error = "Password must be longer than 3 characters"
            return render_template("signup.html", username=username, username_error=user_error, password_error=password_error, verify_error=verify_error)
        
        if len(verify)<1:
            verify_error = "Please verify the password"
            return render_template("signup.html", username=username, username_error=user_error, password_error=password_error, verify_error=verify_error)
        
        #validate user doesn't exist already
        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
            user = User(username=username, password=password)
            db.session.add(user)
            db.session.commit()
            session['user'] = user.username
            return redirect("/newpost")
        else:
            user_error = "User already exists"
            return render_template("signup.html", username=username, username_error=user_error, password_error=password_error, verify_error=verify_error)
        
    else:
        return render_template("signup.html")
      

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        
        user_not_exist = ''
        login_error = ''

        username = request.form['username']
        password = request.form['password']

        #login validation username
        users = User.query.filter_by(username=username)
        if users.count() == 1:
            user = users.first()
            if password == user.password:
                session['user'] = user.username
                
                return redirect("/newpost")
            else:
                if password != user.password:
                    login_error = "Incorrect password, please try again."
                    return render_template('login.html', username=username, login_error=login_error)
        else:
            user_not_exist = "We don't find an account for you"
            return render_template("login.html", user_not_exist=user_not_exist)


#require login to make new post
endpoints_without_login = ['login', 'signup', 'blog', 'index']

@app.route("/logout", methods=['POST'])
def logout():
    del session['user']
    return redirect("/login")  

@app.before_request
def require_login():
    if not ('user' in session or request.endpoint in endpoints_without_login):
        return redirect("/login")    

app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RU'


if __name__ == '__main__':
    app.run()