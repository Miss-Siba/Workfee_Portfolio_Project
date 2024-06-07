#!/usr/bin/env python3
""" Flask APP"""


from flask import Flask, render_template, request, redirect, url_for, session
from flask_mail import Mail, Message
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_mysqldb import MySQL
import os
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
from models import User
from models import Portfolio
from models import Job
from models import init_app

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'default_secret_key')

# Flask-Login Configuration
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'account'

# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'flask_app_db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///example.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Flask-Mail Configuration
mail = Mail(app)
mysql = MySQL(app)
db = SQLAlchemy(app)

def create_app(config_name='default'):
    app = Flask(__name__)
     # Configurations
    if config_name == 'development':
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///development.db'
        app.config['DEBUG'] = True
    elif config_name == 'testing':
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///testing.db'
        app.config['TESTING'] = True
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
    
    # Initialize extensions
    db.init_app(app)

    return app

app = create_app()

# Define User class for Flask-Login
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(user_id):
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))
    user = cursor.fetchone()
    if user:
        return User(id=user['id'], username=user['username'], password=user['password'])
    return None

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('account'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('account.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('You have successfully registered!', 'success')
        return redirect(url_for('login'))
    return render_template('account.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/account')
@login_required
def account():
    user = User.query.filter_by(username=session.get('username')).first()
    return render_template('account.html', user=user)

@app.route('/profile')
@login_required
def profile():
    return f'Logged in as: {current_user.username}'

@app.route('/job_listing', methods=['GET', 'POST'])
@login_required
def job_listing():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        query = "INSERT INTO jobs (title, description) VALUES (%s, %s)"
        cursor.execute(query, (title, description))
        mysql.connection.commit()
        return redirect(url_for('job_listing'))
    else:
        query = "SELECT * FROM jobs"
        cursor.execute(query)
        jobs = cursor.fetchall()
        cursor.close()
        return render_template('job_listing.html', jobs=jobs)

@app.route('/freelancers')
@login_required
def freelancers():
    cursor = mysql.connection.cursor()
    if request.method == 'POST':
        industry = request.form.get('industry')
        query = "SELECT * FROM freelancers WHERE industry = %s"
        cursor.execute(query, (industry,))
        freelancers = cursor.fetchall()
    else:
        query = "SELECT * FROM freelancers"
        cursor.execute(query)
        freelancers = cursor.fetchall()
    cursor.close()
    return render_template('freelancers.html', freelancers=freelancers)


@app.route('/portfolios')
@login_required
def portfolios():
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM portfolios')
    portfolios = cursor.fetchall()
    return render_template('freelancers.html', portfolios=portfolios)

@app.route('/upload-portfolio', methods=['POST'])
@login_required
def upload_portfolio():
    user_id = current_user.id
    file = request.files['portfolio']
    if file:
        filename = file.filename
        portfolio_path = os.path.join('uploads', filename)
        file.save(portfolio_path)

        cursor = mysql.connection.cursor()
        query = "UPDATE users SET portfolio = %s WHERE id = %s"
        cursor.execute(query, (portfolio_path, user_id))
        mysql.connection.commit()

        return redirect(url_for('account'))

@app.route('/update-password', methods=['POST'])
@login_required
def update_password():
    user_id = current_user.id
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')

    cursor = mysql.connection.cursor()
    query = "SELECT * FROM users WHERE id = %s"
    cursor.execute(query, (user_id,))
    user = cursor.fetchone()

    if user and check_password_hash(user['password'], current_password):
        new_hashed_password = generate_password_hash(new_password)
        query = "UPDATE users SET password = %s WHERE id = %s"
        cursor.execute(query, (new_hashed_password, user_id))
        mysql.connection.commit()
        return redirect(url_for('account'))
    else:
        return "Incorrect current password", 403

@app.route('/change-avatar', methods=['POST'])
@login_required
def change_avatar():
    user_id = current_user.id
    file = request.files['avatar']
    if file:
        filename = file.filename
        avatar_path = os.path.join('uploads', filename)
        file.save(avatar_path)

        cursor = mysql.connection.cursor()
        query = "UPDATE users SET avatar = %s WHERE id = %s"
        cursor.execute(query, (avatar_path, user_id))
        mysql.connection.commit()

        return redirect(url_for('account'))

@app.route('/help_desk', methods=['GET', 'POST'])
def help_desk():
    cursor = mysql.connection.cursor()
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        problem = request.form.get('problem')
        screenshots = request.files.getlist('screenshots')

        # Process the form data (e.g., send email)
        send_help_request(name, email, problem, screenshots)
        cursor.close()
        return redirect(url_for('help_request_success'))
    return render_template('help_desk.html')


def send_help_request(name, email, problem):
    msg = Message(
        subject="Help Request",
        sender="Excited User <mailgun@sandbox70e3f4405bfb461d9938c3d97dae5318.mailgun.org>",
        recipients=["sibaquma@gmail.com"],
        body=f"Name: {name}\nEmail: {email}\nProblem Description: {problem}"
    )
    for screenshot in screenshots:
        msg.attach(screenshot.filename, 'image/png', screenshot.read())
    mail.send(msg)

@app.route('/help_request_success')
def help_request_success():
    return render_template('help_desk.html')

@app.route('/users')
@login_required
def users():
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM users')
    users = cursor.fetchall()
    return render_template('users.html', users=users)

@app.route('/register', methods=['POST'])
def register():
    username = request.form.get('reg_username')
    password = request.form.get('reg_password')

    cursor = mysql.connection.cursor()
    query = "SELECT * FROM users WHERE username = %s"
    cursor.execute(query, (username,))
    user = cursor.fetchone()

    if user:
        return "Username already exists", 409

    hashed_password = generate_password_hash(password)
    query = "INSERT INTO users (username, password) VALUES (%s, %s)"
    cursor.execute(query, (username, hashed_password))
    mysql.connection.commit()
    session['username'] = username
    return redirect(url_for('account'))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run()

