from flask import Flask, render_template, request, redirect, url_for, session
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['MAIL_SERVER'] = 'smtp.yourmailserver.com'  # Configure your mail server
app.config['MAIL_PORT'] = 587  # Use appropriate port for your mail server
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'your_email@example.com'  # Replace with your email credentials
app.config['MAIL_PASSWORD'] = 'your_email_password'  # Replace with your email password

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'your_mysql_user'
app.config['MYSQL_PASSWORD'] = 'your_mysql_password'
app.config['MYSQL_DB'] = 'flask_app_db'

mail = Mail(app)
mysql = MySQL(app)

# Sample data for job listings
jobs = [
    {"title": "Web Developer", "description": "Design and develop web applications."},
    {"title": "Graphic Designer", "description": "Create visually appealing designs for clients."},
    {"title": "Content Writer", "description": "Write engaging content for various platforms."},
]

# Mock user data
users = {
    "user1": {
        "username": "user1",
        "password": generate_password_hash("password1"),  # Store hashed passwords
        "messages": ["Welcome to your dashboard!"],
        "portfolio": None,
        "avatar": None
    }
}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/freelancers', methods=['GET', 'POST'])
def freelancers_page():
    if resquest.method == 'POST':
        industry = request.form.get('industry')
        query = "SELECT * FROM freelancers WHERE industry = %s"
        cursor.execute(query, (industry,))
        freelancers = cursor.fetchall()
    else:
        query = "SELECT * FROM freelancers"
        cursor.execute(query)
        freelancers = cursor.fetchall()
    return render_template('freelancers.html', freelancers=freelancers)

@app.route('/job_listing', methods=['GET', 'POST'])
def job_listing():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        query = "INSERT INTO jobs (title, description) VALUES (%s, %s)"
        cursor.execute(query, (title, description))
        db.commit()
        return redirect(url_for('job_listing'))
    else:
        query = "SELECT * FROM jobs"
        cursor.execute(query)
        jobs = cursor.fetchall()
        return render_template('job_listing.html', jobs=job)

@app.route('/help-desk', methods=['GET', 'POST'])
def help_desk():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        problem = request.form.get('problem')
        screenshots = request.files.getlist('screenshots')

        # Process the form data (e.g., send email)
        send_help_request(name, email, problem, screenshots)

        return redirect(url_for('help_request_success'))
    return render_template('help_desk.html')

def send_help_request(name, email, problem, screenshots):
    msg = Message('Help Request', sender='your_email@example.com', recipients=['sibaquma@gmail.com'])
    msg.body = f"Name: {name}\nEmail: {email}\nProblem Description: {problem}"
    for screenshot in screenshots:
        msg.attach(screenshot.filename, 'image/png', screenshot.read())
    mail.send(msg)

@app.route('/help-request-success')
def help_request_success():
    return render_template('help_request_success.html')

@app.route('/account', methods=['GET', 'POST'])
def account():
    if 'username' in session:
        username = session['username']
        query = "SELECT *FROM users WHERE username =%s"
        cursor.execute(query, (username,))
        user = cursor.fetchone()
        return render_template('account.html', user=user)
    else:
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            query = "SELECT * FROM users WHERE username = %s"
            cursor.execute(query, (username,))
            user = cursor.fetchone()
            
            if user and check_password_hash(user['password'], password):
                session['username'] = username
                return redirect(url_for('account'))
            return render_template('account.html')

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
    db.commit()
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
        db.commit()

        return redirect(url_for('acount'))

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

@app.route('/change-avatar', methods=['POST'])
def change_avatar():
    if 'username' not in session:
        return redirect(url_for('account'))

    user = users[session['username']]
    file = request.files['avatar']
    if file:
        user['avatar'] = file.filename  # In a real app, save the file and store the path
        return redirect(url_for('account'))

if __name__ == '__main__':
    app.run(debug=True)
