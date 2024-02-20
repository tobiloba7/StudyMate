from flask import Flask, render_template, request, url_for, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from sqlalchemy.exc import IntegrityError 
from werkzeug.security import generate_password_hash, check_password_hash
import requests
from datetime import datetime

# Initialize the Flask application
app = Flask(__name__)

# Configure the SQLAlchemy database URI and set a secret key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///study_items.db'
app.config['SECRET_KEY'] = 'code_cave'  

# Initialize the SQLAlchemy extension and the LoginManager
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Define the User model with UserMixin for user authentication
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)  # Hashed password
    tasks = db.relationship('Task', backref='user', lazy=True)

    # Method to set the hashed password
    def set_password(self, password):
        self.password = generate_password_hash(password)

    # Method to check the hashed password
    def check_password(self, password):
        return check_password_hash(self.password, password)

# Define the Task model
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task = db.Column(db.String(200), nullable=False)
    done = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# Create database tables
with app.app_context():
    db.create_all()

# User loader function for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Route for user login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        # Verify the user's password
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('layout'))  # Redirect to layout after successful login
        else:
            flash('Incorrect username or password. Please try again.', 'error')

    return render_template('login.html')

# Route for user registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # Check if the password meets the 8-character requirement
        if len(password) < 8:
            flash('Password must be at least 8 characters long.', 'error')
            return redirect(url_for('register'))

        try:
            # Create a new user with hashed password and add to the database
            new_user = User(username=username, email=email)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful. You can now log in.', 'success')
            return redirect(url_for('login'))
        except IntegrityError as e:
            # Handle integrity error (username or email already taken)
            db.session.rollback()
            flash('Username is already taken - please pick another one.', 'error')

    return render_template('register.html')

# Route for layout
@app.route('/layout')
@login_required
def layout():
    return render_template('layout.html')

# Route to display user tasks on the homepage
@app.route('/')
@login_required
def index():
    tasks = current_user.tasks
   # Retrieve the first five tasks for the current user
    tasks = Task.query.filter_by(user_id=current_user.id).limit(5).all()
    
    # Retrieve all tasks for the current user beyond the first five
    remaining_tasks = Task.query.filter_by(user_id=current_user.id).offset(5).all()
    username = current_user.username  # Get the current user's username

    try:
        response = requests.get('http://worldtimeapi.org/api/timezone/Africa/Lagos')
        response.raise_for_status()  # Raise an HTTPError for bad responses
        data = response.json()

        # Extract the 'datetime' value and convert it to a more readable format
        api_datetime = data['datetime']
        formatted_datetime = datetime.strptime(api_datetime, '%Y-%m-%dT%H:%M:%S.%f%z')

        # Format the datetime as "Saturday December 02 2023 HH:MM"
        formatted_datetime_str = formatted_datetime.strftime('%A %B %d %Y %H:%M')

        datetime_info = formatted_datetime_str

    except ValueError as e:
        datetime_info = "N/A"
    except Exception as e:
        datetime_info = "N/A"

    return render_template('index.html', tasks=tasks, remaining_tasks=remaining_tasks, username=username, datetime_info=datetime_info)

# Route to add a new task
@app.route('/add', methods=['POST'])
@login_required
def add():
    task_text = request.form['study_items'].strip()  # Remove leading/trailing whitespace

    if not task_text:  # Check if the task is empty after stripping whitespace
        flash('Cannot add an empty study item. Please enter a task.', 'error')
        return redirect(url_for('index'))
    

    new_task = Task(task=task_text, user_id=current_user.id)
    db.session.add(new_task)
    db.session.commit()

    return redirect(url_for('index'))

# Route to move to completed
@app.route('/completed')
def completed():
    completed_tasks = Task.query.filter_by(done=True).all()
    return render_template('completed_routines.html', completed_task=completed_tasks)

# Route to edit an existing task
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    task = Task.query.get(id)
    if request.method == 'POST':
        task.task = request.form['study_items']
        db.session.commit()
        return redirect(url_for('index'))
    else:
        return render_template('edit.html', task=task)

# Route to mark a task as done or undone
@app.route('/check/<int:id>')
@login_required
def check(id):
    task = Task.query.get(id)
    task.done = True
    # task.done = not task.done
    db.session.commit()
    return redirect(url_for('completed'))
    

# Route to delete a task
@app.route('/delete/<int:id>')
@login_required
def delete(id):
    task = Task.query.get(id)
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for('index'))

# Route for user logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))



# Run the application in debug mode
if __name__ == '__main__':
    app.run(debug=True)



