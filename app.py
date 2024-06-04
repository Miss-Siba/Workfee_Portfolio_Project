#!/usr/bin/python3
"""
app
"""
from flask import Flask, render_template, request, redirect, url_for, session
from flask_mail import Mail, Message
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from MySQLdb.cursors import DictCursor
import re
from flask_mysqldb import MySQL
import os
from flask_sqlalchemy import SQLAlchemy
from models import db, User, Portfolio, Job, Message, Rating


app = Flask(__name__)
app.secret_key = 'Workfee_dev'

login_manager = LoginManager()
login_manager.init_app(app)

# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ' '
app.config['MYSQL_DB'] = 'flask_app_db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///example.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


mail = Mail(app)
mysql = MySQL(app)


# Define User class for Flask-Login
class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username


@login_manager.user_loader
def load_user(user_id):
    # Load and return a User object based on user_id
    cursor = mysql.connection.cursor(DictCursor)
    cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))
    user_data = cursor.fetchone()
    cursor.close()
    if user_data:
        return User(user_data['id'], user_data['username'])
    return None


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/account', methods=['GET', 'POST'])
def account():
    login_msg = 'Welcome back!'
    signup_msg = 'Join our community!'

    if request.method == 'POST':
        if 'login' in request.form:
            # Handle login form
            username = request.form['username']
            password = request.form['password']
            if not username or not password:
                login_msg = 'Please fill out both fields!'
            else:
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute('SELECT * FROM users WHERE username = %s AND password = %s', (username, password))
                user = cursor.fetchone()
                if user and check_password_hash(user['password'], password):
                    # Login successful, use Flask-Login's login_user function
                    login_user(User(user['id'], user['username']))
                    session['loggedin'] = True
                    session['id'] = user['id']
                    session['username'] = user['username']
                    return redirect(url_for('profile'))
                else:
                    login_msg = 'Invalid username or password!'

        elif 'signup' in request.form:
            # Handle signup form
            username = request.form['username']
            password = request.form['password']
            if not username or not password:
                signup_msg = 'Please fill out both fields!'
            else:
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
                account = cursor.fetchone()
                if account:
                    signup_msg = 'Account already exists!'
                else:
                    cursor.execute('INSERT INTO users (username, password) VALUES (%s, %s)', (username, password))
                    mysql.connection.commit()
                    signup_msg = 'You have successfully registered!'
                    return redirect(url_for('account'))

    return render_template('account.html', login_msg=login_msg, signup_msg=signup_msg)


@app.route('/profile')
def profile():
    return f'Logged in as: {current_user.username}'


@app.route('/freelancers', methods=['GET', 'POST'])
def freelancers_page():
    cursor = mysql.connection.cursor(DictCursor)
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


@app.route('/job_listing', methods=['GET', 'POST'])
def job_listing():
    cursor = mysql.connection.cursor(DictCursor)
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


@app.route('/help-desk', methods=['GET', 'POST'])
def help_desk():
    cursor = mysql.connection.cursor(DirctCursor)
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


def send_help_request(name, email, problem, screenshots):
    msg = Message("Help Request", sender="mailgun@sandbox70e3f4405bfb461d9938c3d97dae5318.mailgun.org", recipients=["your-email@example.com"])
    msg.body = f"Name: {name}\nEmail: {email}\nProblem Description: {problem}"
    for screenshot in screenshots:
        msg.attach(screenshot.filename, 'image/png', screenshot.read())
    mail.send(msg)


@app.route('/help-request-success')
def help_request_success():
    return render_template('help_request_success.html')


@app.route('/register', methods=['POST'])
def register():
    username = request.form.get('reg_username')
    password = request.form.get('reg_password')

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


@app.route('/upload-portfolio', methods=['POST'])
def upload_portfolio():
    if 'username' not in session:
        return redirect(url_for('account'))

    user = users[session['username']]
    file = request.files['portfolio']
    if file:
        filename = file.filename
        portfolio_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(portfolio_path)

        query = "UPDATE users SET portfolio = %s WHERE username = %s"
        cursor.execute(query, (portfolio_path, user))
        mysql.connection.commit()

        return redirect(url_for('account'))


@app.route('/update-password', methods=['POST'])
def update_password():
    if 'username' not in session:
        return redirect(url_for('account'))

    user = users[session['username']]
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')

    if check_password_hash(user['password'], current_password):
        user['password'] = generate_password_hash(new_password)
        return redirect(url_for('account'))
    else:
        return "Incorrect current password", 403


@app.route('/users')
def users():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM user')
    users = cursor.fetchall()
    return render_template('users.html', users=users)


@app.route('/change-avatar', methods=['POST'])
def change_avatar():
    if 'username' not in session:
        return redirect(url_for('account'))

    user = users[session['username']]
    file = request.files['avatar']
    if file:
        user['avatar'] = file.filename  # In a real app, save the file and store the path
        return redirect(url_for('account'))


@app.route('/logout')
def logout():
    logout_user()
    session.clear()
    return redirect(url_for('account'))


if __name__ == '__main__':
    app.run(debug=True)
