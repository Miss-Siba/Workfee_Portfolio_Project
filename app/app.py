from flask import Flask, render_template, request, redirect, url_for, session
from flask_mail import Mail, Message
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'default_secret_key')

# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'your_mysql_password'
app.config['MYSQL_DB'] = 'flask_app_db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///example.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
mail = Mail(app)

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
    return User.query.get(int(user_id))

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
            return redirect(url_for('profile'))
        else:
            return 'Invalid username or password'
    return render_template('login.html')

@app.route('/profile')
@login_required
def profile():
    return f'Logged in as: {current_user.username}'

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/job_listing', methods=['GET', 'POST'])
@login_required
def job_listing():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        # Save job to database
        new_job = Job(title=title, description=description)
        db.session.add(new_job)
        db.session.commit()
        return redirect(url_for('job_listing'))
    else:
        jobs = Job.query.all()
        return render_template('job_listing.html', jobs=jobs)

@app.route('/freelancers')
@login_required
def freelancers():
    freelancers = Freelancer.query.all()
    return render_template('freelancers.html', freelancers=freelancers)

@app.route('/portfolios')
@login_required
def portfolios():
    portfolios = Portfolio.query.all()
    return render_template('portfolios.html', portfolios=portfolios)

@app.route('/help_desk', methods=['GET', 'POST'])
def help_desk():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        problem = request.form['problem']
        # Process form data
        send_help_request(name, email, problem)
        return redirect(url_for('help_request_success'))
    return render_template('help_desk.html')

def send_help_request(name, email, problem):
    msg = Message("Help Request", sender="sender@example.com", recipients=["recipient@example.com"])
    msg.body = f"Name: {name}\nEmail: {email}\nProblem Description: {problem}"
    mail.send(msg)

@app.route('/help_request_success')
def help_request_success():
    return render_template('help_request_success.html')

if __name__ == '__main__':
    app.run(debug=True)
